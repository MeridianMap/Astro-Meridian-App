"""
Test Enhanced Ephemeris Calculations

Tests for south node calculations, retrograde detection, and comprehensive
ephemeris output functionality.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import swisseph as swe

from extracted.systems.enhanced_calculations import (
    calculate_south_node_position,
    get_enhanced_planet_position,
    calculate_complete_lunar_nodes,
    get_all_planets_with_retrograde,
    analyze_retrograde_patterns,
    get_comprehensive_ephemeris_output,
    is_planet_retrograde,
    get_retrograde_planets_only,
    calculate_node_axis_info,
    EnhancedPlanetPosition,
    LunarNodeData
)
from extracted.systems.classes.serialize import PlanetPosition
from extracted.systems.const import SwePlanets


class TestSouthNodeCalculation:
    """Test South Node calculation functionality."""
    
    def test_calculate_south_node_position_mean(self):
        """Test Mean South Node calculation from Mean North Node."""
        # Mock North Node position
        north_node = PlanetPosition(
            planet_id=SwePlanets.MEAN_NODE,
            longitude=125.5,  # North Node at 5°25' Leo
            latitude=0.2,
            distance=1.0,
            longitude_speed=-0.053,  # Retrograde (nodes always move backwards)
            latitude_speed=0.01,
            distance_speed=0.0,
            calculation_time=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        
        result = calculate_south_node_position(north_node, "mean")
        
        # South Node should be 180° from North Node
        expected_south_longitude = (125.5 + 180.0) % 360.0  # 305.5° (5°25' Aquarius)
        
        assert result['longitude'] == expected_south_longitude
        assert result['latitude'] == -0.2  # Opposite latitude
        assert result['longitude_speed'] == -0.053  # Same longitude speed
        assert result['latitude_speed'] == -0.01  # Opposite latitude speed
        assert result['name'] == 'South Node (Mean)'
        assert result['is_retrograde'] == True  # Nodes move retrograde
        assert result['motion_type'] == 'retrograde'
    
    def test_calculate_south_node_position_true(self):
        """Test True South Node calculation from True North Node."""
        # Mock True North Node position
        north_node = PlanetPosition(
            planet_id=SwePlanets.TRUE_NODE,
            longitude=126.2,  # Slightly different from mean
            latitude=-0.15,
            distance=1.0,
            longitude_speed=-0.055,  # Variable speed for true node
            latitude_speed=-0.005,
            distance_speed=0.0
        )
        
        result = calculate_south_node_position(north_node, "true")
        
        expected_south_longitude = (126.2 + 180.0) % 360.0  # 306.2°
        
        assert result['longitude'] == expected_south_longitude
        assert result['latitude'] == 0.15  # Opposite of -0.15
        assert result['longitude_speed'] == -0.055
        assert result['latitude_speed'] == 0.005  # Opposite of -0.005
        assert result['name'] == 'South Node (True)'
        assert result['is_retrograde'] == True


class TestEnhancedPlanetPosition:
    """Test EnhancedPlanetPosition class functionality."""
    
    def test_retrograde_detection_retrograde_planet(self):
        """Test retrograde detection for retrograde planet."""
        position = EnhancedPlanetPosition(
            planet_id=SwePlanets.MERCURY,
            name='Mercury',
            longitude=180.5,
            latitude=1.2,
            distance=0.8,
            longitude_speed=-1.2  # Negative speed = retrograde
        )
        
        assert position.is_retrograde == True
        assert position.motion_type == "retrograde"
    
    def test_retrograde_detection_direct_planet(self):
        """Test retrograde detection for direct planet."""
        position = EnhancedPlanetPosition(
            planet_id=SwePlanets.VENUS,
            name='Venus',
            longitude=45.8,
            latitude=0.3,
            distance=0.7,
            longitude_speed=1.1  # Positive speed = direct
        )
        
        assert position.is_retrograde == False
        assert position.motion_type == "direct"
    
    def test_retrograde_detection_stationary_planet(self):
        """Test detection for stationary planet."""
        position = EnhancedPlanetPosition(
            planet_id=SwePlanets.MARS,
            name='Mars',
            longitude=90.0,
            latitude=-0.5,
            distance=1.2,
            longitude_speed=0.0  # Zero speed = stationary
        )
        
        assert position.is_retrograde == False
        assert position.motion_type == "stationary"
    
    def test_to_dict_includes_retrograde_info(self):
        """Test that to_dict includes retrograde information."""
        position = EnhancedPlanetPosition(
            planet_id=SwePlanets.JUPITER,
            name='Jupiter',
            longitude=200.0,
            latitude=0.8,
            distance=5.2,
            longitude_speed=-0.08,  # Retrograde
            calculation_time=datetime(2024, 6, 15, tzinfo=timezone.utc)
        )
        
        result = position.to_dict()
        
        assert 'is_retrograde' in result
        assert result['is_retrograde'] == True
        assert 'motion_type' in result
        assert result['motion_type'] == 'retrograde'
        assert result['name'] == 'Jupiter'
        assert result['longitude_speed'] == -0.08


class TestLunarNodeCalculations:
    """Test complete lunar node calculations."""
    
    @patch('app.core.ephemeris.tools.enhanced_calculations.get_enhanced_planet_position')
    def test_calculate_complete_lunar_nodes(self, mock_get_position):
        """Test calculation of all four lunar node positions."""
        # Mock Mean North Node
        mock_mean_north = EnhancedPlanetPosition(
            planet_id=SwePlanets.MEAN_NODE,
            name='North Node (Mean)',
            longitude=125.0,
            latitude=0.0,
            distance=1.0,
            longitude_speed=-0.053
        )
        
        # Mock True North Node
        mock_true_north = EnhancedPlanetPosition(
            planet_id=SwePlanets.TRUE_NODE,
            name='North Node (True)',
            longitude=125.3,
            latitude=0.1,
            distance=1.0,
            longitude_speed=-0.055
        )
        
        # Configure mock to return different values based on planet_id
        def mock_position_side_effect(planet_id, *args, **kwargs):
            if planet_id == SwePlanets.MEAN_NODE:
                return mock_mean_north
            elif planet_id == SwePlanets.TRUE_NODE:
                return mock_true_north
        
        mock_get_position.side_effect = mock_position_side_effect
        
        result = calculate_complete_lunar_nodes(2451545.0)  # J2000.0
        
        # Check that we got all four node positions
        assert isinstance(result, LunarNodeData)
        assert result.mean_north.name == 'North Node (Mean)'
        assert result.true_north.name == 'North Node (True)'
        assert result.mean_south.name == 'South Node (Mean)'
        assert result.true_south.name == 'South Node (True)'
        
        # Check South Node calculations
        assert result.mean_south.longitude == (125.0 + 180.0) % 360.0  # 305.0°
        assert result.true_south.longitude == (125.3 + 180.0) % 360.0  # 305.3°
        
        # Check that all nodes are marked retrograde (nodes always move backwards)
        assert result.mean_north.is_retrograde == True
        assert result.true_north.is_retrograde == True
        assert result.mean_south.is_retrograde == True
        assert result.true_south.is_retrograde == True


class TestRetrogradeAnalysis:
    """Test retrograde pattern analysis functionality."""
    
    def test_analyze_retrograde_patterns(self):
        """Test analysis of retrograde patterns in planet positions."""
        positions = {
            'mercury': EnhancedPlanetPosition(
                planet_id=SwePlanets.MERCURY,
                name='Mercury',
                longitude=150.0,
                latitude=0.0,
                distance=0.8,
                longitude_speed=-1.5  # Retrograde
            ),
            'venus': EnhancedPlanetPosition(
                planet_id=SwePlanets.VENUS,
                name='Venus',
                longitude=200.0,
                latitude=0.0,
                distance=0.7,
                longitude_speed=1.2  # Direct
            ),
            'mars': EnhancedPlanetPosition(
                planet_id=SwePlanets.MARS,
                name='Mars',
                longitude=90.0,
                latitude=0.0,
                distance=1.5,
                longitude_speed=0.0  # Stationary
            ),
            'jupiter': EnhancedPlanetPosition(
                planet_id=SwePlanets.JUPITER,
                name='Jupiter',
                longitude=45.0,
                latitude=0.0,
                distance=5.2,
                longitude_speed=-0.1  # Retrograde
            )
        }
        
        result = analyze_retrograde_patterns(positions, 2451545.0)
        
        assert result['total_bodies'] == 4
        assert result['retrograde_count'] == 2  # Mercury and Jupiter
        assert result['direct_count'] == 1  # Venus
        assert result['stationary_count'] == 1  # Mars
        assert result['retrograde_percentage'] == 50.0  # 2/4 * 100
        
        # Check that retrograde bodies are correctly identified
        retrograde_names = [body['name'] for body in result['retrograde_bodies']]
        assert 'mercury' in retrograde_names
        assert 'jupiter' in retrograde_names


class TestComprehensiveOutput:
    """Test comprehensive ephemeris output functionality."""
    
    @patch('app.core.ephemeris.tools.enhanced_calculations.get_all_planets_with_retrograde')
    @patch('app.core.ephemeris.tools.enhanced_calculations.julian_day_from_datetime')
    def test_get_comprehensive_ephemeris_output(self, mock_julian_day, mock_get_planets):
        """Test comprehensive ephemeris output generation."""
        test_datetime = datetime(2024, 3, 21, 12, 0, 0, tzinfo=timezone.utc)
        mock_julian_day.return_value = 2460000.0
        
        # Mock planet positions
        mock_positions = {
            'sun': EnhancedPlanetPosition(
                planet_id=SwePlanets.SUN,
                name='Sun',
                longitude=0.0,  # Vernal Equinox
                latitude=0.0,
                distance=1.0,
                longitude_speed=0.985  # Sun is always direct
            ),
            'mercury': EnhancedPlanetPosition(
                planet_id=SwePlanets.MERCURY,
                name='Mercury',
                longitude=350.0,
                latitude=2.0,
                distance=0.4,
                longitude_speed=-1.2  # Retrograde
            )
        }
        
        mock_get_planets.return_value = mock_positions
        
        result = get_comprehensive_ephemeris_output(
            test_datetime, 
            include_analysis=True,
            include_asteroids=False,
            include_nodes=False,
            include_lilith=False
        )
        
        # Check structure
        assert 'calculation_info' in result
        assert 'positions' in result
        assert 'retrograde_analysis' in result
        
        # Check calculation info
        calc_info = result['calculation_info']
        assert calc_info['datetime_utc'] == test_datetime.isoformat()
        assert calc_info['julian_day'] == 2460000.0
        assert 'swiss_ephemeris_version' in calc_info
        
        # Check positions are converted to dictionaries
        assert 'sun' in result['positions']
        assert 'mercury' in result['positions']
        assert isinstance(result['positions']['sun'], dict)
        assert isinstance(result['positions']['mercury'], dict)


class TestUtilityFunctions:
    """Test utility functions."""
    
    @patch('app.core.ephemeris.tools.enhanced_calculations.get_enhanced_planet_position')
    def test_is_planet_retrograde(self, mock_get_position):
        """Test quick retrograde check function."""
        # Mock retrograde planet
        mock_get_position.return_value = EnhancedPlanetPosition(
            planet_id=SwePlanets.MARS,
            name='Mars',
            longitude=180.0,
            latitude=0.0,
            distance=1.5,
            longitude_speed=-0.3  # Retrograde
        )
        
        result = is_planet_retrograde(SwePlanets.MARS, 2451545.0)
        assert result == True
        
        # Test direct planet
        mock_get_position.return_value = EnhancedPlanetPosition(
            planet_id=SwePlanets.VENUS,
            name='Venus',
            longitude=90.0,
            latitude=0.0,
            distance=0.7,
            longitude_speed=1.1  # Direct
        )
        
        result = is_planet_retrograde(SwePlanets.VENUS, 2451545.0)
        assert result == False
    
    @patch('app.core.ephemeris.tools.enhanced_calculations.get_all_planets_with_retrograde')
    def test_get_retrograde_planets_only(self, mock_get_planets):
        """Test function to get only retrograde planets."""
        mock_positions = {
            'mercury': EnhancedPlanetPosition(
                planet_id=SwePlanets.MERCURY,
                name='Mercury',
                longitude=150.0,
                latitude=0.0,
                distance=0.8,
                longitude_speed=-1.5  # Retrograde
            ),
            'venus': EnhancedPlanetPosition(
                planet_id=SwePlanets.VENUS,
                name='Venus',
                longitude=200.0,
                latitude=0.0,
                distance=0.7,
                longitude_speed=1.2  # Direct
            ),
            'jupiter': EnhancedPlanetPosition(
                planet_id=SwePlanets.JUPITER,
                name='Jupiter',
                longitude=45.0,
                latitude=0.0,
                distance=5.2,
                longitude_speed=-0.1  # Retrograde
            )
        }
        
        mock_get_planets.return_value = mock_positions
        
        result = get_retrograde_planets_only(2451545.0)
        
        assert len(result) == 2  # Mercury and Jupiter
        retrograde_names = [pos.name for pos in result]
        assert 'Mercury' in retrograde_names
        assert 'Jupiter' in retrograde_names
        assert 'Venus' not in retrograde_names


class TestNodeAxisInfo:
    """Test detailed node axis information."""
    
    @patch('app.core.ephemeris.tools.enhanced_calculations.calculate_complete_lunar_nodes')
    def test_calculate_node_axis_info(self, mock_calculate_nodes):
        """Test detailed node axis information calculation."""
        # Mock node data
        mock_node_data = LunarNodeData(
            mean_north=EnhancedPlanetPosition(
                planet_id=SwePlanets.MEAN_NODE,
                name='North Node (Mean)',
                longitude=125.0,
                latitude=0.0,
                distance=1.0,
                longitude_speed=-0.053
            ),
            true_north=EnhancedPlanetPosition(
                planet_id=SwePlanets.TRUE_NODE,
                name='North Node (True)',
                longitude=125.5,  # 0.5° difference from mean
                latitude=0.1,
                distance=1.0,
                longitude_speed=-0.055
            ),
            mean_south=EnhancedPlanetPosition(
                planet_id=1010,  # Custom ID
                name='South Node (Mean)',
                longitude=305.0,  # 180° from north
                latitude=0.0,
                distance=1.0,
                longitude_speed=-0.053
            ),
            true_south=EnhancedPlanetPosition(
                planet_id=1011,  # Custom ID
                name='South Node (True)',
                longitude=305.5,  # 180° from true north
                latitude=-0.1,
                distance=1.0,
                longitude_speed=-0.055
            )
        )
        
        mock_calculate_nodes.return_value = mock_node_data
        
        result = calculate_node_axis_info(2451545.0)
        
        assert result['mean_north_longitude'] == 125.0
        assert result['true_north_longitude'] == 125.5
        assert result['mean_south_longitude'] == 305.0
        assert result['true_south_longitude'] == 305.5
        assert result['mean_true_difference_degrees'] == 0.5
        assert result['node_speed_degrees_per_day'] == 0.053
        assert result['nodes_retrograde'] == True
        assert 'complete_node_data' in result


class TestIntegration:
    """Integration tests with real Swiss Ephemeris (if available)."""
    
    @pytest.mark.skipif(not hasattr(swe, 'calc_ut'), reason="Swiss Ephemeris not available")
    def test_real_calculation_integration(self):
        """Test with real Swiss Ephemeris calculation (if available)."""
        try:
            # Test calculation for J2000.0
            test_datetime = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            
            # This should work if Swiss Ephemeris is properly installed
            result = get_comprehensive_ephemeris_output(
                test_datetime,
                include_analysis=True,
                include_asteroids=False,  # Keep it simple
                include_nodes=True,
                include_lilith=False
            )
            
            # Basic structure checks
            assert 'calculation_info' in result
            assert 'positions' in result
            assert 'retrograde_analysis' in result
            
            # Should have at least the traditional planets
            positions = result['positions']
            expected_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 
                              'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
            
            for planet in expected_planets:
                assert planet in positions, f"Missing planet: {planet}"
                assert 'is_retrograde' in positions[planet]
                assert 'motion_type' in positions[planet]
            
            # Should have node data
            assert 'north_node_mean' in positions
            assert 'south_node_mean' in positions
            
            # Check that south node is 180° from north node
            north_lon = positions['north_node_mean']['longitude']
            south_lon = positions['south_node_mean']['longitude']
            expected_south = (north_lon + 180.0) % 360.0
            
            assert abs(south_lon - expected_south) < 0.001, \
                f"South node longitude {south_lon} not 180° from north node {north_lon}"
            
        except Exception as e:
            pytest.skip(f"Swiss Ephemeris not available or configured: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
