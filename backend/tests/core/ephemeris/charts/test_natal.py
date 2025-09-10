"""
Unit tests for the Meridian Ephemeris Engine Natal Chart construction.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from zoneinfo import ZoneInfo

from extracted.systems.charts.subject import Subject, SubjectData
from extracted.systems.charts.natal import NatalChart, ChartData, AspectData
from extracted.systems.ephemeris import PlanetPosition, HouseSystem, ChartAngles
from extracted.systems.const import SwePlanets, HouseSystems


class TestNatalChartInitialization:
    """Test NatalChart initialization and configuration."""
    
    def test_natal_chart_with_subject_object(self):
        """Test creating NatalChart with Subject object."""
        subject = Subject(
            name="John Doe",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        chart = NatalChart(subject)
        
        assert chart.subject_data.name == "John Doe"
        assert chart.house_system == HouseSystems.PLACIDUS
        assert chart.include_asteroids is True
        assert chart.include_nodes is True
        assert chart.include_lilith is True
    
    def test_natal_chart_with_subject_data(self):
        """Test creating NatalChart with SubjectData object."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        subject_data = SubjectData(
            name="Jane Doe",
            datetime=dt,
            julian_day=2451545.0,
            latitude=51.5074,
            longitude=-0.1278
        )
        
        chart = NatalChart(subject_data)
        
        assert chart.subject_data.name == "Jane Doe"
        assert chart.subject_data.latitude == 51.5074
        assert chart.subject_data.longitude == -0.1278
    
    def test_invalid_subject_type(self):
        """Test invalid subject type handling."""
        with pytest.raises(TypeError, match="Expected Subject or SubjectData"):
            NatalChart("invalid subject")
    
    def test_custom_configuration(self):
        """Test custom chart configuration."""
        subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00",
            latitude=0.0,
            longitude=0.0
        )
        
        custom_orbs = {'Conjunction': 10.0, 'Opposition': 9.0}
        
        chart = NatalChart(
            subject,
            house_system=HouseSystems.KOCH,
            include_asteroids=False,
            include_nodes=False,
            include_lilith=False,
            aspect_orbs=custom_orbs,
            parallel_processing=False
        )
        
        assert chart.house_system == HouseSystems.KOCH
        assert chart.include_asteroids is False
        assert chart.include_nodes is False
        assert chart.include_lilith is False
        assert chart.aspect_orbs['Conjunction'] == 10.0
        assert chart.parallel_processing is False


class TestCalculationObjectSelection:
    """Test celestial object selection for calculation."""
    
    def test_default_object_selection(self):
        """Test default object selection."""
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        objects = chart._get_calculation_objects()
        
        # Should include modern planets by default
        assert SwePlanets.SUN in objects
        assert SwePlanets.MOON in objects
        assert SwePlanets.PLUTO in objects
        
        # Should include asteroids, nodes, and lilith by default
        assert SwePlanets.CHIRON in objects
        assert SwePlanets.MEAN_NODE in objects
        assert SwePlanets.MEAN_APOG in objects
    
    def test_minimal_object_selection(self):
        """Test minimal object selection."""
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(
            subject,
            include_asteroids=False,
            include_nodes=False,
            include_lilith=False
        )
        
        objects = chart._get_calculation_objects()
        
        # Should only include modern planets
        assert SwePlanets.SUN in objects
        assert SwePlanets.PLUTO in objects
        
        # Should not include optional objects
        assert SwePlanets.CHIRON not in objects
        assert SwePlanets.MEAN_NODE not in objects
        assert SwePlanets.MEAN_APOG not in objects


class TestSingleObjectCalculation:
    """Test individual celestial object calculation."""
    
    @patch('app.core.ephemeris.charts.natal.get_planet')
    @patch('app.core.ephemeris.charts.natal.get_position_summary')
    def test_successful_object_calculation(self, mock_position_summary, mock_get_planet):
        """Test successful single object calculation."""
        # Mock planet position
        mock_planet = MagicMock()
        mock_planet.longitude = 285.5
        mock_get_planet.return_value = mock_planet
        
        # Mock position summary
        mock_position_summary.return_value = {
            'sign': {'number': 10, 'name': 'Capricorn', 'symbol': '♑'},
            'sign_longitude': 15.5,
            'decan': 2,
            'element': {'number': 2, 'name': 'Earth'},
            'modality': {'number': 1, 'name': 'Cardinal'}
        }
        
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        result = chart._calculate_single_object(SwePlanets.SUN)
        
        assert result is not None
        assert result.longitude == 285.5
        assert result.sign_number == 10
        assert result.sign_name == 'Capricorn'
        assert result.sign_longitude == 15.5
        assert result.decan == 2
        
        mock_get_planet.assert_called_once()
    
    @patch('app.core.ephemeris.charts.natal.get_planet')
    def test_failed_object_calculation(self, mock_get_planet):
        """Test handling of failed object calculation."""
        mock_get_planet.side_effect = Exception("Calculation failed")
        
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        result = chart._calculate_single_object(SwePlanets.SUN)
        
        # Should return None on failure, not raise exception
        assert result is None


class TestHouseAndAngleCalculation:
    """Test house and angle calculation."""
    
    @patch('app.core.ephemeris.charts.natal.get_houses')
    @patch('app.core.ephemeris.charts.natal.get_angles')
    def test_successful_houses_and_angles(self, mock_get_angles, mock_get_houses):
        """Test successful houses and angles calculation."""
        # Mock houses
        mock_houses = MagicMock()
        mock_get_houses.return_value = mock_houses
        
        # Mock angles dictionary
        mock_angles_dict = {
            'ASC': 90.0,
            'MC': 180.0,
            'DESC': 270.0,
            'IC': 0.0
        }
        mock_get_angles.return_value = mock_angles_dict
        
        subject = Subject("Test", "2000-01-01T12:00:00", 40.0, -74.0)
        chart = NatalChart(subject, house_system=HouseSystems.KOCH)
        
        houses, angles = chart._calculate_houses_and_angles()
        
        assert houses == mock_houses
        # Check that angles is ChartAngles object with correct values
        assert angles.ascendant == 90.0
        assert angles.midheaven == 180.0
        assert angles.descendant == 270.0
        assert angles.imum_coeli == 0.0
        
        mock_get_houses.assert_called_once_with(
            chart.subject_data.julian_day,
            40.0,
            -74.0,
            house_system=HouseSystems.KOCH
        )
        
        mock_get_angles.assert_called_once_with(
            chart.subject_data.julian_day,
            40.0,
            -74.0
        )
    
    @patch('app.core.ephemeris.charts.natal.get_houses')
    def test_failed_houses_calculation(self, mock_get_houses):
        """Test handling of failed houses calculation."""
        mock_get_houses.side_effect = Exception("Houses calculation failed")
        
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        with pytest.raises(RuntimeError, match="Failed to calculate houses and angles"):
            chart._calculate_houses_and_angles()


class TestAspectCalculation:
    """Test aspect calculation between objects."""
    
    def test_aspect_calculation_within_orb(self):
        """Test aspect calculation within orb."""
        # Create mock planets
        planets = {
            SwePlanets.SUN: MagicMock(longitude=0.0),
            SwePlanets.MOON: MagicMock(longitude=90.0),  # 90° = Square
        }
        
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        with patch('app.core.ephemeris.charts.natal.get_closest_aspect_angle') as mock_aspect:
            mock_aspect.return_value = {
                'aspect': 'Square',
                'angle': 90,
                'orb': 2.0,
                'separation': 90.0,
                'applying': True
            }
            
            aspects = chart._calculate_aspects(planets)
            
            assert len(aspects) == 1
            aspect = aspects[0]
            assert aspect.object1_id == SwePlanets.SUN
            assert aspect.object2_id == SwePlanets.MOON
            assert aspect.aspect_name == 'Square'
            assert aspect.orb == 2.0
            assert aspect.applying is True
    
    def test_aspect_calculation_outside_orb(self):
        """Test aspect calculation outside orb."""
        planets = {
            SwePlanets.SUN: MagicMock(longitude=0.0),
            SwePlanets.MOON: MagicMock(longitude=45.0),  # 45° semisquare but large orb
        }
        
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        with patch('app.core.ephemeris.charts.natal.get_closest_aspect_angle') as mock_aspect:
            mock_aspect.return_value = {
                'aspect': 'Semisquare',
                'angle': 45,
                'orb': 5.0,  # Larger than default orb of 3.0
                'separation': 45.0,
                'applying': False
            }
            
            aspects = chart._calculate_aspects(planets)
            
            # Should be filtered out due to orb
            assert len(aspects) == 0
    
    def test_no_self_aspects(self):
        """Test that objects don't form aspects with themselves."""
        planets = {
            SwePlanets.SUN: MagicMock(longitude=0.0),
        }
        
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        aspects = chart._calculate_aspects(planets)
        
        # No aspects possible with only one object
        assert len(aspects) == 0


class TestFullChartCalculation:
    """Test complete chart calculation."""
    
    @patch('app.core.ephemeris.charts.natal.NatalChart._calculate_objects_parallel')
    @patch('app.core.ephemeris.charts.natal.NatalChart._calculate_houses_and_angles')
    @patch('app.core.ephemeris.charts.natal.NatalChart._add_house_positions')
    @patch('app.core.ephemeris.charts.natal.NatalChart._calculate_aspects')
    def test_successful_full_calculation(self, mock_aspects, mock_house_pos, 
                                       mock_houses, mock_objects):
        """Test successful complete chart calculation."""
        # Mock objects
        mock_planets = {SwePlanets.SUN: MagicMock(longitude=0.0)}
        mock_objects.return_value = mock_planets
        
        # Mock houses and angles
        mock_house_system = MagicMock()
        mock_chart_angles = MagicMock()
        mock_houses.return_value = (mock_house_system, mock_chart_angles)
        
        # Mock aspects
        mock_aspects.return_value = []
        
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        result = chart.calculate()
        
        assert isinstance(result, ChartData)
        assert result.subject == chart.subject_data
        assert result.planets == mock_planets
        assert result.houses == mock_house_system
        assert result.angles == mock_chart_angles
        assert result.aspects == []
        assert result.chart_type == "natal"
        
        # Verify all calculation steps were called
        mock_objects.assert_called_once()
        mock_houses.assert_called_once()
        mock_house_pos.assert_called_once()
        mock_aspects.assert_called_once()
    
    def test_calculation_caching(self):
        """Test that calculations are cached."""
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        with patch.object(chart, '_calculate_objects_parallel') as mock_calc:
            mock_calc.return_value = {SwePlanets.SUN: MagicMock()}
            
            with patch.object(chart, '_calculate_houses_and_angles') as mock_houses:
                mock_houses.return_value = (MagicMock(), MagicMock())
                
                # First calculation
                result1 = chart.calculate()
                
                # Second calculation should use cache
                result2 = chart.calculate()
                
                assert result1 is result2  # Same object reference
                mock_calc.assert_called_once()  # Only called once
    
    def test_force_recalculation(self):
        """Test forced recalculation bypasses cache."""
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        with patch.object(chart, '_calculate_objects_parallel') as mock_calc:
            mock_calc.return_value = {SwePlanets.SUN: MagicMock()}
            
            with patch.object(chart, '_calculate_houses_and_angles') as mock_houses:
                mock_houses.return_value = (MagicMock(), MagicMock())
                
                # First calculation
                chart.calculate()
                
                # Force recalculation
                chart.calculate(force_recalculate=True)
                
                assert mock_calc.call_count == 2  # Called twice
    
    @patch('app.core.ephemeris.charts.natal.NatalChart._calculate_objects_parallel')
    def test_calculation_failure_no_objects(self, mock_objects):
        """Test calculation failure when no objects calculated."""
        mock_objects.return_value = {}  # No objects
        
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        with pytest.raises(RuntimeError, match="Failed to calculate any celestial object positions"):
            chart.calculate()


class TestChartDataMethods:
    """Test ChartData utility methods."""
    
    def test_get_object_position(self):
        """Test getting object position by ID."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        subject_data = SubjectData("Test", dt, 2451545.0, 0.0, 0.0)
        
        sun_position = MagicMock()
        planets = {SwePlanets.SUN: sun_position}
        
        chart_data = ChartData(
            subject=subject_data,
            planets=planets,
            houses=MagicMock(),
            angles=MagicMock(),
            aspects=[],
            calculation_time=datetime.now()
        )
        
        assert chart_data.get_object_position(SwePlanets.SUN) == sun_position
        assert chart_data.get_object_position(SwePlanets.MOON) is None
    
    def test_get_objects_in_sign(self):
        """Test getting objects in specific sign."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        subject_data = SubjectData("Test", dt, 2451545.0, 0.0, 0.0)
        
        sun = MagicMock()
        sun.sign_number = 1  # Aries
        
        moon = MagicMock()
        moon.sign_number = 2  # Taurus
        
        planets = {SwePlanets.SUN: sun, SwePlanets.MOON: moon}
        
        chart_data = ChartData(
            subject=subject_data,
            planets=planets,
            houses=MagicMock(),
            angles=MagicMock(),
            aspects=[],
            calculation_time=datetime.now()
        )
        
        aries_objects = chart_data.get_objects_in_sign(1)
        assert len(aries_objects) == 1
        assert aries_objects[0] == sun
        
        gemini_objects = chart_data.get_objects_in_sign(3)
        assert len(gemini_objects) == 0


class TestQuickDataAndSerialization:
    """Test quick data access and serialization."""
    
    @patch('app.core.ephemeris.charts.natal.NatalChart._calculate_single_object')
    @patch('app.core.ephemeris.charts.natal.NatalChart._calculate_houses_and_angles')
    def test_get_quick_data(self, mock_houses, mock_object):
        """Test getting quick chart data."""
        # Mock essential object calculation
        mock_planet = MagicMock()
        mock_planet.longitude = 285.5
        mock_planet.sign_name = 'Capricorn'
        mock_planet.sign_longitude = 15.5
        mock_object.return_value = mock_planet
        
        # Mock angles
        mock_angles = MagicMock()
        mock_angles.ascendant = 90.0
        mock_angles.midheaven = 0.0
        mock_houses.return_value = (MagicMock(), mock_angles)
        
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        quick_data = chart.get_quick_data()
        
        assert 'subject' in quick_data
        assert 'datetime' in quick_data
        assert 'planets' in quick_data
        assert 'angles' in quick_data
        
        assert quick_data['subject'] == "Test"
        assert SwePlanets.SUN in quick_data['planets']
        assert quick_data['angles']['ascendant'] == 90.0
    
    def test_repr(self):
        """Test string representation of NatalChart."""
        subject = Subject("John Doe", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject, house_system=HouseSystems.KOCH)
        
        repr_str = repr(chart)
        
        assert "John Doe" in repr_str
        assert "K" in repr_str  # House system code, not full name
        assert "NatalChart" in repr_str


class TestThreadSafety:
    """Test thread safety of chart calculations."""
    
    def test_calculation_lock(self):
        """Test that calculations are properly locked."""
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        # Verify lock exists
        assert hasattr(chart, '_calculation_lock')
        assert chart._calculation_lock is not None
    
    def test_cached_result_thread_safety(self):
        """Test cached result handling is thread-safe."""
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        # Initial state
        assert chart._cached_result is None
        
        # After calculation, should be cached
        with patch.object(chart, '_calculate_objects_parallel', return_value={SwePlanets.SUN: MagicMock()}):
            with patch.object(chart, '_calculate_houses_and_angles', return_value=(MagicMock(), MagicMock())):
                result = chart.calculate()
                assert chart._cached_result is not None
                assert chart._cached_result is result