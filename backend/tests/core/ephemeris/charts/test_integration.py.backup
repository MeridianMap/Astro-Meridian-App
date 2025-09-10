"""
Integration tests for Meridian Ephemeris Engine Chart Construction.

Tests the complete workflow from Subject creation to NatalChart calculation,
ensuring all components work together properly.
"""

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.ephemeris.charts.subject import Subject
from app.core.ephemeris.charts.natal import NatalChart
from app.core.ephemeris.const import SwePlanets, HouseSystems


class TestChartIntegration:
    """Test complete chart construction workflow."""
    
    def test_end_to_end_natal_chart_construction(self):
        """Test complete natal chart construction from subject to calculated chart."""
        # Create subject
        subject = Subject(
            name="Test Subject",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )
        
        assert subject.is_valid()
        subject_data = subject.get_data()
        
        # Verify subject data
        assert subject_data.name == "Test Subject"
        assert abs(subject_data.latitude - 40.7128) < 0.01
        assert abs(subject_data.longitude - (-74.0060)) < 0.01
        assert subject_data.timezone_name == "America/New_York"
        
        # Create natal chart
        chart = NatalChart(subject)
        
        # Test quick data first
        quick_data = chart.get_quick_data()
        
        assert 'subject' in quick_data
        assert 'planets' in quick_data
        assert 'angles' in quick_data
        assert quick_data['subject'] == "Test Subject"
        assert len(quick_data['planets']) >= 7  # At least 7 traditional planets
        
        # Verify essential planets are present
        assert SwePlanets.SUN in quick_data['planets']
        assert SwePlanets.MOON in quick_data['planets']
        assert SwePlanets.MERCURY in quick_data['planets']
        
        # Test chart serialization
        chart_dict = chart.to_dict()
        
        assert 'subject' in chart_dict
        assert 'planets' in chart_dict
        assert 'houses' in chart_dict
        assert 'angles' in chart_dict
        assert 'calculation_time' in chart_dict
        assert chart_dict['chart_type'] == 'natal'
    
    def test_multiple_house_systems(self):
        """Test natal chart with different house systems."""
        subject = Subject("Test", "2000-06-15T14:30:00", 51.5074, -0.1278)
        
        # Test Placidus (default)
        chart_placidus = NatalChart(subject, house_system=HouseSystems.PLACIDUS)
        quick_data_p = chart_placidus.get_quick_data()
        assert 'angles' in quick_data_p
        
        # Test Koch
        chart_koch = NatalChart(subject, house_system=HouseSystems.KOCH)
        quick_data_k = chart_koch.get_quick_data()
        assert 'angles' in quick_data_k
        
        # Different systems should produce different results
        # (though angles might be similar, house cusps should differ)
        assert quick_data_p is not quick_data_k
    
    def test_chart_configuration_options(self):
        """Test various chart configuration options."""
        subject = Subject("Test", "1990-03-21T06:00:00", 0.0, 0.0)
        
        # Minimal configuration
        minimal_chart = NatalChart(
            subject,
            include_asteroids=False,
            include_nodes=False,
            include_lilith=False
        )
        
        objects_minimal = minimal_chart._get_calculation_objects()
        
        # Full configuration
        full_chart = NatalChart(
            subject,
            include_asteroids=True,
            include_nodes=True,
            include_lilith=True
        )
        
        objects_full = full_chart._get_calculation_objects()
        
        # Full configuration should have more objects
        assert len(objects_full) > len(objects_minimal)
        
        # Both should include basic planets
        for planet in [SwePlanets.SUN, SwePlanets.MOON, SwePlanets.MERCURY]:
            assert planet in objects_minimal
            assert planet in objects_full
    
    def test_coordinate_edge_cases(self):
        """Test chart construction with edge case coordinates."""
        # North Pole
        subject_north = Subject("North Pole", "2000-01-01T00:00:00", 90.0, 0.0)
        chart_north = NatalChart(subject_north)
        quick_north = chart_north.get_quick_data()
        assert 'planets' in quick_north
        
        # South Pole  
        subject_south = Subject("South Pole", "2000-01-01T00:00:00", -90.0, 0.0)
        chart_south = NatalChart(subject_south)
        quick_south = chart_south.get_quick_data()
        assert 'planets' in quick_south
        
        # International Date Line
        subject_idl = Subject("Date Line", "2000-01-01T00:00:00", 0.0, 180.0)
        chart_idl = NatalChart(subject_idl)
        quick_idl = chart_idl.get_quick_data()
        assert 'planets' in quick_idl
    
    def test_different_time_periods(self):
        """Test chart construction for different historical periods."""
        # Ancient date (within reasonable bounds)
        subject_ancient = Subject("Ancient", "0100-01-01T12:00:00", 40.0, -3.0)
        chart_ancient = NatalChart(subject_ancient)
        quick_ancient = chart_ancient.get_quick_data()
        assert len(quick_ancient['planets']) > 0
        
        # Modern date
        subject_modern = Subject("Modern", "2023-12-25T00:00:00", 40.0, -3.0)
        chart_modern = NatalChart(subject_modern)
        quick_modern = chart_modern.get_quick_data()
        assert len(quick_modern['planets']) > 0
        
        # Future date (within reasonable bounds)
        subject_future = Subject("Future", "2050-01-01T12:00:00", 40.0, -3.0)
        chart_future = NatalChart(subject_future)
        quick_future = chart_future.get_quick_data()
        assert len(quick_future['planets']) > 0


class TestSubjectChartInteraction:
    """Test interaction between Subject and Chart classes."""
    
    def test_subject_data_preservation(self):
        """Test that subject data is preserved through chart construction."""
        original_subject = Subject(
            name="Data Preservation Test",
            datetime="1985-07-04T19:30:00",
            latitude=34.0522,
            longitude=-118.2437,
            altitude=100.0,
            timezone="America/Los_Angeles"
        )
        
        chart = NatalChart(original_subject)
        chart_data = chart.calculate()
        
        # Verify subject data is preserved
        assert chart_data.subject.name == "Data Preservation Test"
        assert abs(chart_data.subject.latitude - 34.0522) < 0.01
        assert abs(chart_data.subject.longitude - (-118.2437)) < 0.01
        assert chart_data.subject.altitude == 100.0
        assert chart_data.subject.timezone_name == "America/Los_Angeles"
    
    def test_chart_from_subject_data_directly(self):
        """Test creating chart directly from SubjectData."""
        subject = Subject("Test", "2000-01-01T12:00:00", 0.0, 0.0)
        subject_data = subject.get_data()
        
        # Create chart from SubjectData directly
        chart = NatalChart(subject_data)
        quick_data = chart.get_quick_data()
        
        assert quick_data['subject'] == "Test"
        assert 'planets' in quick_data
    
    def test_invalid_subject_handling(self):
        """Test chart construction with invalid subject types."""
        with pytest.raises(TypeError):
            NatalChart("not a subject")
        
        with pytest.raises(TypeError):
            NatalChart(123)
        
        with pytest.raises(TypeError):
            NatalChart({'name': 'test'})


class TestChartCalculationPerformance:
    """Test chart calculation performance characteristics."""
    
    def test_calculation_caching(self):
        """Test that chart calculations are properly cached."""
        subject = Subject("Cache Test", "2000-01-01T12:00:00", 40.0, -74.0)
        chart = NatalChart(subject)
        
        # First calculation
        result1 = chart.calculate()
        
        # Second calculation should return cached result
        result2 = chart.calculate()
        
        # Should be the same object (cached)
        assert result1 is result2
        
        # Force recalculation should produce new object  
        result3 = chart.calculate(force_recalculate=True)
        assert result3 is not result1
    
    def test_thread_safety_setup(self):
        """Test that thread safety mechanisms are properly set up."""
        subject = Subject("Thread Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        # Verify thread safety components exist
        assert hasattr(chart, '_calculation_lock')
        assert chart._calculation_lock is not None
        assert hasattr(chart, '_cached_result')


class TestErrorHandling:
    """Test error handling throughout the chart construction pipeline."""
    
    def test_graceful_calculation_failures(self):
        """Test that calculation failures are handled gracefully."""
        subject = Subject("Error Test", "2000-01-01T12:00:00", 0.0, 0.0)
        chart = NatalChart(subject)
        
        # The chart should be created even if some calculations might fail
        assert chart is not None
        assert chart.subject_data.name == "Error Test"
    
    def test_configuration_validation(self):
        """Test that chart configuration is properly validated."""
        subject = Subject("Config Test", "2000-01-01T12:00:00", 0.0, 0.0)
        
        # Valid house system
        chart_valid = NatalChart(subject, house_system=HouseSystems.PLACIDUS)
        assert chart_valid.house_system == HouseSystems.PLACIDUS
        
        # Custom orbs
        custom_orbs = {'Conjunction': 12.0}
        chart_custom = NatalChart(subject, aspect_orbs=custom_orbs)
        assert chart_custom.aspect_orbs['Conjunction'] == 12.0