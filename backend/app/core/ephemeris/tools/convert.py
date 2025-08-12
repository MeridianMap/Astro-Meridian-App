"""
Meridian Ephemeris Engine - Coordinate Conversion Utilities

Provides robust coordinate conversion functions for DMS (Degrees/Minutes/Seconds) 
and decimal formats, with full parity to Immanuel reference implementation.

Features:
- DMS ↔ Decimal conversions with precision control
- String parsing and formatting in multiple formats
- Latitude/longitude coordinate handling
- Time format conversions
- Robust input type detection and conversion
"""

import math
import re
from typing import List, Tuple, Union, Optional
import swisseph as swe

from ..classes.cache import cached


# Format constants matching Immanuel
class Format:
    """Format constants for coordinate string representation."""
    TIME = 0
    TIME_OFFSET = 1
    DMS = 2
    LAT = 3
    LON = 4


# Rounding precision constants
class RoundTo:
    """Rounding precision constants with Swiss Ephemeris flags."""
    DEGREE = (1, swe.SPLIT_DEG_ROUND_DEG)
    MINUTE = (2, swe.SPLIT_DEG_ROUND_MIN)
    SECOND = (3, swe.SPLIT_DEG_ROUND_SEC)


# Type aliases for better readability
DMSType = Union[List, Tuple]
CoordinateInput = Union[float, List, Tuple, str]
DMSTuple = Tuple[str, int, int, float]


def dms_to_decimal(dms: DMSType) -> float:
    """
    Convert DMS (Degrees, Minutes, Seconds) to decimal degrees.
    
    Args:
        dms: DMS format as [sign, degrees, minutes, seconds] where:
             sign is "+" or "-", degrees/minutes are integers, seconds is float
    
    Returns:
        Decimal degrees as float
        
    Example:
        >>> dms_to_decimal(["+", 45, 30, 15.5])
        45.50430555555556
    """
    if not dms or len(dms) < 2:
        raise ValueError("DMS input must have at least sign and degrees")
    
    sign = dms[0]
    if isinstance(sign, str):
        negative = sign == "-"
    else:
        # Handle numeric first element (assume positive)
        negative = sign < 0
        dms = ["+"] + list(dms)
    
    # Calculate decimal value
    decimal = 0.0
    for i, value in enumerate(dms[1:]):
        if value is not None and value != 0:
            decimal += float(abs(value)) / (60 ** i)
    
    return -decimal if negative else decimal


def decimal_to_dms(
    decimal: float, 
    round_to: Tuple[int, int] = RoundTo.SECOND,
    pad_rounded: bool = False
) -> DMSTuple:
    """
    Convert decimal degrees to DMS format.
    
    Args:
        decimal: Decimal degrees
        round_to: Rounding precision (DEGREE, MINUTE, or SECOND)
        pad_rounded: Whether to pad with zeros for consistent format
        
    Returns:
        DMS tuple as (sign, degrees, minutes, seconds)
        
    Example:
        >>> decimal_to_dms(45.50430555555556)
        ('+', 45, 30, 15.5)
    """
    sign = "-" if decimal < 0 else "+"
    
    # Use Swiss Ephemeris split_deg for precise conversion
    dms_parts = list(swe.split_deg(abs(decimal), round_to[1])[:round_to[0]])
    
    # Ensure we have exactly the right number of components
    while len(dms_parts) < 3:
        dms_parts.append(0)
    
    # Convert to proper types
    degrees = int(dms_parts[0])
    minutes = int(dms_parts[1]) if len(dms_parts) > 1 else 0
    seconds = float(dms_parts[2]) if len(dms_parts) > 2 else 0.0
    
    if pad_rounded or round_to[0] == 3:
        return (sign, degrees, minutes, seconds)
    elif round_to[0] == 2:
        return (sign, degrees, minutes)
    else:
        return (sign, degrees)


def dms_to_string(
    dms: DMSType,
    format_type: int = Format.DMS,
    round_to: Tuple[int, int] = RoundTo.SECOND,
    pad_rounded: Optional[bool] = None
) -> str:
    """
    Convert DMS to formatted string representation.
    
    Args:
        dms: DMS tuple/list
        format_type: Output format (DMS, TIME, LAT, LON, etc.)
        round_to: Rounding precision
        pad_rounded: Whether to pad with zeros
        
    Returns:
        Formatted coordinate string
    """
    # Auto-determine padding for lat/lon formats
    if pad_rounded is None:
        pad_rounded = format_type in (Format.LAT, Format.LON) or format_type != Format.DMS
    
    # Use the DMS as provided to avoid rounding errors
    if not isinstance(dms, (list, tuple)) or len(dms) < 2:
        raise ValueError("Invalid DMS format")
    
    # Ensure we have a proper 4-element tuple
    dms_list = list(dms)
    while len(dms_list) < 4:
        dms_list.append(0)
    
    dms_tuple = tuple(dms_list[:4])
    
    if format_type == Format.DMS:
        return _format_dms(dms_tuple)
    elif format_type == Format.TIME:
        return _format_time(dms_tuple)
    elif format_type == Format.TIME_OFFSET:
        return _format_time_offset(dms_tuple)
    elif format_type == Format.LAT:
        return _format_latitude(dms_tuple)
    elif format_type == Format.LON:
        return _format_longitude(dms_tuple)
    else:
        return _format_dms(dms_tuple)


def string_to_dms(
    string: str,
    round_to: Tuple[int, int] = RoundTo.SECOND,
    pad_rounded: bool = False
) -> DMSTuple:
    """
    Parse string coordinate to DMS format.
    
    Args:
        string: Coordinate string in various formats
        round_to: Rounding precision
        pad_rounded: Whether to pad result
        
    Returns:
        DMS tuple
    """
    decimal = string_to_decimal(string)
    return decimal_to_dms(decimal, round_to, pad_rounded)


def decimal_to_string(
    decimal: float,
    format_type: int = Format.DMS,
    round_to: Tuple[int, int] = RoundTo.SECOND,
    pad_rounded: Optional[bool] = None
) -> str:
    """
    Convert decimal degrees to formatted string.
    
    Args:
        decimal: Decimal degrees
        format_type: Output format
        round_to: Rounding precision
        pad_rounded: Whether to pad with zeros
        
    Returns:
        Formatted coordinate string
    """
    dms_tuple = decimal_to_dms(decimal, round_to, pad_rounded or False)
    return dms_to_string(dms_tuple, format_type, round_to, pad_rounded)


@cached(ttl=300)  # Cache string parsing for 5 minutes
def string_to_decimal(string: str) -> float:
    """
    Parse coordinate string to decimal degrees.
    
    Supports various formats:
    - "45°30'15.5"" (DMS with symbols)
    - "45:30:15.5" (colon-separated)
    - "45N30.25" (latitude format)
    - "120W15.5" (longitude format)
    - "-45.5043" (simple decimal)
    
    Args:
        string: Coordinate string
        
    Returns:
        Decimal degrees
        
    Raises:
        ValueError: If string format is not recognized
    """
    string = string.strip()
    
    # Handle simple decimal numbers
    if _is_numeric(string):
        return float(string)
    
    # Extract numeric values and direction indicators
    digits = re.findall(r"[0-9\.-]+", string)
    if not digits:
        raise ValueError(f"No numeric values found in string: {string}")
    
    # Determine sign from direction character or negative number
    direction_char = ""
    
    # Look for direction characters (N/S/E/W) anywhere in the string
    direction_chars = re.findall(r'[NSEW]', string.upper())
    if direction_chars:
        direction_char = direction_chars[0]
    elif string.startswith('-'):
        direction_char = "-"
    
    # Convert to floats
    values = [float(d) for d in digits]
    
    # Determine if negative based on direction or sign
    negative = (direction_char and direction_char in "SW-") or (values[0] < 0)
    
    # Create DMS array
    sign = "-" if negative else "+"
    dms = [sign] + [abs(v) for v in values]
    
    # Ensure we have at least degrees
    while len(dms) < 2:
        dms.append(0)
    
    return dms_to_decimal(dms)


def to_decimal(value: CoordinateInput) -> Optional[float]:
    """
    Convert any coordinate format to decimal degrees.
    
    Args:
        value: Coordinate in any supported format
        
    Returns:
        Decimal degrees or None if conversion fails
    """
    try:
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, (list, tuple)):
            return dms_to_decimal(value)
        elif isinstance(value, str):
            return string_to_decimal(value)
        else:
            return None
    except (ValueError, TypeError):
        return None


def to_dms(
    value: CoordinateInput,
    round_to: Tuple[int, int] = RoundTo.SECOND,
    pad_rounded: bool = False
) -> Optional[DMSTuple]:
    """
    Convert any coordinate format to DMS.
    
    Args:
        value: Coordinate in any supported format
        round_to: Rounding precision
        pad_rounded: Whether to pad with zeros
        
    Returns:
        DMS tuple or None if conversion fails
    """
    try:
        if isinstance(value, (int, float)):
            return decimal_to_dms(float(value), round_to, pad_rounded)
        elif isinstance(value, (list, tuple)):
            # Already DMS, but standardize format
            decimal = dms_to_decimal(value)
            return decimal_to_dms(decimal, round_to, pad_rounded)
        elif isinstance(value, str):
            if _is_numeric(value):
                return decimal_to_dms(float(value), round_to, pad_rounded)
            else:
                return string_to_dms(value, round_to, pad_rounded)
        else:
            return None
    except (ValueError, TypeError):
        return None


def to_string(
    value: CoordinateInput,
    format_type: int = Format.DMS,
    round_to: Tuple[int, int] = RoundTo.SECOND,
    pad_rounded: Optional[bool] = None
) -> Optional[str]:
    """
    Convert any coordinate format to formatted string.
    
    Args:
        value: Coordinate in any supported format
        format_type: Output format
        round_to: Rounding precision
        pad_rounded: Whether to pad with zeros
        
    Returns:
        Formatted string or None if conversion fails
    """
    try:
        decimal = to_decimal(value)
        if decimal is not None:
            return decimal_to_string(decimal, format_type, round_to, pad_rounded)
        return None
    except (ValueError, TypeError):
        return None


def coordinates(
    latitude: CoordinateInput,
    longitude: CoordinateInput
) -> Tuple[Optional[float], Optional[float]]:
    """
    Convert latitude and longitude to decimal degrees.
    
    Args:
        latitude: Latitude in any supported format
        longitude: Longitude in any supported format
        
    Returns:
        Tuple of (lat_decimal, lon_decimal)
    """
    lat_decimal = to_decimal(latitude)
    lon_decimal = to_decimal(longitude)
    return lat_decimal, lon_decimal


def normalize_longitude(longitude: float) -> float:
    """
    Normalize longitude to 0-360 degree range.
    
    Args:
        longitude: Longitude in degrees
        
    Returns:
        Normalized longitude (0-360°)
    """
    return longitude % 360.0


def normalize_latitude(latitude: float) -> float:
    """
    Clamp latitude to valid -90 to +90 degree range.
    
    Args:
        latitude: Latitude in degrees
        
    Returns:
        Clamped latitude (-90° to +90°)
    """
    return max(-90.0, min(90.0, latitude))


# Private formatting functions
def _format_dms(dms: DMSTuple) -> str:
    """Format DMS as degrees/minutes/seconds with symbols."""
    sign, degrees, minutes, *rest = dms
    seconds = rest[0] if rest else 0
    
    symbols = ("°", "'", '"')
    result = f"{int(degrees):02d}{symbols[0]}"
    
    if len(dms) > 2:
        result += f"{int(minutes):02d}{symbols[1]}"
        if len(dms) > 3:
            result += f"{seconds:04.1f}{symbols[2]}"
    
    return f"{sign[0] if sign == '-' else ''}{result}"


def _format_time(dms: DMSTuple) -> str:
    """Format DMS as time (HH:MM:SS)."""
    sign, degrees, minutes, *rest = dms
    seconds = rest[0] if rest else 0
    
    result = f"{int(degrees):02d}:{int(minutes):02d}"
    if len(dms) > 3:
        result += f":{seconds:04.1f}"
    
    return f"{'-' if sign == '-' else ''}{result}"


def _format_time_offset(dms: DMSTuple) -> str:
    """Format DMS as signed time offset."""
    sign, degrees, minutes, *rest = dms
    seconds = rest[0] if rest else 0
    
    result = f"{int(degrees):02d}:{int(minutes):02d}"
    if len(dms) > 3:
        result += f":{seconds:04.1f}"
    
    return f"{sign}{result}"


def _format_latitude(dms: DMSTuple) -> str:
    """Format DMS as latitude (e.g., 45N30.25)."""
    sign, degrees, minutes, *rest = dms
    seconds = rest[0] if rest else 0
    
    direction = "S" if sign == "-" else "N"
    decimal_minutes = minutes + (seconds / 60.0) if rest else minutes
    
    return f"{int(degrees)}{direction}{decimal_minutes:.2f}"


def _format_longitude(dms: DMSTuple) -> str:
    """Format DMS as longitude (e.g., 120W15.5)."""
    sign, degrees, minutes, *rest = dms
    seconds = rest[0] if rest else 0
    
    direction = "W" if sign == "-" else "E"
    decimal_minutes = minutes + (seconds / 60.0) if rest else minutes
    
    return f"{int(degrees)}{direction}{decimal_minutes:.2f}"


def _is_numeric(value: str) -> bool:
    """Check if string represents a numeric value."""
    return re.match(r"^-?\d+(?:\.\d+)?$", value.strip()) is not None


# Convenience functions for common operations
def degrees_to_hours(degrees: float) -> float:
    """Convert degrees to hours (divide by 15)."""
    return degrees / 15.0


def hours_to_degrees(hours: float) -> float:
    """Convert hours to degrees (multiply by 15)."""
    return hours * 15.0


def distance_between_coordinates(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate great circle distance between two points using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates (decimal degrees)
        lat2, lon2: Second point coordinates (decimal degrees)
        
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    earth_radius = 6371.0
    
    return earth_radius * c