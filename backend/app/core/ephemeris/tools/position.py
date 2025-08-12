"""
Meridian Ephemeris Engine - Position Analysis Utilities

Provides comprehensive position analysis functions for celestial objects,
including zodiac signs, decans, elements, modalities, and house positions.
Maintains full compatibility with Immanuel reference while adding enhanced features.

Features:
- Zodiac sign analysis (sign, decan, element, modality)
- House position calculations with caching
- Opposite sign/house calculations
- Aspect and angular relationships
- Position-based astrological classifications
"""

import json
from typing import Union, Dict, List, Optional, Tuple
import swisseph as swe

from ..const import SIGN_NAMES, SIGN_SYMBOLS, get_sign_from_longitude
from ..classes.cache import cached


# Type aliases
PositionInput = Union[Dict, float]
HouseData = Dict[str, Union[int, float]]


class Element:
    """Elemental classifications."""
    FIRE = 1
    EARTH = 2  
    AIR = 3
    WATER = 4


class Modality:
    """Modal classifications."""
    CARDINAL = 1
    FIXED = 2
    MUTABLE = 3


class Decan:
    """Decan classifications within signs."""
    FIRST = 1
    SECOND = 2
    THIRD = 3


# Element mappings
ELEMENT_NAMES = {
    Element.FIRE: "Fire",
    Element.EARTH: "Earth", 
    Element.AIR: "Air",
    Element.WATER: "Water"
}

ELEMENT_SIGNS = {
    Element.FIRE: [1, 5, 9],      # Aries, Leo, Sagittarius
    Element.EARTH: [2, 6, 10],    # Taurus, Virgo, Capricorn
    Element.AIR: [3, 7, 11],      # Gemini, Libra, Aquarius
    Element.WATER: [4, 8, 12]     # Cancer, Scorpio, Pisces
}

# Modality mappings
MODALITY_NAMES = {
    Modality.CARDINAL: "Cardinal",
    Modality.FIXED: "Fixed",
    Modality.MUTABLE: "Mutable"
}

MODALITY_SIGNS = {
    Modality.CARDINAL: [1, 4, 7, 10],  # Aries, Cancer, Libra, Capricorn
    Modality.FIXED: [2, 5, 8, 11],     # Taurus, Leo, Scorpio, Aquarius
    Modality.MUTABLE: [3, 6, 9, 12]    # Gemini, Virgo, Sagittarius, Pisces
}

# House position cache
_house_cache = {}


def get_longitude(position_input: PositionInput) -> float:
    """
    Extract longitude from various input formats.
    
    Args:
        position_input: Position as dict with 'lon' key or float longitude
        
    Returns:
        Longitude in degrees
    """
    if isinstance(position_input, dict):
        return position_input.get('lon', position_input.get('longitude', 0.0))
    return float(position_input)


def zodiac_sign(position_input: PositionInput) -> int:
    """
    Get zodiac sign number (1-12) for position.
    
    Args:
        position_input: Position as dict or longitude
        
    Returns:
        Sign number (1=Aries, 2=Taurus, ..., 12=Pisces)
        
    Example:
        >>> zodiac_sign(45.0)  # 45° longitude
        2  # Taurus
    """
    longitude = get_longitude(position_input)
    return get_sign_from_longitude(longitude)


def sign_longitude(position_input: PositionInput) -> float:
    """
    Get longitude within the sign (0-30 degrees).
    
    Args:
        position_input: Position as dict or longitude
        
    Returns:
        Longitude within sign (0.0-29.999...)
        
    Example:
        >>> sign_longitude(45.5)
        15.5  # 15.5° within Taurus
    """
    longitude = get_longitude(position_input)
    return longitude % 30.0


def opposite_sign(position_input: PositionInput) -> int:
    """
    Get opposite zodiac sign number.
    
    Args:
        position_input: Position as dict or longitude
        
    Returns:
        Opposite sign number
        
    Example:
        >>> opposite_sign(45.0)  # Taurus
        8  # Scorpio (opposite sign)
    """
    sign_num = zodiac_sign(position_input)
    return sign_num + 6 if sign_num <= 6 else sign_num - 6


def decan(position_input: PositionInput) -> int:
    """
    Get decan number (1-3) within the sign.
    
    Args:
        position_input: Position as dict or longitude
        
    Returns:
        Decan number (1=first 10°, 2=second 10°, 3=third 10°)
        
    Example:
        >>> decan(45.0)  # 15° Taurus  
        2  # Second decan
    """
    sign_lon = sign_longitude(position_input)
    return int(sign_lon // 10) + 1


def element(position_input: PositionInput) -> int:
    """
    Get element classification for position.
    
    Args:
        position_input: Position as dict or longitude
        
    Returns:
        Element number (1=Fire, 2=Earth, 3=Air, 4=Water)
    """
    sign_num = zodiac_sign(position_input)
    return ((sign_num - 1) % 4) + 1


def modality(position_input: PositionInput) -> int:
    """
    Get modality classification for position.
    
    Args:
        position_input: Position as dict or longitude
        
    Returns:
        Modality number (1=Cardinal, 2=Fixed, 3=Mutable)
    """
    sign_num = zodiac_sign(position_input)
    return ((sign_num - 1) % 3) + 1


@cached(ttl=300)  # Cache house calculations for 5 minutes
def house_position(position_input: PositionInput, houses: Dict) -> Optional[HouseData]:
    """
    Calculate which house a position falls into.
    
    Args:
        position_input: Position as dict or longitude
        houses: House system data from ephemeris calculation
        
    Returns:
        House data dict or None if not found
        
    Example:
        >>> house_position(120.0, house_data)
        {'number': 5, 'longitude': 118.5, 'size': 32.1, ...}
    """
    longitude = get_longitude(position_input)
    
    # Create cache key
    cache_key = json.dumps([longitude, sorted(houses.items()) if isinstance(houses, dict) else houses])
    
    if cache_key in _house_cache:
        return _house_cache[cache_key]
    
    # Find the house containing this longitude
    for house_id, house_data in houses.items():
        if not isinstance(house_data, dict):
            continue
        
        # Validate house data has required fields
        if 'number' not in house_data:
            continue
            
        house_lon = house_data.get('lon', house_data.get('longitude', 0))
        house_size = house_data.get('size', 30.0)  # Default 30° if size not specified
        
        # Calculate angular difference using Swiss Ephemeris
        lon_diff = swe.difdeg2n(longitude, house_lon)
        next_cusp_diff = swe.difdeg2n(house_lon + house_size, house_lon)
        
        # Check if position falls within this house
        if 0 <= lon_diff < next_cusp_diff:
            _house_cache[cache_key] = house_data
            return house_data
    
    return None


def opposite_house_position(position_input: PositionInput, houses: Dict) -> Optional[HouseData]:
    """
    Get opposite house position.
    
    Args:
        position_input: Position as dict or longitude
        houses: House system data
        
    Returns:
        Opposite house data or None
    """
    current_house = house_position(position_input, houses)
    if not current_house:
        return None
        
    house_number = current_house.get('number')
    if house_number is None:
        return None
        
    # Calculate opposite house number
    opposite_number = house_number + 6 if house_number <= 6 else house_number - 6
    
    # Find opposite house in houses dict
    for house_data in houses.values():
        if isinstance(house_data, dict) and house_data.get('number') == opposite_number:
            return house_data
            
    return None


def angular_separation(pos1: PositionInput, pos2: PositionInput) -> float:
    """
    Calculate angular separation between two positions.
    
    Args:
        pos1: First position
        pos2: Second position
        
    Returns:
        Angular separation in degrees (0-180)
    """
    lon1 = get_longitude(pos1)
    lon2 = get_longitude(pos2)
    
    # Use Swiss Ephemeris for precise angular difference
    return abs(swe.difdeg2n(lon1, lon2))


def is_in_same_sign(pos1: PositionInput, pos2: PositionInput) -> bool:
    """
    Check if two positions are in the same zodiac sign.
    
    Args:
        pos1: First position
        pos2: Second position
        
    Returns:
        True if in same sign
    """
    return zodiac_sign(pos1) == zodiac_sign(pos2)


def is_in_same_element(pos1: PositionInput, pos2: PositionInput) -> bool:
    """
    Check if two positions share the same element.
    
    Args:
        pos1: First position
        pos2: Second position
        
    Returns:
        True if same element
    """
    return element(pos1) == element(pos2)


def is_in_same_modality(pos1: PositionInput, pos2: PositionInput) -> bool:
    """
    Check if two positions share the same modality.
    
    Args:
        pos1: First position  
        pos2: Second position
        
    Returns:
        True if same modality
    """
    return modality(pos1) == modality(pos2)


def get_position_summary(position_input: PositionInput, houses: Optional[Dict] = None) -> Dict:
    """
    Get comprehensive position analysis.
    
    Args:
        position_input: Position to analyze
        houses: Optional house system data
        
    Returns:
        Dictionary with complete position analysis
        
    Example:
        >>> get_position_summary(125.5)
        {
            'longitude': 125.5,
            'sign': {'number': 5, 'name': 'Leo', 'symbol': '♌'},
            'sign_longitude': 5.5,
            'decan': 1,
            'element': {'number': 1, 'name': 'Fire'},
            'modality': {'number': 2, 'name': 'Fixed'},
            'house': {...} if houses provided
        }
    """
    longitude = get_longitude(position_input)
    sign_num = zodiac_sign(longitude)
    element_num = element(longitude)
    modality_num = modality(longitude)
    
    summary = {
        'longitude': longitude,
        'sign': {
            'number': sign_num,
            'name': SIGN_NAMES.get(sign_num, f"Sign {sign_num}"),
            'symbol': SIGN_SYMBOLS.get(sign_num, "?")
        },
        'sign_longitude': sign_longitude(longitude),
        'decan': decan(longitude),
        'element': {
            'number': element_num,
            'name': ELEMENT_NAMES.get(element_num, f"Element {element_num}")
        },
        'modality': {
            'number': modality_num, 
            'name': MODALITY_NAMES.get(modality_num, f"Modality {modality_num}")
        }
    }
    
    # Add house information if available
    if houses:
        house_data = house_position(longitude, houses)
        if house_data:
            summary['house'] = house_data
    
    return summary


def get_critical_degrees() -> Dict[int, List[float]]:
    """
    Get critical degrees for each zodiac sign.
    
    Returns:
        Dictionary mapping sign numbers to lists of critical degrees
    """
    # Traditional critical degrees
    return {
        1: [0, 13, 26],    # Aries
        2: [9, 21],        # Taurus  
        3: [4, 17],        # Gemini
        4: [0, 13, 26],    # Cancer
        5: [9, 21],        # Leo
        6: [4, 17],        # Virgo
        7: [0, 13, 26],    # Libra
        8: [9, 21],        # Scorpio
        9: [4, 17],        # Sagittarius
        10: [0, 13, 26],   # Capricorn
        11: [9, 21],       # Aquarius
        12: [4, 17]        # Pisces
    }


def is_at_critical_degree(position_input: PositionInput, tolerance: float = 1.0) -> bool:
    """
    Check if position is at a critical degree.
    
    Args:
        position_input: Position to check
        tolerance: Tolerance in degrees for "at" critical degree
        
    Returns:
        True if at critical degree within tolerance
    """
    longitude = get_longitude(position_input)
    sign_num = zodiac_sign(longitude)
    sign_lon = sign_longitude(longitude)
    
    critical_degrees = get_critical_degrees()
    sign_criticals = critical_degrees.get(sign_num, [])
    
    for critical in sign_criticals:
        if abs(sign_lon - critical) <= tolerance:
            return True
            
    return False


def is_at_sign_boundary(position_input: PositionInput, tolerance: float = 1.0) -> bool:
    """
    Check if position is near a sign boundary.
    
    Args:
        position_input: Position to check
        tolerance: Tolerance in degrees
        
    Returns:
        True if near sign boundary
    """
    sign_lon = sign_longitude(position_input)
    return sign_lon <= tolerance or sign_lon >= (30.0 - tolerance)


def get_closest_aspect_angle(pos1: PositionInput, pos2: PositionInput) -> Dict:
    """
    Find closest major aspect between two positions.
    
    Args:
        pos1: First position
        pos2: Second position
        
    Returns:
        Dictionary with aspect information
    """
    separation = angular_separation(pos1, pos2)
    
    # Major aspect angles
    aspects = {
        0: "Conjunction",
        60: "Sextile", 
        90: "Square",
        120: "Trine",
        180: "Opposition"
    }
    
    closest_angle = None
    closest_name = None
    minimum_orb = 180.0
    
    for angle, name in aspects.items():
        orb = min(abs(separation - angle), abs(separation - (360 - angle)))
        if orb < minimum_orb:
            minimum_orb = orb
            closest_angle = angle
            closest_name = name
    
    return {
        'aspect': closest_name,
        'angle': closest_angle,
        'orb': minimum_orb,
        'separation': separation,
        'applying': separation < closest_angle if closest_angle else None
    }


def clear_house_cache():
    """Clear the house position cache."""
    global _house_cache
    _house_cache.clear()


# Convenience functions
def sign_name(position_input: PositionInput) -> str:
    """Get sign name for position."""
    sign_num = zodiac_sign(position_input)
    return SIGN_NAMES.get(sign_num, f"Sign {sign_num}")


def sign_symbol(position_input: PositionInput) -> str:
    """Get sign symbol for position."""
    sign_num = zodiac_sign(position_input)
    return SIGN_SYMBOLS.get(sign_num, "?")


def element_name(position_input: PositionInput) -> str:
    """Get element name for position."""
    element_num = element(position_input)
    return ELEMENT_NAMES.get(element_num, f"Element {element_num}")


def modality_name(position_input: PositionInput) -> str:
    """Get modality name for position."""
    modality_num = modality(position_input)
    return MODALITY_NAMES.get(modality_num, f"Modality {modality_num}")


def format_position(position_input: PositionInput, include_seconds: bool = True) -> str:
    """
    Format position as sign and degree string.
    
    Args:
        position_input: Position to format
        include_seconds: Whether to include seconds in output
        
    Returns:
        Formatted position string (e.g., "15°Leo32'45"")
    """
    longitude = get_longitude(position_input)
    sign_num = zodiac_sign(longitude)
    sign_lon = sign_longitude(longitude)
    
    degrees = int(sign_lon)
    minutes = int((sign_lon - degrees) * 60)
    seconds = ((sign_lon - degrees) * 60 - minutes) * 60
    
    sign_name_str = SIGN_NAMES.get(sign_num, f"Sign{sign_num}")
    
    if include_seconds:
        return f"{degrees:02d}°{sign_name_str}{minutes:02d}'{seconds:04.1f}\""
    else:
        return f"{degrees:02d}°{sign_name_str}{minutes:02d}'"