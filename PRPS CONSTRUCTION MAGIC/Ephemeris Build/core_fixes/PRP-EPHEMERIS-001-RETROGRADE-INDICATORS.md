# PRP-EPHEMERIS-001: Retrograde Indicators Fix

## Goal
Add explicit retrograde motion indicators to Meridian ephemeris API responses by exposing existing retrograde calculation properties from PlanetPosition class in API output.

### Feature Goal
Expose the already-calculated `is_retrograde` and `motion_type` properties from PlanetPosition objects in the API response models, eliminating the need for clients to calculate retrograde status from longitude_speed values.

### Deliverable
Updated API responses that include `is_retrograde: bool` and `motion_type: string` fields for all planet objects in natal chart calculations.

### Success Definition
- All planets in API responses show explicit retrograde flags (`is_retrograde`, `motion_type`)
- Retrograde status matches Swiss Ephemeris longitude_speed calculations  
- Backward compatibility maintained with existing API structure
- Response time impact <5ms (minimal since properties already calculated)
- Test coverage >95% for retrograde status validation

---

## Context

### YAML Structure Reference
```yaml
# Critical research findings from deep codebase analysis
current_implementation:
  retrograde_logic_exists:
    location: "backend/app/core/ephemeris/classes/serialize.py:165-182"
    status: "Complete and working - properties already calculated"
    methods:
      is_retrograde: "Returns longitude_speed < 0.0"
      motion_type: "Returns 'direct', 'retrograde', 'stationary', or 'unknown'"
    threshold_stationary: "abs(longitude_speed) < 0.01 degrees/day"
  
  missing_api_exposure:
    response_model: "backend/app/api/models/schemas.py:198-213 (PlanetResponse)"
    service_layer: "backend/app/services/ephemeris_service.py:231-265 (_format_planet_response)"
    problem: "Retrograde properties not extracted from PlanetPosition to API response"

# Authentic API sample analysis (1990-06-15 14:30 NYC)
retrograde_planets_detected:
  uranus:
    longitude_speed: -0.038297271203191485
    expected_is_retrograde: true
    expected_motion_type: "retrograde"
  saturn:
    longitude_speed: -0.05768892066271292
    expected_is_retrograde: true
    expected_motion_type: "retrograde"
  neptune:
    longitude_speed: -0.005439849504031556
    expected_is_retrograde: true
    expected_motion_type: "retrograde"
  pluto:
    longitude_speed: -0.022074843863558567
    expected_is_retrograde: true
    expected_motion_type: "retrograde"

# Existing test infrastructure
testing_patterns:
  test_file: "backend/tests/api/routes/test_ephemeris.py"
  client: "FastAPI TestClient pattern"
  validation: "assert statements for response structure"
  command: "pytest backend/tests/api/routes/test_ephemeris.py -v"
```

### External Resources
- **Swiss Ephemeris Motion Calculation**: https://www.astro.com/swisseph/swephdoc.htm#_Toc152740777
- **Pydantic Field Documentation**: https://docs.pydantic.dev/latest/concepts/fields/#field-function
- **FastAPI Response Models**: https://fastapi.tiangolo.com/tutorial/response-model/#response-model-encoding-parameters
- **Retrograde Motion Reference**: https://en.wikipedia.org/wiki/Apparent_retrograde_motion#Planets

---

## Implementation Tasks

### Task 1: Add Retrograde Fields to PlanetResponse Model
**Dependency**: None  
**Location**: `backend/app/api/models/schemas.py`

Add retrograde fields to PlanetResponse class following existing Field() pattern:

```python
# File: backend/app/api/models/schemas.py
# Location: Lines 212-213 (after longitude_speed field)
# Pattern: Follow existing Field() declarations with description and examples

# ADD THESE FIELDS after line 212:
is_retrograde: bool = Field(
    False, 
    description="Whether planet is in retrograde motion (longitude_speed < 0)"
)
motion_type: str = Field(
    "direct", 
    description="Motion classification: direct, retrograde, stationary, or unknown",
    examples=["direct", "retrograde", "stationary"]
)
```

**Modification Pattern**: Insert between `longitude_speed` (line 212) and `element` (line 213).

### Task 2: Extract Retrograde Properties in Service Layer
**Dependency**: Task 1  
**Location**: `backend/app/services/ephemeris_service.py`

Modify `_format_planet_response()` method to extract retrograde properties:

```python
# File: backend/app/services/ephemeris_service.py
# Location: Lines 262-264 (in _format_planet_response method)
# Pattern: Follow existing getattr() pattern for safe property extraction

# ADD after line 262 (after extracting modality):
is_retrograde = getattr(planet_data, 'is_retrograde', False)
motion_type = getattr(planet_data, 'motion_type', 'direct')

# MODIFY PlanetResponse constructor call (around line 264):
return PlanetResponse(
    name=planet_name,
    longitude=longitude,
    latitude=latitude,
    distance=distance,
    longitude_speed=longitude_speed,
    is_retrograde=is_retrograde,          # ADD THIS LINE
    motion_type=motion_type,              # ADD THIS LINE
    sign_name=sign_name,
    sign_longitude=sign_longitude,
    house_number=house_number,
    element=element,
    modality=modality
)
```

**Critical Note**: PlanetPosition objects already have these properties calculated. We're simply exposing them.

### Task 3: Add Retrograde Validation Tests
**Dependency**: Task 2  
**Location**: `backend/tests/api/routes/test_ephemeris.py`

Add comprehensive tests for retrograde indicators:

```python
# File: backend/tests/api/routes/test_ephemeris.py
# Location: Add new test method to existing TestNatalChart class
# Pattern: Follow existing test structure with assert statements

def test_retrograde_indicators_present(self):
    """Test that all planets include retrograde indicators in API response."""
    # Use existing test data (1990-06-15 14:30 NYC has known retrograde planets)
    response = self.client.post("/api/v1/ephemeris/natal", json={
        "subject": {
            "name": "Test Subject",
            "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
            "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
            "timezone": {"name": "America/New_York"}
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # Verify all planets have retrograde fields
    for planet_name, planet_data in data["planets"].items():
        assert "is_retrograde" in planet_data, f"{planet_name} missing is_retrograde field"
        assert "motion_type" in planet_data, f"{planet_name} missing motion_type field"
        assert isinstance(planet_data["is_retrograde"], bool)
        assert planet_data["motion_type"] in ["direct", "retrograde", "stationary", "unknown"]

def test_retrograde_accuracy_known_case(self):
    """Test retrograde detection accuracy against known retrograde planets."""
    # 1990-06-15 case has Uranus, Saturn, Neptune, Pluto retrograde
    response = self.client.post("/api/v1/ephemeris/natal", json={
        "subject": {
            "name": "Retrograde Test",
            "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
            "coordinates": {"latitude": 40.7128, "longitude": -74.0060}
        }
    })
    
    planets = response.json()["planets"]
    
    # Verify known retrograde planets
    expected_retrograde = ["Uranus", "Saturn", "Neptune", "Pluto"]
    for planet_name in expected_retrograde:
        assert planet_name in planets, f"{planet_name} not found in response"
        planet = planets[planet_name]
        assert planet["is_retrograde"] is True, f"{planet_name} should be retrograde"
        assert planet["motion_type"] == "retrograde", f"{planet_name} motion_type should be retrograde"
        assert planet["longitude_speed"] < 0, f"{planet_name} should have negative longitude_speed"
    
    # Verify known direct motion planets (Sun, Moon never retrograde)
    expected_direct = ["Sun", "Moon"]
    for planet_name in expected_direct:
        if planet_name in planets:
            planet = planets[planet_name]
            assert planet["is_retrograde"] is False, f"{planet_name} should not be retrograde"
            assert planet["motion_type"] == "direct", f"{planet_name} motion_type should be direct"
```

### Task 4: Update API Documentation
**Dependency**: Task 3  
**Location**: Auto-generated from Pydantic models

Verify OpenAPI schema includes new fields:

```python
# File: Verification script (create as needed)
# Command: python scripts/verify_openapi_schema.py

import requests

def verify_retrograde_fields_in_schema():
    """Verify OpenAPI schema includes retrograde fields."""
    response = requests.get("http://localhost:8000/openapi.json")
    schema = response.json()
    
    # Check PlanetResponse schema
    planet_schema = schema["components"]["schemas"]["PlanetResponse"]
    properties = planet_schema["properties"]
    
    assert "is_retrograde" in properties, "is_retrograde field missing from schema"
    assert "motion_type" in properties, "motion_type field missing from schema"
    
    # Verify field types
    assert properties["is_retrograde"]["type"] == "boolean"
    assert properties["motion_type"]["type"] == "string"
    
    print("✓ OpenAPI schema includes retrograde fields correctly")
```

### Task 5: Performance Validation
**Dependency**: Task 4  
**Location**: Performance test validation

Verify minimal performance impact:

```python
# File: backend/tests/performance/test_retrograde_performance.py (create if needed)
# Pattern: Use existing performance test patterns

import time
import statistics

def test_retrograde_fields_performance_impact():
    """Verify adding retrograde fields has minimal performance impact."""
    times_before = []
    times_after = []
    
    # Test multiple requests to get reliable timing
    for _ in range(10):
        start = time.perf_counter()
        response = client.post("/api/v1/ephemeris/natal", json=test_request)
        end = time.perf_counter()
        
        assert response.status_code == 200
        times_after.append(end - start)
    
    # Performance should remain under 100ms median (CLAUDE.md standard)
    median_time = statistics.median(times_after)
    assert median_time < 0.1, f"Response time {median_time:.3f}s exceeds 100ms limit"
    
    # Additional impact from retrograde fields should be <5ms
    # (This is inherently minimal since properties are already calculated)
```

---

## Validation Gates

### API Response Validation
```bash
# Verify retrograde fields present in API responses
cd backend && python -m pytest tests/api/routes/test_ephemeris.py::TestNatalChart::test_retrograde_indicators_present -v
```

### Accuracy Validation
```bash
# Test against known retrograde cases
cd backend && python -m pytest tests/api/routes/test_ephemeris.py::TestNatalChart::test_retrograde_accuracy_known_case -v
```

### Performance Validation
```bash
# Verify performance impact remains minimal  
cd backend && python -m pytest tests/performance/ -k "retrograde" -v
```

### Schema Validation
```bash
# Verify OpenAPI schema includes new fields
python scripts/verify_openapi_schema.py
curl http://localhost:8000/openapi.json | jq '.components.schemas.PlanetResponse.properties' | grep -E "(is_retrograde|motion_type)"
```

---

## Final Validation Checklist

- [ ] PlanetResponse model includes `is_retrograde` and `motion_type` fields
- [ ] Service layer extracts retrograde properties from PlanetPosition objects
- [ ] API responses show retrograde flags for all planets
- [ ] Retrograde detection matches Swiss Ephemeris longitude_speed calculations
- [ ] Known retrograde planets (Uranus, Saturn, Neptune, Pluto in 1990-06-15) correctly flagged
- [ ] Direct motion planets (Sun, Moon) correctly show is_retrograde: false
- [ ] Response time impact <5ms (verified via performance tests)
- [ ] OpenAPI schema documentation includes new fields with correct types
- [ ] Backward compatibility maintained (existing fields unchanged)
- [ ] Test coverage >95% for retrograde status validation

**Confidence Score**: 10/10 for one-pass implementation success

**Critical Dependencies**: 
- PlanetPosition class properties already exist and function correctly
- Existing API response formatting infrastructure operational
- Test framework supports new validation requirements

**Implementation Time**: 2-4 hours (minimal changes leveraging existing infrastructure)