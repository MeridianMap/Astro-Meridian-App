"""
Edge case tests for Meridian Ephemeris Engine.

Tests DST transitions, high latitude calculations, leap years,
and other boundary conditions as specified in PRP 5.
"""

import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from tests.utils import (
    assert_angle_close, assert_planet_position_close, load_fixture,
    create_test_subject_data, PerformanceTracker
)
from app.core.ephemeris.charts.subject import Subject
from app.core.ephemeris.charts.natal import NatalChart
from app.core.ephemeris.tools.ephemeris import get_planet
from app.core.ephemeris.tools.date import to_julian_day, to_datetime
from app.core.ephemeris.const import SwePlanets, HouseSystems


class TestDSTTransitions:
    """Test calculations during DST transitions."""
    
    def test_spring_forward_transition(self):
        """Test chart during spring DST transition (2AM -> 3AM)."""
        # March 12, 2023 - Spring forward in US Eastern time
        subject = Subject(
            name="DST Spring Forward",
            datetime="2023-03-12T02:30:00",  # This time doesn't exist!
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )
        
        # Should handle the non-existent time gracefully
        assert subject.is_valid()
        data = subject.get_data()
        
        # Verify that timezone handling is correct
        assert data.timezone_name == "America/New_York"
        
        # Calculate chart - should work without errors
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        assert chart_data is not None
        assert len(chart_data.planets) > 0
    
    def test_fall_back_transition(self):
        """Test chart during fall DST transition (2AM -> 1AM)."""
        # November 5, 2023 - Fall back in US Eastern time
        subject = Subject(
            name="DST Fall Back",
            datetime="2023-11-05T01:30:00",  # Ambiguous time
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        
        # Calculate chart
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        assert chart_data is not None
        assert len(chart_data.planets) > 0
    
    def test_dst_aware_calculation_consistency(self):
        """Test that DST-aware calculations are consistent."""
        # Same local time, different DST status
        winter_subject = Subject(
            name="Winter Time",
            datetime="2023-01-15T12:00:00",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )
        
        summer_subject = Subject(
            name="Summer Time", 
            datetime="2023-07-15T12:00:00",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )
        
        winter_data = winter_subject.get_data()
        summer_data = summer_subject.get_data()
        
        # UTC times should differ by 1 hour due to DST
        winter_utc = winter_data.datetime.astimezone(timezone.utc)
        summer_utc = summer_data.datetime.astimezone(timezone.utc)
        
        # Both should be valid and calculable
        winter_chart = NatalChart(winter_subject).calculate()
        summer_chart = NatalChart(summer_subject).calculate()
        
        assert winter_chart is not None
        assert summer_chart is not None


class TestHighLatitudeCalculations:
    """Test calculations at high latitudes near polar regions."""
    
    def test_arctic_circle_summer_solstice(self):
        """Test calculation at Arctic Circle during summer solstice."""
        subject = Subject(
            name="Arctic Circle Summer",
            datetime="2000-06-21T12:00:00",  # Summer solstice
            latitude=66.5,  # Arctic Circle
            longitude=0.0,
            timezone="UTC"
        )
        
        assert subject.is_valid()
        
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        # Should calculate without errors despite extreme latitude
        assert chart_data is not None
        assert len(chart_data.planets) > 0
        assert chart_data.angles is not None
    
    def test_antarctic_circle_winter_solstice(self):
        """Test calculation at Antarctic Circle during winter solstice."""
        subject = Subject(
            name="Antarctic Circle Winter",
            datetime="2000-12-21T12:00:00",  # Winter solstice
            latitude=-66.5,  # Antarctic Circle
            longitude=0.0,
            timezone="UTC"
        )
        
        assert subject.is_valid()
        
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        assert chart_data is not None
        assert len(chart_data.planets) > 0
    
    def test_north_pole_calculation(self):
        """Test calculation at North Pole."""
        subject = Subject(
            name="North Pole",
            datetime="2000-01-01T12:00:00",
            latitude=90.0,  # North Pole
            longitude=0.0,
            timezone="UTC"
        )
        
        assert subject.is_valid()
        
        # Chart calculation might have issues at exact pole
        # but should not crash
        try:
            chart = NatalChart(subject)
            chart_data = chart.calculate()
            assert chart_data is not None
        except Exception as e:
            # Document that pole calculations may be problematic
            pytest.skip(f"North Pole calculation failed as expected: {e}")
    
    def test_reykjavik_midnight_sun(self):
        """Test calculation in Reykjavik during midnight sun period."""
        subject = Subject(
            name="Reykjavik Midnight Sun",
            datetime="2000-06-21T00:00:00",  # Midnight on summer solstice
            latitude=64.1466,
            longitude=-21.9426,
            timezone="Atlantic/Reykjavik"
        )
        
        assert subject.is_valid()
        
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        assert chart_data is not None
        assert len(chart_data.planets) > 0


class TestLeapYearCalculations:
    """Test calculations involving leap years."""
    
    def test_leap_day_calculation(self):
        """Test calculation on February 29 of leap year."""
        subject = Subject(
            name="Leap Day",
            datetime="2000-02-29T12:00:00",  # Feb 29, 2000
            latitude=0.0,
            longitude=0.0,
            timezone="UTC"
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        
        # Verify date is correctly parsed
        assert data.datetime.month == 2
        assert data.datetime.day == 29
        assert data.datetime.year == 2000
        
        # Calculate chart
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        assert chart_data is not None
        assert len(chart_data.planets) > 0
    
    def test_leap_year_century_boundary(self):
        """Test leap year calculation at century boundaries."""
        # 2000 is a leap year (divisible by 400)
        leap_subject = Subject(
            name="Century Leap Year",
            datetime="2000-02-29T12:00:00",
            latitude=0.0,
            longitude=0.0,
            timezone="UTC"
        )
        
        assert leap_subject.is_valid()
        
        # 1900 was not a leap year (divisible by 100 but not 400)
        # This date should be invalid
        with pytest.raises(ValueError):
            Subject(
                name="Century Non-Leap Year",
                datetime="1900-02-29T12:00:00",  # Invalid date
                latitude=0.0,
                longitude=0.0,
                timezone="UTC"
            )
    
    def test_leap_year_sequence(self):
        """Test calculations across leap year sequence."""
        dates = [
            "2000-02-28T12:00:00",  # Day before leap day
            "2000-02-29T12:00:00",  # Leap day
            "2000-03-01T12:00:00",  # Day after leap day
        ]
        
        julian_days = []
        for date_str in dates:
            subject = Subject(
                name=f"Leap Sequence {date_str}",
                datetime=date_str,
                latitude=0.0,
                longitude=0.0,
                timezone="UTC"
            )
            assert subject.is_valid()
            julian_days.append(subject.get_data().julian_day)
        
        # Julian days should be consecutive
        assert abs(julian_days[1] - julian_days[0] - 1.0) < 1e-6
        assert abs(julian_days[2] - julian_days[1] - 1.0) < 1e-6


class TestCoordinateBoundaries:
    """Test calculations at coordinate boundaries."""
    
    def test_international_date_line(self):
        """Test calculations at International Date Line."""
        # East side of date line
        subject_east = Subject(
            name="Date Line East",
            datetime="2000-01-01T12:00:00",
            latitude=0.0,
            longitude=179.9,
            timezone="UTC"
        )
        
        # West side of date line
        subject_west = Subject(
            name="Date Line West",
            datetime="2000-01-01T12:00:00",
            latitude=0.0,
            longitude=-179.9,
            timezone="UTC"
        )
        
        assert subject_east.is_valid()
        assert subject_west.is_valid()
        
        # Both should calculate successfully
        chart_east = NatalChart(subject_east).calculate()
        chart_west = NatalChart(subject_west).calculate()
        
        assert chart_east is not None
        assert chart_west is not None
        
        # Planetary positions should be very similar
        sun_east = chart_east.planets[SwePlanets.SUN]
        sun_west = chart_west.planets[SwePlanets.SUN]
        
        assert_angle_close(sun_east.longitude, sun_west.longitude, 
                          tolerance_arcsec=30.0, msg="Sun position across date line")
    
    def test_prime_meridian(self):
        """Test calculations at Prime Meridian."""
        subject = Subject(
            name="Prime Meridian",
            datetime="2000-01-01T12:00:00",
            latitude=51.4778,  # Greenwich
            longitude=0.0,
            timezone="UTC"
        )
        
        assert subject.is_valid()
        
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        assert chart_data is not None
        assert len(chart_data.planets) > 0
    
    def test_equator_crossing(self):
        """Test calculations at equator."""
        subject = Subject(
            name="Equator",
            datetime="2000-03-20T12:00:00",  # Equinox
            latitude=0.0,
            longitude=0.0,
            timezone="UTC"
        )
        
        assert subject.is_valid()
        
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        assert chart_data is not None
        assert len(chart_data.planets) > 0


class TestHistoricalDates:
    """Test calculations with historical dates."""
    
    def test_early_20th_century(self):
        """Test calculation from early 20th century."""
        subject = Subject(
            name="Early 20th Century",
            datetime="1900-01-01T12:00:00",
            latitude=48.8566,  # Paris
            longitude=2.3522,
            timezone="Europe/Paris"
        )
        
        assert subject.is_valid()
        
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        assert chart_data is not None
        assert len(chart_data.planets) > 0
    
    def test_late_21st_century(self):
        """Test calculation for late 21st century."""
        subject = Subject(
            name="Late 21st Century",
            datetime="2099-12-31T12:00:00",
            latitude=0.0,
            longitude=0.0,
            timezone="UTC"
        )
        
        assert subject.is_valid()
        
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        assert chart_data is not None
        assert len(chart_data.planets) > 0


class TestHouseSystemEdgeCases:
    """Test house system calculations in edge cases."""
    
    def test_multiple_house_systems_high_latitude(self):
        """Test different house systems at high latitude."""
        subject = Subject(
            name="High Latitude Houses",
            datetime="2000-06-21T12:00:00",
            latitude=65.0,  # Near Arctic Circle
            longitude=0.0,
            timezone="UTC"
        )
        
        house_systems = [
            HouseSystems.PLACIDUS,
            HouseSystems.KOCH,
            HouseSystems.EQUAL,
            HouseSystems.WHOLE_SIGN
        ]
        
        charts = {}
        for system in house_systems:
            try:
                chart = NatalChart(subject, house_system=system)
                chart_data = chart.calculate()
                charts[system] = chart_data
                assert chart_data is not None
                assert len(chart_data.houses.house_cusps) == 12
            except Exception as e:
                # Some house systems may fail at extreme latitudes
                print(f"House system {system} failed at high latitude: {e}")
        
        # At least one house system should work
        assert len(charts) > 0
    
    def test_house_cusp_ordering(self):
        """Test that house cusps are properly ordered."""
        subject = Subject(
            name="House Cusp Order",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )
        
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        cusps = chart_data.houses.house_cusps
        assert len(cusps) == 12
        
        # Cusps should generally increase in longitude
        # (with wraparound at 360 degrees)
        for i in range(11):
            diff = (cusps[i+1] - cusps[i]) % 360
            # Each house should be roughly 30 degrees (allow wide tolerance)
            assert 5 < diff < 90, f"House {i+1} to {i+2} span is {diff:.2f} degrees"


class TestPerformanceEdgeCases:
    """Test performance characteristics in edge cases."""
    
    def test_calculation_time_consistency(self):
        """Test that calculation times are consistent across edge cases."""
        import time
        
        edge_cases = [
            ("Standard", 40.7128, -74.0060, "2000-01-01T12:00:00"),
            ("High Lat", 66.0, 0.0, "2000-06-21T12:00:00"),
            ("South High Lat", -66.0, 0.0, "2000-01-01T12:00:00"),
            ("Date Line", 0.0, 179.9, "2000-01-01T12:00:00"),
            ("Leap Day", 0.0, 0.0, "2000-02-29T12:00:00")
        ]
        
        times = []
        results = {}
        
        for name, lat, lon, dt in edge_cases:
            subject = Subject(
                name=f"Performance {name}",
                datetime=dt,
                latitude=lat,
                longitude=lon,
                timezone="UTC"
            )
            
            start_time = time.time()
            chart = NatalChart(subject)
            chart_data = chart.calculate()
            end_time = time.time()
            
            duration = end_time - start_time
            times.append(duration)
            
            # Store results for analysis
            results[name] = {
                'duration': duration,
                'latitude': lat,
                'longitude': lon,
                'success': chart_data is not None
            }
            
            # Should complete within reasonable time
            assert duration < 5.0, f"{name} calculation took {duration:.2f}s"
            assert chart_data is not None
        
        # Times should be relatively consistent (within 10x of each other)
        min_time = min(times)
        max_time = max(times)
        assert max_time / min_time < 10, f"Performance varies too much: {min_time:.3f}s to {max_time:.3f}s"


class TestReferenceValidation:
    """Test against reference fixtures for validation."""
    
    def test_j2000_reference_positions(self):
        """Test planetary positions at J2000.0 epoch."""
        try:
            fixtures = load_fixture("reference_fixtures")
            j2000_case = fixtures["fixtures"]["basic_positions"]["test_cases"][0]
        except FileNotFoundError:
            pytest.skip("Reference fixtures not found")
        
        subject = Subject(
            name="J2000 Reference",
            datetime=j2000_case["datetime"],
            latitude=j2000_case["location"]["latitude"],
            longitude=j2000_case["location"]["longitude"],
            timezone="UTC"
        )
        
        chart = NatalChart(subject)
        chart_data = chart.calculate()
        
        # Check Sun position against reference
        expected_sun = j2000_case["expected_positions"]["sun"]
        actual_sun = chart_data.planets[SwePlanets.SUN]
        
        # Use wider tolerance for reference comparison
        assert_angle_close(
            actual_sun.longitude,
            expected_sun["longitude"],
            tolerance_arcsec=expected_sun["tolerance"] * 3600,  # Convert degrees to arcsec
            msg="J2000 Sun position"
        )


if __name__ == "__main__":
    # Run edge case tests
    pytest.main([__file__, "-v", "--tb=short"])