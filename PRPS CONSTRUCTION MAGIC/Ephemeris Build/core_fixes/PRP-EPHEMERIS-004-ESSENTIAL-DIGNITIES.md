# PRP-EPHEMERIS-004: Essential Dignities System

## Goal
Implement a comprehensive Essential Dignities calculation system for the Meridian ephemeris API, providing traditional astrological analysis of planetary strength and condition through rulership, exaltation, triplicity, term, and face assignments.

### Feature Goal
Create a professional-grade dignities system that calculates and exposes essential dignity scores, mutual receptions, and dispositorship analysis for all planets in natal chart calculations, enabling traditional astrological interpretation.

### Deliverable
Complete essential dignities system with dignity scoring, mutual reception detection, and API integration that adds dignity information to planet response objects.

### Success Definition
- All planets show comprehensive dignity information (rulership, exaltation, triplicity, term, face)
- William Lilly dignity scoring system implemented (+5 to -5 scale)
- Mutual reception detection for all reception types (rulership, exaltation, triplicity)
- Performance impact <10ms for complete dignity analysis
- Professional validation against established astrological software
- API responses include dignity scores and reception information

---

## Context

### YAML Structure Reference
```yaml
# Essential dignity systems research findings
traditional_dignity_hierarchy:
  rulership: "+5 points - planet in own sign (domicile)"
  exaltation: "+4 points - planet in sign of exaltation"  
  triplicity: "+3 points - planet rules element of current sign"
  term_bounds: "+2 points - planet rules degree range (Egyptian terms)"
  face_decan: "+1 point - planet rules 10-degree decan"
  detriment: "-4 points - planet in opposite of rulership"
  fall: "-5 points - planet in opposite of exaltation"

# Traditional rulership assignments (Ptolemaic system)
traditional_rulerships:
  sun: [leo]           # ♌ Leo
  moon: [cancer]       # ♋ Cancer  
  mercury: [gemini, virgo]      # ♊♍ Gemini, Virgo
  venus: [taurus, libra]        # ♉♎ Taurus, Libra
  mars: [aries, scorpio]        # ♈♏ Aries, Scorpio
  jupiter: [sagittarius, pisces] # ♐♓ Sagittarius, Pisces
  saturn: [capricorn, aquarius] # ♑♒ Capricorn, Aquarius

# Modern rulership additions
modern_rulerships:
  uranus: [aquarius]    # ♒ Aquarius (traditional: Saturn)
  neptune: [pisces]     # ♓ Pisces (traditional: Jupiter)
  pluto: [scorpio]      # ♏ Scorpio (traditional: Mars)

# Exaltation degrees (classical system)
exaltation_assignments:
  sun: {sign: aries, degree: 19}      # 19° Aries
  moon: {sign: taurus, degree: 3}     # 3° Taurus  
  mercury: {sign: virgo, degree: 15}  # 15° Virgo
  venus: {sign: pisces, degree: 27}   # 27° Pisces
  mars: {sign: capricorn, degree: 28} # 28° Capricorn
  jupiter: {sign: cancer, degree: 15} # 15° Cancer
  saturn: {sign: libra, degree: 21}   # 21° Libra
  # Modern planets: No traditional exaltations

# Egyptian terms (bounds) - degree ranges per sign
egyptian_terms_sample:
  aries: 
    - {ruler: jupiter, start: 0, end: 6}   # 0-6° Jupiter
    - {ruler: venus, start: 6, end: 12}    # 6-12° Venus
    - {ruler: mercury, start: 12, end: 20} # 12-20° Mercury
    - {ruler: mars, start: 20, end: 25}    # 20-25° Mars
    - {ruler: saturn, start: 25, end: 30}  # 25-30° Saturn

# Performance requirements
performance_standards:
  dignity_calculation: "<10ms for complete planetary dignity analysis"
  table_lookup: "O(1) for degree range queries using binary search"
  cache_integration: "Redis + memory caching for dignity tables"
  memory_usage: "<500KB for all dignity lookup tables"
  batch_processing: "5x improvement for multiple planet dignity analysis"

# Current Meridian integration points
integration_targets:
  planet_response: "backend/app/api/models/schemas.py:198-213 (PlanetResponse)"
  service_layer: "backend/app/services/ephemeris_service.py (planet formatting)"
  cache_system: "backend/app/core/ephemeris/classes/cache.py (extend existing)"
  
# Missing from current system
current_gaps:
  dignity_fields: "No dignity information in PlanetResponse model"
  scoring_system: "No dignity scoring calculation"
  mutual_receptions: "No reception analysis between planets"  
  dispositorship: "No rulership chain analysis"
```

### External Resources
- **William Lilly Christian Astrology**: https://www.astro.com/astrology/in_lillyequivocation_e.htm
- **Essential Dignities Reference**: https://www.skyscript.co.uk/dig1.html
- **Egyptian Terms Tables**: https://www.astro.com/astrology/in_terms_e.htm
- **Triplicity Rulers**: https://sevenstarsastrology.com/traditional-rulerships-triplicities/
- **Mutual Reception Analysis**: https://www.astro.com/astrology/in_recept_e.htm

---

## Implementation Tasks

### Task 1: Create Essential Dignities Data Tables
**Dependency**: None  
**Location**: `backend/app/core/ephemeris/tools/dignities.py` (new file)

Create comprehensive dignity assignment tables with optimized lookup structures:

```python
# File: backend/app/core/ephemeris/tools/dignities.py (CREATE NEW)
# Purpose: Essential dignities calculation system with professional-grade accuracy

"""
Essential Dignities Calculator for Meridian Ephemeris
Implements traditional dignity scoring based on William Lilly's system.
"""

from typing import Dict, List, Optional, Tuple, NamedTuple
from enum import IntEnum
import bisect
from ..const import SwePlanets

class DignityType(IntEnum):
    """Dignity types with traditional scoring."""
    RULERSHIP = 5      # Domicile
    EXALTATION = 4     # Exaltation  
    TRIPLICITY = 3     # Elemental rulership
    TERM = 2           # Egyptian bounds
    FACE = 1           # Chaldean decans
    DETRIMENT = -4     # Opposite of rulership
    FALL = -5          # Opposite of exaltation

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

# Ptolemaic Triplicity Rulers (Day/Night variations)
TRIPLICITY_RULERS: Dict[str, Dict[str, List[int]]] = {
    "fire": {  # Aries, Leo, Sagittarius
        "day": [SwePlanets.SUN, SwePlanets.JUPITER],
        "night": [SwePlanets.JUPITER, SwePlanets.SUN]
    },
    "earth": {  # Taurus, Virgo, Capricorn
        "day": [SwePlanets.VENUS, SwePlanets.MOON],
        "night": [SwePlanets.MOON, SwePlanets.VENUS]
    },
    "air": {  # Gemini, Libra, Aquarius
        "day": [SwePlanets.SATURN, SwePlanets.MERCURY],
        "night": [SwePlanets.MERCURY, SwePlanets.SATURN]
    },
    "water": {  # Cancer, Scorpio, Pisces
        "day": [SwePlanets.VENUS, SwePlanets.MARS],
        "night": [SwePlanets.MARS, SwePlanets.VENUS]
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
        TermRange(6.0, 12.0, SwePlanets.VENUS),
        TermRange(12.0, 20.0, SwePlanets.MERCURY),
        TermRange(20.0, 25.0, SwePlanets.MARS),
        TermRange(25.0, 30.0, SwePlanets.SATURN),
    ],
    # ... (abbreviated for space - full implementation would include all 12 signs)
}

# Chaldean Faces (Decans) - 10-degree segments
CHALDEAN_FACES: Dict[int, List[int]] = {
    1: [SwePlanets.MARS, SwePlanets.SUN, SwePlanets.VENUS],     # Aries
    2: [SwePlanets.MERCURY, SwePlanets.MOON, SwePlanets.SATURN], # Taurus
    # ... (abbreviated - full implementation would include all 12 signs)
}

class EssentialDignitiesCalculator:
    """Professional-grade essential dignities calculator."""
    
    def __init__(self, use_modern_rulers: bool = True):
        """Initialize dignities calculator with ruler system preference."""
        self.use_modern_rulers = use_modern_rulers
    
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
    
    def _calculate_rulership(self, planet_id: int, sign_number: int) -> int:
        """Calculate rulership/detriment score."""
        ruler_signs = TRADITIONAL_RULERS.get(planet_id, [])
        
        if sign_number in ruler_signs:
            return DignityType.RULERSHIP
        
        # Check for detriment (opposite sign of rulership)
        for ruler_sign in ruler_signs:
            opposite_sign = ((ruler_sign - 1 + 6) % 12) + 1
            if sign_number == opposite_sign:
                return DignityType.DETRIMENT
        
        return 0
    
    def _calculate_exaltation(self, planet_id: int, sign_number: int, sign_degree: float) -> int:
        """Calculate exaltation/fall score."""
        if planet_id not in EXALTATIONS:
            return 0
        
        exalt_sign, exalt_degree = EXALTATIONS[planet_id]
        
        if sign_number == exalt_sign:
            return DignityType.EXALTATION
        
        # Fall is opposite sign of exaltation
        fall_sign = ((exalt_sign - 1 + 6) % 12) + 1
        if sign_number == fall_sign:
            return DignityType.FALL
        
        return 0
    
    def _calculate_triplicity(self, planet_id: int, sign_number: int, is_day_chart: bool) -> int:
        """Calculate triplicity rulership score."""
        # Map sign to element
        element_map = {
            1: "fire", 5: "fire", 9: "fire",        # Aries, Leo, Sagittarius
            2: "earth", 6: "earth", 10: "earth",    # Taurus, Virgo, Capricorn
            3: "air", 7: "air", 11: "air",          # Gemini, Libra, Aquarius
            4: "water", 8: "water", 12: "water"     # Cancer, Scorpio, Pisces
        }
        
        element = element_map.get(sign_number)
        if not element:
            return 0
        
        rulers = TRIPLICITY_RULERS[element]
        day_night = "day" if is_day_chart else "night"
        
        if planet_id in rulers[day_night]:
            return DignityType.TRIPLICITY
        
        return 0
    
    def _calculate_term(self, planet_id: int, sign_number: int, sign_degree: float) -> int:
        """Calculate term/bounds score using binary search."""
        if sign_number not in EGYPTIAN_TERMS:
            return 0
        
        terms = EGYPTIAN_TERMS[sign_number]
        
        # Binary search for degree range
        for term_range in terms:
            if term_range.start_degree <= sign_degree < term_range.end_degree:
                if term_range.ruler_planet == planet_id:
                    return DignityType.TERM
                break
        
        return 0
    
    def _calculate_face(self, planet_id: int, sign_number: int, sign_degree: float) -> int:
        """Calculate face/decan score."""
        if sign_number not in CHALDEAN_FACES:
            return 0
        
        # Determine decan (0-10°, 10-20°, 20-30°)
        decan_index = int(sign_degree // 10)
        if decan_index > 2:
            decan_index = 2
        
        faces = CHALDEAN_FACES[sign_number]
        if faces[decan_index] == planet_id:
            return DignityType.FACE
        
        return 0
```

### Task 2: Integrate Dignities with Planet Response Model
**Dependency**: Task 1  
**Location**: `backend/app/api/models/schemas.py`

Add dignity information to PlanetResponse model:

```python
# File: backend/app/api/models/schemas.py
# Location: PlanetResponse class (around line 198-213)
# Pattern: Add dignity fields after existing fields

# ADD TO PlanetResponse class after existing fields:
class EssentialDignityInfo(BaseModel):
    """Essential dignity information for a planet."""
    
    total_score: int = Field(..., description="Total dignity score (William Lilly system)")
    rulership_score: int = Field(0, description="Rulership/detriment score (+5/-4)")
    exaltation_score: int = Field(0, description="Exaltation/fall score (+4/-5)")
    triplicity_score: int = Field(0, description="Triplicity score (+3)")
    term_score: int = Field(0, description="Term/bounds score (+2)")
    face_score: int = Field(0, description="Face/decan score (+1)")
    dignities_held: List[str] = Field(default_factory=list, description="List of dignities held")
    debilities_held: List[str] = Field(default_factory=list, description="List of debilities held")
    
    class Config:
        schema_extra = {
            "example": {
                "total_score": 7,
                "rulership_score": 5,
                "exaltation_score": 0,
                "triplicity_score": 3,
                "term_score": 0,
                "face_score": -1,
                "dignities_held": ["rulership", "triplicity"],
                "debilities_held": []
            }
        }

# MODIFY PlanetResponse class to include dignity information:
class PlanetResponse(BaseModel):
    # ... existing fields ...
    
    # ADD AFTER existing fields:
    essential_dignities: Optional[EssentialDignityInfo] = Field(
        None, 
        description="Essential dignity analysis (requires enhanced calculation)"
    )
```

### Task 3: Implement Dignity Calculation in Service Layer
**Dependency**: Task 2  
**Location**: `backend/app/services/ephemeris_service.py`

Integrate dignity calculations in planet response formatting:

```python
# File: backend/app/services/ephemeris_service.py
# Location: _format_planet_response method (around line 231-265)
# Pattern: Add dignity calculation after existing planet data extraction

# MODIFY _format_planet_response method to include dignities:
def _format_planet_response(
    self, 
    planet_id: int, 
    planet_data: Any, 
    planet_name: str,
    include_dignities: bool = False,
    is_day_chart: bool = True
) -> PlanetResponse:
    """Format planet data for API response with optional dignity analysis."""
    
    # ... existing planet data extraction ...
    
    # ADD dignity calculation if requested:
    essential_dignities = None
    if include_dignities:
        try:
            from app.core.ephemeris.tools.dignities import EssentialDignitiesCalculator
            
            calculator = EssentialDignitiesCalculator()
            dignity_info = calculator.calculate_dignities(
                planet_id=planet_id,
                longitude=longitude,
                is_day_chart=is_day_chart
            )
            
            essential_dignities = EssentialDignityInfo(
                total_score=dignity_info.total_score,
                rulership_score=dignity_info.rulership_score,
                exaltation_score=dignity_info.exaltation_score,
                triplicity_score=dignity_info.triplicity_score,
                term_score=dignity_info.term_score,
                face_score=dignity_info.face_score,
                dignities_held=dignity_info.dignities_held,
                debilities_held=dignity_info.debilities_held
            )
        except Exception as e:
            # Log error but don't fail planet response
            logger.warning(f"Dignity calculation failed for {planet_name}: {e}")
    
    return PlanetResponse(
        name=planet_name,
        longitude=longitude,
        # ... other existing fields ...
        essential_dignities=essential_dignities  # ADD THIS
    )

# MODIFY enhanced natal chart service to determine day/night chart:
async def calculate_natal_chart_enhanced(
    self, 
    request: NatalChartEnhancedRequest
) -> NatalChartEnhancedResponse:
    """Calculate enhanced natal chart with dignity analysis."""
    
    # ... existing chart calculation ...
    
    # Determine if day or night chart for dignity calculations
    is_day_chart = self._determine_day_night_chart(chart_data.angles, chart_data.planets)
    
    # Include dignities in planet formatting
    include_dignities = request.configuration.include_dignities
    
    # ... format planet responses with dignity parameter ...
    
def _determine_day_night_chart(self, angles: Any, planets: Dict) -> bool:
    """Determine if chart is diurnal (day) or nocturnal (night)."""
    try:
        sun_position = planets.get(SwePlanets.SUN)
        if not sun_position:
            return True  # Default to day chart
        
        # Traditional method: Sun in houses 7-12 = day chart
        sun_house = getattr(sun_position, 'house_position', {}).get('number', 1)
        return sun_house in [7, 8, 9, 10, 11, 12]
        
    except Exception:
        return True  # Default to day chart on error
```

### Task 4: Add Mutual Reception Detection
**Dependency**: Task 3  
**Location**: Extend dignities calculator

Add mutual reception analysis to dignity system:

```python
# File: backend/app/core/ephemeris/tools/dignities.py
# Location: Extend EssentialDignitiesCalculator class
# Purpose: Add mutual reception detection

class MutualReception(NamedTuple):
    """Mutual reception between two planets."""
    planet1_id: int
    planet2_id: int
    reception_type: str  # "rulership", "exaltation", "triplicity", "mixed"
    strength: int        # Combined dignity scores

class EssentialDignitiesCalculator:
    # ... existing methods ...
    
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
```

### Task 5: Performance Optimization and Caching
**Dependency**: Task 4  
**Location**: Optimize dignity calculations

Add performance optimizations meeting <10ms target:

```python
# File: backend/app/core/ephemeris/tools/dignities.py
# Location: Add caching and batch processing to calculator

from functools import lru_cache
from app.core.ephemeris.classes.cache import get_global_cache

class EssentialDignitiesCalculator:
    """Performance-optimized dignities calculator."""
    
    def __init__(self, use_modern_rulers: bool = True):
        self.use_modern_rulers = use_modern_rulers
        self._cache = get_global_cache()
        
        # Pre-compute lookup tables for performance
        self._ruler_lookup = self._build_ruler_lookup()
        self._exaltation_lookup = self._build_exaltation_lookup()
    
    def calculate_batch_dignities(
        self, 
        planets_data: Dict[int, Any],
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
            longitude = getattr(planet_data, 'longitude', 0.0)
            results[planet_id] = self.calculate_dignities(
                planet_id, longitude, is_day_chart
            )
        
        # Cache results (1-hour TTL)
        self._cache.put(cache_key, results, ttl=3600)
        return results
    
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
```

### Task 6: Comprehensive Testing Suite
**Dependency**: Task 5  
**Location**: `backend/tests/core/ephemeris/tools/test_dignities.py`

Create comprehensive test suite for dignity calculations:

```python
# File: backend/tests/core/ephemeris/tools/test_dignities.py (CREATE NEW)
# Purpose: Comprehensive testing for essential dignities system

"""
Essential Dignities System Test Suite
Validates dignity calculations against traditional sources and professional software.
"""

import pytest
from app.core.ephemeris.tools.dignities import (
    EssentialDignitiesCalculator, DignityType, DignityInfo
)
from app.core.ephemeris.const import SwePlanets

class TestEssentialDignities:
    """Test essential dignities calculations."""
    
    def setup_method(self):
        """Setup test calculator."""
        self.calculator = EssentialDignitiesCalculator()
    
    def test_sun_in_leo_rulership(self):
        """Test Sun in Leo shows rulership (+5 score)."""
        # Sun at 15° Leo (longitude 135°)
        dignity_info = self.calculator.calculate_dignities(
            planet_id=SwePlanets.SUN,
            longitude=135.0,  # 15° Leo
            is_day_chart=True
        )
        
        assert dignity_info.rulership_score == DignityType.RULERSHIP
        assert dignity_info.total_score >= 5
        assert "rulership" in dignity_info.dignities_held
        assert len(dignity_info.debilities_held) == 0
    
    def test_sun_in_aquarius_detriment(self):
        """Test Sun in Aquarius shows detriment (-4 score)."""
        # Sun at 15° Aquarius (longitude 315°)
        dignity_info = self.calculator.calculate_dignities(
            planet_id=SwePlanets.SUN,
            longitude=315.0,  # 15° Aquarius
            is_day_chart=True
        )
        
        assert dignity_info.rulership_score == DignityType.DETRIMENT
        assert dignity_info.total_score <= -4
        assert "detriment" in dignity_info.debilities_held
        assert "rulership" not in dignity_info.dignities_held
    
    def test_sun_exaltation_in_aries(self):
        """Test Sun exaltation at 19° Aries."""
        # Sun at 19° Aries (longitude 19°) - exact exaltation degree
        dignity_info = self.calculator.calculate_dignities(
            planet_id=SwePlanets.SUN,
            longitude=19.0,  # 19° Aries
            is_day_chart=True
        )
        
        assert dignity_info.exaltation_score == DignityType.EXALTATION
        assert "exaltation" in dignity_info.dignities_held
    
    def test_multiple_dignities_sun_in_aries(self):
        """Test Sun in Aries with multiple dignities (exaltation + triplicity)."""
        dignity_info = self.calculator.calculate_dignities(
            planet_id=SwePlanets.SUN,
            longitude=10.0,  # 10° Aries
            is_day_chart=True  # Sun rules fire triplicity by day
        )
        
        # Sun should have exaltation (4) + triplicity (3) = 7+
        assert dignity_info.exaltation_score == DignityType.EXALTATION
        assert dignity_info.triplicity_score == DignityType.TRIPLICITY
        assert dignity_info.total_score >= 7
        assert "exaltation" in dignity_info.dignities_held
        assert "triplicity" in dignity_info.dignities_held
    
    def test_day_night_triplicity_variation(self):
        """Test triplicity rulers change between day and night charts."""
        # Mars in Cancer (water sign)
        longitude = 105.0  # 15° Cancer
        
        # Day chart: Venus rules water triplicity by day
        day_dignity = self.calculator.calculate_dignities(
            SwePlanets.MARS, longitude, is_day_chart=True
        )
        
        # Night chart: Mars rules water triplicity by night  
        night_dignity = self.calculator.calculate_dignities(
            SwePlanets.MARS, longitude, is_day_chart=False
        )
        
        # Mars should have triplicity in night chart but not day chart
        assert day_dignity.triplicity_score == 0
        assert night_dignity.triplicity_score == DignityType.TRIPLICITY
    
    def test_performance_benchmark(self):
        """Test dignity calculation meets <10ms performance target."""
        import time
        
        # Test batch calculation performance
        planets_data = {
            SwePlanets.SUN: type('Planet', (), {'longitude': 135.0})(),
            SwePlanets.MOON: type('Planet', (), {'longitude': 45.0})(),
            SwePlanets.MERCURY: type('Planet', (), {'longitude': 90.0})(),
            SwePlanets.VENUS: type('Planet', (), {'longitude': 180.0})(),
            SwePlanets.MARS: type('Planet', (), {'longitude': 270.0})(),
        }
        
        start = time.perf_counter()
        results = self.calculator.calculate_batch_dignities(planets_data, True)
        end = time.perf_counter()
        
        duration_ms = (end - start) * 1000
        
        assert duration_ms < 10.0, f"Dignity calculation took {duration_ms:.2f}ms, exceeds 10ms target"
        assert len(results) == 5
        
    def test_mutual_reception_detection(self):
        """Test mutual reception detection between planets."""
        # Set up planets in mutual reception
        planets_dignities = {
            SwePlanets.SUN: self.calculator.calculate_dignities(SwePlanets.SUN, 135.0, True),  # Sun in Leo
            SwePlanets.MOON: self.calculator.calculate_dignities(SwePlanets.MOON, 105.0, True), # Moon in Cancer
        }
        
        receptions = self.calculator.find_mutual_receptions(planets_dignities)
        
        # Sun and Moon should be in mutual reception (both in own signs)
        assert len(receptions) == 1
        reception = receptions[0]
        assert reception.reception_type == "rulership"
        assert reception.strength >= 10  # Both have +5 rulership
```

---

## Validation Gates

### Essential Dignities Calculator Test
```bash
# Test dignity calculation accuracy and performance
cd backend && python -m pytest tests/core/ephemeris/tools/test_dignities.py -v
```

### API Integration Test
```bash
# Test dignities appear in enhanced planet responses
cd backend && python -m pytest tests/api/routes/test_ephemeris.py -k "dignities" -v
```

### Performance Validation
```bash
# Verify <10ms dignity calculation performance
cd backend && python -m pytest tests/performance/ -k "dignities" -v
```

### Professional Validation
```bash
# Test against known dignity cases from traditional sources
python scripts/validate_dignities_against_references.py
```

---

## Final Validation Checklist

- [ ] Complete dignity assignment tables for all traditional systems
- [ ] William Lilly dignity scoring system implemented (+5 to -5 scale)
- [ ] Day/night triplicity variations calculated correctly
- [ ] Egyptian terms and Chaldean faces integrated with binary search optimization
- [ ] Mutual reception detection for rulership, exaltation, and mixed types
- [ ] Performance meets <10ms target for complete dignity analysis
- [ ] API responses include comprehensive dignity information in enhanced mode
- [ ] Batch processing provides 5x+ performance improvement
- [ ] Caching system reduces repeated calculation overhead
- [ ] Professional validation against established astrological references

**Confidence Score**: 9/10 for one-pass implementation success

**Critical Dependencies**:
- Complete dignity tables and lookup optimization are foundation
- Integration with existing planet response model and service layer
- Performance optimization critical for maintaining sub-100ms API response times
- Professional validation ensures accuracy against traditional sources

**Implementation Time**: 8-12 hours (comprehensive system with extensive testing and validation)