# Meridian Ephemeris Core Engine Documentation

## 🎯 Overview

The Meridian Ephemeris Core Engine is the heart of the astrological calculation system, providing high-performance, accurate astronomical calculations using the Swiss Ephemeris as the gold standard.

### Architecture
```
Core Engine Structure:
├── tools/           # Calculation utilities
├── charts/          # Chart construction logic  
├── classes/         # Core data structures
├── const.py         # Constants and enumerations
└── settings.py      # Configuration management
```

## 🏗️ Module Structure

### `/tools` - Calculation Utilities

#### `ephemeris.py` - Swiss Ephemeris Interface
**Primary interface to Swiss Ephemeris calculations**

```python
from app.core.ephemeris.tools.ephemeris import get_planet, julian_day_from_datetime

# Calculate planetary position
jd = julian_day_from_datetime(datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc))
sun_position = get_planet(SwePlanets.SUN, jd)

# Result: PlanetPosition object with longitude, latitude, distance, speed
print(f"Sun at {sun_position.longitude:.2f}° longitude")
```

**Key Functions:**
- `get_planet(planet_id, julian_day)` - Calculate single planet position
- `julian_day_from_datetime(dt)` - Convert datetime to Julian day
- `validate_ephemeris_files()` - Check Swiss Ephemeris file availability

#### `position.py` - House & Angle Calculations
**Calculate house systems and chart angles**

```python
from app.core.ephemeris.tools.position import calculate_houses

houses = calculate_houses(
    julian_day=2451545.0,
    latitude=40.7128,
    longitude=-74.0060,
    house_system="placidus"
)

print(f"Ascendant: {houses.angles['ascendant']:.2f}°")
print(f"House cusps: {houses.cusps}")
```

**Supported House Systems:**
- `placidus` - Placidus (default)
- `koch` - Koch  
- `equal` - Equal House
- `whole_sign` - Whole Sign
- `campanus` - Campanus
- `regiomontanus` - Regiomontanus
- `porphyrius` - Porphyrius
- `alcabitus` - Alcabitus

#### `convert.py` - Format Conversion Utilities
**Convert between coordinate and time formats**

```python
from app.core.ephemeris.tools.convert import (
    dms_to_decimal, decimal_to_dms, coordinates_to_decimal
)

# Convert DMS string to decimal
lat_decimal = dms_to_decimal("40°42'46\"N")  # Returns 40.7128

# Convert decimal to DMS components  
dms = decimal_to_dms(40.7128, "latitude")   # Returns (40, 42, 46, "N")

# Handle multiple coordinate formats
coords = coordinates_to_decimal({
    "latitude": {"dms_string": "40°42'46\"N"},
    "longitude": {"decimal": -74.0060}
})
```

#### `date.py` - Date/Time Utilities
**Handle various datetime formats and timezone conversions**

```python
from app.core.ephemeris.tools.date import parse_datetime_input, to_datetime

# Parse flexible datetime inputs
dt = parse_datetime_input({"iso_string": "1990-06-15T14:30:00"})
dt = parse_datetime_input({"julian_day": 2448079.1041666665})
dt = parse_datetime_input({
    "year": 1990, "month": 6, "day": 15, 
    "hour": 14, "minute": 30, "second": 0
})

# Convert to UTC datetime with timezone handling
utc_dt = to_datetime(dt, timezone_info={"name": "America/New_York"})
```

#### `batch.py` - High-Performance Batch Processing
**Vectorized calculations for multiple subjects**

```python
from app.core.ephemeris.tools.batch import BatchCalculator, BatchRequest

# Create batch requests
requests = [
    BatchRequest(
        name="Subject 1",
        datetime=datetime(2000, 1, 1, tzinfo=timezone.utc),
        latitude=40.7128,
        longitude=-74.0060
    ),
    # ... more subjects
]

# Process batch (10x+ faster than individual calculations)
calculator = BatchCalculator()
results = calculator.calculate_batch_positions(requests)

# Results contain success/error status and calculated data
for result in results:
    if result.success:
        print(f"✅ {result.name}: {result.data['planets']['sun']['longitude']:.2f}°")
    else:
        print(f"❌ {result.name}: {result.error}")
```

### `/charts` - Chart Construction

#### `natal.py` - Natal Chart Logic
**Main natal chart calculation orchestrator**

```python
from app.core.ephemeris.charts.natal import calculate_natal_chart

chart = calculate_natal_chart(
    subject_data={
        "name": "John Doe",
        "datetime": {"iso_string": "1990-06-15T14:30:00"},
        "latitude": {"decimal": 40.7128},
        "longitude": {"decimal": -74.0060},
        "timezone": {"name": "America/New_York"}
    },
    settings={
        "house_system": "placidus",
        "include_aspects": True
    }
)

# Returns complete NatalChart object
print(chart.subject.name)
print(chart.planets["sun"].longitude)
print(chart.houses.angles["ascendant"])
```

#### `subject.py` - Subject Data Processing
**Validate and process birth data**

```python
from app.core.ephemeris.charts.subject import ChartSubject

subject = ChartSubject(
    name="John Doe",
    datetime_input={"iso_string": "1990-06-15T14:30:00"},
    latitude_input={"decimal": 40.7128},
    longitude_input={"decimal": -74.0060},
    timezone_input={"name": "America/New_York"}
)

# Automatically parses, validates, and normalizes all inputs
print(f"Normalized datetime: {subject.datetime}")
print(f"Coordinates: {subject.latitude}, {subject.longitude}")
```

### `/classes` - Core Data Structures

#### `serialize.py` - Data Models
**Pydantic models for type safety and serialization**

```python
from app.core.ephemeris.classes.serialize import (
    PlanetPosition, HouseSystem, NatalChart, ChartSubject
)

# Type-safe planetary position
planet = PlanetPosition(
    longitude=24.123,
    latitude=0.0002, 
    distance=1.0145,
    longitude_speed=0.9583,
    retrograde=False
)

# Complete chart structure
chart = NatalChart(
    subject=subject,
    planets={"sun": planet},
    houses=house_system,
    metadata={"processing_time_ms": 45.2}
)
```

**Key Models:**
- `ChartSubject` - Birth data with validation
- `PlanetPosition` - Complete planetary position data
- `HouseSystem` - House cusps and angles
- `NatalChart` - Complete chart structure
- `CalculationSettings` - Chart calculation options

#### `cache.py` - Memory Caching System
**High-performance in-memory caching with LRU eviction**

```python
from app.core.ephemeris.classes.cache import get_global_cache

cache = get_global_cache()

# Cache calculation results
cache_key = f"natal_{subject_hash}_{settings_hash}"
cached_result = cache.get(cache_key)

if cached_result is None:
    result = perform_calculation()
    cache.put(cache_key, result, ttl=3600)  # 1 hour TTL
else:
    result = cached_result  # 10-100x faster
```

**Cache Features:**
- **LRU Eviction**: Automatic cleanup of old entries
- **TTL Support**: Time-based expiration
- **Thread-Safe**: Safe for concurrent access
- **Memory Efficient**: Configurable size limits
- **Hit Rate Tracking**: Performance monitoring

### `/const.py` - Constants & Enumerations

**Swiss Ephemeris constants and astrological definitions**

```python
from app.core.ephemeris.const import SwePlanets, SweObjects, get_planet_name

# Planet IDs for Swiss Ephemeris
sun_id = SwePlanets.SUN        # 0
moon_id = SwePlanets.MOON      # 1
mercury_id = SwePlanets.MERCURY # 2

# Get human-readable names
planet_name = get_planet_name(SwePlanets.SUN)  # "Sun"

# All supported celestial objects
all_planets = [
    SwePlanets.SUN, SwePlanets.MOON, SwePlanets.MERCURY,
    SwePlanets.VENUS, SwePlanets.MARS, SwePlanets.JUPITER, 
    SwePlanets.SATURN, SwePlanets.URANUS, SwePlanets.NEPTUNE,
    SwePlanets.PLUTO
]

additional_objects = [
    SweObjects.MEAN_NODE,     # North Node (Mean)
    SweObjects.TRUE_NODE,     # North Node (True)  
    SweObjects.CHIRON,        # Chiron
    SweObjects.LILITH         # Black Moon Lilith
]
```

### `/settings.py` - Configuration Management

**Thread-safe configuration with Swiss Ephemeris path management**

```python
from app.core.ephemeris.settings import settings

# Access current configuration
print(f"Ephemeris path: {settings.ephemeris_path}")
print(f"Default house system: {settings.default_house_system}")
print(f"Cache enabled: {settings.enable_cache}")

# Update settings at runtime
settings.update(
    default_house_system="koch",
    cache_ttl=7200,  # 2 hours
    enable_redis_cache=True
)

# Export settings for debugging
config_dict = settings.to_dict()
```

**Configuration Options:**
- `ephemeris_path` - Location of Swiss Ephemeris data files
- `default_house_system` - Default house system for calculations
- `enable_cache` - Enable/disable memory caching
- `enable_redis_cache` - Enable/disable Redis caching  
- `cache_ttl` - Cache time-to-live in seconds
- `angle_precision` - Decimal places for angle calculations
- `coordinate_system` - Tropical or sidereal calculations

## 🚀 Performance Optimizations

### 1. Caching Strategy
The engine implements a multi-layer caching strategy:

```python
# Cache lookup priority:
# 1. Redis Cache (persistent, shared)
# 2. Memory Cache (fast, process-local)  
# 3. Calculate (Swiss Ephemeris)

def cached_calculation(input_data):
    # Try Redis first
    redis_result = redis_cache.get("calculation_type", input_data)
    if redis_result:
        return redis_result
    
    # Try memory cache
    memory_result = memory_cache.get(cache_key)
    if memory_result:
        return memory_result
    
    # Calculate and cache at both levels
    result = perform_calculation(input_data)
    memory_cache.put(cache_key, result)
    redis_cache.set("calculation_type", input_data, result)
    
    return result
```

### 2. Batch Processing
Vectorized calculations provide 10x+ performance improvements:

```python
# Individual processing (slow)
results = []
for subject in subjects:
    result = calculate_natal_chart(subject)  # 65ms each
    results.append(result)
# Total: 65ms × 100 subjects = 6.5 seconds

# Batch processing (fast)  
batch_results = BatchCalculator().calculate_batch_positions(subjects)
# Total: ~650ms for 100 subjects (10x improvement)
```

### 3. Memory Optimization
Efficient memory usage for large-scale processing:

```python
# Structure-of-arrays for large datasets
from app.core.performance.optimizations import MemoryOptimizations

# Convert list-of-dicts to arrays for better cache locality
optimized_data = MemoryOptimizations.optimize_array_operations(chart_data)

# Pre-allocated memory pools for frequent operations
memory_pool = MemoryOptimizations.create_memory_pool(size=1000)
```

## 🧪 Testing Patterns

### Unit Testing
```python
import pytest
from app.core.ephemeris.tools.ephemeris import get_planet
from app.core.ephemeris.const import SwePlanets

class TestPlanetCalculation:
    def test_sun_calculation_j2000(self):
        """Test Sun position at J2000.0 epoch."""
        jd = 2451545.0  # J2000.0
        sun = get_planet(SwePlanets.SUN, jd)
        
        # Validate result structure
        assert sun.longitude is not None
        assert 0 <= sun.longitude < 360
        assert -90 <= sun.latitude <= 90
        assert sun.distance > 0
        
        # Validate approximate position (within 0.1°)
        expected_longitude = 279.9  # Approximate Sun position at J2000
        assert abs(sun.longitude - expected_longitude) < 0.1
    
    def test_invalid_planet_id(self):
        """Test error handling for invalid planet ID."""
        with pytest.raises(ValueError):
            get_planet(999, 2451545.0)  # Invalid planet ID
```

### Performance Testing  
```python
import pytest

class TestPerformance:
    @pytest.mark.benchmark(group="calculations")  
    def test_planet_calculation_speed(self, benchmark):
        """Benchmark single planet calculation."""
        jd = 2451545.0
        
        result = benchmark(get_planet, SwePlanets.SUN, jd)
        assert result is not None
        
    def test_batch_performance_improvement(self):
        """Verify batch processing meets 5x improvement target."""
        subjects = create_test_subjects(100)
        
        # Time individual processing
        start = time.time()
        for subject in subjects[:10]:  # Sample
            calculate_natal_chart(subject)
        individual_time = (time.time() - start) * 10  # Extrapolate
        
        # Time batch processing
        start = time.time()
        BatchCalculator().calculate_batch_positions(subjects)
        batch_time = time.time() - start
        
        improvement = individual_time / batch_time
        assert improvement >= 5.0  # 5x minimum improvement
```

### Integration Testing
```python
def test_complete_natal_chart():
    """Test complete natal chart calculation workflow."""
    subject_data = {
        "name": "Test Subject",
        "datetime": {"iso_string": "2000-01-01T12:00:00"},
        "latitude": {"decimal": 40.7128},
        "longitude": {"decimal": -74.0060}, 
        "timezone": {"name": "America/New_York"}
    }
    
    chart = calculate_natal_chart(subject_data)
    
    # Validate complete chart structure
    assert chart.subject.name == "Test Subject"
    assert len(chart.planets) >= 10  # Major planets
    assert len(chart.houses.cusps) == 12  # 12 houses
    assert chart.houses.angles["ascendant"] is not None
    assert chart.metadata["processing_time_ms"] < 100  # Performance target
```

## 🔧 Common Integration Patterns

### 1. Adding New Celestial Objects
```python
# 1. Add to constants
class SweObjects:
    CERES = 1  # Add new object ID
    
# 2. Update calculation functions
def get_object_position(object_id: int, julian_day: float) -> ObjectPosition:
    result = swe.calc_ut(julian_day, object_id)
    return ObjectPosition(
        longitude=result[0][0],
        latitude=result[0][1],
        # ... other fields
    )

# 3. Add to supported objects list
SUPPORTED_OBJECTS = [
    *SwePlanets.all(),
    SweObjects.CERES  # Include new object
]
```

### 2. Implementing New House Systems
```python
# 1. Add to house system mapping
HOUSE_SYSTEMS = {
    "placidus": "P",
    "new_system": "X",  # Add new system code
}

# 2. Update calculation function  
def calculate_houses(jd, lat, lng, system):
    swe_code = HOUSE_SYSTEMS.get(system, "P")
    cusps, angles = swe.houses(jd, lat, lng, swe_code.encode())
    # Process results...
```

### 3. Custom Calculation Functions
```python
from app.core.monitoring.metrics import timed_calculation
from app.core.ephemeris.classes.cache import get_global_cache

@timed_calculation("custom_calculation")
def calculate_custom_aspect(planet1_pos, planet2_pos, orb=8.0):
    """Calculate custom aspect between two planets."""
    
    # Check cache first
    cache = get_global_cache()
    cache_key = f"aspect_{planet1_pos.longitude}_{planet2_pos.longitude}_{orb}"
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Perform calculation
    angle_diff = abs(planet1_pos.longitude - planet2_pos.longitude)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    
    # Check for major aspects
    aspects = {
        "conjunction": 0,
        "sextile": 60, 
        "square": 90,
        "trine": 120,
        "opposition": 180
    }
    
    result = None
    for aspect_name, aspect_angle in aspects.items():
        if abs(angle_diff - aspect_angle) <= orb:
            result = {
                "type": aspect_name,
                "orb": abs(angle_diff - aspect_angle),
                "exact": abs(angle_diff - aspect_angle) < 0.1
            }
            break
    
    # Cache result
    cache.put(cache_key, result, ttl=3600)
    return result
```

## ⚠️ Important Considerations

### Thread Safety
- All cache operations are thread-safe
- Swiss Ephemeris calls are not inherently thread-safe (use locks for concurrent access)
- Settings object uses RLock for thread-safe updates

### Error Handling
```python
try:
    result = get_planet(planet_id, julian_day)
except SwissEphemerisError as e:
    # Swiss Ephemeris specific error
    logger.error(f"Ephemeris calculation failed: {e}")
    raise CalculationError(f"Planet calculation failed: {e}")
except ValueError as e:
    # Validation error
    logger.error(f"Invalid input: {e}")
    raise ValidationError(f"Invalid input: {e}")
```

### Performance Monitoring
All core functions are instrumented with metrics:
```python
# Automatic performance tracking
from app.core.monitoring.metrics import get_metrics

metrics = get_metrics()
print(f"Calculation rate: {metrics.calculation_rate}")
print(f"Cache hit rate: {metrics.cache_hit_rate}")
```

## 📚 Reference Data

### Swiss Ephemeris Files Required
- `sepl_*.se1` - Planetary ephemeris files
- `semo_*.se1` - Moon ephemeris files  
- `seleapsec.txt` - Leap second data
- `sedeltat` - Delta T data
- `sefstars.txt` - Fixed star catalog

### Coordinate Systems
- **Tropical**: Based on seasons (default)
- **Sidereal**: Based on fixed stars
- **Geocentric**: Earth-centered (default)
- **Heliocentric**: Sun-centered (optional)

The Meridian Ephemeris Core Engine provides the foundation for accurate, high-performance astrological calculations. Follow these patterns for optimal integration and maintain the performance standards! 🌟