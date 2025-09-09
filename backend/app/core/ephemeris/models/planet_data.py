"""
Unified Planet Data Model

Single dataclass representing all celestial body data throughout the pipeline.
Replaces: PlanetPosition, EnhancedPlanetPosition, PlanetResponse, ACGBodyData, PlanetaryPosition

This consolidates 5 separate planet data classes and 12+ transformation functions
into a single, comprehensive model with computed properties and adapters.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, Union
import math


@dataclass
class PlanetData:
    """
    Unified planet/celestial body data model.
    
    Replaces multiple classes:
    - PlanetPosition (serialize.py:136)
    - EnhancedPlanetPosition (enhanced_calculations.py:26)  
    - PlanetResponse (schemas.py:198)
    - ACGBodyData (acg_types.py:254)
    - PlanetaryPosition (paran_models.py:395)
    """
    # Core Swiss Ephemeris data
    object_id: int
    name: str
    longitude: float  # Degrees 0-360
    latitude: float   # Degrees -90 to +90
    distance: float   # AU
    longitude_speed: float  # Degrees/day
    latitude_speed: float   # Degrees/day  
    distance_speed: float   # AU/day
    calculation_time: datetime
    flags: int
    
    # Optional house position (set after house calculation)
    house_number: Optional[int] = None
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Apply Mean Lilith retrograde fix from original issue
        if self.object_id == 12 and self.longitude_speed > 0:  # SwePlanets.MEAN_APOG = 12
            # Force negative speed for Mean Lilith (retrograde by convention)
            self.longitude_speed = -abs(self.longitude_speed)
    
    # Computed properties following serialize.py:169 pattern
    @property
    def is_retrograde(self) -> bool:
        """
        Whether planet is in retrograde motion (longitude_speed < 0).
        
        Based on Swiss Ephemeris longitude_speed calculation.
        Threshold from serialize.py:169 pattern.
        """
        return self.longitude_speed < 0.0
    
    @property 
    def motion_type(self) -> str:
        """
        Motion classification: direct, retrograde, stationary, or unknown.
        
        Stationary threshold: abs(longitude_speed) < 0.01 degrees/day
        Based on serialize.py patterns and astronomical standards.
        """
        if abs(self.longitude_speed) < 0.01:  # Stationary threshold from serialize.py
            return 'stationary'
        elif self.longitude_speed < 0.0:
            return 'retrograde'
        elif self.longitude_speed > 0.0:
            return 'direct'
        else:
            return 'unknown'
    
    # Astrological context properties
    @property
    def sign_number(self) -> int:
        """Zodiac sign number (0-11). Aries=0, Taurus=1, etc."""
        return int(self.longitude // 30) % 12
    
    @property
    def sign_name(self) -> str:
        """Zodiac sign name."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[self.sign_number]
    
    @property
    def sign_longitude(self) -> float:
        """Longitude within sign (0-29.999...)."""
        return self.longitude % 30
    
    @property
    def element(self) -> str:
        """Zodiac element for sign: Fire, Earth, Air, Water."""
        elements = ["Fire", "Earth", "Air", "Water"]
        return elements[self.sign_number % 4]
    
    @property
    def modality(self) -> str:
        """Zodiac modality for sign: Cardinal, Fixed, Mutable."""
        modalities = ["Cardinal", "Fixed", "Mutable"]
        return modalities[self.sign_number % 3]
    
    @property
    def normalized_longitude(self) -> float:
        """Longitude normalized to 0-360 range."""
        lon = self.longitude
        while lon < 0:
            lon += 360
        while lon >= 360:
            lon -= 360
        return lon
    
    def to_api_response(self) -> Dict[str, Any]:
        """
        Convert to API response format.
        
        This replaces multiple transformation functions and ensures
        consistent API output format across all endpoints.
        """
        return {
            'name': self.name,
            'longitude': round(self.normalized_longitude, 6),
            'latitude': round(self.latitude, 6),
            'distance': round(self.distance, 8),
            'longitude_speed': round(self.longitude_speed, 6),
            'is_retrograde': self.is_retrograde,
            'motion_type': self.motion_type,
            'sign_name': self.sign_name,
            'sign_longitude': round(self.sign_longitude, 6),
            'element': self.element,
            'modality': self.modality,
            'house_number': self.house_number
        }
    
    def to_acg_data(self) -> Dict[str, Any]:
        """
        Convert to ACG calculation format.
        
        Replaces ACGBodyData transformation logic.
        """
        return {
            'object_id': self.object_id,
            'name': self.name,
            'longitude': self.normalized_longitude,
            'latitude': self.latitude,
            'distance': self.distance,
            'longitude_speed': self.longitude_speed,
            'is_retrograde': self.is_retrograde
        }
    
    def to_aspect_calculation_data(self) -> Dict[str, Any]:
        """
        Convert to aspect calculation format.
        
        Standardizes planet data for aspect calculations.
        """
        return {
            'name': self.name,
            'longitude': self.normalized_longitude,
            'latitude': self.latitude,
            'is_retrograde': self.is_retrograde,
            'motion_type': self.motion_type
        }
    
    def get_degrees_minutes_seconds(self, coordinate: str = 'longitude') -> Dict[str, int]:
        """
        Convert longitude or latitude to degrees, minutes, seconds format.
        
        Args:
            coordinate: 'longitude' or 'latitude'
            
        Returns:
            Dict with degrees, minutes, seconds
        """
        if coordinate == 'longitude':
            decimal_degrees = self.sign_longitude  # Within sign
        else:
            decimal_degrees = abs(self.latitude)
        
        degrees = int(decimal_degrees)
        minutes_float = (decimal_degrees - degrees) * 60
        minutes = int(minutes_float)
        seconds = int((minutes_float - minutes) * 60)
        
        return {
            'degrees': degrees,
            'minutes': minutes,
            'seconds': seconds
        }
    
    def is_asteroid(self) -> bool:
        """Check if this object is an asteroid (object_id >= 10000)."""
        return self.object_id >= 10000
    
    def is_planet(self) -> bool:
        """Check if this object is a traditional planet (0 <= object_id <= 9)."""
        return 0 <= self.object_id <= 9
    
    def is_lunar_node(self) -> bool:
        """Check if this object is a lunar node (True/Mean Node)."""
        return self.object_id in [10, 11]  # TRUE_NODE, MEAN_NODE
    
    def is_lilith_point(self) -> bool:
        """Check if this object is a Lilith point (Mean/Osculating Apogee)."""
        return self.object_id in [12, 13]  # MEAN_APOG, OSCULATING_APOG
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name}: {self.longitude:.2f}° {self.sign_name} ({self.motion_type})"
    
    def __repr__(self) -> str:
        """Developer string representation."""
        return (f"PlanetData(name='{self.name}', longitude={self.longitude:.2f}, "
                f"latitude={self.latitude:.2f}, motion_type='{self.motion_type}')")


def create_planet_data_from_swiss_ephemeris(object_id: int, name: str, 
                                          position_data: list, calculation_time: datetime,
                                          flags: int) -> PlanetData:
    """
    Factory function to create PlanetData from Swiss Ephemeris calculation results.
    
    Args:
        object_id: Swiss Ephemeris object ID
        name: Object name
        position_data: Result from swe.calc_ut() - [lon, lat, dist, lon_speed, lat_speed, dist_speed]
        calculation_time: When calculation was performed
        flags: Swiss Ephemeris flags used
        
    Returns:
        PlanetData instance
        
    Raises:
        ValueError: If position_data is invalid
    """
    if len(position_data) < 6:
        raise ValueError(f"Invalid position data for {name}: {position_data}")
    
    return PlanetData(
        object_id=object_id,
        name=name,
        longitude=position_data[0],
        latitude=position_data[1],
        distance=position_data[2],
        longitude_speed=position_data[3],
        latitude_speed=position_data[4],
        distance_speed=position_data[5],
        calculation_time=calculation_time,
        flags=flags
    )