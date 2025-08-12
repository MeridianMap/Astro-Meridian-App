"""
Unit tests for the Meridian Ephemeris Engine ephemeris tools module.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.core.ephemeris.tools.ephemeris import (
    julian_day_from_datetime, datetime_from_julian_day,
    get_planet, get_houses, get_angles, get_point, get_fixed_star,
    calculate_planetary_chart, validate_ephemeris_files
)
from app.core.ephemeris.const import SwePlanets
from app.core.ephemeris.classes.serialize import PlanetPosition, HouseSystem


class TestJulianDayConversions:
    """Test Julian Day conversion utilities."""
    
    def test_julian_day_from_datetime_utc(self):
        """Test Julian Day calculation from UTC datetime."""
        # J2000.0 epoch: January 1, 2000, 12:00:00 UTC
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = julian_day_from_datetime(dt)
        
        # J2000.0 is defined as JD 2451545.0
        assert abs(jd - 2451545.0) < 0.001
    
    def test_julian_day_from_datetime_naive(self):
        """Test Julian Day calculation from naive datetime."""
        dt = datetime(2000, 1, 1, 12, 0, 0)
        jd = julian_day_from_datetime(dt)
        
        assert abs(jd - 2451545.0) < 0.001
    
    def test_datetime_from_julian_day(self):
        """Test datetime reconstruction from Julian Day."""
        jd = 2451545.0  # J2000.0
        dt = datetime_from_julian_day(jd)
        
        assert dt.year == 2000
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12
        assert dt.tzinfo == timezone.utc
    
    def test_round_trip_conversion(self):
        """Test round-trip datetime ↔ Julian Day conversion."""
        original_dt = datetime(2024, 6, 15, 18, 30, 45, tzinfo=timezone.utc)
        jd = julian_day_from_datetime(original_dt)
        reconstructed_dt = datetime_from_julian_day(jd)
        
        # Allow small precision loss in seconds
        time_diff = abs((original_dt - reconstructed_dt).total_seconds())
        assert time_diff < 1.0


class TestGetPlanet:
    """Test planet position calculation."""
    
    @patch('swisseph.calc_ut')
    def test_get_planet_basic(self, mock_calc_ut):
        """Test basic planet position calculation."""
        # Mock Swiss Ephemeris response
        mock_result = [120.5, 2.3, 1.016, 0.985, 0.001, -0.002]
        mock_calc_ut.return_value = (mock_result, 258)
        
        jd = 2451545.0
        position = get_planet(SwePlanets.SUN, jd)
        
        assert isinstance(position, PlanetPosition)
        assert position.planet_id == SwePlanets.SUN
        assert position.longitude == 120.5
        assert position.latitude == 2.3
        assert position.distance == 1.016
        assert position.longitude_speed == 0.985
    
    @patch('swisseph.calc_ut')
    @patch('swisseph.set_topo')
    def test_get_planet_topocentric(self, mock_set_topo, mock_calc_ut):
        """Test topocentric planet position calculation."""
        mock_result = [120.5, 2.3, 1.016, 0.985, 0.001, -0.002]
        mock_calc_ut.return_value = (mock_result, 258)
        
        jd = 2451545.0
        position = get_planet(SwePlanets.MOON, jd, latitude=51.5074, longitude=-0.1278)
        
        # Verify topocentric coordinates were set
        mock_set_topo.assert_called_once_with(-0.1278, 51.5074, 0.0)
        assert position.planet_id == SwePlanets.MOON
    
    @patch('app.core.ephemeris.tools.ephemeris.swe.calc_ut')
    def test_get_planet_error_handling(self, mock_calc_ut):
        """Test error handling in planet calculation."""
        # Mock Swiss Ephemeris failure
        mock_calc_ut.side_effect = Exception("Swiss Ephemeris error")
        
        with pytest.raises(RuntimeError, match="Failed to calculate Sun position"):
            get_planet(SwePlanets.SUN, 2451545.0)


class TestGetHouses:
    """Test house system calculation."""
    
    @patch('swisseph.houses')
    def test_get_houses_basic(self, mock_houses):
        """Test basic house calculation."""
        # Mock Swiss Ephemeris response
        mock_cusps = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]
        mock_ascmc = [15.5, 105.3, 285.2, 195.1, 0.0, 0.0, 0.0, 0.0]
        mock_houses.return_value = (mock_cusps, mock_ascmc)
        
        jd = 2451545.0
        houses = get_houses(jd, 51.5074, -0.1278, 'P')
        
        assert isinstance(houses, HouseSystem)
        assert houses.system_code == 'P'
        assert len(houses.house_cusps) == 13
        assert houses.ascendant == 15.5
        assert houses.midheaven == 105.3
        assert houses.latitude == 51.5074
        assert houses.longitude == -0.1278
    
    @patch('swisseph.houses')
    def test_get_houses_error_handling(self, mock_houses):
        """Test error handling in house calculation."""
        mock_houses.side_effect = Exception("House calculation error")
        
        with pytest.raises(RuntimeError, match="Failed to calculate houses"):
            get_houses(2451545.0, 51.5074, -0.1278)


class TestGetAngles:
    """Test chart angles calculation."""
    
    @patch('app.core.ephemeris.tools.ephemeris.get_houses')
    def test_get_angles(self, mock_get_houses):
        """Test chart angles calculation."""
        # Mock house system
        mock_houses = MagicMock()
        mock_houses.ascendant = 15.5
        mock_houses.midheaven = 105.3
        mock_houses.descendant = 195.5
        mock_houses.imum_coeli = 285.3
        mock_houses.ascmc = [15.5, 105.3, 285.2, 195.1]
        mock_get_houses.return_value = mock_houses
        
        angles = get_angles(2451545.0, 51.5074, -0.1278)
        
        assert isinstance(angles, dict)
        assert 'ASC' in angles
        assert 'MC' in angles
        assert 'DESC' in angles
        assert 'IC' in angles
        assert angles['ASC'] == 15.5
        assert angles['MC'] == 105.3


class TestGetPoint:
    """Test astrological point calculations."""
    
    @patch('app.core.ephemeris.tools.ephemeris.get_planet')
    def test_get_point_north_node(self, mock_get_planet):
        """Test North Node calculation."""
        mock_position = MagicMock()
        mock_position.longitude = 125.6
        mock_position.latitude = 0.2
        mock_position.longitude_speed = 0.053
        mock_get_planet.return_value = mock_position
        
        result = get_point('north_node', 2451545.0)
        
        assert isinstance(result, dict)
        assert result['name'] == 'North Node (Mean)'
        assert result['longitude'] == 125.6
        mock_get_planet.assert_called_with(SwePlanets.MEAN_NODE, 2451545.0)
    
    @patch('app.core.ephemeris.tools.ephemeris.get_planet')
    def test_get_point_south_node(self, mock_get_planet):
        """Test South Node calculation."""
        mock_position = MagicMock()
        mock_position.longitude = 125.6
        mock_position.latitude = 0.2
        mock_position.longitude_speed = 0.053
        mock_get_planet.return_value = mock_position
        
        result = get_point('south_node', 2451545.0)
        
        # South Node should be 180° from North Node
        expected_longitude = (125.6 + 180.0) % 360.0
        assert result['longitude'] == expected_longitude
        assert result['latitude'] == -0.2  # Opposite latitude
    
    @patch('app.core.ephemeris.tools.ephemeris.get_planet')
    @patch('app.core.ephemeris.tools.ephemeris.get_angles')
    def test_get_point_part_of_fortune(self, mock_get_angles, mock_get_planet):
        """Test Part of Fortune calculation."""
        # Mock Sun and Moon positions
        def mock_planet_side_effect(planet_id, jd):
            mock_pos = MagicMock()
            if planet_id == SwePlanets.SUN:
                mock_pos.longitude = 90.0
            elif planet_id == SwePlanets.MOON:
                mock_pos.longitude = 180.0
            return mock_pos
        
        mock_get_planet.side_effect = mock_planet_side_effect
        mock_get_angles.return_value = {'ASC': 30.0}
        
        result = get_point('part_of_fortune', 2451545.0, 51.5, -0.13)
        
        # POF = ASC + Moon - Sun = 30 + 180 - 90 = 120°
        assert result['longitude'] == 120.0
        assert result['name'] == 'Part of Fortune'
    
    def test_get_point_unknown_type(self):
        """Test error handling for unknown point type."""
        with pytest.raises(ValueError, match="Unknown point type"):
            get_point('unknown_point', 2451545.0)
    
    def test_get_point_missing_coordinates(self):
        """Test error handling for missing coordinates."""
        with pytest.raises(ValueError, match="required for Vertex calculation"):
            get_point('vertex', 2451545.0)


class TestGetFixedStar:
    """Test fixed star calculation."""
    
    @patch('swisseph.fixstar_ut')
    def test_get_fixed_star_basic(self, mock_fixstar_ut):
        """Test basic fixed star calculation."""
        mock_result = [45.6, 12.3, 1000.0, 0.001, 0.0, -0.05]
        mock_info = "Aldebaran,  9Tau09, 2451545.0"
        mock_fixstar_ut.return_value = (mock_result, mock_info)
        
        result = get_fixed_star('Aldebaran', 2451545.0)
        
        assert isinstance(result, dict)
        assert result['name'] == 'Aldebaran'
        assert result['longitude'] == 45.6
        assert result['latitude'] == 12.3
        assert result['info'] == mock_info
    
    @patch('swisseph.fixstar_ut')
    def test_get_fixed_star_error_handling(self, mock_fixstar_ut):
        """Test error handling in fixed star calculation."""
        mock_fixstar_ut.side_effect = Exception("Star not found")
        
        with pytest.raises(RuntimeError, match="Failed to calculate fixed star"):
            get_fixed_star('NonexistentStar', 2451545.0)


class TestCalculatePlanetaryChart:
    """Test complete planetary chart calculation."""
    
    @patch('app.core.ephemeris.tools.ephemeris.get_planet')
    @patch('app.core.ephemeris.tools.ephemeris.get_houses')
    @patch('app.core.ephemeris.tools.ephemeris.get_angles')
    def test_calculate_planetary_chart(self, mock_get_angles, mock_get_houses, mock_get_planet):
        """Test complete chart calculation."""
        # Mock planet positions
        mock_position = MagicMock()
        mock_position.planet_id = SwePlanets.SUN
        mock_get_planet.return_value = mock_position
        
        # Mock houses
        mock_houses = MagicMock()
        mock_get_houses.return_value = mock_houses
        
        # Mock angles
        mock_angles = {'ASC': 15.5, 'MC': 105.3}
        mock_get_angles.return_value = mock_angles
        
        jd = 2451545.0
        chart = calculate_planetary_chart(
            jd, 51.5074, -0.1278, planets=[SwePlanets.SUN]
        )
        
        assert isinstance(chart, dict)
        assert 'planets' in chart
        assert 'houses' in chart
        assert 'angles' in chart
        assert 'julian_day' in chart
        assert 'observer' in chart
        assert chart['julian_day'] == jd
        assert chart['observer']['latitude'] == 51.5074


class TestValidateEphemerisFiles:
    """Test ephemeris file validation."""
    
    @patch('app.core.ephemeris.tools.ephemeris.get_planet')
    @patch('app.core.ephemeris.tools.ephemeris.get_houses')
    @patch('app.core.ephemeris.tools.ephemeris.get_fixed_star')
    def test_validate_ephemeris_files_success(self, mock_get_fixed_star, 
                                            mock_get_houses, mock_get_planet):
        """Test successful validation of ephemeris files."""
        # Mock successful calculations
        mock_get_planet.return_value = MagicMock()
        mock_get_houses.return_value = MagicMock()
        mock_get_fixed_star.return_value = MagicMock()
        
        validation = validate_ephemeris_files()
        
        assert isinstance(validation, dict)
        assert 'Sun' in validation
        assert 'Houses' in validation
        assert validation['Sun'] is True
        assert validation['Houses'] is True
    
    @patch('app.core.ephemeris.tools.ephemeris.get_planet')
    def test_validate_ephemeris_files_failure(self, mock_get_planet):
        """Test validation with missing ephemeris files."""
        # Mock calculation failures
        mock_get_planet.side_effect = Exception("Ephemeris file not found")
        
        validation = validate_ephemeris_files()
        
        # All planets should fail
        for planet_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                          'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
            assert validation.get(planet_name) is False


class TestIntegrationScenarios:
    """Integration tests with realistic scenarios."""
    
    def test_natal_chart_calculation_scenario(self):
        """Test a complete natal chart calculation scenario."""
        # This is a mock integration test - in real usage this would
        # require actual Swiss Ephemeris files
        
        # Birth data: January 1, 2000, 12:00 UTC, London
        birth_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = julian_day_from_datetime(birth_dt)
        latitude = 51.5074
        longitude = -0.1278
        
        # Verify Julian Day calculation
        assert abs(jd - 2451545.0) < 0.001
        
        # In a real scenario, we would call:
        # chart = calculate_planetary_chart(jd, latitude, longitude)
        # and verify all planets and houses are calculated correctly
    
    @pytest.mark.parametrize("longitude,expected_normalized", [
        (0.0, 0.0),
        (180.0, 180.0),
        (360.0, 0.0),
        (450.0, 90.0),
        (-90.0, 270.0),
        (720.5, 0.5)
    ])
    def test_longitude_normalization_scenarios(self, longitude, expected_normalized):
        """Test longitude normalization in various scenarios."""
        from app.core.ephemeris.const import normalize_longitude
        result = normalize_longitude(longitude)
        assert abs(result - expected_normalized) < 0.001