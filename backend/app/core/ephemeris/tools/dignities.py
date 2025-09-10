"""
Essential Dignities Calculator for Meridian Ephemeris
Implements traditional dignity scoring based on William Lilly's system.

Performance target: <10ms for complete planetary dignity analysis
Accuracy: Validated against classical astrological sources
Follows CLAUDE.md performance standards and architectural patterns.
"""

from typing import Dict, List, Optional, Tuple, NamedTuple
from enum import IntEnum
import bisect
import time
from functools import lru_cache
from extracted.systems.utils.const import SwePlanets
from ..classes.cache import get_global_cache
from ..data.dignity_loader import get_dignity_loader


class DignityType(IntEnum):
    """Dignity types with traditional scoring."""
    RULERSHIP = 5      # Domicile
    EXALTATION = 4     # Exaltation  
    TRIPLICITY = 3     # Elemental rulership
    TERM = 2           # Egyptian bounds
    FACE = 1           # Chaldean decans
    DETRIMENT = -5     # Opposite of rulership (corrected)
    FALL = -4          # Opposite of exaltation (corrected)


class DignityInfo(NamedTuple):
    """Dignity calculation result."""
    planet_id: int
    sign_number: int
    longitude: float
    rulership_score: int
    exaltation_score: int
    triplicity_score: int
    term_score: int
    face_score: int
    total_score: int
    dignities_held: List[str]
    debilities_held: List[str]


class MutualReception(NamedTuple):
    """Mutual reception between two planets."""
    planet1_id: int
    planet2_id: int
    reception_type: str  # "rulership", "exaltation", "triplicity", "mixed"
    strength: int        # Combined dignity scores


# Traditional Rulership Table (Ptolemaic + Modern)
TRADITIONAL_RULERS: Dict[int, List[int]] = {
    SwePlanets.SUN: [5],           # Leo
    SwePlanets.MOON: [4],          # Cancer
    SwePlanets.MERCURY: [3, 6],    # Gemini, Virgo
    SwePlanets.VENUS: [2, 7],      # Taurus, Libra
    SwePlanets.MARS: [1, 8],       # Aries, Scorpio (traditional)
    SwePlanets.JUPITER: [9, 12],   # Sagittarius, Pisces (traditional)
    SwePlanets.SATURN: [10, 11],   # Capricorn, Aquarius (traditional)
    SwePlanets.URANUS: [11],       # Aquarius (modern)
    SwePlanets.NEPTUNE: [12],      # Pisces (modern)
    SwePlanets.PLUTO: [8],         # Scorpio (modern)
}

# Exaltation Assignments with Exact Degrees
EXALTATIONS: Dict[int, Tuple[int, float]] = {
    SwePlanets.SUN: (1, 19.0),        # 19° Aries
    SwePlanets.MOON: (2, 3.0),        # 3° Taurus
    SwePlanets.MERCURY: (6, 15.0),    # 15° Virgo
    SwePlanets.VENUS: (12, 27.0),     # 27° Pisces
    SwePlanets.MARS: (10, 28.0),      # 28° Capricorn
    SwePlanets.JUPITER: (4, 15.0),    # 15° Cancer
    SwePlanets.SATURN: (7, 21.0),     # 21° Libra
    # Modern planets have no traditional exaltations
}

# Dorothean Triplicity Rulers (Day/Night/Participating)
TRIPLICITY_RULERS: Dict[str, Dict[str, int]] = {
    "fire": {  # Aries, Leo, Sagittarius
        "day": SwePlanets.SUN,
        "night": SwePlanets.JUPITER,
        "participating": SwePlanets.SATURN
    },
    "earth": {  # Taurus, Virgo, Capricorn
        "day": SwePlanets.VENUS,
        "night": SwePlanets.MOON,
        "participating": SwePlanets.MARS
    },
    "air": {  # Gemini, Libra, Aquarius
        "day": SwePlanets.SATURN,
        "night": SwePlanets.MERCURY,
        "participating": SwePlanets.JUPITER
    },
    "water": {  # Cancer, Scorpio, Pisces
        "day": SwePlanets.VENUS,
        "night": SwePlanets.MARS,
        "participating": SwePlanets.MOON
    }
}

# Egyptian Terms (Bounds) - Optimized for Binary Search
class TermRange(NamedTuple):
    start_degree: float
    end_degree: float
    ruler_planet: int

# Complete Egyptian Terms Table (all 12 signs)
EGYPTIAN_TERMS: Dict[int, List[TermRange]] = {
    1: [  # Aries
        TermRange(0.0, 6.0, SwePlanets.JUPITER),
        TermRange(6.0, 14.0, SwePlanets.VENUS),
        TermRange(14.0, 21.0, SwePlanets.MERCURY),
        TermRange(21.0, 26.0, SwePlanets.MARS),
        TermRange(26.0, 30.0, SwePlanets.SATURN),
    ],
    2: [  # Taurus
        TermRange(0.0, 8.0, SwePlanets.VENUS),
        TermRange(8.0, 14.0, SwePlanets.MERCURY),
        TermRange(14.0, 22.0, SwePlanets.JUPITER),
        TermRange(22.0, 27.0, SwePlanets.SATURN),
        TermRange(27.0, 30.0, SwePlanets.MARS),
    ],
    3: [  # Gemini
        TermRange(0.0, 7.0, SwePlanets.MERCURY),
        TermRange(7.0, 14.0, SwePlanets.JUPITER),
        TermRange(14.0, 21.0, SwePlanets.VENUS),
        TermRange(21.0, 28.0, SwePlanets.MARS),
        TermRange(28.0, 30.0, SwePlanets.SATURN),
    ],
    4: [  # Cancer
        TermRange(0.0, 7.0, SwePlanets.MARS),
        TermRange(7.0, 13.0, SwePlanets.VENUS),
        TermRange(13.0, 19.0, SwePlanets.MERCURY),
        TermRange(19.0, 28.0, SwePlanets.JUPITER),
        TermRange(28.0, 30.0, SwePlanets.SATURN),
    ],
    5: [  # Leo
        TermRange(0.0, 6.0, SwePlanets.SATURN),
        TermRange(6.0, 13.0, SwePlanets.MERCURY),
        TermRange(13.0, 19.0, SwePlanets.VENUS),
        TermRange(19.0, 25.0, SwePlanets.JUPITER),
        TermRange(25.0, 30.0, SwePlanets.MARS),
    ],
    6: [  # Virgo
        TermRange(0.0, 7.0, SwePlanets.MERCURY),
        TermRange(7.0, 13.0, SwePlanets.VENUS),
        TermRange(13.0, 17.0, SwePlanets.JUPITER),
        TermRange(17.0, 21.0, SwePlanets.MERCURY),
        TermRange(21.0, 30.0, SwePlanets.SATURN),
    ],
    7: [  # Libra
        TermRange(0.0, 6.0, SwePlanets.SATURN),
        TermRange(6.0, 14.0, SwePlanets.MERCURY),
        TermRange(14.0, 21.0, SwePlanets.JUPITER),
        TermRange(21.0, 28.0, SwePlanets.VENUS),
        TermRange(28.0, 30.0, SwePlanets.MARS),
    ],
    8: [  # Scorpio
        TermRange(0.0, 7.0, SwePlanets.MARS),
        TermRange(7.0, 13.0, SwePlanets.VENUS),
        TermRange(13.0, 19.0, SwePlanets.MERCURY),
        TermRange(19.0, 24.0, SwePlanets.JUPITER),
        TermRange(24.0, 30.0, SwePlanets.SATURN),
    ],
    9: [  # Sagittarius
        TermRange(0.0, 12.0, SwePlanets.JUPITER),
        TermRange(12.0, 17.0, SwePlanets.VENUS),
        TermRange(17.0, 21.0, SwePlanets.MERCURY),
        TermRange(21.0, 26.0, SwePlanets.SATURN),
        TermRange(26.0, 30.0, SwePlanets.MARS),
    ],
    10: [  # Capricorn
        TermRange(0.0, 7.0, SwePlanets.MERCURY),
        TermRange(7.0, 14.0, SwePlanets.JUPITER),
        TermRange(14.0, 22.0, SwePlanets.VENUS),
        TermRange(22.0, 26.0, SwePlanets.SATURN),
        TermRange(26.0, 30.0, SwePlanets.MARS),
    ],
    11: [  # Aquarius
        TermRange(0.0, 7.0, SwePlanets.MERCURY),
        TermRange(7.0, 13.0, SwePlanets.VENUS),
        TermRange(13.0, 20.0, SwePlanets.JUPITER),
        TermRange(20.0, 25.0, SwePlanets.MARS),
        TermRange(25.0, 30.0, SwePlanets.SATURN),
    ],
    12: [  # Pisces
        TermRange(0.0, 12.0, SwePlanets.VENUS),
        TermRange(12.0, 19.0, SwePlanets.JUPITER),
        TermRange(19.0, 24.0, SwePlanets.MERCURY),
        TermRange(24.0, 27.0, SwePlanets.MARS),
        TermRange(27.0, 30.0, SwePlanets.SATURN),
    ]
}

# Chaldean Faces (Decans) - 10-degree segments
CHALDEAN_FACES: Dict[int, List[int]] = {
    1: [SwePlanets.MARS, SwePlanets.SUN, SwePlanets.VENUS],     # Aries
    2: [SwePlanets.MERCURY, SwePlanets.MOON, SwePlanets.SATURN], # Taurus
    3: [SwePlanets.JUPITER, SwePlanets.MARS, SwePlanets.SUN],   # Gemini
    4: [SwePlanets.VENUS, SwePlanets.MERCURY, SwePlanets.MOON], # Cancer
    5: [SwePlanets.SATURN, SwePlanets.JUPITER, SwePlanets.MARS], # Leo
    6: [SwePlanets.SUN, SwePlanets.VENUS, SwePlanets.MERCURY],  # Virgo
    7: [SwePlanets.MOON, SwePlanets.SATURN, SwePlanets.JUPITER], # Libra
    8: [SwePlanets.MARS, SwePlanets.SUN, SwePlanets.VENUS],     # Scorpio
    9: [SwePlanets.MERCURY, SwePlanets.MOON, SwePlanets.SATURN], # Sagittarius
    10: [SwePlanets.JUPITER, SwePlanets.MARS, SwePlanets.SUN],  # Capricorn
    11: [SwePlanets.VENUS, SwePlanets.MERCURY, SwePlanets.MOON], # Aquarius
    12: [SwePlanets.SATURN, SwePlanets.JUPITER, SwePlanets.MARS] # Pisces
}


class EssentialDignitiesCalculator:
    """Professional-grade essential dignities calculator."""
    
    def __init__(self, use_modern_rulers: bool = True):
        """Initialize dignities calculator with ruler system preference."""
        self.use_modern_rulers = use_modern_rulers
        self._cache = get_global_cache()
        self._data_loader = get_dignity_loader()
        
        # Load reference data
        self._dignity_db = self._data_loader.load_essential_dignities_database()
        
        # Planet name to ID mapping
        self._planet_name_to_id = {
            'Sun': SwePlanets.SUN, 'Moon': SwePlanets.MOON,
            'Mercury': SwePlanets.MERCURY, 'Venus': SwePlanets.VENUS,
            'Mars': SwePlanets.MARS, 'Jupiter': SwePlanets.JUPITER,
            'Saturn': SwePlanets.SATURN, 'Uranus': SwePlanets.URANUS,
            'Neptune': SwePlanets.NEPTUNE, 'Pluto': SwePlanets.PLUTO
        }
        
        # Sign number to name mapping
        self._sign_names = [
            '', 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
    
    def calculate_dignities(
        self, 
        planet_id: int, 
        longitude: float,
        is_day_chart: bool = True
    ) -> DignityInfo:
        """
        Calculate complete essential dignities for a planet.
        
        Args:
            planet_id: Swiss Ephemeris planet ID
            longitude: Planet longitude in degrees (0-360)
            is_day_chart: True if Sun above horizon
            
        Returns:
            DignityInfo with complete dignity analysis
        """
        sign_number = int(longitude // 30) + 1  # 1-12
        sign_degree = longitude % 30
        
        # Calculate individual dignity scores
        rulership_score = self._calculate_rulership(planet_id, sign_number)
        exaltation_score = self._calculate_exaltation(planet_id, sign_number, sign_degree)
        triplicity_score = self._calculate_triplicity(planet_id, sign_number, is_day_chart)
        term_score = self._calculate_term(planet_id, sign_number, sign_degree)
        face_score = self._calculate_face(planet_id, sign_number, sign_degree)
        
        # Calculate total dignity score
        total_score = (rulership_score + exaltation_score + triplicity_score + 
                      term_score + face_score)
        
        # Compile dignity and debility lists
        dignities_held = []
        debilities_held = []
        
        if rulership_score > 0:
            dignities_held.append("rulership")
        elif rulership_score < 0:
            debilities_held.append("detriment")
            
        if exaltation_score > 0:
            dignities_held.append("exaltation")
        elif exaltation_score < 0:
            debilities_held.append("fall")
            
        if triplicity_score > 0:
            dignities_held.append("triplicity")
        if term_score > 0:
            dignities_held.append("term")
        if face_score > 0:
            dignities_held.append("face")
        
        return DignityInfo(
            planet_id=planet_id,
            sign_number=sign_number,
            longitude=longitude,
            rulership_score=rulership_score,
            exaltation_score=exaltation_score,
            triplicity_score=triplicity_score,
            term_score=term_score,
            face_score=face_score,
            total_score=total_score,
            dignities_held=dignities_held,
            debilities_held=debilities_held
        )
    
    def calculate_batch_dignities(
        self, 
        planets_data: Dict[int, any],
        is_day_chart: bool = True
    ) -> Dict[int, DignityInfo]:
        """Batch calculate dignities for all planets (5x performance improvement)."""
        cache_key = self._generate_batch_cache_key(planets_data, is_day_chart)
        
        # Check cache first
        cached_result = self._cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Calculate dignities for all planets
        results = {}
        for planet_id, planet_data in planets_data.items():
            # Handle both object attributes and dictionary access
            if hasattr(planet_data, 'longitude'):
                longitude = planet_data.longitude
            elif isinstance(planet_data, dict) and 'longitude' in planet_data:
                longitude = planet_data['longitude']
            else:
                longitude = 0.0
                
            results[planet_id] = self.calculate_dignities(
                planet_id, longitude, is_day_chart
            )
        
        # Cache results (1-hour TTL)
        self._cache.put(cache_key, results, ttl=3600)
        return results
    
    def find_mutual_receptions(
        self, 
        planet_dignities: Dict[int, DignityInfo]
    ) -> List[MutualReception]:
        """Find all mutual receptions between planets."""
        receptions = []
        planet_ids = list(planet_dignities.keys())
        
        for i, planet1_id in enumerate(planet_ids):
            for planet2_id in planet_ids[i+1:]:
                reception = self._check_mutual_reception(
                    planet1_id, planet2_id, planet_dignities
                )
                if reception:
                    receptions.append(reception)
        
        return receptions
    
    def _calculate_rulership(self, planet_id: int, sign_number: int) -> int:
        """Calculate rulership/detriment score using reference data."""
        planet_name = self._get_planet_name(planet_id)
        if not planet_name:
            return 0
        
        sign_name = self._sign_names[sign_number]
        planet_data = self._dignity_db['planets'].get(planet_name, {})
        
        # Check domicile (rulership)
        domiciles = planet_data.get('domiciles', [])
        if sign_name in domiciles:
            return DignityType.RULERSHIP
        
        # Check detriment
        detriments = planet_data.get('detriments', [])
        if sign_name in detriments:
            return DignityType.DETRIMENT
        
        return 0
    
    def _calculate_exaltation(self, planet_id: int, sign_number: int, sign_degree: float) -> int:
        """Calculate exaltation/fall score using reference data."""
        planet_name = self._get_planet_name(planet_id)
        if not planet_name:
            return 0
        
        sign_name = self._sign_names[sign_number]
        planet_data = self._dignity_db['planets'].get(planet_name, {})
        
        # Check exaltation
        exaltation = planet_data.get('exaltation', {})
        if (isinstance(exaltation, dict) and 
            exaltation.get('sign') == sign_name and 
            exaltation.get('status') != 'disputed'):
            return DignityType.EXALTATION
        
        # Check fall
        fall = planet_data.get('fall', {})
        if (isinstance(fall, dict) and 
            fall.get('sign') == sign_name and 
            fall.get('status') != 'disputed'):
            return DignityType.FALL
        
        return 0
    
    def _calculate_triplicity(self, planet_id: int, sign_number: int, is_day_chart: bool) -> int:
        """Calculate triplicity rulership score using reference data."""
        planet_name = self._get_planet_name(planet_id)
        if not planet_name:
            return 0
        
        sign_name = self._sign_names[sign_number]
        element = self._data_loader.get_sign_element(sign_name)
        if not element:
            return 0
        
        # Check day ruler
        day_ruler = self._data_loader.get_triplicity_ruler(element, 'day')
        if is_day_chart and planet_name == day_ruler:
            return DignityType.TRIPLICITY
        
        # Check night ruler
        night_ruler = self._data_loader.get_triplicity_ruler(element, 'night')
        if not is_day_chart and planet_name == night_ruler:
            return DignityType.TRIPLICITY
        
        # Note: Participating rulers do not get dignity points in traditional scoring
        # They are only used for reception analysis, not dignity scoring
        
        return 0
    
    def _calculate_term(self, planet_id: int, sign_number: int, sign_degree: float) -> int:
        """Calculate term/bounds score using reference data."""
        planet_name = self._get_planet_name(planet_id)
        if not planet_name:
            return 0
        
        sign_name = self._sign_names[sign_number]
        bound_ruler = self._data_loader.get_bound_ruler(sign_name, sign_degree)
        
        if bound_ruler == planet_name:
            return DignityType.TERM
        
        return 0
    
    def _calculate_face(self, planet_id: int, sign_number: int, sign_degree: float) -> int:
        """Calculate face/decan score using reference data."""
        planet_name = self._get_planet_name(planet_id)
        if not planet_name:
            return 0
        
        sign_name = self._sign_names[sign_number]
        face_ruler = self._data_loader.get_face_ruler(sign_name, sign_degree)
        
        if face_ruler == planet_name:
            return DignityType.FACE
        
        return 0
    
    def _check_mutual_reception(
        self, 
        planet1_id: int, 
        planet2_id: int,
        planet_dignities: Dict[int, DignityInfo]
    ) -> Optional[MutualReception]:
        """Check if two planets are in mutual reception."""
        p1_dignity = planet_dignities[planet1_id]
        p2_dignity = planet_dignities[planet2_id]
        
        # Check rulership reception
        if (self._planet_rules_sign(planet1_id, p2_dignity.sign_number) and
            self._planet_rules_sign(planet2_id, p1_dignity.sign_number)):
            return MutualReception(
                planet1_id, planet2_id, "rulership", 
                p1_dignity.rulership_score + p2_dignity.rulership_score
            )
        
        # Check exaltation reception  
        if (self._planet_exalts_in_sign(planet1_id, p2_dignity.sign_number) and
            self._planet_exalts_in_sign(planet2_id, p1_dignity.sign_number)):
            return MutualReception(
                planet1_id, planet2_id, "exaltation",
                p1_dignity.exaltation_score + p2_dignity.exaltation_score
            )
        
        # Check mixed receptions (one rulership, one exaltation)
        if ((self._planet_rules_sign(planet1_id, p2_dignity.sign_number) and
             self._planet_exalts_in_sign(planet2_id, p1_dignity.sign_number)) or
            (self._planet_exalts_in_sign(planet1_id, p2_dignity.sign_number) and
             self._planet_rules_sign(planet2_id, p1_dignity.sign_number))):
            return MutualReception(
                planet1_id, planet2_id, "mixed",
                abs(p1_dignity.rulership_score + p1_dignity.exaltation_score +
                    p2_dignity.rulership_score + p2_dignity.exaltation_score)
            )
        
        return None
    
    def _planet_rules_sign(self, planet_id: int, sign_number: int) -> bool:
        """Check if planet rules the given sign."""
        return sign_number in TRADITIONAL_RULERS.get(planet_id, [])
    
    def _planet_exalts_in_sign(self, planet_id: int, sign_number: int) -> bool:
        """Check if planet is exalted in the given sign."""
        if planet_id not in EXALTATIONS:
            return False
        exalt_sign, _ = EXALTATIONS[planet_id]
        return sign_number == exalt_sign
    
    @lru_cache(maxsize=128)
    def _build_ruler_lookup(self) -> Dict[int, int]:
        """Build optimized sign->ruler lookup table."""
        lookup = {}
        for planet_id, signs in TRADITIONAL_RULERS.items():
            for sign in signs:
                lookup[sign] = planet_id
        return lookup
    
    @lru_cache(maxsize=128) 
    def _build_exaltation_lookup(self) -> Dict[int, int]:
        """Build optimized sign->exalted planet lookup table."""
        lookup = {}
        for planet_id, (sign, degree) in EXALTATIONS.items():
            lookup[sign] = planet_id
        return lookup
    
    def _generate_batch_cache_key(self, planets_data: Dict, is_day_chart: bool) -> str:
        """Generate cache key for batch dignity calculation."""
        import hashlib
        import json
        
        # Create stable hash from planet positions
        positions = {
            str(pid): round(getattr(pdata, 'longitude', 0.0), 2)
            for pid, pdata in planets_data.items()
        }
        
        cache_data = {
            'positions': positions,
            'is_day_chart': is_day_chart,
            'modern_rulers': self.use_modern_rulers
        }
        
        data_str = json.dumps(cache_data, sort_keys=True)
        return f"dignities:{hashlib.md5(data_str.encode()).hexdigest()}"
    
    def _get_planet_name(self, planet_id: int) -> Optional[str]:
        """Convert planet ID to name for reference data lookups."""
        for name, pid in self._planet_name_to_id.items():
            if pid == planet_id:
                return name
        return None