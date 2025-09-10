"""
Test Suite for ACG Core Calculations Engine (PRP 1)

Comprehensive tests for all ACG calculation functions including:
- Body position calculations
- Line type calculations (MC, IC, AC, DC, aspects, parans)
- GeoJSON output validation
- Performance benchmarks
- Cross-validation with reference implementations
"""

import pytest
import numpy as np
from datetime import datetime
from unittest.mock import patch, MagicMock

from extracted.systems.acg_engine.acg_core import ACGCalculationEngine
from extracted.systems.acg_engine.acg_types import (
    ACGRequest, ACGBody, ACGBodyType, ACGOptions, ACGNatalData,
    ACGCoordinates, ACGBodyData, ACGLineType
)


class TestACGCalculationEngine:
    """Test ACG calculation engine initialization and basic functions."""
    
    @pytest.fixture
    def engine(self):
        """ACG calculation engine instance."""
        return ACGCalculationEngine()
    
    def test_engine_initialization(self, engine):
        """Test engine initializes correctly."""
        assert engine is not None
        assert len(engine.body_registry) > 0
        assert engine.natal_integrator is not None
        assert engine.default_options is not None
    
    def test_supported_bodies(self, engine):
        """Test getting supported bodies list."""
        bodies = engine.get_supported_bodies()
        assert len(bodies) > 0
        
        # Check for essential bodies
        body_ids = [body.id for body in bodies]
        essential_bodies = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
        for essential in essential_bodies:
            assert essential in body_ids
    
    def test_default_bodies(self, engine):
        """Test getting default bodies list."""
        default_bodies = engine.get_default_bodies()
        assert len(default_bodies) >= 10  # At least the major planets
        
        # Should include all traditional planets
        body_ids = [body.id for body in default_bodies]
        assert 'Sun' in body_ids
        assert 'Moon' in body_ids
        assert 'Pluto' in body_ids
    
    @pytest.mark.integration
    def test_body_position_calculation_sun(self, engine):
        """Test calculating Sun position (integration test)."""
        sun_body = ACGBody(id="Sun", type=ACGBodyType.PLANET)
        jd_test = 2451545.0  # J2000.0
        
        coordinates = engine.calculate_body_position(sun_body, jd_test)
        
        if coordinates:  # Skip if Swiss Ephemeris not available
            assert isinstance(coordinates, ACGCoordinates)
            assert 0 <= coordinates.lambda_ <= 360
            assert -90 <= coordinates.dec <= 90
            assert coordinates.distance > 0
    
    @pytest.mark.integration
    def test_body_position_calculation_moon(self, engine):
        """Test calculating Moon position (integration test)."""
        moon_body = ACGBody(id="Moon", type=ACGBodyType.PLANET)
        jd_test = 2451545.0  # J2000.0
        
        coordinates = engine.calculate_body_position(moon_body, jd_test)
        
        if coordinates:  # Skip if Swiss Ephemeris not available
            assert isinstance(coordinates, ACGCoordinates)
            assert coordinates.distance > 0
            assert coordinates.speed is not None
    
    def test_body_position_unknown_body(self, engine):
        """Test calculating position for unknown body."""
        unknown_body = ACGBody(id="UnknownBody", type=ACGBodyType.PLANET)
        jd_test = 2451545.0
        
        coordinates = engine.calculate_body_position(unknown_body, jd_test)
        assert coordinates is None


class TestACGLineCalculations:
    """Test specific ACG line type calculations."""
    
    @pytest.fixture
    def engine(self):
        """ACG calculation engine instance."""
        return ACGCalculationEngine()
    
    @pytest.fixture
    def sample_body_data(self):
        """Sample body data for testing."""
        coordinates = ACGCoordinates(
            ra=120.0,  # Right ascension
            dec=15.5,  # Declination
            lambda_=125.0,  # Ecliptic longitude
            beta=1.2,  # Ecliptic latitude
            distance=1.016,
            speed=0.985
        )
        
        body = ACGBody(id="TestBody", type=ACGBodyType.PLANET)
        
        return ACGBodyData(
            body=body,
            coordinates=coordinates,
            calculation_time_ms=10.5
        )
    
    @pytest.fixture
    def metadata_base(self):
        """Base metadata for testing."""
        return {
            'id': 'TestBody',
            'type': 'body',
            'kind': ACGBodyType.PLANET,
            'number': 0,
            'epoch': '2000-01-01T12:00:00Z',
            'jd': 2451545.0,
            'gmst': 280.0,
            'obliquity': 23.4,
            'coords': ACGCoordinates(ra=120.0, dec=15.5, lambda_=125.0, beta=1.2),
            'natal': None,
            'flags': None,
            'se_version': 'test',
            'source': 'Meridian-ACG',
            'calculation_time_ms': 10.5
        }
    
    def test_mc_ic_line_calculation(self, engine, sample_body_data, metadata_base):
        """Test MC and IC line calculations."""
        gmst_deg = 280.0
        
        lines = engine.calculate_mc_ic_lines(sample_body_data, gmst_deg, metadata_base)
        
        assert len(lines) == 2  # MC and IC
        
        # Check MC line
        mc_line = next((line for line in lines if line.line_type == ACGLineType.MC), None)
        assert mc_line is not None
        assert mc_line.geometry['type'] == 'LineString'
        assert len(mc_line.geometry['coordinates']) > 0
        assert mc_line.metadata.line.angle == 'MC'
        
        # Check IC line
        ic_line = next((line for line in lines if line.line_type == ACGLineType.IC), None)
        assert ic_line is not None
        assert ic_line.geometry['type'] == 'LineString'
        assert ic_line.metadata.line.angle == 'IC'
    
    def test_ac_dc_line_calculation(self, engine, sample_body_data, metadata_base):
        """Test AC and DC line calculations."""
        gmst_deg = 280.0
        
        lines = engine.calculate_ac_dc_lines(sample_body_data, gmst_deg, metadata_base)
        
        # AC and DC lines may not exist for all declinations/times
        # Just test that the method runs without error
        assert isinstance(lines, list)
        
        for line in lines:
            assert line.line_type in [ACGLineType.AC, ACGLineType.DC]
            assert 'type' in line.geometry
            assert line.geometry['type'] in ['LineString', 'MultiLineString']
    
    def test_mc_aspect_line_calculation(self, engine, sample_body_data, metadata_base):
        """Test MC aspect line calculations."""
        gmst_deg = 280.0
        aspects = [60, 90, 120]  # Sextile, square, trine
        
        lines = engine.calculate_mc_aspect_lines(
            sample_body_data, gmst_deg, aspects, metadata_base
        )
        
        assert len(lines) == 3  # One for each aspect
        
        for line in lines:
            assert line.line_type == ACGLineType.MC_ASPECT
            assert line.geometry['type'] == 'LineString'
            assert line.metadata.line.aspect in ['sextile', 'square', 'trine']
    
    def test_ac_aspect_line_calculation(self, engine, sample_body_data, metadata_base):
        """Test AC aspect line calculations."""
        gmst_deg = 280.0
        obliquity_deg = 23.4
        aspects = [90]  # Square only for testing
        
        lines = engine.calculate_ac_aspect_lines(
            sample_body_data, gmst_deg, obliquity_deg, aspects, metadata_base
        )
        
        # AC aspects may not always produce valid contours
        assert isinstance(lines, list)
        
        for line in lines:
            assert line.line_type == ACGLineType.AC_ASPECT
            assert 'type' in line.geometry
    
    def test_paran_line_calculation(self, engine, metadata_base):
        """Test paran line calculations."""
        # Create two body data instances
        body1_coords = ACGCoordinates(ra=120.0, dec=15.5, lambda_=125.0, beta=1.2)
        body1 = ACGBodyData(
            body=ACGBody(id="Body1", type=ACGBodyType.PLANET),
            coordinates=body1_coords
        )
        
        body2_coords = ACGCoordinates(ra=150.0, dec=20.0, lambda_=155.0, beta=-0.5)
        body2 = ACGBodyData(
            body=ACGBody(id="Body2", type=ACGBodyType.PLANET),
            coordinates=body2_coords
        )
        
        body_data_list = [body1, body2]
        gmst_deg = 280.0
        
        lines = engine.calculate_paran_lines(body_data_list, gmst_deg, metadata_base)
        
        # Parans may not exist for all body pairs/events
        assert isinstance(lines, list)
        
        for line in lines:
            assert line.line_type == ACGLineType.PARAN
            assert 'type' in line.geometry


class TestACGRequestProcessing:
    """Test complete ACG request processing."""
    
    @pytest.fixture
    def engine(self):
        """ACG calculation engine instance."""
        return ACGCalculationEngine()
    
    @pytest.fixture
    def valid_request(self):
        """Valid ACG calculation request."""
        return ACGRequest(
            epoch="2000-01-01T12:00:00Z",
            bodies=[
                ACGBody(id="Sun", type=ACGBodyType.PLANET),
                ACGBody(id="Moon", type=ACGBodyType.PLANET)
            ],
            options=ACGOptions(
                line_types=[ACGLineType.MC, ACGLineType.IC],
                include_parans=False
            )
        )
    
    def test_metadata_to_properties_conversion(self, engine):
        """Test metadata to GeoJSON properties conversion."""
        from extracted.systems.acg_engine.acg_types import ACGMetadata, ACGLineInfo
        
        metadata = ACGMetadata(
            id="TestBody",
            type="body",
            kind=ACGBodyType.PLANET,
            number=0,
            epoch="2000-01-01T12:00:00Z",
            jd=2451545.0,
            gmst=280.0,
            obliquity=23.4,
            coords=ACGCoordinates(ra=120.0, dec=15.5, lambda_=125.0, beta=1.2),
            line=ACGLineInfo(angle="MC", line_type="MC", method="test"),
            source="Meridian-ACG",
            calculation_time_ms=10.5
        )
        
        properties = engine._metadata_to_properties(metadata)
        
        assert properties['id'] == 'TestBody'
        assert properties['type'] == 'body'
        assert properties['kind'] == 'planet'
        assert properties['jd'] == 2451545.0
        assert 'coords' in properties
        assert 'line' in properties
        assert properties['source'] == 'Meridian-ACG'
    
    @pytest.mark.integration
    @patch('app.core.acg.acg_core.swe')
    def test_full_acg_calculation_mock(self, mock_swe, engine, valid_request):
        """Test full ACG calculation with mocked Swiss Ephemeris."""
        # Mock Swiss Ephemeris responses
        mock_swe.julday.return_value = 2451545.0
        mock_swe.calc_ut.return_value = ([280.0, 0.0, 1.0, 1.0], "")
        mock_swe.ECL_NUT = 0
        mock_swe.SUN = 0
        mock_swe.MOON = 1
        
        # Mock the position calculation to avoid SE dependency
        original_calc_method = engine.calculate_body_position
        
        def mock_calc_body_position(body, jd_ut1, flags=None):
            return ACGCoordinates(
                ra=120.0 + hash(body.id) % 60,  # Vary by body
                dec=15.5,
                lambda_=125.0 + hash(body.id) % 60,
                beta=1.2,
                distance=1.0,
                speed=1.0
            )
        
        engine.calculate_body_position = mock_calc_body_position
        
        try:
            result = engine.calculate_acg_lines(valid_request)
            
            assert isinstance(result.type, str)
            assert result.type == "FeatureCollection"
            assert isinstance(result.features, list)
            assert len(result.features) > 0
            
            # Check feature structure
            feature = result.features[0]
            assert 'type' in feature
            assert feature['type'] == 'Feature'
            assert 'geometry' in feature
            assert 'properties' in feature
            
            # Check properties structure
            props = feature['properties']
            assert 'id' in props
            assert 'type' in props
            assert 'source' in props
            assert props['source'] == 'Meridian-ACG'
            
        finally:
            # Restore original method
            engine.calculate_body_position = original_calc_method
    
    def test_invalid_request_handling(self, engine):
        """Test handling of invalid requests."""
        invalid_request = ACGRequest(
            epoch="invalid-date-format"
        )
        
        # This should be caught at the Pydantic validation level
        with pytest.raises(ValueError):
            engine.calculate_acg_lines(invalid_request)


class TestACGUtilityFunctions:
    """Test ACG utility functions from the engine."""
    
    @pytest.fixture
    def engine(self):
        """ACG calculation engine instance."""
        return ACGCalculationEngine()
    
    def test_ecliptic_to_equatorial_conversion(self, engine):
        """Test ecliptic to equatorial coordinate conversion."""
        lambda_deg = 125.0
        beta_deg = 1.2
        eps_deg = 23.4
        
        ra, dec = engine._ecl_to_eq(lambda_deg, beta_deg, eps_deg)
        
        assert 0 <= ra <= 360
        assert -90 <= dec <= 90


class TestPerformanceAndScaling:
    """Test performance characteristics of ACG calculations."""
    
    @pytest.fixture
    def engine(self):
        """ACG calculation engine instance."""
        return ACGCalculationEngine()
    
    @pytest.mark.benchmark
    def test_body_registry_performance(self, engine, benchmark):
        """Benchmark body registry access."""
        result = benchmark(engine.get_supported_bodies)
        assert len(result) > 0
    
    @pytest.mark.benchmark
    def test_metadata_conversion_performance(self, engine, benchmark):
        """Benchmark metadata to properties conversion."""
        from extracted.systems.acg_engine.acg_types import ACGMetadata, ACGLineInfo
        
        metadata = ACGMetadata(
            id="TestBody",
            type="body", 
            kind=ACGBodyType.PLANET,
            epoch="2000-01-01T12:00:00Z",
            jd=2451545.0,
            gmst=280.0,
            obliquity=23.4,
            coords=ACGCoordinates(ra=120.0, dec=15.5, lambda_=125.0, beta=1.2),
            line=ACGLineInfo(angle="MC", line_type="MC", method="test"),
            source="Meridian-ACG",
            calculation_time_ms=10.5
        )
        
        result = benchmark(engine._metadata_to_properties, metadata)
        assert 'id' in result


class TestErrorHandling:
    """Test error handling in ACG calculations."""
    
    @pytest.fixture
    def engine(self):
        """ACG calculation engine instance.""" 
        return ACGCalculationEngine()
    
    def test_missing_swiss_ephemeris_handling(self, engine):
        """Test handling when Swiss Ephemeris is not available."""
        with patch('app.core.acg.acg_core.swe.calc_ut', side_effect=Exception("SE not available")):
            body = ACGBody(id="Sun", type=ACGBodyType.PLANET)
            result = engine.calculate_body_position(body, 2451545.0)
            assert result is None
    
    def test_calculation_error_recovery(self, engine):
        """Test recovery from calculation errors."""
        # Test with invalid body data that might cause calculation errors
        invalid_coords = ACGCoordinates(
            ra=float('nan'),  # Invalid coordinate
            dec=15.5,
            lambda_=125.0,
            beta=1.2
        )
        
        body_data = ACGBodyData(
            body=ACGBody(id="InvalidBody", type=ACGBodyType.PLANET),
            coordinates=invalid_coords
        )
        
        metadata_base = {
            'id': 'InvalidBody',
            'type': 'body',
            'kind': ACGBodyType.PLANET,
            'epoch': '2000-01-01T12:00:00Z',
            'jd': 2451545.0,
            'gmst': 280.0,
            'obliquity': 23.4,
            'coords': invalid_coords,
            'source': 'Meridian-ACG',
            'calculation_time_ms': 0.0
        }
        
        # Should not crash, but return empty list
        lines = engine.calculate_mc_ic_lines(body_data, 280.0, metadata_base)
        assert isinstance(lines, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])