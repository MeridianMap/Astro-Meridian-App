# PRP-EPHEMERIS-002: Nomenclature Consistency Fix

## Goal
Replace generic "Object X" and "Planet X" references throughout the Meridian ephemeris system with proper IAU-compliant astronomical names for all major celestial objects.

### Feature Goal
Update the incomplete PLANET_NAMES dictionary and fix hardcoded naming inconsistencies to ensure all celestial objects display professional astronomical names (Ceres, Pallas, Juno, Vesta, Chiron, Pholus) instead of generic fallback names.

### Deliverable
Complete nomenclature consistency across all API responses, aspect calculations, and internal references with IAU-compliant naming for asteroids, centaurs, and lunar nodes.

### Success Definition
- No "Object X" or "Planet X" references in any API responses
- All major asteroids (Ceres, Pallas, Juno, Vesta) properly named
- All centaurs (Chiron, Pholus) properly named
- Consistent naming across aspects and planetary calculations
- Test coverage >95% for nomenclature validation
- Professional appearance matching established astrological software

---

## Context

### YAML Structure Reference
```yaml
# Critical nomenclature issues from deep research
current_problems:
  incomplete_planet_names:
    location: "backend/app/core/ephemeris/const.py:152-169"
    issue: "PLANET_NAMES dictionary missing IDs 16-20"
    fallback_function: "get_planet_name() lines 267-269 returns generic names"
    
  authentic_sample_issues:
    object_17: "Should be 'Ceres' (1 Ceres - first asteroid, dwarf planet)"
    object_18: "Should be 'Pallas' (2 Pallas - second asteroid)"
    object_19: "Should be 'Juno' (3 Juno - third asteroid)"  
    object_20: "Should be 'Vesta' (4 Vesta - fourth asteroid)"
    object_16: "Should be 'Pholus' (5145 Pholus - centaur)"

  aspect_inconsistencies:
    location: "backend/app/core/ephemeris/tools/aspects.py:377"
    issue: "Hardcoded planet mapping conflicts with PLANET_NAMES"
    examples: ["Planet 10", "Planet 12", inconsistent "True Node"]

# Swiss Ephemeris ID mappings (verified)
se_object_ids:
  CHIRON: 15        # (2060) Chiron - centaur
  PHOLUS: 16        # (5145) Pholus - centaur  
  CERES: 17         # (1) Ceres - dwarf planet
  PALLAS: 18        # (2) Pallas - asteroid
  JUNO: 19          # (3) Juno - asteroid
  VESTA: 20         # (4) Vesta - asteroid

# IAU official designations
iau_nomenclature:
  ceres: "(1) Ceres - First asteroid discovered (1801), reclassified as dwarf planet (2006)"
  pallas: "(2) Pallas - Second asteroid discovered (1802), named after Pallas Athena"
  juno: "(3) Juno - Third asteroid discovered (1804), named after Roman goddess"
  vesta: "(4) Vesta - Fourth asteroid discovered (1807), named after Roman goddess"
  chiron: "(2060) Chiron - Centaur discovered (1977), dual comet/asteroid nature"
  pholus: "(5145) Pholus - Second centaur discovered (1992), mythological brother of Chiron"

# Professional symbols (Unicode)
astronomical_symbols:
  ceres: "⚳"        # Official Ceres symbol
  pallas: "⚴"       # Official Pallas symbol
  juno: "⚵"         # Official Juno symbol
  vesta: "⚶"        # Official Vesta symbol
  chiron: "⚷"       # Chiron symbol
  pholus: "⚷"       # Centaur symbol (shared with Chiron)
```

### External Resources
- **IAU Minor Planet Names**: https://www.iau.org/public/themes/naming/#minorplanets
- **Swiss Ephemeris Object IDs**: https://www.astro.com/swisseph/swephdoc.htm#_Toc152740777
- **Astronomical Symbol Reference**: https://en.wikipedia.org/wiki/Astronomical_symbols
- **Asteroid Database**: https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/
- **Centaur Classification**: https://en.wikipedia.org/wiki/Centaur_(small_Solar_System_body)

---

## Implementation Tasks

### Task 1: Update PLANET_NAMES Dictionary with Missing Objects
**Dependency**: None  
**Location**: `backend/app/core/ephemeris/const.py`

Replace the incomplete PLANET_NAMES dictionary with comprehensive mapping:

```python
# File: backend/app/core/ephemeris/const.py
# Location: Lines 152-169 (replace entire dictionary)
# Pattern: Follow existing structure, add missing objects 16-20

PLANET_NAMES: Dict[int, str] = {
    SwePlanets.SUN: 'Sun',                          # 0
    SwePlanets.MOON: 'Moon',                        # 1
    SwePlanets.MERCURY: 'Mercury',                  # 2
    SwePlanets.VENUS: 'Venus',                      # 3
    SwePlanets.MARS: 'Mars',                        # 4
    SwePlanets.JUPITER: 'Jupiter',                  # 5
    SwePlanets.SATURN: 'Saturn',                    # 6
    SwePlanets.URANUS: 'Uranus',                    # 7
    SwePlanets.NEPTUNE: 'Neptune',                  # 8
    SwePlanets.PLUTO: 'Pluto',                      # 9
    SwePlanets.MEAN_NODE: 'North Node (Mean)',      # 10
    SwePlanets.TRUE_NODE: 'North Node (True)',      # 11
    SwePlanets.MEAN_APOG: 'Lilith (Mean)',         # 12
    SwePlanets.OSCULATING_APOG: 'Lilith (True)',   # 13
    SwePlanets.EARTH: 'Earth',                      # 14
    SwePlanets.CHIRON: 'Chiron',                    # 15
    # ADD MISSING OBJECTS (this fixes the "Object X" issue):
    16: 'Pholus',                                   # (5145) Pholus - centaur
    17: 'Ceres',                                    # (1) Ceres - dwarf planet
    18: 'Pallas',                                   # (2) Pallas - asteroid
    19: 'Juno',                                     # (3) Juno - asteroid
    20: 'Vesta',                                    # (4) Vesta - asteroid
}
```

**Critical Note**: This single change eliminates all "Object 17", "Object 18", etc. from API responses.

### Task 2: Add Professional Astronomical Symbols
**Dependency**: Task 1  
**Location**: `backend/app/core/ephemeris/const.py`

Extend PLANET_SYMBOLS dictionary to include missing objects:

```python
# File: backend/app/core/ephemeris/const.py
# Location: Lines 188-189 (after existing PLANET_SYMBOLS entries)
# Pattern: Follow existing symbol format with Unicode symbols

# ADD MISSING SYMBOLS after line 189:
    16: '⚷',  # Pholus (centaur symbol)
    17: '⚳',  # Ceres (official symbol)
    18: '⚴',  # Pallas (official symbol)
    19: '⚵',  # Juno (official symbol)
    20: '⚶',  # Vesta (official symbol)
```

### Task 3: Fix Hardcoded Aspect Naming Inconsistency
**Dependency**: Task 1  
**Location**: `backend/app/core/ephemeris/tools/aspects.py`

Remove hardcoded planet name mapping that conflicts with PLANET_NAMES:

```python
# File: backend/app/core/ephemeris/tools/aspects.py
# Location: Around line 377 (find hardcoded mapping)
# Problem: Hardcoded mapping that returns "Planet X" instead of using PLANET_NAMES

# REPLACE hardcoded mapping with consistent approach:
def _get_consistent_planet_name(self, planet_id: int) -> str:
    """Get planet name using consistent PLANET_NAMES system."""
    from ..const import get_planet_name
    return get_planet_name(planet_id)

# UPDATE all aspect calculation references to use this method
# REPLACE: PLANET_NAMES.get(planet_id, f"Planet_{planet_id}")
# WITH: self._get_consistent_planet_name(planet_id)
```

**Key Change**: Eliminates "Planet 10", "Planet 12" inconsistencies in aspect calculations.

### Task 4: Create Nomenclature Validation System
**Dependency**: Task 2  
**Location**: `backend/scripts/validate_nomenclature.py` (new file)

Create comprehensive validation to prevent future generic naming:

```python
# File: backend/scripts/validate_nomenclature.py (CREATE NEW FILE)
# Purpose: Validate all nomenclature is professional and consistent

"""
Meridian Ephemeris Nomenclature Validation Script
Ensures all celestial objects have proper astronomical names.
"""

from app.core.ephemeris.const import PLANET_NAMES, get_planet_name

def validate_nomenclature() -> dict:
    """
    Comprehensive nomenclature validation.
    
    Returns:
        dict: Validation results with any issues found
    """
    issues = []
    major_objects = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    
    # Check for generic naming
    for obj_id in major_objects:
        name = get_planet_name(obj_id)
        if name.startswith('Planet ') or name.startswith('Object '):
            issues.append(f"Generic name for ID {obj_id}: {name}")
    
    # Check required objects are mapped
    required_objects = {
        15: 'Chiron',
        16: 'Pholus', 
        17: 'Ceres',
        18: 'Pallas',
        19: 'Juno',
        20: 'Vesta'
    }
    
    for obj_id, expected_name in required_objects.items():
        actual_name = get_planet_name(obj_id)
        if actual_name != expected_name:
            issues.append(f"ID {obj_id}: expected '{expected_name}', got '{actual_name}'")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'total_objects_checked': len(major_objects)
    }

def main():
    """Run validation and report results."""
    results = validate_nomenclature()
    
    if results['valid']:
        print("✓ All nomenclature validated successfully")
        print(f"✓ Checked {results['total_objects_checked']} objects")
    else:
        print("❌ NOMENCLATURE ISSUES FOUND:")
        for issue in results['issues']:
            print(f"  - {issue}")
        print(f"\nTotal issues: {len(results['issues'])}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

### Task 5: Add Comprehensive Nomenclature Tests
**Dependency**: Task 3  
**Location**: `backend/tests/core/ephemeris/test_const.py`

Add comprehensive tests to prevent nomenclature regression:

```python
# File: backend/tests/core/ephemeris/test_const.py
# Location: Add to existing TestPlanetNames class
# Pattern: Follow existing test structure with assert statements

def test_major_asteroids_have_proper_names(self):
    """Test that major asteroids have proper IAU names, not generic ones."""
    asteroid_mappings = {
        17: 'Ceres',    # (1) Ceres - first asteroid
        18: 'Pallas',   # (2) Pallas - second asteroid
        19: 'Juno',     # (3) Juno - third asteroid
        20: 'Vesta',    # (4) Vesta - fourth asteroid
    }
    
    for asteroid_id, expected_name in asteroid_mappings.items():
        actual_name = get_planet_name(asteroid_id)
        assert actual_name == expected_name, f"Asteroid {asteroid_id}: expected '{expected_name}', got '{actual_name}'"
        assert asteroid_id in PLANET_NAMES, f"Asteroid {asteroid_id} not in PLANET_NAMES dictionary"

def test_centaurs_have_proper_names(self):
    """Test that centaurs have proper names, not generic ones."""
    centaur_mappings = {
        15: 'Chiron',   # (2060) Chiron
        16: 'Pholus',   # (5145) Pholus
    }
    
    for centaur_id, expected_name in centaur_mappings.items():
        actual_name = get_planet_name(centaur_id)
        assert actual_name == expected_name, f"Centaur {centaur_id}: expected '{expected_name}', got '{actual_name}'"

def test_no_generic_names_for_known_objects(self):
    """Test that no known objects return generic 'Object X' or 'Planet X' names."""
    known_object_ids = list(PLANET_NAMES.keys())
    
    for obj_id in known_object_ids:
        name = get_planet_name(obj_id)
        assert not name.startswith('Object '), f"Generic 'Object' name for ID {obj_id}: {name}"
        assert not name.startswith('Planet '), f"Generic 'Planet' name for ID {obj_id}: {name}"

def test_symbols_exist_for_all_named_objects(self):
    """Test that all named objects have corresponding symbols."""
    from app.core.ephemeris.const import PLANET_SYMBOLS
    
    for obj_id in PLANET_NAMES.keys():
        assert obj_id in PLANET_SYMBOLS, f"Missing symbol for object ID {obj_id} ({PLANET_NAMES[obj_id]})"

def test_api_response_nomenclature_consistency(self):
    """Integration test: verify API responses use proper names."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # Use test case known to include asteroids
    response = client.post("/api/v1/ephemeris/natal", json={
        "subject": {
            "name": "Nomenclature Test",
            "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
            "coordinates": {"latitude": 40.7128, "longitude": -74.0060}
        },
        "configuration": {"include_asteroids": True}
    })
    
    assert response.status_code == 200
    planets = response.json()["planets"]
    
    # Verify no generic names in API response
    for planet_name, planet_data in planets.items():
        assert not planet_name.startswith("Object "), f"Generic name in API: {planet_name}"
        assert not planet_name.startswith("Planet "), f"Generic name in API: {planet_name}"
    
    # Verify specific proper names present
    expected_names = ["Ceres", "Pallas", "Juno", "Vesta", "Chiron", "Pholus"]
    for expected_name in expected_names:
        if expected_name in planets:  # May not all be included depending on configuration
            assert planets[expected_name]["name"] == expected_name
```

### Task 6: Update API Response Validation
**Dependency**: Task 4  
**Location**: Integration with existing API tests

Add nomenclature validation to existing API tests:

```python
# File: backend/tests/api/routes/test_ephemeris.py
# Location: Add to existing test methods
# Pattern: Add nomenclature assertions to existing natal chart tests

# ADD to existing test_natal_chart_calculation method:
def validate_nomenclature_in_response(self, response_data):
    """Helper method to validate nomenclature in API responses."""
    planets = response_data.get("planets", {})
    
    for planet_name, planet_data in planets.items():
        # Ensure no generic names
        assert not planet_name.startswith("Object "), f"Generic 'Object' name: {planet_name}"
        assert not planet_name.startswith("Planet "), f"Generic 'Planet' name: {planet_name}"
        
        # Verify name field matches key
        if "name" in planet_data:
            assert planet_data["name"] == planet_name, f"Name mismatch: key='{planet_name}', name='{planet_data['name']}'"
    
    # Validate aspects nomenclature
    aspects = response_data.get("aspects", [])
    for aspect in aspects:
        for obj_key in ["object1", "object2"]:
            if obj_key in aspect:
                obj_name = aspect[obj_key]
                assert not obj_name.startswith("Object "), f"Generic name in aspects: {obj_name}"
                assert not obj_name.startswith("Planet "), f"Generic name in aspects: {obj_name}"
```

---

## Validation Gates

### Core Nomenclature Validation
```bash
# Run comprehensive nomenclature validation
cd backend && python scripts/validate_nomenclature.py
```

### Unit Tests Validation
```bash
# Test PLANET_NAMES dictionary completeness
cd backend && python -m pytest tests/core/ephemeris/test_const.py::TestPlanetNames -v
```

### API Response Validation
```bash
# Verify no generic names in API responses
cd backend && python -m pytest tests/api/routes/test_ephemeris.py -k "nomenclature" -v
```

### Integration Validation
```bash
# Full test suite to catch nomenclature regressions
cd backend && python -m pytest tests/ -k "planet" -v
```

---

## Final Validation Checklist

- [ ] PLANET_NAMES dictionary includes all objects 0-20 with proper names
- [ ] PLANET_SYMBOLS dictionary includes all objects 0-20 with Unicode symbols
- [ ] No "Object X" references in any API responses  
- [ ] No "Planet X" references in aspect calculations
- [ ] All major asteroids show proper names: Ceres, Pallas, Juno, Vesta
- [ ] All centaurs show proper names: Chiron, Pholus
- [ ] Aspect calculations use consistent naming system
- [ ] Nomenclature validation script passes all checks
- [ ] Comprehensive test coverage for all nomenclature scenarios
- [ ] API responses maintain professional appearance
- [ ] Backward compatibility maintained for existing proper names

**Confidence Score**: 10/10 for one-pass implementation success

**Critical Dependencies**:
- PLANET_NAMES dictionary update is the primary fix (eliminates 90% of issues)
- Aspect calculation consistency prevents remaining generic references
- Test coverage ensures no regression of nomenclature quality

**Implementation Time**: 2-3 hours (straightforward dictionary updates and test additions)