"""
Enhanced Ephemeris Calculations - Swiss Ephemeris Integration

This module provides advanced calculations for:
- South Node calculations (mean and true)
- Retrograde motion detection
- Extended lunar node functionality
- All planets and features output

Based on Swiss Ephemeris documentation and retrograde detection patterns.
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass

import swisseph as swe

from ..const import SwePlanets, SweFlags, DEFAULT_FLAGS, normalize_longitude
from ..classes.serialize import PlanetPosition
from .ephemeris import get_planet, julian_day_from_datetime


@dataclass
class EnhancedPlanetPosition:
    """Extended planet position with retrograde detection."""
    planet_id: int
    name: str
    longitude: float
    latitude: float
    distance: float
    longitude_speed: float
    latitude_speed: float = 0.0
    distance_speed: float = 0.0
    calculation_time: Optional[datetime] = None
    flags: int = 0
    
    @property
    def is_retrograde(self) -> bool:
        """Detect retrograde motion based on longitude speed."""
        return self.longitude_speed < 0.0
    
    @property
    def motion_type(self) -> str:
        """Return motion type as string."""
        if self.longitude_speed < 0.0:
            return "retrograde"
        elif self.longitude_speed > 0.0:
            return "direct"
        else:
            return "stationary"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with retrograde information."""
        return {
            'planet_id': self.planet_id,
            'name': self.name,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'distance': self.distance,
            'longitude_speed': self.longitude_speed,
            'latitude_speed': self.latitude_speed,
            'distance_speed': self.distance_speed,
            'is_retrograde': self.is_retrograde,
            'motion_type': self.motion_type,
            'calculation_time': self.calculation_time.isoformat() if self.calculation_time else None,
            'flags': self.flags
        }


@dataclass
class LunarNodeData:
    """Complete lunar node information (mean and true)."""
    mean_north: EnhancedPlanetPosition
    true_north: EnhancedPlanetPosition
    mean_south: EnhancedPlanetPosition
    true_south: EnhancedPlanetPosition
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all node data to dictionary."""
        return {
            'mean_north_node': self.mean_north.to_dict(),
            'true_north_node': self.true_north.to_dict(),
            'mean_south_node': self.mean_south.to_dict(),
            'true_south_node': self.true_south.to_dict()
        }


def calculate_south_node_position(
    north_node_position: PlanetPosition,
    calculation_type: str = "mean"
) -> Dict[str, Union[float, str]]:
    """
    Calculate South Node position from North Node.
    
    The South Node is always 180° opposite the North Node.
    Its latitude is the negative of the North Node's latitude.
    Speed values maintain the same magnitude but opposite sign for latitude.
    
    Args:
        north_node_position: North Node position data
        calculation_type: "mean" or "true" for naming
    
    Returns:
        South Node position dictionary
    """
    # South Node longitude is North Node + 180°
    south_longitude = normalize_longitude(north_node_position.longitude + 180.0)
    
    # South Node latitude is opposite of North Node
    south_latitude = -north_node_position.latitude
    
    # Speed calculations
    # Longitude speed maintains same value (nodes move together)
    # Latitude speed is negated
    south_longitude_speed = north_node_position.longitude_speed
    south_latitude_speed = -north_node_position.latitude_speed
    
    return {
        'longitude': south_longitude,
        'latitude': south_latitude,
        'distance': north_node_position.distance,  # Same distance as North Node
        'longitude_speed': south_longitude_speed,
        'latitude_speed': south_latitude_speed,
        'distance_speed': north_node_position.distance_speed,
        'name': f'South Node ({calculation_type.title()})',
        'is_retrograde': south_longitude_speed < 0.0,
        'motion_type': 'retrograde' if south_longitude_speed < 0.0 else 'direct',
        'calculation_time': north_node_position.calculation_time,
        'flags': north_node_position.flags
    }


def get_enhanced_planet_position(
    planet_id: int,
    julian_day: float,
    planet_name: str = None,
    flags: Optional[int] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    altitude: float = 0.0
) -> EnhancedPlanetPosition:
    """
    Get planet position with retrograde detection.
    
    Args:
        planet_id: Swiss Ephemeris planet constant
        julian_day: Julian Day Number
        planet_name: Optional planet name
        flags: Swiss Ephemeris calculation flags
        latitude: Observer latitude for topocentric
        longitude: Observer longitude for topocentric
        altitude: Observer altitude
    
    Returns:
        EnhancedPlanetPosition with retrograde information
    """
    # Get basic position
    position = get_planet(planet_id, julian_day, flags, latitude, longitude, altitude)
    
    # Determine planet name if not provided
    if planet_name is None:
        planet_names = {
            SwePlanets.SUN: 'Sun',
            SwePlanets.MOON: 'Moon',
            SwePlanets.MERCURY: 'Mercury',
            SwePlanets.VENUS: 'Venus',
            SwePlanets.MARS: 'Mars',
            SwePlanets.JUPITER: 'Jupiter',
            SwePlanets.SATURN: 'Saturn',
            SwePlanets.URANUS: 'Uranus',
            SwePlanets.NEPTUNE: 'Neptune',
            SwePlanets.PLUTO: 'Pluto',
            SwePlanets.MEAN_NODE: 'North Node (Mean)',
            SwePlanets.TRUE_NODE: 'North Node (True)',
            SwePlanets.CHIRON: 'Chiron'
        }
        planet_name = planet_names.get(planet_id, f'Planet {planet_id}')
    
    return EnhancedPlanetPosition(
        planet_id=planet_id,
        name=planet_name,
        longitude=position.longitude,
        latitude=position.latitude,
        distance=position.distance,
        longitude_speed=position.longitude_speed,
        latitude_speed=position.latitude_speed,
        distance_speed=position.distance_speed,
        calculation_time=position.calculation_time,
        flags=position.flags
    )


def calculate_complete_lunar_nodes(
    julian_day: float,
    flags: Optional[int] = None
) -> LunarNodeData:
    """
    Calculate complete lunar node data (mean and true, north and south).
    
    Args:
        julian_day: Julian Day Number
        flags: Swiss Ephemeris calculation flags
    
    Returns:
        LunarNodeData with all four node positions
    """
    # Calculate Mean North Node
    mean_north = get_enhanced_planet_position(
        SwePlanets.MEAN_NODE, julian_day, "North Node (Mean)", flags
    )
    
    # Calculate True North Node
    true_north = get_enhanced_planet_position(
        SwePlanets.TRUE_NODE, julian_day, "North Node (True)", flags
    )
    
    # Calculate Mean South Node from Mean North
    mean_south_data = calculate_south_node_position(
        PlanetPosition(
            planet_id=SwePlanets.MEAN_NODE,
            longitude=mean_north.longitude,
            latitude=mean_north.latitude,
            distance=mean_north.distance,
            longitude_speed=mean_north.longitude_speed,
            latitude_speed=mean_north.latitude_speed,
            distance_speed=mean_north.distance_speed,
            calculation_time=mean_north.calculation_time,
            flags=mean_north.flags
        ),
        "mean"
    )
    
    mean_south = EnhancedPlanetPosition(
        planet_id=SwePlanets.MEAN_NODE + 1000,  # Custom ID for South Node
        name=mean_south_data['name'],
        longitude=mean_south_data['longitude'],
        latitude=mean_south_data['latitude'],
        distance=mean_south_data['distance'],
        longitude_speed=mean_south_data['longitude_speed'],
        latitude_speed=mean_south_data['latitude_speed'],
        distance_speed=mean_south_data['distance_speed'],
        calculation_time=mean_north.calculation_time,
        flags=mean_north.flags
    )
    
    # Calculate True South Node from True North
    true_south_data = calculate_south_node_position(
        PlanetPosition(
            planet_id=SwePlanets.TRUE_NODE,
            longitude=true_north.longitude,
            latitude=true_north.latitude,
            distance=true_north.distance,
            longitude_speed=true_north.longitude_speed,
            latitude_speed=true_north.latitude_speed,
            distance_speed=true_north.distance_speed,
            calculation_time=true_north.calculation_time,
            flags=true_north.flags
        ),
        "true"
    )
    
    true_south = EnhancedPlanetPosition(
        planet_id=SwePlanets.TRUE_NODE + 1000,  # Custom ID for True South Node
        name=true_south_data['name'],
        longitude=true_south_data['longitude'],
        latitude=true_south_data['latitude'],
        distance=true_south_data['distance'],
        longitude_speed=true_south_data['longitude_speed'],
        latitude_speed=true_south_data['latitude_speed'],
        distance_speed=true_south_data['distance_speed'],
        calculation_time=true_north.calculation_time,
        flags=true_north.flags
    )
    
    return LunarNodeData(
        mean_north=mean_north,
        true_north=true_north,
        mean_south=mean_south,
        true_south=true_south
    )


def get_all_planets_with_retrograde(
    julian_day: float,
    include_asteroids: bool = True,
    include_nodes: bool = True,
    include_lilith: bool = True,
    flags: Optional[int] = None
) -> Dict[str, EnhancedPlanetPosition]:
    """
    Calculate positions for all planets and features with retrograde detection.
    
    This implements the "all planets and features output" as referenced in the
    technical specification document.
    
    Args:
        julian_day: Julian Day Number
        include_asteroids: Include major asteroids
        include_nodes: Include lunar nodes
        include_lilith: Include Lilith points
        flags: Swiss Ephemeris calculation flags
    
    Returns:
        Dictionary of all calculated positions with retrograde information
    """
    results = {}
    
    # Traditional Planets (Luminaries + 7 planets)
    traditional_planets = [
        (SwePlanets.SUN, 'Sun'),
        (SwePlanets.MOON, 'Moon'),
        (SwePlanets.MERCURY, 'Mercury'),
        (SwePlanets.VENUS, 'Venus'),
        (SwePlanets.MARS, 'Mars'),
        (SwePlanets.JUPITER, 'Jupiter'),
        (SwePlanets.SATURN, 'Saturn'),
        (SwePlanets.URANUS, 'Uranus'),
        (SwePlanets.NEPTUNE, 'Neptune'),
        (SwePlanets.PLUTO, 'Pluto')
    ]
    
    for planet_id, name in traditional_planets:
        try:
            results[name.lower()] = get_enhanced_planet_position(
                planet_id, julian_day, name, flags
            )
        except Exception as e:
            print(f"Warning: Failed to calculate {name}: {e}")
    
    # Major Asteroids
    if include_asteroids:
        asteroids = [
            (SwePlanets.CHIRON, 'Chiron'),
            (swe.CERES, 'Ceres'),
            (swe.PALLAS, 'Pallas'),
            (swe.JUNO, 'Juno'),
            (swe.VESTA, 'Vesta')
        ]
        
        for asteroid_id, name in asteroids:
            try:
                results[name.lower()] = get_enhanced_planet_position(
                    asteroid_id, julian_day, name, flags
                )
            except Exception as e:
                print(f"Warning: Failed to calculate {name}: {e}")
    
    # Lunar Nodes
    if include_nodes:
        try:
            node_data = calculate_complete_lunar_nodes(julian_day, flags)
            results['north_node_mean'] = node_data.mean_north
            results['north_node_true'] = node_data.true_north
            results['south_node_mean'] = node_data.mean_south
            results['south_node_true'] = node_data.true_south
        except Exception as e:
            print(f"Warning: Failed to calculate lunar nodes: {e}")
    
    # Lilith Points
    if include_lilith:
        lilith_points = [
            (SwePlanets.MEAN_APOG, 'Lilith (Mean)'),
            (SwePlanets.OSCULATING_APOG, 'Lilith (True)')
        ]
        
        for lilith_id, name in lilith_points:
            try:
                results[name.lower().replace(' ', '_').replace('(', '').replace(')', '')] = \
                    get_enhanced_planet_position(lilith_id, julian_day, name, flags)
            except Exception as e:
                print(f"Warning: Failed to calculate {name}: {e}")
    
    return results


def analyze_retrograde_patterns(
    positions: Dict[str, EnhancedPlanetPosition],
    julian_day: float
) -> Dict[str, Any]:
    """
    Analyze retrograde patterns in the calculated positions.
    
    Args:
        positions: Dictionary of planet positions
        julian_day: Julian Day Number for context
    
    Returns:
        Analysis results including retrograde statistics
    """
    retrograde_bodies = []
    direct_bodies = []
    stationary_bodies = []
    
    for name, position in positions.items():
        if position.is_retrograde:
            retrograde_bodies.append({
                'name': name,
                'longitude_speed': position.longitude_speed,
                'longitude': position.longitude
            })
        elif position.longitude_speed == 0.0:
            stationary_bodies.append({
                'name': name,
                'longitude': position.longitude
            })
        else:
            direct_bodies.append({
                'name': name,
                'longitude_speed': position.longitude_speed,
                'longitude': position.longitude
            })
    
    return {
        'calculation_date': datetime.fromtimestamp(
            (julian_day - 2440587.5) * 86400, tz=timezone.utc
        ).isoformat(),
        'julian_day': julian_day,
        'total_bodies': len(positions),
        'retrograde_count': len(retrograde_bodies),
        'direct_count': len(direct_bodies),
        'stationary_count': len(stationary_bodies),
        'retrograde_bodies': retrograde_bodies,
        'direct_bodies': direct_bodies,
        'stationary_bodies': stationary_bodies,
        'retrograde_percentage': len(retrograde_bodies) / len(positions) * 100 if positions else 0
    }


def get_comprehensive_ephemeris_output(
    datetime_utc: datetime,
    include_analysis: bool = True,
    include_asteroids: bool = True,
    include_nodes: bool = True,
    include_lilith: bool = True,
    flags: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive ephemeris output with all planets and features.
    
    This is the main function that implements the complete "all planets and 
    features output from ephemeris" as described in the technical documentation.
    
    Args:
        datetime_utc: UTC datetime for calculation
        include_analysis: Include retrograde analysis
        include_asteroids: Include major asteroids
        include_nodes: Include lunar nodes (mean and true, north and south)
        include_lilith: Include Lilith points
        flags: Swiss Ephemeris calculation flags
    
    Returns:
        Comprehensive ephemeris data with retrograde information
    """
    julian_day = julian_day_from_datetime(datetime_utc)
    
    # Get all planet positions
    positions = get_all_planets_with_retrograde(
        julian_day, include_asteroids, include_nodes, include_lilith, flags
    )
    
    # Convert positions to dictionary format
    positions_dict = {name: pos.to_dict() for name, pos in positions.items()}
    
    result = {
        'calculation_info': {
            'datetime_utc': datetime_utc.isoformat(),
            'julian_day': julian_day,
            'swiss_ephemeris_version': swe.version,
            'flags_used': flags or DEFAULT_FLAGS,
            'coordinate_system': 'geocentric_tropical',
            'precision': 'arc_second_level'
        },
        'positions': positions_dict
    }
    
    # Add retrograde analysis if requested
    if include_analysis:
        result['retrograde_analysis'] = analyze_retrograde_patterns(positions, julian_day)
    
    return result


# Utility functions for specific use cases

def is_planet_retrograde(planet_id: int, julian_day: float) -> bool:
    """Quick check if a specific planet is retrograde."""
    try:
        position = get_enhanced_planet_position(planet_id, julian_day)
        return position.is_retrograde
    except Exception:
        return False


def get_retrograde_planets_only(julian_day: float) -> List[EnhancedPlanetPosition]:
    """Get only the planets that are currently retrograde."""
    all_positions = get_all_planets_with_retrograde(julian_day)
    return [pos for pos in all_positions.values() if pos.is_retrograde]


def calculate_node_axis_info(julian_day: float) -> Dict[str, Any]:
    """Calculate detailed information about the lunar node axis."""
    node_data = calculate_complete_lunar_nodes(julian_day)
    
    # Calculate the angle between mean and true nodes
    mean_true_difference = abs(node_data.mean_north.longitude - node_data.true_north.longitude)
    if mean_true_difference > 180:
        mean_true_difference = 360 - mean_true_difference
    
    return {
        'mean_north_longitude': node_data.mean_north.longitude,
        'true_north_longitude': node_data.true_north.longitude,
        'mean_south_longitude': node_data.mean_south.longitude,
        'true_south_longitude': node_data.true_south.longitude,
        'mean_true_difference_degrees': mean_true_difference,
        'node_speed_degrees_per_day': abs(node_data.mean_north.longitude_speed),
        'nodes_retrograde': node_data.mean_north.is_retrograde,
        'complete_node_data': node_data.to_dict()
    }
