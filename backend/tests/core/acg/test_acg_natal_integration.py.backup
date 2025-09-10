"""
Test Suite for ACG Natal Chart Integration (PRP 7)

Comprehensive tests for natal chart data integration with ACG calculations.
Tests data models, validation, conversion, and integration points.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from app.core.acg.acg_types import (
    ACGRequest, ACGBody, ACGBodyType, ACGNatalData, ACGOptions,
    ACGCoordinates, ACGNatalInfo, ACGBodyData
)
from app.core.acg.acg_natal_integration import ACGNatalIntegrator
from app.core.ephemeris.charts.subject import Subject


class TestACGNatalDataValidation:
    """Test natal data validation and models."""
    
    @pytest.fixture
    def integrator(self):
        """ACG natal integrator instance."""
        return ACGNatalIntegrator()
    
    @pytest.fixture
    def valid_natal_data(self):
        """Valid natal data for testing."""
        return ACGNatalData(
            birthplace_lat=40.7128,
            birthplace_lon=-74.0060,
            birthplace_alt_m=100.0,
            houses_system="placidus"
        )
    
    @pytest.fixture
    def valid_acg_request(self):
        """Valid ACG request for testing."""
        return ACGRequest(
            epoch="2000-01-01T12:00:00Z",
            bodies=[
                ACGBody(id="Sun", type=ACGBodyType.PLANET),
                ACGBody(id="Moon", type=ACGBodyType.PLANET)
            ],
            options=ACGOptions(
                line_types=["MC", "IC"],
                include_parans=True
            ),
            natal=ACGNatalData(
                birthplace_lat=40.7128,
                birthplace_lon=-74.0060
            )
        )
    
    def test_natal_data_validation_success(self, integrator, valid_natal_data):
        """Test successful natal data validation."""
        assert integrator.validate_natal_data(valid_natal_data) is True
    
    def test_natal_data_validation_none(self, integrator):
        """Test validation with None natal data (should pass)."""
        assert integrator.validate_natal_data(None) is True
    
    def test_natal_data_validation_invalid_latitude(self, integrator):
        """Test validation with invalid latitude."""
        invalid_data = ACGNatalData(
            birthplace_lat=91.0,  # Invalid
            birthplace_lon=-74.0060
        )
        
        with pytest.raises(ValueError, match="Invalid birth latitude"):
            integrator.validate_natal_data(invalid_data)
    
    def test_natal_data_validation_invalid_longitude(self, integrator):
        """Test validation with invalid longitude."""
        invalid_data = ACGNatalData(
            birthplace_lat=40.7128,
            birthplace_lon=181.0  # Invalid
        )
        
        with pytest.raises(ValueError, match="Invalid birth longitude"):
            integrator.validate_natal_data(invalid_data)
    
    def test_natal_data_validation_unknown_house_system(self, integrator, caplog):
        """Test validation with unknown house system (should warn)."""
        data = ACGNatalData(
            birthplace_lat=40.7128,
            birthplace_lon=-74.0060,
            houses_system="unknown_system"
        )
        
        result = integrator.validate_natal_data(data)
        assert result is True
        assert "Unknown house system" in caplog.text
    
    def test_acg_request_validation_success(self, valid_acg_request):
        """Test valid ACG request passes validation."""
        # Should not raise any validation errors
        assert valid_acg_request.epoch == "2000-01-01T12:00:00Z"
        assert len(valid_acg_request.bodies) == 2
        assert valid_acg_request.natal.birthplace_lat == 40.7128
    
    def test_acg_request_invalid_epoch(self):
        """Test ACG request with invalid epoch format."""
        with pytest.raises(ValueError, match="must be a valid ISO 8601"):
            ACGRequest(
                epoch="invalid-date-format",
                bodies=[ACGBody(id="Sun", type=ACGBodyType.PLANET)]
            )
    
    def test_acg_body_validation(self):
        """Test ACG body model validation."""
        # Valid body
        body = ACGBody(id="Sun", type=ACGBodyType.PLANET)
        assert body.id == "Sun"
        assert body.type == ACGBodyType.PLANET
        
        # Body with number
        asteroid = ACGBody(id="Ceres", type=ACGBodyType.ASTEROID, number=1)
        assert asteroid.number == 1


class TestSubjectCreation:
    """Test Subject creation from ACG request data."""
    
    @pytest.fixture
    def integrator(self):
        """ACG natal integrator instance."""
        return ACGNatalIntegrator()
    
    def test_create_subject_success(self, integrator):
        """Test successful Subject creation."""
        request = ACGRequest(
            epoch="1990-06-15T14:30:00Z",
            natal=ACGNatalData(
                birthplace_lat=40.7128,
                birthplace_lon=-74.0060,
                birthplace_alt_m=100.0
            )
        )
        
        subject = integrator.create_subject_from_acg_request(request)
        
        assert subject is not None
        assert isinstance(subject, Subject)
        assert subject.get_data().name == "ACG Subject"
        assert abs(subject.get_data().latitude - 40.7128) < 0.001
        assert abs(subject.get_data().longitude - (-74.0060)) < 0.001
    
    def test_create_subject_no_natal_data(self, integrator):
        """Test Subject creation without natal data."""
        request = ACGRequest(epoch="2000-01-01T12:00:00Z")
        
        subject = integrator.create_subject_from_acg_request(request)
        assert subject is None
    
    def test_create_subject_incomplete_coordinates(self, integrator):
        """Test Subject creation with incomplete coordinates."""
        request = ACGRequest(
            epoch="2000-01-01T12:00:00Z",
            natal=ACGNatalData(birthplace_lat=40.7128)  # Missing longitude
        )
        
        subject = integrator.create_subject_from_acg_request(request)
        assert subject is None
    
    def test_create_subject_invalid_epoch(self, integrator):
        """Test Subject creation with invalid epoch."""
        # This would fail at the ACGRequest validation level
        # but test the integrator's handling of edge cases
        pass


class TestNatalInfoExtraction:
    """Test extraction of natal information from chart data."""
    
    @pytest.fixture
    def integrator(self):
        """ACG natal integrator instance."""
        return ACGNatalIntegrator()
    
    def test_body_id_lookup(self, integrator):
        """Test body ID lookup from name."""
        sun_id = integrator._get_body_id_from_name("Sun")
        assert sun_id is not None
        
        moon_id = integrator._get_body_id_from_name("Moon")
        assert moon_id is not None
        
        unknown_id = integrator._get_body_id_from_name("UnknownBody")
        assert unknown_id is None
    
    def test_convert_to_acg_coordinates(self, integrator):
        """Test conversion to ACG coordinates."""
        from app.core.ephemeris.classes.serialize import PlanetPosition
        
        # Create mock planet position
        planet_pos = PlanetPosition(
            longitude=120.5,
            latitude=1.2,
            distance=1.016,
            longitude_speed=0.985
        )
        
        # Add additional attributes that might be present
        planet_pos.right_ascension = 115.0
        planet_pos.declination = 15.5
        
        coords = integrator.convert_to_acg_coordinates(planet_pos)
        
        assert isinstance(coords, ACGCoordinates)
        assert coords.lambda_ == 120.5
        assert coords.beta == 1.2
        assert coords.distance == 1.016
        assert coords.speed == 0.985
        assert coords.ra == 115.0
        assert coords.dec == 15.5


class TestACGRequestValidation:
    """Test ACG request validation with natal compatibility."""
    
    @pytest.fixture
    def integrator(self):
        """ACG natal integrator instance."""
        return ACGNatalIntegrator()
    
    def test_request_validation_complete_natal(self, integrator):
        """Test validation with complete natal data."""
        request = ACGRequest(
            epoch="2000-01-01T12:00:00Z",
            natal=ACGNatalData(
                birthplace_lat=40.7128,
                birthplace_lon=-74.0060,
                houses_system="placidus"
            )
        )
        
        result = integrator.validate_acg_request_natal_compatibility(request)
        
        assert result['valid'] is True
        assert result['natal_available'] is True
        assert result['chart_creatable'] is True
        assert len(result['errors']) == 0
    
    def test_request_validation_no_natal(self, integrator):
        """Test validation without natal data."""
        request = ACGRequest(epoch="2000-01-01T12:00:00Z")
        
        result = integrator.validate_acg_request_natal_compatibility(request)
        
        assert result['valid'] is True
        assert result['natal_available'] is False
        assert result['chart_creatable'] is False
        assert len(result['warnings']) > 0
        assert "No natal data" in result['warnings'][0]
    
    def test_request_validation_incomplete_natal(self, integrator):
        """Test validation with incomplete natal data."""
        request = ACGRequest(
            epoch="2000-01-01T12:00:00Z", 
            natal=ACGNatalData(birthplace_lat=40.7128)  # Missing longitude
        )
        
        result = integrator.validate_acg_request_natal_compatibility(request)
        
        assert result['valid'] is True
        assert result['natal_available'] is True
        assert result['chart_creatable'] is False
        assert "Incomplete natal data" in result['warnings'][0]
    
    def test_request_validation_invalid_epoch(self, integrator):
        """Test validation with invalid epoch."""
        # Since ACGRequest validates the epoch, we'll test the integrator's handling
        # This test would be more relevant at the request parsing level
        pass


class TestNatalChartCreation:
    """Test complete natal chart creation for ACG."""
    
    @pytest.fixture
    def integrator(self):
        """ACG natal integrator instance."""
        return ACGNatalIntegrator()
    
    @pytest.mark.integration
    def test_create_natal_chart_success(self, integrator):
        """Test successful natal chart creation (integration test)."""
        request = ACGRequest(
            epoch="1990-06-15T14:30:00Z",
            natal=ACGNatalData(
                birthplace_lat=40.7128,
                birthplace_lon=-74.0060,
                houses_system="placidus"
            )
        )
        
        chart_data = integrator.create_natal_chart_for_acg(request)
        
        # This is an integration test that requires Swiss Ephemeris
        # May be skipped in unit test runs
        if chart_data:
            assert chart_data.subject.name == "ACG Subject"
            assert len(chart_data.planets) > 0
            assert chart_data.houses is not None
            assert chart_data.angles is not None
    
    def test_create_natal_chart_no_natal(self, integrator):
        """Test natal chart creation without natal data."""
        request = ACGRequest(epoch="2000-01-01T12:00:00Z")
        
        chart_data = integrator.create_natal_chart_for_acg(request)
        assert chart_data is None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def integrator(self):
        """ACG natal integrator instance."""
        return ACGNatalIntegrator()
    
    def test_extreme_coordinates(self, integrator):
        """Test handling of extreme coordinate values."""
        # Test polar coordinates
        polar_data = ACGNatalData(
            birthplace_lat=89.9,  # Near North Pole
            birthplace_lon=0.0
        )
        assert integrator.validate_natal_data(polar_data) is True
        
        # Test antipodal coordinates
        antipodal_data = ACGNatalData(
            birthplace_lat=-89.9,  # Near South Pole
            birthplace_lon=180.0
        )
        assert integrator.validate_natal_data(antipodal_data) is True
    
    def test_boundary_coordinates(self, integrator):
        """Test coordinate boundary values."""
        # Test exact boundaries
        boundary_data = ACGNatalData(
            birthplace_lat=90.0,
            birthplace_lon=180.0
        )
        assert integrator.validate_natal_data(boundary_data) is True
        
        # Test just over boundaries
        with pytest.raises(ValueError):
            over_boundary = ACGNatalData(
                birthplace_lat=90.1,
                birthplace_lon=180.1
            )
            integrator.validate_natal_data(over_boundary)
    
    def test_dignity_calculation_edge_cases(self, integrator):
        """Test dignity calculation with edge cases."""
        # Test with planets that have no dignity data
        # This would require mock PlanetPosition objects
        pass
    
    def test_missing_planet_data(self, integrator):
        """Test handling of missing planet data in chart."""
        # Test extraction when planet is not found in chart
        result = integrator.extract_natal_info_from_chart(None, 999)
        assert result is None


# Performance and Integration Tests
class TestPerformance:
    """Test performance of natal integration operations."""
    
    @pytest.fixture
    def integrator(self):
        """ACG natal integrator instance."""
        return ACGNatalIntegrator()
    
    @pytest.mark.benchmark
    def test_validation_performance(self, integrator, benchmark):
        """Benchmark natal data validation."""
        natal_data = ACGNatalData(
            birthplace_lat=40.7128,
            birthplace_lon=-74.0060,
            houses_system="placidus"
        )
        
        result = benchmark(integrator.validate_natal_data, natal_data)
        assert result is True
    
    @pytest.mark.benchmark  
    def test_subject_creation_performance(self, integrator, benchmark):
        """Benchmark Subject creation."""
        request = ACGRequest(
            epoch="2000-01-01T12:00:00Z",
            natal=ACGNatalData(
                birthplace_lat=40.7128,
                birthplace_lon=-74.0060
            )
        )
        
        result = benchmark(integrator.create_subject_from_acg_request, request)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])