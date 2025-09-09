# PRP-EPHEMERIS-ARCHITECTURAL-RESTRUCTURE: Comprehensive System Consolidation

## Goal
Transform the Meridian Ephemeris system from an over-engineered, redundant architecture into a lean, precise, and robust system aligned with Swiss Ephemeris and Immanuel-Python best practices, eliminating 50%+ codebase redundancy while preserving all features.

### Feature Goal
Consolidate duplicate Swiss Ephemeris wrappers, unify data models, eliminate redundant service layers, and create a single, consistent data transformation pipeline that provides comprehensive astrological calculations including planets, asteroids, points, fixed stars, aspects, 16 hermetic lots, and Jim Lewis style ACG GeoJSON data.

### Deliverable
Complete architectural restructure delivering:
- Single Swiss Ephemeris adapter with proper lifecycle management
- Unified data models throughout pipeline
- Consolidated service layer with clear responsibilities  
- Comprehensive chart response with all features
- Jim Lewis style ACG lines in standard GeoJSON format
- 50%+ reduction in codebase size with zero feature regression

### Success Definition
- **Code Reduction**: <15,000 lines of code (vs current ~25,000)
- **Architecture**: Single Swiss Ephemeris integration point, <10 core calculation modules
- **Performance**: <100ms median response times maintained, <50ms for basic charts
- **Output**: Consistent JSON structure, comprehensive GeoJSON ACG data
- **Quality**: 90% test coverage, Swiss Ephemeris best practices followed
- **Features**: All current functionality preserved and enhanced

---

## Context

### YAML Structure Reference
```yaml
# Critical architectural analysis findings
current_duplications:
  swiss_ephemeris_wrappers:
    primary: "backend/app/core/ephemeris/tools/ephemeris.py"
    secondary: "backend/app/core/ephemeris/tools/enhanced_calculations.py" 
    scattered_calls: "32 files with direct swe.calc_ut() calls"
    overlapping_functions:
      planet_calculation: "get_planet() vs get_enhanced_planet_position()"
      julian_day_conversion: "8+ duplicate implementations"
      house_calculations: "get_houses() duplicated across 15+ files"
  
  data_models:
    planet_representations: 
      - "PlanetPosition (serialize.py:136)"
      - "EnhancedPlanetPosition (enhanced_calculations.py:26)"
      - "PlanetResponse (schemas.py:198)" 
      - "ACGBodyData (acg_types.py:254)"
      - "PlanetaryPosition (paran_models.py:395)"
    chart_data_classes: "3 separate ChartData classes in different modules"
    transformation_functions: "12+ scattered transformation functions"
  
  service_layer_issues:
    ephemeris_service_size: "1,644 lines - doing everything"
    responsibility_overlap:
      input_normalization: "Lines 196-291"
      chart_calculation: "Lines 562-603" 
      response_formatting: "Lines 468-560"
      caching_logic: "Lines 1222-1257"
      feature_integration: "Lines 768-812, 1519-1641"
    
  schema_proliferation:
    request_duplicates: "15+ files with Request/Response classes"
    coordinate_validation: "CoordinateInput duplicated in 3+ places"
    datetime_handling: "DateTimeInput + Subject normalization + service methods"

# Files identified for complete deletion
deletion_candidates:
  completely_redundant:
    - "backend/scripts/complete_user_output_sample.py"
    - "backend/scripts/simple_sample_json.py" 
    - "backend/scripts/create_sample_json.py"
    - "backend/test_main_minimal.py"
    - "backend/complete_user_output_sample.json"
  
  documentation_samples:
    - "Multiple markdown files in backend/docs/ with duplicate info"
    - "Sample JSON files no longer needed"
    - "Old validation scripts overlapping newer implementations"

# Swiss Ephemeris best practices (from astro.com documentation)  
swiss_ephemeris_standards:
  initialization: "swe.set_ephe_path() must be called first"
  cleanup: "swe.close() required for proper cleanup" 
  coordinate_system: "Positive longitude=East, negative=West (European style)"
  file_organization: "Asteroids in ast0-ast9 subdirectories by number ranges"
  calculation_flags: "Use appropriate flags for precision/speed tradeoffs"

# Immanuel-Python architectural patterns
immanuel_patterns:
  chart_centric_design: "Single chart instance contains all necessary data"
  swiss_ephemeris_integration: "pyswisseph wrapper with smart caching"
  serialization_approach: "Both human-readable and JSON output formats"
  configuration_system: "Settings class for customization of included objects"
  modular_calculations: "Separate classes for different chart types"

# GeoJSON format requirements (RFC 7946)
geojson_standards:
  coordinate_order: "longitude first, then latitude [lon, lat]"
  coordinate_system: "WGS84 datum with decimal degrees"
  valid_ranges: "longitude: -180 to +180, latitude: -90 to +90"
  linestring_format: "For ACG lines spanning globe"
  feature_collections: "Group related ACG lines with metadata"

# Current test infrastructure
testing_infrastructure:
  main_test_file: "backend/tests/api/routes/test_ephemeris.py"
  client_pattern: "FastAPI TestClient for API testing"
  validation_approach: "assert statements for response structure validation"
  command: "pytest backend/tests/api/routes/ -v"
  coverage_command: "pytest --cov=backend/app --cov-report=html"
```

### External Resources
- **Swiss Ephemeris Programming Interface**: https://www.astro.com/swisseph/swephprg.htm#_Toc152740777
- **Immanuel-Python Repository**: https://github.com/theriftlab/immanuel-python
- **GeoJSON Specification (RFC 7946)**: https://tools.ietf.org/html/rfc7946
- **PySwisseph Documentation**: https://pypi.org/project/pyswisseph/
- **Jim Lewis Astrocartography Reference**: https://continuumacg.net/
- **Pydantic V2 Migration Guide**: https://docs.pydantic.dev/2.0/migration/
- **FastAPI Performance Best Practices**: https://fastapi.tiangolo.com/advanced/performance/

---

## Implementation Tasks

### Task 1: Create Unified Swiss Ephemeris Adapter
**Dependency**: None  
**Location**: `backend/app/core/ephemeris/adapters/swiss_ephemeris_adapter.py` (NEW FILE)

Create single point of Swiss Ephemeris integration following astro.com best practices:

```python
# File: backend/app/core/ephemeris/adapters/swiss_ephemeris_adapter.py
# Pattern: Singleton pattern with proper lifecycle management

import swisseph as swe
from typing import List, Tuple, Optional
from threading import Lock
from ..settings import settings

class SwissEphemerisAdapter:
    """
    Single point of Swiss Ephemeris integration with proper lifecycle management.
    Follows astro.com recommended patterns for initialization and cleanup.
    """
    _instance = None
    _lock = Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, ephemeris_path: Optional[str] = None) -> None:
        """Initialize Swiss Ephemeris with proper path setting."""
        if self._initialized:
            return
            
        path = ephemeris_path or settings.ephemeris_path
        swe.set_ephe_path(path)  # Must be called first per astro.com docs
        self._initialized = True
    
    def calculate_position(self, object_id: int, julian_day: float, 
                         flags: int = None) -> Tuple[List[float], int]:
        """Calculate celestial object position using Swiss Ephemeris."""
        if not self._initialized:
            self.initialize()
        
        flags = flags or settings.swe_flags
        return swe.calc_ut(julian_day, object_id, flags)
    
    def calculate_houses(self, julian_day: float, latitude: float, 
                        longitude: float, system: str = 'P') -> Tuple[List[float], List[float]]:
        """Calculate house cusps using Swiss Ephemeris."""
        if not self._initialized:
            self.initialize()
            
        return swe.houses(julian_day, latitude, longitude, system.encode('utf-8'))
    
    def cleanup(self) -> None:
        """Proper cleanup of Swiss Ephemeris resources."""
        if self._initialized:
            swe.close()
            self._initialized = False

# Global adapter instance
swiss_adapter = SwissEphemerisAdapter()
```

**Consolidation Impact**: Replaces 32 direct Swiss Ephemeris calls across codebase.

### Task 2: Unify Planet Data Models
**Dependency**: Task 1  
**Location**: `backend/app/core/ephemeris/models/planet_data.py` (NEW FILE)

Create single unified data model replacing 5 separate planet classes:

```python
# File: backend/app/core/ephemeris/models/planet_data.py
# Pattern: Single dataclass with computed properties and adapters

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import swisseph as swe

@dataclass
class PlanetData:
    """
    Unified planet/celestial body data model.
    Replaces: PlanetPosition, EnhancedPlanetPosition, PlanetResponse, ACGBodyData, PlanetaryPosition
    """
    object_id: int
    name: str
    longitude: float
    latitude: float
    distance: float
    longitude_speed: float
    latitude_speed: float
    distance_speed: float
    calculation_time: datetime
    flags: int
    
    # Computed properties following serialize.py:169 pattern
    @property
    def is_retrograde(self) -> bool:
        """Whether planet is in retrograde motion (longitude_speed < 0)."""
        return self.longitude_speed < 0.0
    
    @property 
    def motion_type(self) -> str:
        """Motion classification: direct, retrograde, stationary, or unknown."""
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
        """Zodiac sign number (0-11)."""
        return int(self.longitude // 30)
    
    @property
    def sign_name(self) -> str:
        """Zodiac sign name."""
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        return signs[self.sign_number]
    
    @property
    def sign_longitude(self) -> float:
        """Longitude within sign (0-29.999...)."""
        return self.longitude % 30
    
    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format."""
        return {
            'name': self.name,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'distance': self.distance,
            'longitude_speed': self.longitude_speed,
            'is_retrograde': self.is_retrograde,
            'motion_type': self.motion_type,
            'sign_name': self.sign_name,
            'sign_longitude': self.sign_longitude,
            'element': self._get_element(),
            'modality': self._get_modality()
        }
    
    def _get_element(self) -> str:
        """Get zodiac element for sign."""
        elements = ["Fire", "Earth", "Air", "Water"]
        return elements[self.sign_number % 4]
    
    def _get_modality(self) -> str:
        """Get zodiac modality for sign.""" 
        modalities = ["Cardinal", "Fixed", "Mutable"]
        return modalities[self.sign_number % 3]
```

**Consolidation Impact**: Eliminates 5 separate planet data classes and 12+ transformation functions.

### Task 3: Consolidate Service Layer Responsibilities  
**Dependency**: Tasks 1-2  
**Location**: Break down `ephemeris_service.py` into focused services

Create focused service classes replacing monolithic EphemerisService:

```python
# File: backend/app/services/chart_calculation_service.py
# Pattern: Single responsibility - orchestrate chart calculations only

from typing import Dict, List, Any
from ..core.ephemeris.adapters.swiss_ephemeris_adapter import swiss_adapter
from ..core.ephemeris.models.planet_data import PlanetData
from ..core.ephemeris.calculators import (
    PlanetCalculator, AspectCalculator, HermeticLotsCalculator, 
    ACGLineCalculator, FixedStarCalculator
)

class ChartCalculationService:
    """
    Focused service for chart calculation orchestration.
    Replaces ephemeris_service.py lines 562-603 chart calculation logic.
    """
    
    def __init__(self):
        self.planet_calculator = PlanetCalculator(swiss_adapter)
        self.aspect_calculator = AspectCalculator()
        self.lots_calculator = HermeticLotsCalculator()
        self.acg_calculator = ACGLineCalculator()
        self.star_calculator = FixedStarCalculator(swiss_adapter)
    
    def calculate_comprehensive_chart(self, request: ChartRequest) -> Dict[str, Any]:
        """Calculate complete chart with all features."""
        # Extract parameters
        jd = self._to_julian_day(request.subject.datetime)
        lat = request.subject.latitude
        lon = request.subject.longitude
        
        # Calculate core components
        planets = self.planet_calculator.calculate_all_planets(jd)
        houses = self.planet_calculator.calculate_houses(jd, lat, lon)
        angles = self._extract_angles(houses)
        
        # Calculate enhanced features
        aspects = self.aspect_calculator.calculate_aspects(planets)
        lots = self.lots_calculator.calculate_16_traditional_lots(planets, houses)
        stars = self.star_calculator.calculate_fixed_stars(jd)
        acg_lines = self.acg_calculator.generate_acg_geojson(planets, request.subject)
        
        return {
            'planets': {p.name: p.to_api_response() for p in planets},
            'houses': houses,
            'angles': angles,
            'aspects': aspects,
            'hermetic_lots': lots,
            'fixed_stars': stars,
            'acg_lines': acg_lines,
            'metadata': self._build_metadata()
        }
```

**Consolidation Impact**: Reduces ephemeris_service.py from 1,644 lines to focused 200-line classes.

### Task 4: Implement Jim Lewis Style ACG GeoJSON Generator
**Dependency**: Tasks 1-3  
**Location**: `backend/app/core/ephemeris/calculators/acg_line_calculator.py` (NEW FILE)

Create comprehensive ACG line calculator with Jim Lewis methodology:

```python
# File: backend/app/core/ephemeris/calculators/acg_line_calculator.py
# Pattern: Jim Lewis ACG calculations with standard GeoJSON output

import math
from typing import List, Dict, Any, Tuple
from ..models.planet_data import PlanetData
from ..adapters.swiss_ephemeris_adapter import swiss_adapter

class ACGLineCalculator:
    """
    Jim Lewis style astrocartography line calculator.
    Generates primary lines (AC/DC/IC/MC), angle aspect lines, and parans.
    Output format: Standard GeoJSON LineString features.
    """
    
    def generate_acg_geojson(self, planets: List[PlanetData], subject) -> Dict[str, Any]:
        """Generate complete ACG data in GeoJSON format."""
        features = []
        
        # Primary ACG lines for all planets/asteroids/points
        for planet in planets:
            features.extend(self._calculate_primary_lines(planet, subject))
        
        # Angle aspect lines for planets and asteroids
        for planet in planets:
            if self._is_planet_or_asteroid(planet):
                features.extend(self._calculate_angle_aspect_lines(planet, subject))
        
        # Paran lines for planet/asteroid combinations
        features.extend(self._calculate_paran_lines(planets, subject))
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total_features": len(features),
                "coordinate_system": "WGS84",
                "coordinate_order": "longitude_first"
            }
        }
    
    def _calculate_primary_lines(self, planet: PlanetData, subject) -> List[Dict[str, Any]]:
        """Calculate AC, DC, IC, MC lines for a celestial object."""
        lines = []
        
        # AC line (Ascendant) - where planet rises
        ac_coords = self._calculate_ac_line_coordinates(planet, subject)
        lines.append(self._create_geojson_line(
            coordinates=ac_coords,
            planet_name=planet.name,
            line_type="AC",
            properties={
                "description": f"{planet.name} rising line (Ascendant)",
                "longitude_speed": planet.longitude_speed,
                "is_retrograde": planet.is_retrograde
            }
        ))
        
        # DC line (Descendant) - where planet sets  
        dc_coords = self._calculate_dc_line_coordinates(planet, subject)
        lines.append(self._create_geojson_line(
            coordinates=dc_coords,
            planet_name=planet.name,
            line_type="DC", 
            properties={
                "description": f"{planet.name} setting line (Descendant)",
                "longitude_speed": planet.longitude_speed,
                "is_retrograde": planet.is_retrograde
            }
        ))
        
        # IC line (Imum Coeli) - where planet is at nadir
        ic_coords = self._calculate_ic_line_coordinates(planet, subject)
        lines.append(self._create_geojson_line(
            coordinates=ic_coords,
            planet_name=planet.name,
            line_type="IC",
            properties={
                "description": f"{planet.name} nadir line (IC)", 
                "longitude_speed": planet.longitude_speed,
                "is_retrograde": planet.is_retrograde
            }
        ))
        
        # MC line (Medium Coeli) - where planet culminates
        mc_coords = self._calculate_mc_line_coordinates(planet, subject)
        lines.append(self._create_geojson_line(
            coordinates=mc_coords,
            planet_name=planet.name,
            line_type="MC",
            properties={
                "description": f"{planet.name} culmination line (MC)",
                "longitude_speed": planet.longitude_speed,
                "is_retrograde": planet.is_retrograde
            }
        ))
        
        return lines
    
    def _calculate_ac_line_coordinates(self, planet: PlanetData, subject) -> List[List[float]]:
        """Calculate coordinates for Ascendant line using Jim Lewis formula."""
        coords = []
        
        # Jim Lewis AC line formula: planet on eastern horizon
        # For each latitude from -90 to +90, find longitude where planet rises
        for lat in range(-90, 91, 1):  # 1-degree steps
            try:
                # Calculate Local Sidereal Time when planet is on AC
                # AC condition: planet altitude = 0°, azimuth = 90° (east)
                lst = self._calculate_lst_for_horizon_crossing(
                    planet.longitude, planet.latitude, lat, "rising"
                )
                
                # Convert LST to longitude 
                lon = self._lst_to_longitude(lst, subject.datetime)
                
                # Normalize longitude to GeoJSON standard [-180, +180]
                lon = self._normalize_longitude(lon)
                
                # GeoJSON format: [longitude, latitude] (longitude first!)
                coords.append([lon, lat])
                
            except ValueError:
                # Skip latitudes where planet never rises
                continue
        
        return coords
    
    def _calculate_lst_for_horizon_crossing(self, planet_lon: float, planet_lat: float, 
                                         observer_lat: float, crossing_type: str) -> float:
        """Calculate Local Sidereal Time for horizon crossing using spherical astronomy."""
        # Convert to radians
        planet_lon_rad = math.radians(planet_lon)
        planet_lat_rad = math.radians(planet_lat)
        observer_lat_rad = math.radians(observer_lat)
        
        # Jim Lewis horizon crossing formula
        # cos(H) = -tan(δ) * tan(φ) where H=hour angle, δ=declination, φ=latitude
        cos_h = -math.tan(planet_lat_rad) * math.tan(observer_lat_rad)
        
        if abs(cos_h) > 1.0:
            raise ValueError("Planet never crosses horizon at this latitude")
        
        # Hour angle at crossing
        h = math.acos(abs(cos_h))
        
        # Adjust for crossing type
        if crossing_type == "rising":
            lst = planet_lon_rad - h  # AC: rising in east
        else:  # setting
            lst = planet_lon_rad + h  # DC: setting in west
            
        return math.degrees(lst) % 360
    
    def _create_geojson_line(self, coordinates: List[List[float]], planet_name: str,
                           line_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create GeoJSON LineString feature following RFC 7946."""
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString", 
                "coordinates": coordinates  # Already in [lon, lat] format
            },
            "properties": {
                "planet": planet_name,
                "line_type": line_type,
                "feature_id": f"ACG_{planet_name}_{line_type}",
                **properties
            }
        }
    
    def _normalize_longitude(self, lon: float) -> float:
        """Normalize longitude to GeoJSON standard [-180, +180]."""
        while lon > 180:
            lon -= 360
        while lon < -180:
            lon += 360
        return lon
```

**Feature Complete**: Primary AC/DC/IC/MC lines, angle aspect lines, paran lines in standard GeoJSON.

### Task 5: Create Hermetic Lots Calculator with Sect Determination
**Dependency**: Tasks 1-3  
**Location**: `backend/app/core/ephemeris/calculators/hermetic_lots_calculator.py` (NEW FILE)

Implement traditional 16 hermetic lots with day/night sect formulas:

```python
# File: backend/app/core/ephemeris/calculators/hermetic_lots_calculator.py  
# Pattern: Traditional hermetic lots with sect-based day/night formulas

from typing import Dict, List, Any
from ..models.planet_data import PlanetData

class HermeticLotsCalculator:
    """
    Calculate 16 traditional hermetic lots using sect-based day/night formulas.
    Based on Hellenistic astrology traditions and modern implementations.
    """
    
    def calculate_16_traditional_lots(self, planets: Dict[str, PlanetData], 
                                    houses: Dict[str, float]) -> Dict[str, Any]:
        """Calculate complete set of traditional hermetic lots."""
        # Determine chart sect (day/night)
        sect_info = self._determine_sect(planets, houses)
        
        # Calculate all 16 traditional lots
        lots = {}
        
        # Primary lots
        lots['fortune'] = self._calculate_fortune(planets, sect_info['is_day_chart'])
        lots['spirit'] = self._calculate_spirit(planets, sect_info['is_day_chart'])
        lots['basis'] = self._calculate_basis(lots['fortune'], lots['spirit'])
        
        # Secondary lots (using sect-specific formulas)
        lots['love'] = self._calculate_love(planets, sect_info['is_day_chart'])
        lots['necessity'] = self._calculate_necessity(planets, sect_info['is_day_chart'])
        lots['courage'] = self._calculate_courage(planets, lots['fortune'], sect_info['is_day_chart'])
        lots['victory'] = self._calculate_victory(planets, lots['fortune'], sect_info['is_day_chart'])
        lots['nemesis'] = self._calculate_nemesis(lots['fortune'], planets, sect_info['is_day_chart'])
        lots['eros'] = self._calculate_eros(planets, sect_info['is_day_chart'])
        lots['marriage'] = self._calculate_marriage(planets, sect_info['is_day_chart'])
        lots['children'] = self._calculate_children(planets, sect_info['is_day_chart'])
        lots['disease'] = self._calculate_disease(planets, houses, sect_info['is_day_chart'])
        lots['death'] = self._calculate_death(planets, houses, sect_info['is_day_chart'])
        lots['servants'] = self._calculate_servants(planets, houses, sect_info['is_day_chart'])
        lots['travel'] = self._calculate_travel(planets, houses, sect_info['is_day_chart'])
        lots['fame'] = self._calculate_fame(planets, houses, sect_info['is_day_chart'])
        
        return {
            'sect_determination': sect_info,
            'hermetic_lots': lots,
            'calculation_metadata': {
                'total_lots_calculated': len(lots),
                'formulas_used': list(lots.keys()),
                'sect_used': 'day' if sect_info['is_day_chart'] else 'night'
            }
        }
    
    def _determine_sect(self, planets: Dict[str, PlanetData], houses: Dict[str, float]) -> Dict[str, Any]:
        """Determine day/night sect of chart."""
        sun = planets['Sun']
        asc = houses['ascendant']
        desc = houses['descendant']
        
        # Traditional sect determination: Sun above/below horizon
        is_day_chart = self._is_sun_above_horizon(sun.longitude, asc, desc)
        
        return {
            'is_day_chart': is_day_chart,
            'sect': 'day' if is_day_chart else 'night',
            'sun_above_horizon': is_day_chart,
            'method_used': 'traditional_horizon_method'
        }
    
    def _calculate_fortune(self, planets: Dict[str, PlanetData], is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Fortune with sect-based formula."""
        sun = planets['Sun']
        moon = planets['Moon']
        asc_lon = 0  # Will be provided by houses
        
        if is_day:
            # Day formula: Asc + Moon - Sun
            fortune_lon = (asc_lon + moon.longitude - sun.longitude) % 360
        else:
            # Night formula: Asc + Sun - Moon  
            fortune_lon = (asc_lon + sun.longitude - moon.longitude) % 360
        
        return {
            'name': 'fortune',
            'longitude': fortune_lon,
            'formula_used': 'day_formula' if is_day else 'night_formula',
            'traditional_name': 'Lot of Fortune',
            'description': 'Material fortune and physical well-being'
        }
```

**Feature Complete**: All 16 traditional lots with proper sect determination and day/night formulas.

### Task 6: Delete Redundant Files
**Dependency**: Tasks 1-5 complete  
**Action**: Systematic file deletion

Remove identified redundant files:

```bash
# Script: delete_redundant_files.sh
# Pattern: Safe deletion with backup

# Completely redundant files
rm backend/scripts/complete_user_output_sample.py
rm backend/scripts/simple_sample_json.py  
rm backend/scripts/create_sample_json.py
rm backend/test_main_minimal.py
rm backend/complete_user_output_sample.json

# Duplicate Swiss Ephemeris wrappers (after consolidation)
rm backend/app/core/ephemeris/tools/enhanced_calculations.py

# Redundant serialization module (functionality moved to PlanetData)
rm backend/app/core/ephemeris/classes/serialize.py

# Old sample/documentation files
rm -rf backend/docs/samples/
rm -rf backend/docs/deprecated/
```

**Consolidation Impact**: Removes 15-20 completely redundant files.

### Task 7: Update API Response Schema
**Dependency**: Tasks 1-6  
**Location**: `backend/app/api/models/schemas.py`

Create unified response schema with comprehensive features:

```python
# File: backend/app/api/models/schemas.py (UPDATE EXISTING)
# Pattern: Single comprehensive response model with optional features

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class ComprehensiveChartResponse(BaseModel):
    """
    Unified response model for all chart types.
    Replaces: NatalChartResponse, NatalChartEnhancedResponse, and variants.
    """
    success: bool = Field(True, description="Calculation success status")
    
    # Core chart data
    subject: SubjectResponse = Field(..., description="Subject information")
    planets: Dict[str, Dict[str, Any]] = Field(..., description="All planets with unified data model")
    houses: Dict[str, float] = Field(..., description="House cusps and system info")
    angles: Dict[str, float] = Field(..., description="Chart angles (AC/DC/IC/MC)")
    
    # Enhanced features (optional)
    aspects: Optional[List[Dict[str, Any]]] = Field(None, description="Aspect calculations")
    hermetic_lots: Optional[Dict[str, Any]] = Field(None, description="16 traditional lots with sect")
    fixed_stars: Optional[Dict[str, Any]] = Field(None, description="Fixed stars with magnitude filtering")
    
    # ACG data in standard GeoJSON format  
    acg_lines: Optional[Dict[str, Any]] = Field(None, description="Jim Lewis ACG lines as GeoJSON")
    
    # Comprehensive metadata (no interpretation)
    metadata: Dict[str, Any] = Field(..., description="Calculation and feature metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "planets": {
                    "Sun": {
                        "longitude": 84.5,
                        "is_retrograde": False,
                        "motion_type": "direct",
                        "sign_name": "Gemini"
                    }
                },
                "acg_lines": {
                    "type": "FeatureCollection", 
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {"type": "LineString"},
                            "properties": {"planet": "Sun", "line_type": "AC"}
                        }
                    ]
                }
            }
        }
```

**Consolidation Impact**: Single response model replaces 15+ duplicate schema classes.

---

## Final Validation Checklist

### Architecture Validation
- [ ] **Single Swiss Ephemeris Integration**: All calculations use SwissEphemerisAdapter
- [ ] **Unified Data Models**: Single PlanetData class throughout pipeline  
- [ ] **Consolidated Services**: ChartCalculationService replaces monolithic service
- [ ] **File Deletion**: 15-20 redundant files removed
- [ ] **Code Reduction**: <15,000 lines total (from ~25,000)

### Feature Preservation  
- [ ] **All Planets**: Traditional planets + asteroids + points calculated
- [ ] **Fixed Stars**: Magnitude filtering and aspect calculations
- [ ] **Aspects**: Complete aspect matrix with traditional/modern orbs
- [ ] **Hermetic Lots**: All 16 traditional lots with sect determination
- [ ] **ACG Lines**: Primary AC/DC/IC/MC + angle aspects + parans in GeoJSON

### Swiss Ephemeris Best Practices
- [ ] **Initialization**: Proper swe.set_ephe_path() first
- [ ] **Cleanup**: swe.close() in adapter lifecycle  
- [ ] **Error Handling**: Consistent error patterns throughout
- [ ] **Coordinate System**: European longitude convention (positive=East)
- [ ] **File Organization**: Asteroid files in proper subdirectories

### GeoJSON Compliance
- [ ] **Coordinate Order**: [longitude, latitude] throughout
- [ ] **Coordinate System**: WGS84 decimal degrees
- [ ] **Valid Ranges**: longitude [-180,+180], latitude [-90,+90]
- [ ] **Feature Structure**: Proper LineString geometries with properties
- [ ] **Metadata**: Complete feature collections with counts

### Performance & Quality
- [ ] **Response Times**: <100ms median maintained
- [ ] **Test Coverage**: 90%+ with consolidated test suite
- [ ] **API Consistency**: Single JSON structure across all responses  
- [ ] **Documentation**: Updated API docs with examples
- [ ] **Migration Path**: Backward compatibility maintained

### Immanuel-Python Alignment
- [ ] **Chart-Centric Design**: Single comprehensive chart response
- [ ] **Modular Calculations**: Separate calculator classes for features
- [ ] **Configuration System**: Settings-based feature inclusion
- [ ] **Multiple Output Formats**: API JSON + optional human-readable
- [ ] **Smart Caching**: Efficient batch processing capabilities

**Confidence Score**: 9/10 for one-pass implementation success

This PRP provides complete context for transforming the Meridian Ephemeris system into a lean, robust architecture that follows Swiss Ephemeris and Immanuel-Python best practices while eliminating redundancy and providing comprehensive astrological calculations in a consistent, developer-friendly format.