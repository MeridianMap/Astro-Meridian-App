"""
Meridian Ephemeris Engine - Fixed Stars Calculator

Provides calculation and integration of fixed stars into natal charts.
Supports both Swiss Ephemeris star catalog (when available) and built-in star data.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from extracted.systems.utils.swiss_ephemeris import (
    ensure_swiss_ephemeris_setup,
    safe_fixstar_ut,
)

# Ensure Swiss Ephemeris is configured via centralized wrapper
ensure_swiss_ephemeris_setup()

from extracted.systems.utils.const import normalize_longitude


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


@dataclass
class FixedStarData:
    """Data structure for a fixed star."""
    name: str
    magnitude: float
    spectral_class: str
    se_name: Optional[str] = None  # Swiss Ephemeris name
    longitude_2000: Optional[float] = None  # J2000 longitude if known
    latitude_2000: Optional[float] = None   # J2000 latitude if known
    proper_motion_ra: Optional[float] = None  # mas/year
    proper_motion_dec: Optional[float] = None # mas/year
    constellation: Optional[str] = None
    traditional_name: Optional[str] = None


class FixedStarCalculator:
    """
    Calculator for fixed star positions and aspects.
    
    Provides integration with Swiss Ephemeris when star catalog files are available,
    and fallback calculations for known stars.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Registry of available fixed stars
        self.star_registry = self._initialize_star_registry()
        
        # Test Swiss Ephemeris star availability
        self.swe_stars_available = self._test_star_catalog_availability()
        
    def _initialize_star_registry(self) -> Dict[str, FixedStarData]:
        """
        Initialize registry of fixed stars with their data.
        
        Returns:
            Dictionary mapping star names to FixedStarData objects
        """
        stars = {
            # Foundation 24 Fixed Stars (traditional astrology's most important stars)
            "Spica": FixedStarData(
                name="Spica",
                magnitude=0.97,
                spectral_class="B1III-IV",
                se_name="Spica",
                constellation="Virgo",
                traditional_name="Azimech"
            ),
            "Regulus": FixedStarData(
                name="Regulus",
                magnitude=1.35,
                spectral_class="B8IVn",
                se_name="Regulus",
                constellation="Leo",
                traditional_name="Cor Leonis"
            ),
            "Aldebaran": FixedStarData(
                name="Aldebaran",
                magnitude=0.85,
                spectral_class="K5III",
                se_name="Aldebaran",
                constellation="Taurus",
                traditional_name="Rohini"
            ),
            "Antares": FixedStarData(
                name="Antares",
                magnitude=1.09,
                spectral_class="M1.5Iab-Ib",
                se_name="Antares",
                constellation="Scorpius",
                traditional_name="Rival of Mars"
            ),
            "Fomalhaut": FixedStarData(
                name="Fomalhaut",
                magnitude=1.16,
                spectral_class="A3V",
                se_name="Fomalhaut",
                constellation="Piscis Austrinus",
                traditional_name="Royal Star"
            ),
            "Sirius": FixedStarData(
                name="Sirius",
                magnitude=-1.46,
                spectral_class="A1V",
                se_name="Sirius",
                constellation="Canis Major",
                traditional_name="Dog Star"
            ),
            "Arcturus": FixedStarData(
                name="Arcturus",
                magnitude=-0.05,
                spectral_class="K1.5IIIFe-0.5",
                se_name="Arcturus",
                constellation="Boötes",
                traditional_name="Job's Star"
            ),
            "Vega": FixedStarData(
                name="Vega",
                magnitude=0.03,
                spectral_class="A0V",
                se_name="Vega",
                constellation="Lyra",
                traditional_name="Waki"
            ),
            "Capella": FixedStarData(
                name="Capella",
                magnitude=0.08,
                spectral_class="G5III",
                se_name="Capella",
                constellation="Auriga",
                traditional_name="Little Goat"
            ),
            "Algol": FixedStarData(
                name="Algol",
                magnitude=2.12,
                spectral_class="B8V",
                se_name="Algol",
                constellation="Perseus",
                traditional_name="Demon Star"
            ),
            "Betelgeuse": FixedStarData(
                name="Betelgeuse",
                magnitude=0.50,
                spectral_class="M1-2Ia-ab",
                se_name="Betelgeuse",
                constellation="Orion",
                traditional_name="Giant's Shoulder"
            ),
            "Rigel": FixedStarData(
                name="Rigel",
                magnitude=0.13,
                spectral_class="B8Ia",
                se_name="Rigel",
                constellation="Orion",
                traditional_name="Left Foot of Orion"
            ),
            "Procyon": FixedStarData(
                name="Procyon",
                magnitude=0.34,
                spectral_class="F5IV-V",
                se_name="Procyon",
                constellation="Canis Minor",
                traditional_name="Little Dog Star"
            ),
            "Canopus": FixedStarData(
                name="Canopus",
                magnitude=-0.74,
                spectral_class="A9II",
                se_name="Canopus",
                constellation="Carina",
                traditional_name="Agastya"
            ),
            "Altair": FixedStarData(
                name="Altair",
                magnitude=0.77,
                spectral_class="A7V",
                se_name="Altair",
                constellation="Aquila",
                traditional_name="Eagle Star"
            ),
            "Deneb": FixedStarData(
                name="Deneb",
                magnitude=1.25,
                spectral_class="A2Ia",
                se_name="Deneb",
                constellation="Cygnus",
                traditional_name="Tail of the Swan"
            ),
            "Bellatrix": FixedStarData(
                name="Bellatrix",
                magnitude=1.64,
                spectral_class="B2III",
                se_name="Bellatrix",
                constellation="Orion",
                traditional_name="Amazon Star"
            ),
            "Alcyone": FixedStarData(
                name="Alcyone",
                magnitude=2.87,
                spectral_class="B7IIIe",
                se_name="Alcyone",
                constellation="Taurus",
                traditional_name="Central One of Pleiades"
            ),
            "Achernar": FixedStarData(
                name="Achernar",
                magnitude=0.46,
                spectral_class="Be",
                se_name="Achernar",
                constellation="Eridanus",
                traditional_name="River's End"
            ),
            "Acrux": FixedStarData(
                name="Acrux",
                magnitude=0.77,
                spectral_class="B0.5IV",
                se_name="Acrux",
                constellation="Crux",
                traditional_name="Alpha Crucis"
            ),
            "Alphecca": FixedStarData(
                name="Alphecca",
                magnitude=2.23,
                spectral_class="A0V",
                se_name="Alphecca",
                constellation="Corona Borealis",
                traditional_name="Gemma"
            ),
            "Rasalhague": FixedStarData(
                name="Rasalhague",
                magnitude=2.08,
                spectral_class="A5III-IV",
                se_name="Rasalhague",
                constellation="Ophiuchus",
                traditional_name="Head of the Serpent Bearer"
            ),
            "Denebola": FixedStarData(
                name="Denebola",
                magnitude=2.14,
                spectral_class="A3V",
                se_name="Denebola",
                constellation="Leo",
                traditional_name="Tail of the Lion"
            ),
            "Markab": FixedStarData(
                name="Markab",
                magnitude=2.49,
                spectral_class="A0III",
                se_name="Markab",
                constellation="Pegasus",
                traditional_name="Shoulder of Pegasus"
            )
        }
        
        return stars
    
    def _test_star_catalog_availability(self) -> bool:
        """
        Test if Swiss Ephemeris star catalog files are available.
        
        Returns:
            True if star catalog is available, False otherwise
        """
        try:
            # Test with a known star
            result = safe_fixstar_ut("Spica", 2451545.0)
            self.logger.info("Swiss Ephemeris limited star catalog available (only built-in stars like Spica)")
            return True
        except Exception as e:
            self.logger.warning(f"Swiss Ephemeris star catalog not available: {e}")
            return False
    
    def get_available_stars(self) -> List[str]:
        """
        Get list of available fixed stars.
        
        Returns:
            List of star names that can be calculated
        """
        # Test each star individually to see which ones work
        available = []
        for star_name, star_data in self.star_registry.items():
            if self._test_individual_star(star_data.se_name or star_name):
                available.append(star_name)
                self.logger.debug(f"Star {star_name} available via Swiss Ephemeris")
            else:
                self.logger.debug(f"Star {star_name} not available (Swiss Ephemeris catalog missing)")
        
        if available:
            self.logger.info(f"Found {len(available)} available fixed stars: {available}")
        else:
            self.logger.warning("No fixed stars available - Swiss Ephemeris star catalog missing")
            
        return available
    
    def _test_individual_star(self, star_name: str) -> bool:
        """Test if an individual star can be calculated."""
        try:
            safe_fixstar_ut(star_name, 2451545.0)
            return True
        except:
            return False
    
    def calculate_star_position(
        self,
        star_name: str,
        julian_day: float,
        flags: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate position of a fixed star.
        
        Args:
            star_name: Name of the star
            julian_day: Julian Day for calculation
            flags: Swiss Ephemeris calculation flags
            
        Returns:
            Dictionary with star position data or None if calculation fails
        """
        if star_name not in self.star_registry:
            self.logger.error(f"Unknown star: {star_name}")
            return None
        
        star_data = self.star_registry[star_name]
        se_name = star_data.se_name or star_name
        
        try:
            # Note: flags not supported in fixstar_ut wrapper; Swiss Ephemeris uses global flags
            result = safe_fixstar_ut(se_name, julian_day)
            
            if len(result) < 2 or len(result[0]) < 3:
                self.logger.error(f"Invalid result for star {star_name}")
                return None
            
            coords = result[0]
            star_info = result[1] if len(result) > 1 else ""
            
            return {
                'name': star_name,
                'longitude': normalize_longitude(coords[0]),
                'latitude': coords[1],
                'distance': coords[2] if len(coords) > 2 else None,
                'longitude_speed': coords[3] if len(coords) > 3 else None,
                'latitude_speed': coords[4] if len(coords) > 4 else None,
                'distance_speed': coords[5] if len(coords) > 5 else None,
                'magnitude': star_data.magnitude,
                'spectral_class': star_data.spectral_class,
                'constellation': star_data.constellation,
                'traditional_name': star_data.traditional_name,
                'se_info': star_info,
                'julian_day': julian_day  # Store JD instead of problematic datetime conversion
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate position for star {star_name}: {e}")
            return None
    
    def calculate_multiple_stars(
        self,
        star_names: Optional[List[str]],
        julian_day: float,
        flags: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate positions for multiple fixed stars.
        
        Args:
            star_names: List of star names (None for all available stars)
            julian_day: Julian Day for calculation
            flags: Swiss Ephemeris calculation flags
            
        Returns:
            Dictionary mapping star names to position data
        """
        if star_names is None:
            star_names = self.get_available_stars()
        
        results = {}
        for star_name in star_names:
            position = self.calculate_star_position(star_name, julian_day, flags)
            if position:
                results[star_name] = position
        
        return results
    
    def find_stars_by_magnitude(self, max_magnitude: float = 2.0) -> List[str]:
        """
        Find stars brighter than specified magnitude.
        
        Args:
            max_magnitude: Maximum magnitude (lower = brighter)
            
        Returns:
            List of star names meeting criteria
        """
        bright_stars = []
        for name, data in self.star_registry.items():
            if data.magnitude <= max_magnitude:
                bright_stars.append(name)
        
        return sorted(bright_stars, key=lambda x: self.star_registry[x].magnitude)
    
    def get_foundation_24_stars(self) -> List[str]:
        """
        Get the traditional Foundation 24 fixed stars.
        
        Returns:
            List of the 24 most important fixed stars in traditional astrology (only those available)
        """
        foundation_stars = [
            "Regulus", "Aldebaran", "Antares", "Fomalhaut",  # Royal Stars
            "Spica", "Arcturus", "Sirius", "Vega", "Capella", 
            "Algol", "Betelgeuse", "Rigel", "Procyon", "Canopus",
            "Altair", "Deneb", "Bellatrix", "Alcyone", "Achernar",
            "Acrux", "Alphecca", "Rasalhague", "Denebola", "Markab"
        ]
        
        # Filter to only available stars
        available = self.get_available_stars()
        available_foundation = [star for star in foundation_stars if star in available]
        
        if len(available_foundation) < len(foundation_stars):
            self.logger.warning(f"Only {len(available_foundation)} of {len(foundation_stars)} Foundation 24 stars available")
            
        return available_foundation
    
    def calculate_star_aspects(
        self,
        star_positions: Dict[str, Dict[str, Any]],
        planet_positions: Dict[str, Any],
        orb_degrees: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Calculate aspects between fixed stars and planets.
        
        Args:
            star_positions: Dictionary of star positions
            planet_positions: Dictionary of planet positions  
            orb_degrees: Orb for aspects in degrees
            
        Returns:
            List of aspect dictionaries
        """
        aspects = []
        aspect_angles = [0, 60, 90, 120, 180]  # Conjunction, sextile, square, trine, opposition
        aspect_names = {0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}
        
        for star_name, star_data in star_positions.items():
            star_longitude = star_data['longitude']
            
            for planet_name, planet_data in planet_positions.items():
                if isinstance(planet_data, dict) and 'longitude' in planet_data:
                    planet_longitude = planet_data['longitude']
                elif hasattr(planet_data, 'longitude'):
                    planet_longitude = planet_data.longitude
                else:
                    continue
                
                # Calculate angular separation
                diff = abs(star_longitude - planet_longitude)
                if diff > 180:
                    diff = 360 - diff
                
                # Check for aspects within orb
                for angle in aspect_angles:
                    orb = abs(diff - angle)
                    if orb <= orb_degrees:
                        aspects.append({
                            'star': star_name,
                            'planet': planet_name,
                            'aspect': aspect_names[angle],
                            'angle': angle,
                            'orb': orb,
                            'exact': orb < 0.1,
                            'star_longitude': star_longitude,
                            'planet_longitude': planet_longitude
                        })
        
        return aspects
    
    def get_star_data(self, star_name: str) -> Optional[FixedStarData]:
        """
        Get star data for a specific star.
        
        Args:
            star_name: Name of the star
            
        Returns:
            FixedStarData object or None if not found
        """
        return self.star_registry.get(star_name)
    
    def validate_star_availability(self) -> Dict[str, Any]:
        """
        Validate which stars are available for calculation.
        
        Returns:
            Dictionary with availability status
        """
        validation_results = {
            'swe_catalog_available': self.swe_stars_available,
            'total_stars_in_registry': len(self.star_registry),
            'available_stars': [],
            'unavailable_stars': [],
            'foundation_24_available': 0,
            'foundation_24_total': 24
        }
        
        available_stars = self.get_available_stars()
        validation_results['available_stars'] = available_stars
        validation_results['unavailable_stars'] = [
            star for star in self.star_registry.keys() if star not in available_stars
        ]
        
        foundation_24 = self.get_foundation_24_stars()
        validation_results['foundation_24_available'] = len(foundation_24)
        
        return validation_results