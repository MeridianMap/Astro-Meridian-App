"""
Enhanced ACG Line Metadata System - Retrograde-Aware Astrocartography

This module provides enhanced metadata for ACG lines including:
- Retrograde motion status and timing
- Planetary dignity and zodiacal information
- Motion-based styling hints for visualization
- Station timing and approach information

Integrates with existing ACG system while maintaining performance standards.
"""

import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from extracted.systems.ephemeris_utils.tools.enhanced_calculations import EnhancedPlanetPosition
from extracted.systems.ephemeris_utils.const import normalize_longitude, PLANET_NAMES


class MotionStatus(Enum):
    """Planet motion status classifications."""
    DIRECT = "direct"
    RETROGRADE = "retrograde"
    STATIONARY_DIRECT = "stationary_direct"
    STATIONARY_RETROGRADE = "stationary_retrograde"


class PlanetaryDignity(Enum):
    """Planetary dignity classifications."""
    RULERSHIP = "rulership"
    EXALTATION = "exaltation"
    DETRIMENT = "detriment"
    FALL = "fall"
    NEUTRAL = "neutral"


@dataclass
class RetrogradeAwareLineMetadata:
    """
    Enhanced metadata for ACG lines with retrograde motion integration.
    
    Provides comprehensive motion analysis, styling hints, and 
    astronomical context for advanced astrocartography visualization.
    """
    
    # Motion Information
    motion_status: MotionStatus = MotionStatus.DIRECT
    daily_motion: float = 0.0  # degrees per day
    motion_speed_percentile: float = 50.0  # relative to normal speed (0-100)
    is_approaching_station: bool = False
    days_until_station: Optional[int] = None
    days_since_station: Optional[int] = None
    
    # Retrograde Period Information
    retrograde_period_start: Optional[datetime] = None
    retrograde_period_end: Optional[datetime] = None
    retrograde_period_duration_days: Optional[float] = None
    current_retrograde_phase: Optional[str] = None  # "approaching", "peak", "separating"
    
    # Astronomical Context
    planetary_dignity: PlanetaryDignity = PlanetaryDignity.NEUTRAL
    current_zodiac_sign: str = ""
    zodiac_degree: int = 0
    zodiac_minute: int = 0
    element: str = ""  # fire, earth, air, water
    modality: str = ""  # cardinal, fixed, mutable
    
    # House System Positions (for context)
    house_positions: Dict[str, int] = field(default_factory=dict)
    
    # Motion Speed Analysis
    average_daily_motion: float = 0.0
    maximum_daily_motion: float = 0.0
    minimum_daily_motion: float = 0.0
    speed_variation_factor: float = 1.0  # current/average speed ratio
    
    # Station Analysis
    last_station_date: Optional[datetime] = None
    last_station_type: Optional[MotionStatus] = None
    next_station_date: Optional[datetime] = None
    next_station_type: Optional[MotionStatus] = None
    station_cycle_position: float = 0.0  # 0-1, position in current station cycle
    
    # Visualization Styling Hints
    styling_hints: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate derived fields and styling hints."""
        self._generate_styling_hints()
        self._determine_retrograde_phase()
    
    def _generate_styling_hints(self) -> None:
        """Generate visualization styling hints based on motion status."""
        base_styling = {
            "opacity": 0.8,
            "line_width": 2.0,
            "interactive": True,
            "tooltip_priority": "normal"
        }
        
        # Motion-based styling
        if self.motion_status == MotionStatus.RETROGRADE:
            motion_styling = {
                "color_hint": "#cc3333",  # Red for retrograde
                "line_style": "dashed",
                "opacity": 0.7,
                "glow_effect": True,
                "tooltip_priority": "high"
            }
        elif self.motion_status == MotionStatus.DIRECT:
            motion_styling = {
                "color_hint": "#3366cc",  # Blue for direct
                "line_style": "solid",
                "opacity": 0.9,
                "glow_effect": False
            }
        elif "stationary" in self.motion_status.value:
            motion_styling = {
                "color_hint": "#ffaa00",  # Orange for stations
                "line_style": "dotted",
                "opacity": 0.8,
                "glow_effect": True,
                "pulse_animation": True,
                "tooltip_priority": "highest"
            }
        else:
            motion_styling = base_styling.copy()
        
        # Speed-based modifications
        if self.motion_speed_percentile < 20:  # Very slow
            motion_styling["line_width"] = 1.5
            motion_styling["opacity"] *= 0.8
        elif self.motion_speed_percentile > 80:  # Very fast  
            motion_styling["line_width"] = 2.5
            motion_styling["opacity"] *= 1.1
        
        # Station approach modifications
        if self.is_approaching_station and self.days_until_station:
            if self.days_until_station <= 7:
                motion_styling["pulse_animation"] = True
                motion_styling["tooltip_priority"] = "highest"
        
        self.styling_hints = {**base_styling, **motion_styling}
    
    def _determine_retrograde_phase(self) -> None:
        """Determine current phase within retrograde period."""
        if (self.motion_status == MotionStatus.RETROGRADE and 
            self.retrograde_period_start and self.retrograde_period_end):
            
            now = datetime.now(timezone.utc)
            period_start = self.retrograde_period_start
            period_end = self.retrograde_period_end
            
            total_duration = (period_end - period_start).total_seconds()
            elapsed_duration = (now - period_start).total_seconds()
            
            phase_position = elapsed_duration / total_duration if total_duration > 0 else 0
            
            if phase_position < 0.33:
                self.current_retrograde_phase = "approaching"
            elif phase_position < 0.67:
                self.current_retrograde_phase = "peak"
            else:
                self.current_retrograde_phase = "separating"
    
    def get_motion_description(self) -> str:
        """Get human-readable motion description."""
        base_desc = f"{self.motion_status.value.replace('_', ' ').title()}"
        
        if self.current_retrograde_phase:
            base_desc += f" ({self.current_retrograde_phase})"
        
        if self.is_approaching_station and self.days_until_station:
            base_desc += f", station in {self.days_until_station} days"
        
        return base_desc
    
    def get_zodiacal_position_string(self) -> str:
        """Get formatted zodiacal position."""
        return f"{self.zodiac_degree:02d}°{self.zodiac_minute:02d}' {self.current_zodiac_sign}"
    
    def is_in_retrograde_shadow(self, calculation_date: datetime) -> bool:
        """Check if date falls within retrograde shadow period."""
        if not (self.retrograde_period_start and self.retrograde_period_end):
            return False
        
        # Shadow periods extend ~2 weeks before/after actual retrograde
        shadow_start = self.retrograde_period_start - timedelta(days=14)
        shadow_end = self.retrograde_period_end + timedelta(days=14)
        
        return shadow_start <= calculation_date <= shadow_end
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation for API responses."""
        return {
            "motion": {
                "status": self.motion_status.value,
                "daily_motion_deg": self.daily_motion,
                "speed_percentile": self.motion_speed_percentile,
                "description": self.get_motion_description(),
                "is_approaching_station": self.is_approaching_station,
                "days_until_station": self.days_until_station,
                "days_since_station": self.days_since_station
            },
            "retrograde_period": {
                "start": self.retrograde_period_start.isoformat() if self.retrograde_period_start else None,
                "end": self.retrograde_period_end.isoformat() if self.retrograde_period_end else None,
                "duration_days": self.retrograde_period_duration_days,
                "current_phase": self.current_retrograde_phase
            },
            "astronomical_context": {
                "dignity": self.planetary_dignity.value,
                "zodiac_sign": self.current_zodiac_sign,
                "zodiac_position": self.get_zodiacal_position_string(),
                "element": self.element,
                "modality": self.modality,
                "house_positions": self.house_positions
            },
            "motion_analysis": {
                "average_daily_motion": self.average_daily_motion,
                "current_speed_ratio": self.speed_variation_factor,
                "station_cycle_position": self.station_cycle_position
            },
            "stations": {
                "last_station": {
                    "date": self.last_station_date.isoformat() if self.last_station_date else None,
                    "type": self.last_station_type.value if self.last_station_type else None
                },
                "next_station": {
                    "date": self.next_station_date.isoformat() if self.next_station_date else None,
                    "type": self.next_station_type.value if self.next_station_type else None
                }
            },
            "visualization": self.styling_hints
        }


class EnhancedACGLineMetadataGenerator:
    """
    Generator for enhanced ACG line metadata with retrograde integration.
    
    Combines retrograde motion data from enhanced_calculations with
    astrological context and visualization styling information.
    """
    
    # Planetary dignity mappings (simplified traditional system)
    DIGNITY_MAPPINGS = {
        # Sun
        0: {
            "rulership": ["Leo"], 
            "exaltation": ["Aries"],
            "detriment": ["Aquarius"],
            "fall": ["Libra"]
        },
        # Moon  
        1: {
            "rulership": ["Cancer"],
            "exaltation": ["Taurus"], 
            "detriment": ["Capricorn"],
            "fall": ["Scorpio"]
        },
        # Mercury
        2: {
            "rulership": ["Gemini", "Virgo"],
            "exaltation": ["Virgo"],
            "detriment": ["Sagittarius", "Pisces"],
            "fall": ["Pisces"]
        },
        # Venus
        3: {
            "rulership": ["Taurus", "Libra"],
            "exaltation": ["Pisces"],
            "detriment": ["Scorpio", "Aries"], 
            "fall": ["Virgo"]
        },
        # Mars
        4: {
            "rulership": ["Aries", "Scorpio"],
            "exaltation": ["Capricorn"],
            "detriment": ["Libra", "Taurus"],
            "fall": ["Cancer"]
        },
        # Jupiter
        5: {
            "rulership": ["Sagittarius", "Pisces"],
            "exaltation": ["Cancer"],
            "detriment": ["Gemini", "Virgo"],
            "fall": ["Capricorn"]
        },
        # Saturn
        6: {
            "rulership": ["Capricorn", "Aquarius"],
            "exaltation": ["Libra"],
            "detriment": ["Cancer", "Leo"],
            "fall": ["Aries"]
        }
    }
    
    # Sign classifications
    SIGN_ELEMENTS = {
        "Aries": "fire", "Taurus": "earth", "Gemini": "air", "Cancer": "water",
        "Leo": "fire", "Virgo": "earth", "Libra": "air", "Scorpio": "water", 
        "Sagittarius": "fire", "Capricorn": "earth", "Aquarius": "air", "Pisces": "water"
    }
    
    SIGN_MODALITIES = {
        "Aries": "cardinal", "Taurus": "fixed", "Gemini": "mutable", "Cancer": "cardinal",
        "Leo": "fixed", "Virgo": "mutable", "Libra": "cardinal", "Scorpio": "fixed",
        "Sagittarius": "mutable", "Capricorn": "cardinal", "Aquarius": "fixed", "Pisces": "mutable"
    }
    
    # Average daily motions for speed percentile calculations (degrees/day)
    AVERAGE_DAILY_MOTIONS = {
        0: 0.9856,    # Sun
        1: 13.176,    # Moon  
        2: 1.38,      # Mercury
        3: 1.2,       # Venus
        4: 0.524,     # Mars
        5: 0.083,     # Jupiter
        6: 0.033,     # Saturn
        7: 0.0117,    # Uranus
        8: 0.006,     # Neptune
        9: 0.004      # Pluto
    }
    
    def generate_enhanced_metadata(
        self,
        planet_position: EnhancedPlanetPosition,
        calculation_date: datetime,
        include_station_analysis: bool = True
    ) -> RetrogradeAwareLineMetadata:
        """
        Generate comprehensive enhanced metadata for an ACG line.
        
        Args:
            planet_position: Enhanced planet position with retrograde data
            calculation_date: Date of calculation for context
            include_station_analysis: Include station timing analysis
            
        Returns:
            RetrogradeAwareLineMetadata with all enhancement data
        """
        metadata = RetrogradeAwareLineMetadata()
        
        # Basic motion information
        metadata.daily_motion = planet_position.longitude_speed
        metadata.motion_status = self._determine_motion_status(planet_position)
        
        # Speed analysis
        self._calculate_speed_percentile(metadata, planet_position)
        
        # Zodiacal position
        self._calculate_zodiacal_position(metadata, planet_position)
        
        # Planetary dignity
        metadata.planetary_dignity = self._determine_dignity(
            planet_position.planet_id, metadata.current_zodiac_sign
        )
        
        # Station analysis (if requested)
        if include_station_analysis:
            self._analyze_station_timing(metadata, planet_position, calculation_date)
        
        return metadata
    
    def _determine_motion_status(self, planet_position: EnhancedPlanetPosition) -> MotionStatus:
        """Determine detailed motion status from position data."""
        speed = planet_position.longitude_speed
        
        if abs(speed) < 0.0001:  # Practically stationary
            if hasattr(planet_position, 'speed_trend'):
                return MotionStatus.STATIONARY_DIRECT if planet_position.speed_trend > 0 else MotionStatus.STATIONARY_RETROGRADE
            else:
                return MotionStatus.STATIONARY_DIRECT  # Default assumption
        
        return MotionStatus.RETROGRADE if speed < 0 else MotionStatus.DIRECT
    
    def _calculate_speed_percentile(
        self, 
        metadata: RetrogradeAwareLineMetadata,
        planet_position: EnhancedPlanetPosition
    ) -> None:
        """Calculate speed percentile relative to average motion."""
        planet_id = planet_position.planet_id
        current_speed = abs(planet_position.longitude_speed)
        
        if planet_id in self.AVERAGE_DAILY_MOTIONS:
            average_speed = self.AVERAGE_DAILY_MOTIONS[planet_id]
            metadata.average_daily_motion = average_speed
            metadata.speed_variation_factor = current_speed / average_speed if average_speed > 0 else 1.0
            
            # Convert to percentile (50% = average, 100% = maximum typical, 0% = stationary)
            percentile = min(100.0, max(0.0, (current_speed / average_speed) * 50.0))
            metadata.motion_speed_percentile = percentile
        else:
            metadata.motion_speed_percentile = 50.0  # Default to average
    
    def _calculate_zodiacal_position(
        self,
        metadata: RetrogradeAwareLineMetadata, 
        planet_position: EnhancedPlanetPosition
    ) -> None:
        """Calculate zodiacal position and sign information."""
        longitude = normalize_longitude(planet_position.longitude)
        
        # Determine sign
        sign_names = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        sign_index = int(longitude // 30)
        metadata.current_zodiac_sign = sign_names[sign_index]
        
        # Degree and minute within sign
        sign_position = longitude % 30
        metadata.zodiac_degree = int(sign_position)
        metadata.zodiac_minute = int((sign_position % 1) * 60)
        
        # Element and modality
        metadata.element = self.SIGN_ELEMENTS.get(metadata.current_zodiac_sign, "")
        metadata.modality = self.SIGN_MODALITIES.get(metadata.current_zodiac_sign, "")
    
    def _determine_dignity(self, planet_id: int, sign: str) -> PlanetaryDignity:
        """Determine planetary dignity in current sign."""
        if planet_id not in self.DIGNITY_MAPPINGS:
            return PlanetaryDignity.NEUTRAL
        
        dignities = self.DIGNITY_MAPPINGS[planet_id]
        
        if sign in dignities.get("rulership", []):
            return PlanetaryDignity.RULERSHIP
        elif sign in dignities.get("exaltation", []):
            return PlanetaryDignity.EXALTATION
        elif sign in dignities.get("detriment", []):
            return PlanetaryDignity.DETRIMENT
        elif sign in dignities.get("fall", []):
            return PlanetaryDignity.FALL
        else:
            return PlanetaryDignity.NEUTRAL
    
    def _analyze_station_timing(
        self,
        metadata: RetrogradeAwareLineMetadata,
        planet_position: EnhancedPlanetPosition, 
        calculation_date: datetime
    ) -> None:
        """Analyze station timing and approach (simplified implementation)."""
        # This is a simplified implementation - full station analysis would require
        # more complex calculations using Swiss Ephemeris search functions
        
        current_speed = abs(planet_position.longitude_speed)
        average_speed = self.AVERAGE_DAILY_MOTIONS.get(planet_position.planet_id, 1.0)
        
        # Heuristic: if moving much slower than average, might be approaching station
        if current_speed < average_speed * 0.2:  # Less than 20% of average speed
            metadata.is_approaching_station = True
            # Rough estimate based on speed reduction
            metadata.days_until_station = int(current_speed * 30) if current_speed > 0 else 1
        
        # Station cycle position (simplified)
        speed_ratio = current_speed / average_speed if average_speed > 0 else 1.0
        metadata.station_cycle_position = min(1.0, max(0.0, 1.0 - speed_ratio))
    
    def batch_generate_metadata(
        self,
        planet_positions: List[EnhancedPlanetPosition],
        calculation_date: datetime,
        include_station_analysis: bool = True
    ) -> Dict[int, RetrogradeAwareLineMetadata]:
        """
        Generate enhanced metadata for multiple planets efficiently.
        
        Args:
            planet_positions: List of enhanced planet positions
            calculation_date: Calculation date for context
            include_station_analysis: Include station analysis
            
        Returns:
            Dictionary mapping planet_id to enhanced metadata
        """
        metadata_dict = {}
        
        for planet_pos in planet_positions:
            metadata = self.generate_enhanced_metadata(
                planet_pos, calculation_date, include_station_analysis
            )
            metadata_dict[planet_pos.planet_id] = metadata
        
        return metadata_dict