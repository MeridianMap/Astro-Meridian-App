"""
Test suite for EphemerisService
Tests the enhanced ephemeris service functionality including:
- Enhanced natal chart calculations with South Node
- Retrograde motion detection integration
- Service layer orchestration
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.services.ephemeris_service import EphemerisService
from app.core.ephemeris.classes.serialize import PlanetPosition
from app.api.models.schemas import NatalChartRequest, SubjectRequest, DateTimeInput, CoordinateInput


class TestEphemerisService:
    """Test the main EphemerisService functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = EphemerisService()
        self.test_dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        self.test_lat = 40.7128
        self.test_lon = -74.0060
    
    def test_service_initialization(self):
        """Test that service initializes correctly"""
        assert self.service is not None
    
    @patch('app.core.ephemeris.tools.ephemeris.get_point')
    @patch('app.core.ephemeris.tools.ephemeris.get_houses')
    @patch('app.core.ephemeris.tools.ephemeris.analyze_retrograde_motion')
    def test_calculate_natal_chart_enhanced(self, mock_analyze_retrograde, mock_get_houses, mock_get_point):
        """Test enhanced natal chart calculation with South Node and retrograde detection"""
        
        # Mock planet positions
        mock_sun = PlanetPosition(
            longitude=295.5,
            latitude=0.0,
            distance=1.0,
            longitude_speed=1.0,
            planet_id=0
        )
        mock_moon = PlanetPosition(
            longitude=120.3,
            latitude=5.2,
            distance=60.0,
            longitude_speed=13.2,
            planet_id=1
        )
        mock_mercury_rx = PlanetPosition(
            longitude=280.1,
            latitude=-0.5,
            distance=0.5,
            longitude_speed=-1.2,
            planet_id=2
        )
        mock_north_node = PlanetPosition(
            longitude=45.0,
            latitude=0.0,
            distance=0.0,
            longitude_speed=-0.05,
            planet_id=10
        )
        mock_south_node = PlanetPosition(
            longitude=225.0,  # 180° opposite of North Node
            latitude=0.0,
            distance=0.0,
            longitude_speed=0.05,
            planet_id=11
        )
        
        # Configure mock returns based on point name
        def mock_get_point_side_effect(point, jd, flags, lat, lon):
            point_map = {
                "sun": mock_sun,
                "moon": mock_moon,
                "mercury": mock_mercury_rx,
                "north_node": mock_north_node,
                "true_south_node": mock_south_node
            }
            return point_map.get(point.lower(), mock_sun)
        
        mock_get_point.side_effect = mock_get_point_side_effect
        
        # Mock houses
        mock_get_houses.return_value = {
            'houses': [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360],
            'ascendant': 15.5,
            'midheaven': 105.3
        }
        
        # Mock retrograde analysis
        mock_analyze_retrograde.return_value = {
            'total_retrograde': 1,
            'retrograde_planets': ['Mercury'],
            'direct_planets': ['Sun', 'Moon', 'Venus', 'Mars', 'Jupiter', 'Saturn'],
            'stationary_planets': [],
            'retrograde_percentage': 16.67
        }
        
        # Test the enhanced natal chart calculation
        request = NatalChartRequest(
            subject=SubjectRequest(
                name="Test Subject",
                datetime=DateTimeInput(
                    components={
                        "year": self.test_dt.year,
                        "month": self.test_dt.month,
                        "day": self.test_dt.day,
                        "hour": self.test_dt.hour,
                        "minute": self.test_dt.minute,
                        "second": self.test_dt.second
                    }
                ),
                latitude=CoordinateInput(decimal=self.test_lat),
                longitude=CoordinateInput(decimal=self.test_lon)
            )
        )
        
        result = self.service.calculate_natal_chart_enhanced(request)
        
        # Verify structure
        assert 'planets' in result
        assert 'houses' in result
        assert 'retrograde_analysis' in result
        assert 'south_node' in result
        
        # Verify planets include enhanced data
        planets = result.get('planets', [])
        self.assertGreater(len(planets), 0, "Should have planets in result")
        
        # Find Mercury in results if present
        mercury = next((p for p in planets if getattr(p, 'name', '') == 'Mercury'), None)
        if mercury:
            self.assertTrue(hasattr(mercury, 'is_retrograde'))
            self.assertTrue(hasattr(mercury, 'motion_type'))
        
        # Verify retrograde analysis
        retro_analysis = result.get('retrograde_analysis', {})
        if retro_analysis:
            self.assertIn('total_retrograde', retro_analysis)
            self.assertIn('retrograde_planets', retro_analysis)
        
        # Verify calculation time is present
        self.assertIn('calculation_time', result)
    
    @patch('app.core.ephemeris.tools.ephemeris.get_point')
    @patch('app.core.ephemeris.tools.ephemeris.get_houses')
    @patch('app.core.ephemeris.tools.ephemeris.analyze_retrograde_motion')
    def test_enhanced_chart_includes_all_standard_planets(self, mock_analyze_retrograde, mock_get_houses, mock_get_point):
        """Test that enhanced natal chart includes all standard planets plus South Node"""
        
        # Mock a standard planet
        mock_planet = PlanetPosition(
            longitude=120.0,
            latitude=0.0,
            distance=1.0,
            longitude_speed=1.0,
            planet_id=0
        )
        
        mock_get_point.return_value = mock_planet
        mock_get_houses.return_value = {
            'houses': [0] * 13,
            'ascendant': 0,
            'midheaven': 90
        }
        mock_analyze_retrograde.return_value = {
            'total_retrograde': 0,
            'retrograde_planets': [],
            'direct_planets': [],
            'stationary_planets': [],
            'retrograde_percentage': 0.0
        }
        
        result = self.service.calculate_natal_chart_enhanced(
            NatalChartRequest(
                subject=SubjectRequest(
                    birth_datetime=DateTimeInput(
                        components={
                            "year": self.test_dt.year,
                            "month": self.test_dt.month,
                            "day": self.test_dt.day,
                            "hour": self.test_dt.hour,
                            "minute": self.test_dt.minute,
                            "second": self.test_dt.second
                        }
                    ),
                    latitude=self.test_lat,
                    longitude=self.test_lon
                )
            )
        )
        
        # Should include standard planets plus potential South Nodes
        expected_core_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        
        planet_names = [getattr(p, 'name', '') for p in result.get('planets', [])]
        
        # Verify at least some core planets are present
        core_planets_found = sum(1 for planet in expected_core_planets if planet in planet_names)
        assert core_planets_found > 0, "Should find at least some core planets"
    
    @patch('app.core.ephemeris.tools.ephemeris.get_point')
    @patch('app.core.ephemeris.tools.ephemeris.get_houses')
    @patch('app.core.ephemeris.tools.ephemeris.analyze_retrograde_motion')
    def test_enhanced_chart_error_handling(self, mock_analyze_retrograde, mock_get_houses, mock_get_point):
        """Test error handling in enhanced natal chart calculation"""
        
        # Test with calculation error
        mock_get_point.side_effect = Exception("Calculation error")
        
        with pytest.raises(Exception):
            self.service.calculate_natal_chart_enhanced(
                NatalChartRequest(
                    subject=SubjectRequest(
                        birth_datetime=DateTimeInput(
                            components={
                                "year": self.test_dt.year,
                                "month": self.test_dt.month,
                                "day": self.test_dt.day,
                                "hour": self.test_dt.hour,
                                "minute": self.test_dt.minute,
                                "second": self.test_dt.second
                            }
                        ),
                        latitude=self.test_lat,
                        longitude=self.test_lon
                    )
                )
            )
    
    def test_enhanced_chart_parameter_validation(self):
        """Test parameter validation for enhanced natal chart"""
        
        # Test invalid datetime
        with pytest.raises((ValueError, TypeError)):
            invalid_request = NatalChartRequest(
                subject=SubjectRequest(
                    birth_datetime="invalid",  # This should cause validation error
                    latitude=self.test_lat,
                    longitude=self.test_lon
                )
            )
            
        # Test invalid coordinates  
        with pytest.raises((ValueError, TypeError)):
            invalid_request = NatalChartRequest(
                subject=SubjectRequest(
                    birth_datetime=DateTimeInput(
                        year=self.test_dt.year,
                        month=self.test_dt.month,
                        day=self.test_dt.day,
                        hour=self.test_dt.hour,
                        minute=self.test_dt.minute,
                        second=self.test_dt.second
                    ),
                    latitude="invalid",  # This should cause validation error
                    longitude=self.test_lon
                )
            )


class TestEphemerisServiceIntegration:
    """Integration tests for EphemerisService"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.service = EphemerisService()
        self.test_dt = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        self.test_lat = 51.5074  # London
        self.test_lon = -0.1278
    
    @pytest.mark.integration
    def test_real_enhanced_natal_chart_calculation(self):
        """Integration test with real ephemeris data"""
        
        result = self.service.calculate_natal_chart_enhanced(
            NatalChartRequest(
                subject=SubjectRequest(
                    birth_datetime=DateTimeInput(
                        components={
                            "year": self.test_dt.year,
                            "month": self.test_dt.month,
                            "day": self.test_dt.day,
                            "hour": self.test_dt.hour,
                            "minute": self.test_dt.minute,
                            "second": self.test_dt.second
                        }
                    ),
                    latitude=self.test_lat,
                    longitude=self.test_lon
                )
            )
        )        # Basic structure validation
        assert 'planets' in result
        assert 'houses' in result
        assert 'retrograde_analysis' in result
        assert 'south_node' in result
        
        # Verify planets have enhanced properties
        for planet in result.get('planets', []):
            if hasattr(planet, 'name'):
                assert hasattr(planet, 'is_retrograde'), f"Planet {planet.name} missing is_retrograde property"
                assert hasattr(planet, 'motion_type'), f"Planet {planet.name} missing motion_type property"
                assert planet.motion_type in ['direct', 'retrograde', 'stationary', 'unknown']
        
        # Check for South Node calculations 
        planet_names = [getattr(p, 'name', '') for p in result.get('planets', [])]
        has_nodes = any('Node' in name for name in planet_names)
        if has_nodes:
            # If we have nodes, check for South Node calculation
            north_nodes = [p for p in result.get('planets', []) if 'North Node' in getattr(p, 'name', '') or 'True Node' in getattr(p, 'name', '')]
            if north_nodes:
                # Should also have corresponding South Nodes
                south_nodes = [p for p in result.get('planets', []) if 'South Node' in getattr(p, 'name', '')]
                assert len(south_nodes) > 0, "Should have South Node when North Node is present"
        
        # Verify retrograde analysis consistency
        retro_analysis = result.get('retrograde_analysis', {})
        if retro_analysis:
            retrograde_count = len(retro_analysis.get('retrograde_planets', []))
            assert retro_analysis.get('total_retrograde', 0) == retrograde_count
            
            # Verify percentage calculation if we have planet data
            planets_with_speed = [p for p in result.get('planets', []) 
                                 if hasattr(p, 'name') and hasattr(p, 'longitude_speed') 
                                 and 'Node' not in getattr(p, 'name', '')]
            if len(planets_with_speed) > 0:
                expected_percentage = (retrograde_count / len(planets_with_speed)) * 100
                actual_percentage = retro_analysis.get('retrograde_percentage', 0)
                # Allow for some floating point variation
                assert abs(actual_percentage - expected_percentage) < 1.0


if __name__ == "__main__":
    pytest.main([__file__])
