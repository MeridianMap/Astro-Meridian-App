"""
Unit tests for the Meridian Ephemeris Engine date/time utilities.
"""

import pytest
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import patch, MagicMock

from app.core.ephemeris.tools.date import (
    to_datetime, to_julian_day, localize_datetime, get_timezone_info,
    lookup_timezone_by_coordinates, get_timezone_name, is_ambiguous_time,
    is_dst_active, get_utc_offset, normalize_datetime_to_utc,
    datetime_difference, create_datetime, get_current_julian_day,
    julian_day_to_calendar_date, is_leap_year, days_in_month,
    add_time_to_julian_day
)


class TestDateTimeConversion:
    """Test datetime conversion functions."""
    
    def test_to_datetime_from_string(self):
        """Test datetime conversion from ISO string."""
        result = to_datetime("2000-01-01T12:00:00")
        assert result.year == 2000
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.tzinfo == ZoneInfo("UTC")
    
    def test_to_datetime_from_julian_day(self):
        """Test datetime conversion from Julian Day."""
        jd = 2451545.0  # J2000.0 epoch
        result = to_datetime(jd)
        assert result.year == 2000
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.tzinfo == ZoneInfo("UTC")
    
    def test_to_datetime_from_datetime_object(self):
        """Test datetime conversion from datetime object."""
        dt = datetime(2000, 1, 1, 12, 0, 0)
        result = to_datetime(dt)
        assert result.year == 2000
        assert result.tzinfo == ZoneInfo("UTC")
    
    def test_to_datetime_with_timezone_name(self):
        """Test datetime conversion with explicit timezone."""
        result = to_datetime("2000-01-01T12:00:00", timezone_name="America/New_York")
        assert result.tzinfo == ZoneInfo("America/New_York")
    
    def test_to_datetime_with_utc_offset(self):
        """Test datetime conversion with UTC offset."""
        result = to_datetime("2000-01-01T12:00:00", utc_offset=-5.0)
        assert result.utcoffset() == timedelta(hours=-5)
    
    @patch('app.core.ephemeris.tools.date.lookup_timezone_by_coordinates')
    def test_to_datetime_with_coordinates(self, mock_lookup):
        """Test datetime conversion with coordinates."""
        mock_lookup.return_value = "America/New_York"
        result = to_datetime("2000-01-01T12:00:00", latitude=40.7, longitude=-74.0)
        assert result is not None
        mock_lookup.assert_called_with(40.7, -74.0)
    
    def test_to_datetime_invalid_input(self):
        """Test datetime conversion with invalid input."""
        assert to_datetime("invalid date") is None
        assert to_datetime(2451545.0) is not None  # Valid Julian Day (J2000.0)
        assert to_datetime([1, 2, 3]) is None  # Invalid type


class TestJulianDayConversion:
    """Test Julian Day conversion functions."""
    
    def test_to_julian_day_from_datetime(self):
        """Test Julian Day conversion from datetime."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        jd = to_julian_day(dt)
        assert abs(jd - 2451545.0) < 0.001
    
    def test_to_julian_day_from_string(self):
        """Test Julian Day conversion from string."""
        jd = to_julian_day("2000-01-01T12:00:00")
        assert abs(jd - 2451545.0) < 0.001
    
    def test_to_julian_day_from_julian_day(self):
        """Test Julian Day conversion from Julian Day (should return same)."""
        original_jd = 2451545.0
        result_jd = to_julian_day(original_jd)
        assert result_jd == original_jd
    
    def test_to_julian_day_with_timezone(self):
        """Test Julian Day conversion with timezone handling."""
        # Same moment in different timezones should give same Julian Day
        utc_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        est_dt = datetime(2000, 1, 1, 7, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        
        utc_jd = to_julian_day(utc_dt)
        est_jd = to_julian_day(est_dt)
        
        assert abs(utc_jd - est_jd) < 0.001
    
    def test_to_julian_day_invalid_input(self):
        """Test Julian Day conversion with invalid input."""
        assert to_julian_day("invalid") is None
        assert to_julian_day([1, 2, 3]) is None


class TestTimezoneHandling:
    """Test timezone-related functions."""
    
    def test_get_timezone_info_explicit_name(self):
        """Test timezone info with explicit name."""
        tz_info = get_timezone_info(None, None, None, "America/New_York")
        assert tz_info == ZoneInfo("America/New_York")
    
    def test_get_timezone_info_utc_offset(self):
        """Test timezone info with UTC offset."""
        tz_info = get_timezone_info(None, None, -5.0, None)
        assert tz_info == timezone(timedelta(hours=-5))
    
    @patch('app.core.ephemeris.tools.date.lookup_timezone_by_coordinates')
    def test_get_timezone_info_coordinates(self, mock_lookup):
        """Test timezone info with coordinates."""
        mock_lookup.return_value = "Europe/London"
        tz_info = get_timezone_info(51.5, -0.1, None, None)
        assert tz_info == ZoneInfo("Europe/London")
        mock_lookup.assert_called_with(51.5, -0.1)
    
    def test_get_timezone_info_none_inputs(self):
        """Test timezone info with no valid inputs."""
        tz_info = get_timezone_info(None, None, None, None)
        assert tz_info is None
    
    @patch('app.core.ephemeris.tools.date._converter')
    def test_lookup_timezone_by_coordinates(self, mock_converter):
        """Test coordinate-based timezone lookup."""
        mock_finder = MagicMock()
        mock_finder.timezone_at.return_value = "America/New_York"
        mock_converter.timezone_finder = mock_finder
        
        result = lookup_timezone_by_coordinates(40.7, -74.0)
        assert result == "America/New_York"
        mock_finder.timezone_at.assert_called_with(lat=40.7, lng=-74.0)
    
    def test_get_timezone_name(self):
        """Test timezone name extraction."""
        dt_utc = datetime(2000, 1, 1, tzinfo=ZoneInfo("UTC"))
        assert get_timezone_name(dt_utc) == "UTC"
        
        dt_naive = datetime(2000, 1, 1)
        assert get_timezone_name(dt_naive) is None
    
    def test_localize_datetime(self):
        """Test datetime localization."""
        naive_dt = datetime(2000, 1, 1, 12, 0, 0)
        localized = localize_datetime(naive_dt, timezone_name="America/New_York")
        
        assert localized.tzinfo == ZoneInfo("America/New_York")
        assert localized.year == 2000


class TestDSTAndAmbiguity:
    """Test DST and time ambiguity handling."""
    
    def test_is_dst_active(self):
        """Test DST detection."""
        # Summer time in New York (DST active)
        summer_dt = datetime(2023, 7, 1, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        assert is_dst_active(summer_dt) is True
        
        # Winter time in New York (standard time)
        winter_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        assert is_dst_active(winter_dt) is False
        
        # UTC has no DST
        utc_dt = datetime(2023, 7, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        assert is_dst_active(utc_dt) is False
        
        # Naive datetime
        naive_dt = datetime(2023, 7, 1, 12, 0, 0)
        assert is_dst_active(naive_dt) is None
    
    def test_get_utc_offset(self):
        """Test UTC offset calculation."""
        # EST (UTC-5)
        est_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        offset = get_utc_offset(est_dt)
        assert offset == -5.0
        
        # EDT (UTC-4) 
        edt_dt = datetime(2023, 7, 1, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        offset = get_utc_offset(edt_dt)
        assert offset == -4.0
        
        # UTC
        utc_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        offset = get_utc_offset(utc_dt)
        assert offset == 0.0
        
        # Naive datetime
        naive_dt = datetime(2023, 1, 1, 12, 0, 0)
        assert get_utc_offset(naive_dt) is None


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_normalize_datetime_to_utc(self):
        """Test UTC normalization."""
        # Already UTC
        utc_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        result = normalize_datetime_to_utc(utc_dt)
        assert result == utc_dt
        
        # Naive datetime (treated as UTC)
        naive_dt = datetime(2000, 1, 1, 12, 0, 0)
        result = normalize_datetime_to_utc(naive_dt)
        assert result.tzinfo == ZoneInfo("UTC")
        
        # Timezone-aware datetime
        est_dt = datetime(2000, 1, 1, 7, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        result = normalize_datetime_to_utc(est_dt)
        assert result.tzinfo == ZoneInfo("UTC")
        assert result.hour == 12  # Should be converted to UTC
    
    def test_datetime_difference(self):
        """Test datetime difference calculation."""
        dt1 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        dt2 = datetime(2000, 1, 1, 13, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        diff = datetime_difference(dt2, dt1)
        assert diff == timedelta(hours=1)
        
        # Test with different timezones
        utc_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        est_dt = datetime(2000, 1, 1, 7, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        
        diff = datetime_difference(utc_dt, est_dt)
        assert abs(diff.total_seconds()) < 1  # Should be nearly zero
    
    def test_create_datetime(self):
        """Test datetime creation helper."""
        dt = create_datetime(2000, 1, 1, 12, 0, 0)
        assert dt.year == 2000
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12
        assert dt.tzinfo == ZoneInfo("UTC")
        
        # With explicit timezone
        dt = create_datetime(2000, 1, 1, timezone_info=ZoneInfo("America/New_York"))
        assert dt.tzinfo == ZoneInfo("America/New_York")


class TestCalendarFunctions:
    """Test calendar-related functions."""
    
    def test_julian_day_to_calendar_date(self):
        """Test Julian Day to calendar conversion."""
        jd = 2451545.0  # J2000.0
        year, month, day, hour = julian_day_to_calendar_date(jd)
        
        assert year == 2000
        assert month == 1
        assert day == 1
        assert abs(hour - 12.0) < 0.001
    
    def test_is_leap_year(self):
        """Test leap year detection."""
        assert is_leap_year(2000) is True   # Divisible by 400
        assert is_leap_year(2004) is True   # Divisible by 4
        assert is_leap_year(1900) is False  # Divisible by 100 but not 400
        assert is_leap_year(2001) is False  # Not divisible by 4
        assert is_leap_year(2024) is True   # Recent leap year
    
    def test_days_in_month(self):
        """Test days in month calculation."""
        # Regular months
        assert days_in_month(2023, 1) == 31   # January
        assert days_in_month(2023, 4) == 30   # April
        assert days_in_month(2023, 2) == 28   # February (non-leap)
        
        # Leap year February
        assert days_in_month(2024, 2) == 29
        
        # Invalid month
        with pytest.raises(ValueError):
            days_in_month(2023, 13)
    
    def test_add_time_to_julian_day(self):
        """Test adding time to Julian Day."""
        jd = 2451545.0  # J2000.0 at noon
        
        # Add 12 hours (should be midnight next day)
        jd_plus_12h = add_time_to_julian_day(jd, hours=12)
        assert abs(jd_plus_12h - 2451545.5) < 0.001
        
        # Add 1 day
        jd_plus_1d = add_time_to_julian_day(jd, hours=24)
        assert abs(jd_plus_1d - 2451546.0) < 0.001
        
        # Add minutes and seconds
        jd_plus_time = add_time_to_julian_day(jd, minutes=30, seconds=30)
        expected_addition = (30 * 60 + 30) / 86400.0  # Convert to days
        assert abs(jd_plus_time - (jd + expected_addition)) < 0.0001


class TestEdgeCasesAndErrors:
    """Test edge cases and error conditions."""
    
    def test_invalid_iso_strings(self):
        """Test handling of invalid ISO strings."""
        assert to_datetime("not a date") is None
        assert to_datetime("2000-13-01") is None  # Invalid month
        assert to_datetime("") is None
    
    def test_extreme_julian_days(self):
        """Test handling of extreme Julian Day values."""
        # Early date within datetime range (year 100 AD)
        early_jd = 1757585.0  # Approximately year 100 AD
        result = to_datetime(early_jd)
        assert result is not None
        
        # Late date within datetime range (year 3000 AD)
        late_jd = 2816788.0  # Approximately year 3000 AD
        result = to_datetime(late_jd)
        assert result is not None
    
    def test_timezone_lookup_errors(self):
        """Test timezone lookup error handling."""
        # Invalid coordinates (middle of ocean)
        result = lookup_timezone_by_coordinates(0, 0)
        # Should not raise exception, may return None or UTC
        assert result is None or isinstance(result, str)
        
        # Extreme coordinates
        result = lookup_timezone_by_coordinates(91, 181)  # Invalid lat/lon
        # Should handle gracefully
        assert result is None or isinstance(result, str)
    
    @pytest.mark.parametrize("year,month,expected_days", [
        (2023, 1, 31), (2023, 2, 28), (2024, 2, 29), (2023, 4, 30),
        (2023, 12, 31), (2000, 2, 29), (1900, 2, 28)
    ])
    def test_days_in_month_various_cases(self, year, month, expected_days):
        """Test days in month for various cases."""
        assert days_in_month(year, month) == expected_days


class TestRoundTripConversions:
    """Test round-trip conversions to ensure consistency."""
    
    def test_datetime_julian_day_round_trip(self):
        """Test datetime → Julian Day → datetime consistency."""
        original_dt = datetime(2023, 6, 15, 14, 30, 45, tzinfo=ZoneInfo("UTC"))
        
        # Convert to Julian Day and back
        jd = to_julian_day(original_dt)
        result_dt = to_datetime(jd)
        
        # Should be very close (within seconds due to precision)
        time_diff = abs((original_dt - result_dt).total_seconds())
        assert time_diff < 1.0
    
    def test_string_datetime_round_trip(self):
        """Test string → datetime → string consistency."""
        original_string = "2023-06-15T14:30:45"
        
        # Convert to datetime and back to Julian Day
        dt = to_datetime(original_string)
        jd = to_julian_day(dt)
        back_to_dt = to_datetime(jd)
        
        # Should preserve the essential time information
        assert back_to_dt.year == 2023
        assert back_to_dt.month == 6
        assert back_to_dt.day == 15
        assert back_to_dt.hour == 14