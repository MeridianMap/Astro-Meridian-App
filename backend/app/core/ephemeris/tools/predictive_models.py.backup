"""
Predictive Data Models - Eclipse & Transit Calculator

Comprehensive data models for eclipse and transit calculations with NASA-validated
accuracy requirements. Supports solar/lunar eclipses, planetary transits, and 
sign ingresses with professional astronomical metadata.

Follows CLAUDE.md performance standards and integrates with Swiss Ephemeris engine.
"""

import math
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..const import normalize_longitude, PLANET_NAMES


class EclipseType(Enum):
    """Eclipse type classifications."""
    SOLAR_TOTAL = "total_solar"
    SOLAR_PARTIAL = "partial_solar"
    SOLAR_ANNULAR = "annular_solar"
    SOLAR_HYBRID = "hybrid_solar"
    LUNAR_TOTAL = "total_lunar"
    LUNAR_PARTIAL = "partial_lunar"
    LUNAR_PENUMBRAL = "penumbral_lunar"


class LunarEclipseType(Enum):
    """Lunar eclipse specific type classifications."""
    TOTAL = "total"
    PARTIAL = "partial"
    PENUMBRAL = "penumbral"


class TransitType(Enum):
    """Transit calculation types."""
    LONGITUDE_DEGREE = "longitude_degree"
    SIGN_INGRESS = "sign_ingress"
    ASPECT_TRANSIT = "aspect_transit"
    RETURN_TRANSIT = "return_transit"


class RetrogradeStatus(Enum):
    """Planetary motion status."""
    DIRECT = "direct"
    RETROGRADE = "retrograde"
    STATIONARY_DIRECT = "stationary_direct"
    STATIONARY_RETROGRADE = "stationary_retrograde"


@dataclass
class GeographicLocation:
    """Geographic location for eclipse visibility calculations."""
    
    latitude: float   # Degrees (-90 to +90)
    longitude: float  # Degrees (-180 to +180)
    elevation: float = 0.0  # Meters above sea level
    name: Optional[str] = None
    timezone: Optional[str] = None
    
    def __post_init__(self):
        """Validate coordinates."""
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Latitude must be between -90 and +90, got {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Longitude must be between -180 and +180, got {self.longitude}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "elevation": self.elevation,
            "name": self.name,
            "timezone": self.timezone
        }


@dataclass
class EclipseVisibility:
    """Eclipse visibility data for specific location."""
    
    location_latitude: float
    location_longitude: float
    location_name: Optional[str] = None
    
    # Eclipse timing for location
    eclipse_begins: Optional[datetime] = None
    maximum_eclipse: Optional[datetime] = None
    eclipse_ends: Optional[datetime] = None
    
    # Visibility characteristics
    maximum_obscuration: float = 0.0  # Percentage (0-100)
    maximum_magnitude: float = 0.0    # Eclipse magnitude at location
    altitude_at_maximum: float = 0.0  # Sun altitude during maximum
    azimuth_at_maximum: float = 0.0   # Sun azimuth during maximum
    
    # Eclipse quality indicators
    is_visible: bool = False
    is_total_at_location: bool = False
    is_partial_at_location: bool = False
    eclipse_quality: str = "not_visible"  # "excellent", "good", "fair", "poor", "not_visible"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "location": {
                "latitude": self.location_latitude,
                "longitude": self.location_longitude,
                "name": self.location_name
            },
            "timing": {
                "begins": self.eclipse_begins.isoformat() if self.eclipse_begins else None,
                "maximum": self.maximum_eclipse.isoformat() if self.maximum_eclipse else None,
                "ends": self.eclipse_ends.isoformat() if self.eclipse_ends else None
            },
            "visibility": {
                "is_visible": self.is_visible,
                "maximum_obscuration_percent": self.maximum_obscuration,
                "maximum_magnitude": self.maximum_magnitude,
                "eclipse_quality": self.eclipse_quality,
                "is_total": self.is_total_at_location,
                "is_partial": self.is_partial_at_location
            },
            "sun_position": {
                "altitude_degrees": self.altitude_at_maximum,
                "azimuth_degrees": self.azimuth_at_maximum
            }
        }


@dataclass
class SolarEclipse:
    """Comprehensive solar eclipse data model."""
    
    # Basic eclipse identification
    eclipse_type: EclipseType
    maximum_eclipse_time: datetime
    eclipse_id: str = field(default="")  # Unique identifier
    
    # Eclipse characteristics
    eclipse_magnitude: float = 0.0        # Greatest eclipse magnitude
    eclipse_obscuration: float = 0.0      # Maximum obscuration percentage
    gamma: float = 0.0                    # Eclipse parameter (-1.7 to +1.7)
    
    # Duration information
    duration_totality: Optional[float] = None      # Duration at greatest eclipse (seconds)
    duration_partial: Optional[float] = None       # Total partial duration (seconds)
    path_width: Optional[float] = None             # Width of totality path (km)
    
    # Astronomical data
    saros_series: Optional[int] = None             # Saros cycle number
    saros_member: Optional[int] = None             # Member number in saros
    lunation_number: Optional[int] = None          # Brown Lunation Number
    delta_t: float = 0.0                          # Delta T at eclipse time
    
    # Geographic data
    greatest_eclipse_lat: Optional[float] = None   # Latitude of greatest eclipse
    greatest_eclipse_lon: Optional[float] = None   # Longitude of greatest eclipse
    eclipse_path: Optional[List[Tuple[float, float]]] = None  # Path coordinates
    
    # Calculation metadata
    calculation_accuracy: float = 0.0             # Estimated accuracy in seconds
    swiss_ephemeris_version: str = ""
    calculation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_status: str = "unvalidated"        # "validated", "unvalidated", "flagged"
    
    def __post_init__(self):
        """Generate eclipse ID if not provided."""
        if not self.eclipse_id:
            date_str = self.maximum_eclipse_time.strftime("%Y%m%d")
            type_abbrev = self.eclipse_type.value[:4].upper()
            self.eclipse_id = f"SE{date_str}_{type_abbrev}"
    
    def get_eclipse_phase_names(self) -> List[str]:
        """Get list of eclipse phases for this type."""
        if self.eclipse_type == EclipseType.SOLAR_TOTAL:
            return ["first_contact", "second_contact", "maximum", "third_contact", "fourth_contact"]
        elif self.eclipse_type == EclipseType.SOLAR_ANNULAR:
            return ["first_contact", "second_contact", "maximum", "third_contact", "fourth_contact"]
        else:  # Partial
            return ["first_contact", "maximum", "fourth_contact"]
    
    def is_central_eclipse(self) -> bool:
        """Check if this is a central eclipse (total, annular, or hybrid)."""
        return self.eclipse_type in [
            EclipseType.SOLAR_TOTAL, 
            EclipseType.SOLAR_ANNULAR, 
            EclipseType.SOLAR_HYBRID
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "eclipse_id": self.eclipse_id,
            "type": self.eclipse_type.value,
            "maximum_time": self.maximum_eclipse_time.isoformat(),
            "characteristics": {
                "magnitude": self.eclipse_magnitude,
                "obscuration_percent": self.eclipse_obscuration,
                "gamma": self.gamma,
                "is_central": self.is_central_eclipse()
            },
            "duration": {
                "totality_seconds": self.duration_totality,
                "partial_seconds": self.duration_partial,
                "path_width_km": self.path_width
            },
            "astronomical_data": {
                "saros_series": self.saros_series,
                "saros_member": self.saros_member,
                "lunation_number": self.lunation_number,
                "delta_t": self.delta_t
            },
            "location": {
                "greatest_eclipse_lat": self.greatest_eclipse_lat,
                "greatest_eclipse_lon": self.greatest_eclipse_lon,
                "eclipse_path": self.eclipse_path
            },
            "metadata": {
                "calculation_accuracy_seconds": self.calculation_accuracy,
                "swiss_ephemeris_version": self.swiss_ephemeris_version,
                "calculation_time": self.calculation_time.isoformat(),
                "validation_status": self.validation_status,
                "eclipse_phases": self.get_eclipse_phase_names()
            }
        }


@dataclass
class LunarEclipse:
    """Comprehensive lunar eclipse data model."""
    
    # Basic eclipse identification
    eclipse_type: EclipseType
    maximum_eclipse_time: datetime
    eclipse_id: str = field(default="")
    
    # Eclipse magnitudes
    eclipse_magnitude: float = 0.0         # Umbral magnitude
    penumbral_magnitude: float = 0.0       # Penumbral magnitude
    
    # Duration information (seconds)
    totality_duration: Optional[float] = None      # Duration of totality
    partial_duration: float = 0.0                  # Duration of partial eclipse
    penumbral_duration: float = 0.0                # Duration of penumbral eclipse
    
    # Eclipse timing phases
    penumbral_begins: Optional[datetime] = None
    partial_begins: Optional[datetime] = None
    totality_begins: Optional[datetime] = None
    maximum_eclipse: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    totality_ends: Optional[datetime] = None
    partial_ends: Optional[datetime] = None
    penumbral_ends: Optional[datetime] = None
    
    # Astronomical data
    saros_series: Optional[int] = None
    saros_member: Optional[int] = None
    lunation_number: Optional[int] = None
    delta_t: float = 0.0
    
    # Moon position at maximum
    moon_altitude: Optional[float] = None          # Moon altitude for observer
    moon_azimuth: Optional[float] = None           # Moon azimuth for observer
    moon_distance: float = 0.0                     # Earth-Moon distance (km)
    
    # Eclipse characteristics
    gamma: float = 0.0                             # Eclipse parameter
    radius_ratio: float = 0.0                      # Umbra/penumbra ratio
    eclipse_brightness: Optional[float] = None     # Predicted eclipse brightness
    
    # Calculation metadata
    calculation_accuracy: float = 0.0
    swiss_ephemeris_version: str = ""
    calculation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_status: str = "unvalidated"
    
    def __post_init__(self):
        """Generate eclipse ID if not provided."""
        if not self.eclipse_id:
            date_str = self.maximum_eclipse_time.strftime("%Y%m%d")
            type_abbrev = self.eclipse_type.value[:4].upper()
            self.eclipse_id = f"LE{date_str}_{type_abbrev}"
    
    def get_eclipse_contacts(self) -> Dict[str, Optional[datetime]]:
        """Get all eclipse contact times."""
        return {
            "P1": self.penumbral_begins,      # First penumbral contact
            "U1": self.partial_begins,        # First umbral contact
            "U2": self.totality_begins,       # Second umbral contact (totality begins)
            "Maximum": self.maximum_eclipse,   # Greatest eclipse
            "U3": self.totality_ends,         # Third umbral contact (totality ends)
            "U4": self.partial_ends,          # Fourth umbral contact
            "P4": self.penumbral_ends         # Last penumbral contact
        }
    
    def is_total_eclipse(self) -> bool:
        """Check if this is a total lunar eclipse."""
        return self.eclipse_type == EclipseType.LUNAR_TOTAL
    
    def is_visible_eclipse(self) -> bool:
        """Check if eclipse is visible (not just penumbral)."""
        return self.eclipse_type in [EclipseType.LUNAR_TOTAL, EclipseType.LUNAR_PARTIAL]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        contacts = self.get_eclipse_contacts()
        
        return {
            "eclipse_id": self.eclipse_id,
            "type": self.eclipse_type.value,
            "maximum_time": self.maximum_eclipse_time.isoformat(),
            "magnitudes": {
                "umbral_magnitude": self.eclipse_magnitude,
                "penumbral_magnitude": self.penumbral_magnitude
            },
            "duration": {
                "totality_seconds": self.totality_duration,
                "partial_seconds": self.partial_duration,
                "penumbral_seconds": self.penumbral_duration
            },
            "contacts": {
                phase: time.isoformat() if time else None 
                for phase, time in contacts.items()
            },
            "astronomical_data": {
                "saros_series": self.saros_series,
                "saros_member": self.saros_member,
                "lunation_number": self.lunation_number,
                "delta_t": self.delta_t,
                "gamma": self.gamma
            },
            "moon_position": {
                "altitude_degrees": self.moon_altitude,
                "azimuth_degrees": self.moon_azimuth,
                "distance_km": self.moon_distance
            },
            "visibility": {
                "is_total": self.is_total_eclipse(),
                "is_visible": self.is_visible_eclipse(),
                "brightness_estimate": self.eclipse_brightness
            },
            "metadata": {
                "calculation_accuracy_seconds": self.calculation_accuracy,
                "swiss_ephemeris_version": self.swiss_ephemeris_version,
                "calculation_time": self.calculation_time.isoformat(),
                "validation_status": self.validation_status
            }
        }


@dataclass
class Transit:
    """Planetary transit calculation result."""
    
    # Basic transit information
    planet_id: int
    planet_name: str
    target_longitude: float                # Target degree (0-360)
    exact_time: datetime
    transit_type: TransitType
    
    # Transit characteristics
    is_retrograde: bool = False
    retrograde_status: RetrogradeStatus = RetrogradeStatus.DIRECT
    transit_speed: float = 0.0             # Degrees per day at transit
    orb_approaching: float = 1.0           # Orb for "approaching" phase
    orb_separating: float = 1.0            # Orb for "separating" phase
    
    # Duration information
    approach_duration: float = 0.0         # Days approaching target
    separation_duration: float = 0.0       # Days separating from target
    total_influence_duration: float = 0.0  # Total days within orb
    
    # Multiple crossing information (for retrograde)
    crossing_number: int = 1               # Which crossing (1st, 2nd, 3rd for retrograde)
    total_crossings: int = 1               # Total expected crossings
    previous_crossing: Optional[datetime] = None
    next_crossing: Optional[datetime] = None
    
    # Astronomical data
    planet_longitude: float = 0.0          # Exact longitude at transit
    planet_latitude: float = 0.0           # Planet latitude at transit
    planet_distance: float = 0.0           # Planet distance at transit
    daily_motion: float = 0.0              # Daily motion at transit time
    
    # Context information
    zodiac_sign: str = ""                  # Sign being transited
    zodiac_degree: int = 0                 # Degree within sign (0-29)
    zodiac_minute: int = 0                 # Minute within degree (0-59)
    
    # Calculation metadata
    calculation_accuracy: float = 0.0      # Estimated accuracy in seconds
    search_iterations: int = 0             # Number of search iterations used
    calculation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Calculate derived fields."""
        if not self.planet_name:
            self.planet_name = PLANET_NAMES.get(self.planet_id, f"Planet_{self.planet_id}")
        
        # Calculate zodiacal position
        normalized_lon = normalize_longitude(self.target_longitude)
        self.zodiac_degree = int(normalized_lon % 30)
        self.zodiac_minute = int((normalized_lon % 1) * 60)
        
        # Determine zodiac sign
        sign_names = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        sign_index = int(normalized_lon // 30)
        self.zodiac_sign = sign_names[sign_index]
        
        # Set total influence duration
        self.total_influence_duration = self.approach_duration + self.separation_duration
    
    def is_multiple_crossing_transit(self) -> bool:
        """Check if this is a multiple crossing transit due to retrograde motion."""
        return self.total_crossings > 1
    
    def get_zodiacal_position_string(self) -> str:
        """Get formatted zodiacal position string."""
        return f"{self.zodiac_degree:02d}°{self.zodiac_minute:02d}' {self.zodiac_sign}"
    
    def get_phase_description(self) -> str:
        """Get description of transit phase."""
        if self.crossing_number == 1 and self.total_crossings > 1:
            return "First crossing (applying)"
        elif self.crossing_number == self.total_crossings and self.total_crossings > 1:
            return "Final crossing (separating)"
        elif self.crossing_number > 1 and self.crossing_number < self.total_crossings:
            return f"Middle crossing #{self.crossing_number}"
        else:
            return "Single crossing"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "planet": {
                "id": self.planet_id,
                "name": self.planet_name
            },
            "transit": {
                "target_longitude": self.target_longitude,
                "exact_time": self.exact_time.isoformat(),
                "type": self.transit_type.value,
                "zodiacal_position": self.get_zodiacal_position_string(),
                "phase_description": self.get_phase_description()
            },
            "motion": {
                "is_retrograde": self.is_retrograde,
                "retrograde_status": self.retrograde_status.value,
                "transit_speed_deg_per_day": self.transit_speed,
                "daily_motion": self.daily_motion
            },
            "duration": {
                "approach_days": self.approach_duration,
                "separation_days": self.separation_duration,
                "total_influence_days": self.total_influence_duration,
                "orb_approaching": self.orb_approaching,
                "orb_separating": self.orb_separating
            },
            "crossings": {
                "crossing_number": self.crossing_number,
                "total_crossings": self.total_crossings,
                "is_multiple_crossing": self.is_multiple_crossing_transit(),
                "previous_crossing": self.previous_crossing.isoformat() if self.previous_crossing else None,
                "next_crossing": self.next_crossing.isoformat() if self.next_crossing else None
            },
            "astronomical_data": {
                "planet_longitude": self.planet_longitude,
                "planet_latitude": self.planet_latitude,
                "planet_distance": self.planet_distance,
                "zodiac_sign": self.zodiac_sign,
                "zodiac_degree": self.zodiac_degree,
                "zodiac_minute": self.zodiac_minute
            },
            "metadata": {
                "calculation_accuracy_seconds": self.calculation_accuracy,
                "search_iterations": self.search_iterations,
                "calculation_time": self.calculation_time.isoformat()
            }
        }


@dataclass
class SignIngress:
    """Zodiac sign ingress calculation result."""
    
    # Basic ingress information
    planet_id: int
    planet_name: str
    from_sign: str
    to_sign: str
    ingress_time: datetime
    
    # Motion information
    retrograde_status: RetrogradeStatus = RetrogradeStatus.DIRECT
    ingress_speed: float = 0.0             # Degrees per day at ingress
    daily_motion: float = 0.0              # Daily motion at ingress time
    
    # Duration information
    time_in_previous_sign: float = 0.0     # Days spent in previous sign
    expected_time_in_new_sign: float = 0.0 # Expected days in new sign
    
    # Multiple ingress information (for retrograde)
    ingress_number: int = 1                # Which ingress (for retrograde re-entries)
    total_ingresses: int = 1               # Total expected ingresses
    is_final_ingress: bool = True          # Is this the final ingress for this sign change
    
    # Re-ingress tracking (for retrograde motion)
    previous_ingress: Optional[datetime] = None  # Previous ingress time
    next_re_ingress: Optional[datetime] = None   # Next re-ingress time (if retrograde)
    
    # Astronomical data
    exact_longitude: float = 0.0           # Exact longitude at ingress (should be 0°, 30°, 60°, etc.)
    planet_latitude: float = 0.0           # Planet latitude at ingress
    planet_distance: float = 0.0           # Planet distance at ingress
    
    # Context information
    sign_change_type: str = "normal"       # "normal", "retrograde_exit", "retrograde_re_entry"
    seasonal_significance: str = ""        # "spring_equinox", "summer_solstice", etc.
    
    # Calculation metadata
    calculation_accuracy: float = 0.0      # Estimated accuracy in seconds
    search_iterations: int = 0             # Search iterations used
    calculation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Calculate derived fields."""
        if not self.planet_name:
            self.planet_name = PLANET_NAMES.get(self.planet_id, f"Planet_{self.planet_id}")
        
        # Determine sign change type
        if self.retrograde_status == RetrogradeStatus.RETROGRADE:
            if self.ingress_number == 1:
                self.sign_change_type = "retrograde_exit"
            elif not self.is_final_ingress:
                self.sign_change_type = "retrograde_re_entry"
            else:
                self.sign_change_type = "retrograde_final_entry"
        
        # Check for seasonal significance (Sun only)
        if self.planet_id == 0:  # Sun
            seasonal_signs = {
                "Aries": "spring_equinox",
                "Cancer": "summer_solstice", 
                "Libra": "autumn_equinox",
                "Capricorn": "winter_solstice"
            }
            self.seasonal_significance = seasonal_signs.get(self.to_sign, "")
    
    def is_retrograde_ingress(self) -> bool:
        """Check if this is a retrograde-related ingress."""
        return self.retrograde_status in [RetrogradeStatus.RETROGRADE, RetrogradeStatus.STATIONARY_RETROGRADE]
    
    def has_multiple_ingresses(self) -> bool:
        """Check if this sign change involves multiple ingresses."""
        return self.total_ingresses > 1
    
    def get_ingress_description(self) -> str:
        """Get descriptive text for this ingress."""
        base = f"{self.planet_name} enters {self.to_sign}"
        
        if self.seasonal_significance:
            base += f" ({self.seasonal_significance.replace('_', ' ').title()})"
        
        if self.has_multiple_ingresses():
            base += f" ({self.ingress_number} of {self.total_ingresses})"
        
        if self.is_retrograde_ingress():
            base += " [Retrograde]"
        
        return base
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "planet": {
                "id": self.planet_id,
                "name": self.planet_name
            },
            "ingress": {
                "from_sign": self.from_sign,
                "to_sign": self.to_sign,
                "ingress_time": self.ingress_time.isoformat(),
                "description": self.get_ingress_description(),
                "seasonal_significance": self.seasonal_significance
            },
            "motion": {
                "retrograde_status": self.retrograde_status.value,
                "ingress_speed_deg_per_day": self.ingress_speed,
                "daily_motion": self.daily_motion,
                "is_retrograde": self.is_retrograde_ingress()
            },
            "duration": {
                "time_in_previous_sign_days": self.time_in_previous_sign,
                "expected_time_in_new_sign_days": self.expected_time_in_new_sign
            },
            "multiple_ingresses": {
                "ingress_number": self.ingress_number,
                "total_ingresses": self.total_ingresses,
                "is_final_ingress": self.is_final_ingress,
                "has_multiple": self.has_multiple_ingresses(),
                "sign_change_type": self.sign_change_type,
                "previous_ingress": self.previous_ingress.isoformat() if self.previous_ingress else None,
                "next_re_ingress": self.next_re_ingress.isoformat() if self.next_re_ingress else None
            },
            "astronomical_data": {
                "exact_longitude": self.exact_longitude,
                "planet_latitude": self.planet_latitude,
                "planet_distance": self.planet_distance
            },
            "metadata": {
                "calculation_accuracy_seconds": self.calculation_accuracy,
                "search_iterations": self.search_iterations,
                "calculation_time": self.calculation_time.isoformat()
            }
        }


@dataclass
class PlanetaryStation:
    """Planetary station (stationary point) calculation result."""
    
    # Basic station information
    planet_id: int
    planet_name: str
    station_time: datetime
    station_type: RetrogradeStatus  # STATIONARY_DIRECT or STATIONARY_RETROGRADE
    
    # Position at station
    station_longitude: float = 0.0         # Longitude at stationary point
    station_latitude: float = 0.0          # Latitude at stationary point
    station_distance: float = 0.0          # Distance from Earth at station
    
    # Motion information
    longitude_speed_before: float = 0.0    # Speed before station (deg/day)
    longitude_speed_after: float = 0.0     # Speed after station (deg/day)
    speed_change: float = 0.0              # Change in speed through station
    
    # Duration information
    stationary_duration: float = 0.0       # Duration of stationary phase (hours)
    time_to_next_station: Optional[float] = None    # Days to next station
    time_from_last_station: Optional[float] = None  # Days from last station
    
    # Station context
    station_number: int = 1                # Station number in cycle
    total_stations_in_cycle: int = 2       # Total stations in retrograde cycle
    is_loop_beginning: bool = False        # Is this the beginning of retrograde loop
    is_loop_ending: bool = False           # Is this the end of retrograde loop
    
    # Zodiacal position
    zodiac_sign: str = ""
    zodiac_degree: int = 0
    zodiac_minute: int = 0
    
    # Calculation metadata
    calculation_accuracy: float = 0.0      # Estimated accuracy in seconds
    search_iterations: int = 0
    calculation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Calculate derived fields."""
        if not self.planet_name:
            self.planet_name = PLANET_NAMES.get(self.planet_id, f"Planet_{self.planet_id}")
        
        # Calculate zodiacal position
        normalized_lon = normalize_longitude(self.station_longitude)
        self.zodiac_degree = int(normalized_lon % 30)
        self.zodiac_minute = int((normalized_lon % 1) * 60)
        
        # Determine zodiac sign
        sign_names = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        sign_index = int(normalized_lon // 30)
        self.zodiac_sign = sign_names[sign_index]
        
        # Calculate speed change
        self.speed_change = abs(self.longitude_speed_after - self.longitude_speed_before)
        
        # Determine loop position
        if self.station_type == RetrogradeStatus.STATIONARY_RETROGRADE:
            self.is_loop_beginning = True
        elif self.station_type == RetrogradeStatus.STATIONARY_DIRECT:
            self.is_loop_ending = True
    
    def is_retrograde_station(self) -> bool:
        """Check if this is the beginning of retrograde motion."""
        return self.station_type == RetrogradeStatus.STATIONARY_RETROGRADE
    
    def is_direct_station(self) -> bool:
        """Check if this is the end of retrograde motion."""
        return self.station_type == RetrogradeStatus.STATIONARY_DIRECT
    
    def get_zodiacal_position_string(self) -> str:
        """Get formatted zodiacal position string."""
        return f"{self.zodiac_degree:02d}°{self.zodiac_minute:02d}' {self.zodiac_sign}"
    
    def get_station_description(self) -> str:
        """Get descriptive text for this station."""
        motion_type = "Direct" if self.is_direct_station() else "Retrograde"
        return f"{self.planet_name} stations {motion_type} at {self.get_zodiacal_position_string()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "planet": {
                "id": self.planet_id,
                "name": self.planet_name
            },
            "station": {
                "time": self.station_time.isoformat(),
                "type": self.station_type.value,
                "description": self.get_station_description(),
                "longitude": self.station_longitude,
                "latitude": self.station_latitude,
                "distance": self.station_distance
            },
            "motion": {
                "speed_before_deg_per_day": self.longitude_speed_before,
                "speed_after_deg_per_day": self.longitude_speed_after,
                "speed_change": self.speed_change,
                "stationary_duration_hours": self.stationary_duration
            },
            "zodiacal_position": {
                "sign": self.zodiac_sign,
                "degree": self.zodiac_degree,
                "minute": self.zodiac_minute,
                "formatted": self.get_zodiacal_position_string()
            },
            "cycle": {
                "station_number": self.station_number,
                "total_stations": self.total_stations_in_cycle,
                "is_loop_beginning": self.is_loop_beginning,
                "is_loop_ending": self.is_loop_ending,
                "time_to_next_station_days": self.time_to_next_station,
                "time_from_last_station_days": self.time_from_last_station
            },
            "metadata": {
                "calculation_accuracy_seconds": self.calculation_accuracy,
                "search_iterations": self.search_iterations,
                "calculation_time": self.calculation_time.isoformat()
            }
        }


@dataclass
class PredictiveCalculationRequest:
    """Base request model for predictive calculations."""
    
    start_date: datetime
    end_date: Optional[datetime] = None
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    timezone_offset: float = 0.0           # Hours offset from UTC
    
    # Calculation options
    calculation_precision: str = "high"    # "low", "medium", "high", "ultra"
    include_metadata: bool = True
    validate_against_nasa: bool = False
    
    def get_search_span_days(self) -> float:
        """Get search span in days."""
        if self.end_date:
            return (self.end_date - self.start_date).total_seconds() / 86400
        return 365.25  # Default to one year


@dataclass
class ValidationResult:
    """NASA/JPL validation result."""
    
    is_validated: bool = False
    validation_source: str = ""           # "nasa_canon", "jpl_horizons", "usno"
    accuracy_seconds: float = 0.0         # Accuracy compared to reference
    reference_time: Optional[datetime] = None
    calculated_time: Optional[datetime] = None
    deviation_seconds: float = 0.0        # Signed deviation
    validation_notes: str = ""
    validation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_within_tolerance(self, tolerance_seconds: float) -> bool:
        """Check if validation is within acceptable tolerance."""
        return abs(self.deviation_seconds) <= tolerance_seconds
    
    def get_accuracy_grade(self) -> str:
        """Get accuracy grade based on deviation."""
        abs_deviation = abs(self.deviation_seconds)
        if abs_deviation <= 10:
            return "A+"  # Excellent
        elif abs_deviation <= 30:
            return "A"   # Very good
        elif abs_deviation <= 60:
            return "B"   # Good
        elif abs_deviation <= 300:
            return "C"   # Acceptable
        else:
            return "F"   # Unacceptable


# Union types for convenient handling
Eclipse = Union[SolarEclipse, LunarEclipse]
PredictiveResult = Union[SolarEclipse, LunarEclipse, Transit, SignIngress]