# Implementation Patterns Guide

## 🏗️ Architectural Patterns to Preserve

### 1. Single Swiss Ephemeris Adapter Pattern
**Status**: EXTRACT AND PRESERVE

```python
# Pattern found in: backend/app/core/ephemeris/tools/ephemeris.py
class SwissEphemerisAdapter:
    def calculate_position(self, jd: float, body_id: int) -> PlanetPosition:
        # Direct swe.calc_ut() call with proper error handling
        # This pattern works - preserve it
```

### 2. Clean Dependency Injection Pattern  
**Status**: EXTRACT AND ENHANCE

```python
# Pattern found in ACG service integration
class ACGService:
    def __init__(self, ephemeris_service: EphemerisService):
        self.ephemeris = ephemeris_service  # Reuse calculations
        
    def calculate_acg_lines(self, natal_request):
        natal_chart = self.ephemeris.calculate_natal(natal_request)
        return self._transform_to_acg_lines(natal_chart)
```

### 3. Geographic Coordinate Transformation
**Status**: EXTRACT - HIGH VALUE

Mathematical formulas for coordinate system transformations found in ACG core.
Preserve these exact calculations.

## 🚫 Anti-Patterns to Avoid

### 1. Multiple Redundant Calculator Classes
**Problem**: Found 5+ different planet calculation implementations
**Solution**: Consolidate to single Swiss Ephemeris adapter

### 2. Massive Response Objects
**Problem**: 9MB+ JSON responses with excessive metadata  
**Solution**: Implement selective field inclusion

### 3. Complex Inheritance Hierarchies
**Problem**: Deep inheritance causing maintenance issues
**Solution**: Prefer composition over inheritance

## 🎯 Performance Patterns to Preserve

### Caching Strategies
- **get_acg_cache_manager** (backend/app/core/acg/acg_cache.py) - Caching pattern: get_acg_cache_manager
- **generate_cache_key** (backend/app/core/acg/acg_cache.py) - Caching pattern: generate_cache_key
- **get_cached_result** (backend/app/core/acg/acg_cache.py) - Caching pattern: get_cached_result
- **set_cached_result** (backend/app/core/acg/acg_cache.py) - Caching pattern: set_cached_result
- **get_cached_body_positions** (backend/app/core/acg/acg_cache.py) - Caching pattern: get_cached_body_positions
- **set_cached_body_positions** (backend/app/core/acg/acg_cache.py) - Caching pattern: set_cached_body_positions
- **generate_position_cache_key** (backend/app/core/acg/acg_cache.py) - Caching pattern: generate_position_cache_key
- **warm_cache_for_common_requests** (backend/app/core/acg/acg_cache.py) - Caching pattern: warm_cache_for_common_requests
- **get_cache_statistics** (backend/app/core/acg/acg_cache.py) - Caching pattern: get_cache_statistics
- **clear_cache** (backend/app/core/acg/acg_cache.py) - Caching pattern: clear_cache


### Error Handling Patterns
- **get_planet** (backend/app/core/ephemeris/tools/ephemeris.py) - Swiss Ephemeris integration: get_planet
- **get_houses** (backend/app/core/ephemeris/tools/ephemeris.py) - Swiss Ephemeris integration: get_houses
- **get_fixed_star** (backend/app/core/ephemeris/tools/ephemeris.py) - Swiss Ephemeris integration: get_fixed_star
- **generate_cache_key** (backend/app/core/acg/acg_cache.py) - Caching pattern: generate_cache_key
- **get_cached_result** (backend/app/core/acg/acg_cache.py) - Caching pattern: get_cached_result
- **set_cached_result** (backend/app/core/acg/acg_cache.py) - Caching pattern: set_cached_result
- **get_cached_body_positions** (backend/app/core/acg/acg_cache.py) - Caching pattern: get_cached_body_positions
- **set_cached_body_positions** (backend/app/core/acg/acg_cache.py) - Caching pattern: set_cached_body_positions
- **warm_cache_for_common_requests** (backend/app/core/acg/acg_cache.py) - Caching pattern: warm_cache_for_common_requests
- **get_cache_statistics** (backend/app/core/acg/acg_cache.py) - Caching pattern: get_cache_statistics


## 📐 Mathematical Formula Patterns

### ACG Line Calculations
*None found*

### Coordinate Transformations
- **normalize_geojson_coordinates** (backend/app/core/acg/acg_utils.py) - ACG utility function: normalize_geojson_coordinates


---
*Use these patterns in lean rebuild implementation*
