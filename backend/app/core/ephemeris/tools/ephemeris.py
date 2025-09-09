"""
Meridian Ephemeris Engine - Core Ephemeris Tools

Provides the core Swiss Ephemeris calculation functions:
- get_planet: Planet positions and speeds
- get_houses: House system calculations  
- get_angles: Chart angles (ASC, MC, etc.)
- get_point: Calculated points (nodes, asteroids, etc.)
- get_fixed_star: Fixed star positions

All functions use Swiss Ephemeris as the authoritative backend.
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass

import swisseph as swe

from ..const import (
    SwePlanets, SweFlags, HouseSystems, DEFAULT_FLAGS,
    PLANET_NAMES, get_planet_name, normalize_longitude
)
from ..settings import settings
from ..classes.cache import cached
from ..models.planet_data import PlanetData


# Legacy compatibility classes for existing code
@dataclass(frozen=True)
class PlanetPosition:
    """Legacy compatibility class - use PlanetData instead."""
    longitude: float
    latitude: float
    distance: float
    longitude_speed: float
    latitude_speed: float
    distance_speed: float
    name: str
    object_id: int
    flags: int = 0

@dataclass(frozen=True)
class ChartAngles:
    """Chart angles (ASC, MC, etc.)."""
    ascendant: float
    midheaven: float
    descendant: float
    imum_coeli: float
    calculation_time: datetime


@dataclass(frozen=True)
class HouseSystem:
    """House system data."""
    cusps: List[float]
    angles: ChartAngles
    system: str


@dataclass(frozen=True)  
class ChartData:
    """Legacy compatibility class for chart data."""
    planets: Dict[str, PlanetPosition]
    houses: HouseSystem
    angles: ChartAngles


def julian_day_from_datetime(dt: datetime) -> float:
    """Convert datetime to Julian Day Number."""
    # Convert to UTC if timezone-aware
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    
    # SwissEph expects separate date/time components
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour + dt.minute/60.0 + dt.second/3600.0 + dt.microsecond/3600000000.0
    
    return swe.julday(year, month, day, hour)


def datetime_from_julian_day(jd: float) -> datetime:
    """Convert Julian Day Number to datetime."""
    year, month, day, hour = swe.revjul(jd)
    
    # Convert fractional hour to hour, minute, second, microsecond
    hour_int = int(hour)
    minute_float = (hour - hour_int) * 60
    minute_int = int(minute_float)
    second_float = (minute_float - minute_int) * 60
    second_int = int(second_float)
    microsecond_int = int((second_float - second_int) * 1000000)
    
    return datetime(
        year, month, day, hour_int, minute_int, second_int, microsecond_int,
        tzinfo=timezone.utc
    )


def get_planet(
    planet_id: int,
    julian_day: float,
    flags: Optional[int] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    altitude: float = 0.0
) -> PlanetPosition:
    """
    Calculate planet position using Swiss Ephemeris.
    
    Args:
        planet_id: Swiss Ephemeris planet constant
        julian_day: Julian Day Number for calculation
        flags: Swiss Ephemeris calculation flags
        latitude: Observer latitude (for topocentric calculations)
        longitude: Observer longitude (for topocentric calculations)  
        altitude: Observer altitude in meters (default 0)
    
    Returns:
        PlanetPosition object with longitude, latitude, distance, and speeds
        
    Raises:
        RuntimeError: If Swiss Ephemeris calculation fails
    """
    if flags is None:
        flags = settings.swe_flags or DEFAULT_FLAGS
    
    # Set topocentric position if coordinates provided
    if latitude is not None and longitude is not None:
        swe.set_topo(longitude, latitude, altitude)
        flags |= SweFlags.TOPOCTR
    
    try:
        # Calculate planet position
        result, ret_flags = swe.calc_ut(julian_day, planet_id, flags)
        
        if len(result) < 6:
            raise RuntimeError(f"Swiss Ephemeris calculation failed for planet {planet_id}")
        
        # Create position object
        position = PlanetPosition(
            planet_id=planet_id,
            longitude=normalize_longitude(result[0]),
            latitude=result[1],
            distance=result[2],
            longitude_speed=result[3],
            latitude_speed=result[4],
            distance_speed=result[5],
            calculation_time=datetime_from_julian_day(julian_day),
            flags=ret_flags
        )
        
        # Apply Mean Lilith sign convention correction
        if planet_id == SwePlanets.MEAN_APOG and position.longitude_speed > 0:
            # Create corrected position with negative speed
            position = PlanetPosition(
                planet_id=planet_id,
                longitude=position.longitude,
                latitude=position.latitude,
                distance=position.distance,
                longitude_speed=-abs(position.longitude_speed),  # Force negative for retrograde
                latitude_speed=position.latitude_speed,
                distance_speed=position.distance_speed,
                calculation_time=position.calculation_time,
                flags=position.flags
            )
        
        return position
        
    except Exception as e:
        planet_name = get_planet_name(planet_id)
        raise RuntimeError(f"Failed to calculate {planet_name} position: {str(e)}") from e


@cached(ttl=3600)  # Cache for 1 hour
def get_houses(
    julian_day: float,
    latitude: float,
    longitude: float,
    house_system: str = 'P'
) -> HouseSystem:
    """
    Calculate house system using Swiss Ephemeris.
    
    Args:
        julian_day: Julian Day Number for calculation
        latitude: Observer latitude in degrees
        longitude: Observer longitude in degrees
        house_system: House system code (P=Placidus, K=Koch, etc.)
    
    Returns:
        HouseSystem object with house cusps and angles
        
    Raises:
        RuntimeError: If house calculation fails
    """
    try:
        # Validate house system
        if house_system not in ['P', 'K', 'O', 'R', 'C', 'E', 'W', 'B', 'M', 'U', 'G', 'H', 'T', 'D', 'V', 'X', 'N', 'I']:
            house_system = settings.get_house_system_code(house_system)
        
        # Calculate houses
        house_cusps, ascmc = swe.houses(julian_day, latitude, longitude, house_system.encode('utf-8'))

        # Swiss Ephemeris returns 12 cusps (1..12). Some consumers/tests expect 13 with index 0 unused.
        cusps_list = list(house_cusps)
        if len(cusps_list) == 12:
            cusps_list = [0.0] + cusps_list

        return HouseSystem(
            house_cusps=cusps_list,
            ascmc=list(ascmc),
            system_code=house_system,
            calculation_time=datetime_from_julian_day(julian_day),
            latitude=latitude,
            longitude=longitude
        )
        
    except Exception as e:
        raise RuntimeError(f"Failed to calculate houses: {str(e)}") from e


def get_angles(
    julian_day: float,
    latitude: float,
    longitude: float,
    house_system: str = 'P'
) -> Dict[str, float]:
    """
    Calculate chart angles (ASC, MC, DESC, IC) using house calculation.
    
    Args:
        julian_day: Julian Day Number for calculation
        latitude: Observer latitude in degrees
        longitude: Observer longitude in degrees
        house_system: House system code for calculation
    
    Returns:
        Dictionary with angle names and degrees
    """
    houses = get_houses(julian_day, latitude, longitude, house_system)
    
    return {
        'ASC': houses.ascendant,
        'MC': houses.midheaven,
        'DESC': houses.descendant,
        'IC': houses.imum_coeli,
        'ARMC': houses.ascmc[2] if len(houses.ascmc) > 2 else 0.0,
        'Vertex': houses.ascmc[3] if len(houses.ascmc) > 3 else 0.0,
    }


@cached(ttl=3600)
def get_point(
    point_type: str,
    julian_day: float,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    house_system: str = 'P'
) -> Dict[str, Union[float, str]]:
    """
    Calculate various astrological points.
    
    Args:
        point_type: Type of point ('north_node', 'south_node', 'lilith', 'vertex', etc.)
        julian_day: Julian Day Number
        latitude: Observer latitude (required for some points)
        longitude: Observer longitude (required for some points)
        house_system: House system for angle-based points
    
    Returns:
        Dictionary with point calculation results
        
    Raises:
        ValueError: If point type is unknown or required coordinates missing
    """
    point_type = point_type.lower()
    
    # Map point types to calculations
    if point_type in ['north_node', 'mean_node']:
        result = get_planet(SwePlanets.MEAN_NODE, julian_day)
        return {
            'longitude': result.longitude,
            'latitude': result.latitude,
            'speed': result.longitude_speed,
            'name': 'North Node (Mean)'
        }
    
    elif point_type in ['true_north_node', 'true_node']:
        result = get_planet(SwePlanets.TRUE_NODE, julian_day)
        return {
            'longitude': result.longitude,
            'latitude': result.latitude,
            'speed': result.longitude_speed,
            'name': 'North Node (True)'
        }
    
    elif point_type == 'south_node':
        result = get_planet(SwePlanets.MEAN_NODE, julian_day)
        return {
            'longitude': normalize_longitude(result.longitude + 180.0),
            'latitude': -result.latitude,
            'speed': result.longitude_speed,
            'name': 'South Node (Mean)',
            'is_retrograde': result.is_retrograde,
            'motion_type': result.motion_type
        }
    
    elif point_type in ['true_south_node', 'south_node_true']:
        result = get_planet(SwePlanets.TRUE_NODE, julian_day)
        return {
            'longitude': normalize_longitude(result.longitude + 180.0),
            'latitude': -result.latitude,
            'speed': result.longitude_speed,
            'name': 'South Node (True)',
            'is_retrograde': result.is_retrograde,
            'motion_type': result.motion_type
        }
    
    elif point_type in ['lilith', 'mean_lilith']:
        result = get_planet(SwePlanets.MEAN_APOG, julian_day)
        # Mean Lilith should be consistently retrograde (~-0.1119°/day)
        # Apply correct sign convention if needed
        corrected_speed = result.longitude_speed
        if corrected_speed > 0:
            corrected_speed = -abs(corrected_speed)  # Ensure negative (retrograde)
        
        return {
            'longitude': result.longitude,
            'latitude': result.latitude,
            'speed': corrected_speed,
            'name': 'Lilith (Mean Apogee)',
            'is_retrograde': corrected_speed < 0.0,
            'motion_type': 'retrograde' if corrected_speed < 0.0 else 'direct'
        }
    
    elif point_type in ['true_lilith', 'osculating_lilith']:
        result = get_planet(SwePlanets.OSCULATING_APOG, julian_day)
        return {
            'longitude': result.longitude,
            'latitude': result.latitude,
            'speed': result.longitude_speed,
            'name': 'Lilith (Osculating Apogee)',
            'is_retrograde': result.is_retrograde,
            'motion_type': result.motion_type
        }
    
    elif point_type == 'vertex':
        if latitude is None or longitude is None:
            raise ValueError("Latitude and longitude required for Vertex calculation")
        
        angles = get_angles(julian_day, latitude, longitude, house_system)
        return {
            'longitude': angles['Vertex'],
            'latitude': 0.0,
            'speed': 0.0,
            'name': 'Vertex'
        }
    
    elif point_type == 'part_of_fortune':
        if latitude is None or longitude is None:
            raise ValueError("Latitude and longitude required for Part of Fortune calculation")
        
        # Calculate Part of Fortune: ASC + Moon - Sun (day formula)
        sun = get_planet(SwePlanets.SUN, julian_day)
        moon = get_planet(SwePlanets.MOON, julian_day)
        angles = get_angles(julian_day, latitude, longitude, house_system)
        
        pof = normalize_longitude(angles['ASC'] + moon.longitude - sun.longitude)
        
        return {
            'longitude': pof,
            'latitude': 0.0,
            'speed': 0.0,
            'name': 'Part of Fortune'
        }
    
    else:
        raise ValueError(f"Unknown point type: {point_type}")


def get_fixed_star(
    star_name: str,
    julian_day: float
) -> Dict[str, Union[float, str]]:
    """
    Calculate fixed star position using Swiss Ephemeris.
    
    Args:
        star_name: Name of the fixed star
        julian_day: Julian Day Number for calculation
    
    Returns:
        Dictionary with star position data
        
    Raises:
        RuntimeError: If star calculation fails
    """
    try:
        # Swiss Ephemeris fixed star calculation
        result = swe.fixstar_ut(star_name, julian_day, DEFAULT_FLAGS)
        
        if len(result[0]) < 6:
            raise RuntimeError(f"Failed to calculate position for star: {star_name}")
        
        star_data = result[0]
        star_info = result[1] if len(result) > 1 else ""
        
        return {
            'longitude': normalize_longitude(star_data[0]),
            'latitude': star_data[1],
            'distance': star_data[2],
            'longitude_speed': star_data[3],
            'latitude_speed': star_data[4],
            'distance_speed': star_data[5],
            'name': star_name,
            'info': star_info
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to calculate fixed star {star_name}: {str(e)}") from e


def calculate_planetary_chart(
    julian_day: float,
    latitude: float,
    longitude: float,
    altitude: float = 0.0,
    planets: Optional[List[int]] = None,
    house_system: str = 'P',
    include_speeds: bool = True
) -> Dict[str, Union[Dict, HouseSystem]]:
    """
    Calculate complete planetary chart with houses.
    
    Args:
        julian_day: Julian Day Number for calculation
        latitude: Observer latitude in degrees
        longitude: Observer longitude in degrees
        altitude: Observer altitude in meters
        planets: List of planet IDs to calculate (default: all major planets)
        house_system: House system code
        include_speeds: Whether to include planetary speeds
    
    Returns:
        Dictionary containing planets and houses data
    """
    if planets is None:
        planets = settings.default_planets + settings.default_points
    
    # Calculate planet positions
    planet_positions = {}
    for planet_id in planets:
        try:
            position = get_planet(planet_id, julian_day, latitude=latitude, 
                               longitude=longitude, altitude=altitude)
            planet_positions[planet_id] = position
        except RuntimeError as e:
            # Log error but continue with other planets
            print(f"Warning: {str(e)}")
            continue
    
    # Calculate house system
    houses = get_houses(julian_day, latitude, longitude, house_system)
    
    # Calculate additional points
    angles = get_angles(julian_day, latitude, longitude, house_system)
    
    return {
        'planets': planet_positions,
        'houses': houses,
        'angles': angles,
        'julian_day': julian_day,
        'calculation_time': datetime_from_julian_day(julian_day),
        'observer': {
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude
        },
        'settings': {
            'house_system': house_system,
            'flags': settings.swe_flags
        }
    }


def validate_ephemeris_files() -> Dict[str, bool]:
    """
    Validate that required ephemeris files are available.
    
    Returns:
        Dictionary with file availability status
    """
    validation_results = {}
    
    # Test basic planet calculations for a known date
    test_jd = 2451545.0  # J2000.0
    
    # Test major planets
    test_planets = [
        SwePlanets.SUN, SwePlanets.MOON, SwePlanets.MERCURY,
        SwePlanets.VENUS, SwePlanets.MARS, SwePlanets.JUPITER,
        SwePlanets.SATURN, SwePlanets.URANUS, SwePlanets.NEPTUNE,
        SwePlanets.PLUTO
    ]
    
    for planet_id in test_planets:
        try:
            get_planet(planet_id, test_jd)
            validation_results[get_planet_name(planet_id)] = True
        except Exception:
            validation_results[get_planet_name(planet_id)] = False
    
    # Test house calculation
    try:
        get_houses(test_jd, 51.5074, -0.1278)  # London coordinates
        validation_results['Houses'] = True
    except Exception:
        validation_results['Houses'] = False
    
    # Test fixed stars (if available)
    try:
        get_fixed_star('Aldebaran', test_jd)
        validation_results['Fixed Stars'] = True
    except Exception:
        validation_results['Fixed Stars'] = False
    
    return validation_results


def analyze_retrograde_motion(
    positions: Dict[str, Union[PlanetPosition, Dict[str, Any]]],
    julian_day: Optional[float] = None
) -> Dict[str, Any]:
    """
    Analyze retrograde motion patterns in calculated positions.
    
    Args:
        positions: Dictionary of planet positions (PlanetPosition objects or dicts)
        julian_day: Optional Julian Day for context
    
    Returns:
        Dictionary with retrograde analysis results
    """
    retrograde_bodies = []
    direct_bodies = []
    stationary_bodies = []
    
    for name, position in positions.items():
        # Handle both PlanetPosition objects and dictionaries
        if isinstance(position, PlanetPosition):
            speed = position.longitude_speed
            is_retrograde = position.is_retrograde
            longitude = position.longitude
        elif isinstance(position, dict):
            speed = position.get('longitude_speed', 0.0)
            is_retrograde = position.get('is_retrograde', speed < 0.0)
            longitude = position.get('longitude', 0.0)
        else:
            continue  # Skip invalid entries
        
        body_data = {
            'name': name,
            'longitude_speed': speed,
            'longitude': longitude
        }
        
        if is_retrograde:
            retrograde_bodies.append(body_data)
        elif speed == 0.0:
            stationary_bodies.append(body_data)
        else:
            direct_bodies.append(body_data)
    
    total_bodies = len(retrograde_bodies) + len(direct_bodies) + len(stationary_bodies)
    
    analysis = {
        'total_bodies': total_bodies,
        'retrograde_count': len(retrograde_bodies),
        'direct_count': len(direct_bodies),
        'stationary_count': len(stationary_bodies),
        'retrograde_percentage': (len(retrograde_bodies) / total_bodies * 100) if total_bodies > 0 else 0,
        'retrograde_bodies': retrograde_bodies,
        'direct_bodies': direct_bodies,
        'stationary_bodies': stationary_bodies
    }
    
    if julian_day:
        analysis['julian_day'] = julian_day
        analysis['calculation_date'] = datetime_from_julian_day(julian_day).isoformat()
    
    return analysis