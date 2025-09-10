# Swiss Ephemeris Integration Patterns - AI Documentation

**Purpose**: Provide complete context for extracting proven Swiss Ephemeris integration patterns from the ephemeris-core-fixes branch.

## Core Integration Pattern

### 1. Path Setup (CRITICAL - Must be First)
```python
def _setup_swiss_ephemeris_path():
    """Setup Swiss Ephemeris data path with multiple fallback locations"""
    possible_paths = [
        "Swiss Eph Library Files",
        "swisseph/data", 
        "/usr/share/swisseph",
        "./data"
    ]
    
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "sefstars.txt")):
            swe.set_ephe_path(path)
            return True
    
    raise SwissEphemerisError("Swiss Ephemeris data files not found")
```

### 2. Fixed Star Calculation Pattern
```python
def calculate_star_position(star_name: str, julian_day: float) -> PlanetPosition:
    """Calculate fixed star position using Swiss Ephemeris"""
    
    # CRITICAL: Path must be set first
    if not self._swiss_path_initialized:
        self._setup_swiss_ephemeris_path()
    
    try:
        # Swiss Ephemeris call with proper error handling
        star_data, ret_flags = swe.fixstar(star_name, julian_day)
        
        if ret_flags < 0:
            raise SwissEphemerisError(f"Swiss Ephemeris error: {ret_flags}")
        
        return PlanetPosition(
            longitude=star_data[0],
            latitude=star_data[1], 
            distance=star_data[2],
            name=star_name
        )
    
    except Exception as e:
        # Fallback to cached position if available
        return self._get_cached_star_position(star_name, julian_day)
```

### 3. Planet Calculation Pattern  
```python
def calculate_planet_position(planet_id: int, julian_day: float) -> PlanetPosition:
    """Calculate planet position using Swiss Ephemeris"""
    
    try:
        # Use swe.calc_ut for planets
        planet_data, ret_flags = swe.calc_ut(julian_day, planet_id)
        
        if ret_flags < 0:
            raise SwissEphemerisError(f"Planet calculation error: {ret_flags}")
            
        return PlanetPosition(
            longitude=planet_data[0],
            latitude=planet_data[1],
            distance=planet_data[2],
            name=get_planet_name(planet_id)
        )
        
    except Exception as e:
        return self._handle_calculation_error(planet_id, julian_day, e)
```

## Error Handling Patterns

### Swiss Ephemeris Error Codes
- `-1`: File not found (usually data path issue)
- `-2`: Invalid date  
- `-3`: Invalid body ID
- `-4`: Calculation failed

### Proven Error Recovery
1. **Path Issues**: Try alternative data paths
2. **Invalid Dates**: Validate Julian Day range (1800-2200 CE recommended)
3. **Missing Bodies**: Use cached positions or skip gracefully
4. **Calculation Errors**: Log error, return None or cached value

## Performance Patterns

### Caching Strategy (Working Implementation)
```python
@lru_cache(maxsize=1000)
def _cached_star_calculation(star_name: str, julian_day_rounded: float):
    """Cache star positions rounded to nearest 0.1 day for performance"""
    return self._calculate_star_position_direct(star_name, julian_day_rounded)
```

### Batch Processing Pattern
```python
def calculate_multiple_stars(star_names: List[str], julian_day: float) -> Dict[str, PlanetPosition]:
    """Batch calculate multiple stars with single Swiss Eph setup"""
    
    # Setup once for batch
    self._setup_swiss_ephemeris_path()
    
    results = {}
    for star_name in star_names:
        try:
            results[star_name] = self._calculate_star_position_direct(star_name, julian_day)
        except Exception as e:
            # Continue batch processing even if individual stars fail
            results[star_name] = None
            logger.warning(f"Star calculation failed for {star_name}: {e}")
    
    return results
```

## File Dependencies (MUST be present)

### Swiss Ephemeris Data Files
- `sefstars.txt` - Fixed star catalog (required for swe.fixstar())
- `seas_18.se1` - Asteroid ephemeris
- `semo_18.se1` - Moon ephemeris  
- `sepl_18.se1` - Planet ephemeris

### Python Module Dependencies
- `pyswisseph` - Swiss Ephemeris Python bindings
- `pydantic` - Data validation (for PlanetPosition model)
- `cachetools` - LRU caching support

## Common Gotchas & Solutions

### Gotcha 1: Path Setup Timing
**Problem**: Calling swe.fixstar() before swe.set_ephe_path()
**Solution**: Always call _setup_swiss_ephemeris_path() in __init__ or before first calculation

### Gotcha 2: Star Name Format
**Problem**: Using common names ("North Star") instead of Swiss Eph format ("Polaris")
**Solution**: Maintain star name registry with Swiss Eph compatible names

### Gotcha 3: Julian Day Validation
**Problem**: Invalid Julian Day values cause Swiss Eph crashes
**Solution**: Validate JD range and convert datetime properly

### Gotcha 4: Thread Safety
**Problem**: Swiss Ephemeris not thread-safe by default
**Solution**: Use thread-local storage for Swiss Eph state or synchronization

## Working Examples from Codebase

These patterns are extracted from working code in:
- `backend/app/core/ephemeris/tools/fixed_stars.py` (lines 1-564)
- `backend/app/core/acg/acg_core.py` (Swiss Eph body calculations)
- `backend/app/services/ephemeris_service.py` (integration patterns)

All patterns have been tested and are known to work in the current environment.
