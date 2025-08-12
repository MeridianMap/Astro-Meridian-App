"""
Meridian Ephemeris Engine - Date and Time Utilities

Provides robust date/time conversion utilities with timezone support,
DST handling, and cross-platform compatibility. Maintains full parity
with Immanuel reference implementation while adding enhanced features.

Features:
- String/datetime/Julian Date conversions
- Timezone-aware calculations using coordinates
- DST-safe time handling with ambiguity resolution  
- Cross-platform timezone support
- High-precision Julian Date calculations
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Tuple
from zoneinfo import ZoneInfo

import swisseph as swe
from dateutil import tz
from timezonefinder import TimezoneFinder

from .convert import dms_to_decimal, decimal_to_dms
from ..classes.cache import cached


# Type aliases
DateTimeInput = Union[str, float, datetime]
TimezoneInput = Union[str, float, None]


class DateTimeConverter:
    """Main converter class for date/time operations."""
    
    def __init__(self):
        """Initialize with cached timezone finder."""
        self._tz_finder = None
    
    @property
    def timezone_finder(self) -> TimezoneFinder:
        """Lazy-loaded timezone finder instance."""
        if self._tz_finder is None:
            self._tz_finder = TimezoneFinder()
        return self._tz_finder


# Global converter instance
_converter = DateTimeConverter()


def to_datetime(
    dt_input: DateTimeInput,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    utc_offset: Optional[float] = None,
    timezone_name: Optional[str] = None,
    is_dst: Optional[bool] = None
) -> Optional[datetime]:
    """
    Convert various date/time formats to timezone-aware datetime.
    
    Args:
        dt_input: Date/time as string, Julian Date, or datetime object
        latitude: Observer latitude for timezone calculation
        longitude: Observer longitude for timezone calculation  
        utc_offset: UTC offset in hours (alternative to coordinates)
        timezone_name: Explicit timezone name (e.g., 'America/New_York')
        is_dst: DST flag for ambiguous times (True/False/None)
        
    Returns:
        Timezone-aware datetime object or None if conversion fails
        
    Examples:
        >>> to_datetime("2000-01-01 12:00:00")
        datetime(2000, 1, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        
        >>> to_datetime(2451545.0)  # J2000.0
        datetime(2000, 1, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
    """
    try:
        # Check if timezone info is needed
        needs_tz = any([latitude is not None, longitude is not None, 
                       utc_offset is not None, timezone_name is not None])
        
        if isinstance(dt_input, str):
            # Parse ISO format string
            dt = _parse_iso_string(dt_input)
            if dt is None:
                return None
                
            if not needs_tz:
                return dt.replace(tzinfo=ZoneInfo("UTC")) if dt.tzinfo is None else dt
            else:
                return localize_datetime(dt, latitude, longitude, utc_offset, timezone_name, is_dst)
                
        elif isinstance(dt_input, float):
            # Convert Julian Date to datetime
            ut_tuple = swe.revjul(dt_input)
            time_dms = decimal_to_dms(ut_tuple[3])
            
            dt = datetime(
                year=int(ut_tuple[0]),
                month=int(ut_tuple[1]), 
                day=int(ut_tuple[2]),
                hour=int(time_dms[1]),
                minute=int(time_dms[2]),
                second=int(time_dms[3]),
                microsecond=int((time_dms[3] % 1) * 1000000),
                tzinfo=ZoneInfo("UTC")
            )
            
            if not needs_tz:
                return dt
            else:
                return dt.astimezone(get_timezone_info(latitude, longitude, utc_offset, timezone_name))
                
        elif isinstance(dt_input, datetime):
            if not needs_tz:
                return dt_input.replace(tzinfo=ZoneInfo("UTC")) if dt_input.tzinfo is None else dt_input
            else:
                return localize_datetime(dt_input, latitude, longitude, utc_offset, timezone_name, is_dst)
                
        else:
            return None
            
    except Exception:
        return None


def to_julian_day(
    dt_input: DateTimeInput,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    utc_offset: Optional[float] = None,
    timezone_name: Optional[str] = None,
    is_dst: Optional[bool] = None
) -> Optional[float]:
    """
    Convert various date/time formats to Julian Day Number.
    
    Args:
        dt_input: Date/time in any supported format
        latitude: Observer latitude for timezone calculation
        longitude: Observer longitude for timezone calculation
        utc_offset: UTC offset in hours
        timezone_name: Explicit timezone name
        is_dst: DST flag for ambiguous times
        
    Returns:
        Julian Day Number or None if conversion fails
        
    Examples:
        >>> to_julian_day("2000-01-01 12:00:00")
        2451545.0
        
        >>> to_julian_day(datetime(2000, 1, 1, 12, 0))
        2451545.0
    """
    try:
        if isinstance(dt_input, float):
            return dt_input
            
        # Convert to datetime first
        dt = None
        if isinstance(dt_input, str):
            dt = _parse_iso_string(dt_input)
        elif isinstance(dt_input, datetime):
            dt = dt_input
        else:
            return None
            
        if dt is None:
            return None
            
        # Apply timezone if specified
        if any([latitude is not None, longitude is not None, timezone_name is not None]):
            dt = localize_datetime(dt, latitude, longitude, utc_offset, timezone_name, is_dst)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            
        # Convert to UTC for Julian Day calculation
        dt_utc = dt.astimezone(ZoneInfo("UTC"))
        
        # Calculate fractional hour for Swiss Ephemeris
        hour_decimal = dms_to_decimal([
            "+", dt_utc.hour, dt_utc.minute, 
            dt_utc.second + dt_utc.microsecond / 1000000.0
        ])
        
        return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)
        
    except Exception:
        return None


def localize_datetime(
    dt: datetime,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    utc_offset: Optional[float] = None,
    timezone_name: Optional[str] = None,
    is_dst: Optional[bool] = None
) -> Optional[datetime]:
    """
    Localize a naive datetime with timezone information.
    
    Args:
        dt: Naive or aware datetime object
        latitude: Observer latitude
        longitude: Observer longitude  
        utc_offset: UTC offset in hours
        timezone_name: Explicit timezone name
        is_dst: DST flag (None=auto, True=DST, False=standard time)
        
    Returns:
        Timezone-aware datetime or None if localization fails
    """
    try:
        timezone_info = get_timezone_info(latitude, longitude, utc_offset, timezone_name)
        if timezone_info is None:
            return dt.replace(tzinfo=ZoneInfo("UTC")) if dt.tzinfo is None else dt
            
        # Handle DST ambiguity with fold parameter
        fold_value = 0  # Default: first occurrence
        if is_dst is False:
            fold_value = 1  # Second occurrence (standard time)
            
        return dt.replace(tzinfo=timezone_info, fold=fold_value)
        
    except Exception:
        return None


@cached(ttl=3600)  # Cache timezone lookups for 1 hour
def get_timezone_info(
    latitude: Optional[float],
    longitude: Optional[float], 
    utc_offset: Optional[float],
    timezone_name: Optional[str]
) -> Optional[timezone]:
    """
    Get timezone info from various sources.
    
    Args:
        latitude: Observer latitude
        longitude: Observer longitude
        utc_offset: UTC offset in hours
        timezone_name: Explicit timezone name
        
    Returns:
        Timezone info object or None
    """
    try:
        # Explicit timezone name has highest priority
        if timezone_name is not None:
            return ZoneInfo(timezone_name)
            
        # UTC offset
        if utc_offset is not None:
            return timezone(timedelta(hours=utc_offset))
            
        # Coordinate-based timezone lookup
        if latitude is not None and longitude is not None:
            tz_name = lookup_timezone_by_coordinates(latitude, longitude)
            if tz_name:
                return ZoneInfo(tz_name)
                
        return None
        
    except Exception:
        return None


@cached(ttl=86400)  # Cache coordinate lookups for 24 hours
def lookup_timezone_by_coordinates(latitude: float, longitude: float) -> Optional[str]:
    """
    Look up timezone name by coordinates.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        
    Returns:
        Timezone name (e.g., 'America/New_York') or None
    """
    try:
        return _converter.timezone_finder.timezone_at(lat=latitude, lng=longitude)
    except Exception:
        return None


def get_timezone_name(dt: datetime) -> Optional[str]:
    """
    Get timezone name from datetime object.
    
    Args:
        dt: Timezone-aware datetime
        
    Returns:
        Timezone name string or None
    """
    if dt.tzinfo is not None:
        return str(dt.tzinfo)
    return None


def is_ambiguous_time(dt: datetime) -> bool:
    """
    Check if datetime falls in DST transition (ambiguous time).
    
    Args:
        dt: Timezone-aware datetime
        
    Returns:
        True if time is ambiguous (occurs twice due to DST)
    """
    try:
        return tz.datetime_ambiguous(dt)
    except Exception:
        return False


def is_dst_active(dt: datetime) -> Optional[bool]:
    """
    Check if DST is active for given datetime.
    
    Args:
        dt: Timezone-aware datetime
        
    Returns:
        True if DST active, False if standard time, None if unknown
    """
    try:
        if dt.tzinfo is None:
            return None
        return bool(dt.dst())
    except Exception:
        return None


def get_utc_offset(dt: datetime) -> Optional[float]:
    """
    Get UTC offset in hours for datetime.
    
    Args:
        dt: Timezone-aware datetime
        
    Returns:
        UTC offset in hours or None if timezone-naive
    """
    try:
        if dt.tzinfo is None:
            return None
        offset_td = dt.utcoffset()
        if offset_td is not None:
            return offset_td.total_seconds() / 3600.0
        return None
    except Exception:
        return None


def normalize_datetime_to_utc(dt: datetime) -> datetime:
    """
    Convert datetime to UTC, handling timezone-naive as UTC.
    
    Args:
        dt: Datetime object (naive or aware)
        
    Returns:
        UTC datetime
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo("UTC"))


def datetime_difference(dt1: datetime, dt2: datetime) -> timedelta:
    """
    Calculate difference between two datetimes, handling timezones.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        
    Returns:
        Time difference as timedelta
    """
    # Normalize both to UTC for comparison
    dt1_utc = normalize_datetime_to_utc(dt1)
    dt2_utc = normalize_datetime_to_utc(dt2)
    return dt1_utc - dt2_utc


# Helper functions
def _parse_iso_string(iso_string: str) -> Optional[datetime]:
    """
    Parse ISO format datetime string.
    
    Args:
        iso_string: ISO format string (e.g., '2000-01-01T12:00:00')
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        # Handle various ISO format variations
        iso_string = iso_string.strip()
        
        # Replace space with T for ISO compliance
        iso_string = re.sub(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})', r'\1T\2', iso_string)
        
        return datetime.fromisoformat(iso_string)
    except Exception:
        return None


def create_datetime(
    year: int,
    month: int = 1,
    day: int = 1, 
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
    timezone_info: Optional[timezone] = None
) -> datetime:
    """
    Create datetime with optional timezone.
    
    Args:
        year: Year
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59)
        microsecond: Microsecond (0-999999)
        timezone_info: Timezone info
        
    Returns:
        Datetime object
    """
    return datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
        tzinfo=timezone_info or ZoneInfo("UTC")
    )


def get_current_julian_day() -> float:
    """Get current Julian Day Number."""
    return to_julian_day(datetime.now(ZoneInfo("UTC")))


def julian_day_to_calendar_date(jd: float) -> Tuple[int, int, int, float]:
    """
    Convert Julian Day to calendar date.
    
    Args:
        jd: Julian Day Number
        
    Returns:
        Tuple of (year, month, day, hour_decimal)
    """
    return swe.revjul(jd)


def is_leap_year(year: int) -> bool:
    """
    Check if year is a leap year.
    
    Args:
        year: Year to check
        
    Returns:
        True if leap year, False otherwise
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    """
    Get number of days in month for given year.
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        Number of days in month
    """
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        return 29 if is_leap_year(year) else 28
    else:
        raise ValueError(f"Invalid month: {month}")


def add_time_to_julian_day(jd: float, hours: float = 0, minutes: float = 0, seconds: float = 0) -> float:
    """
    Add time to Julian Day Number.
    
    Args:
        jd: Julian Day Number
        hours: Hours to add
        minutes: Minutes to add  
        seconds: Seconds to add
        
    Returns:
        New Julian Day Number
    """
    total_seconds = hours * 3600 + minutes * 60 + seconds
    days_to_add = total_seconds / 86400.0  # Convert to days
    return jd + days_to_add