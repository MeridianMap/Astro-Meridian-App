# Enhanced Ephemeris Calculations Documentation

## Overview

This document describes the enhanced ephemeris calculations implemented for the Meridian Astro App, focusing on **South Node calculations** and **retrograde motion detection**. These enhancements build upon the Swiss Ephemeris foundation to provide comprehensive astronomical calculations.

## Key Features

### 1. South Node Calculations

The South Node is always positioned exactly 180° opposite the North Node along the ecliptic. Our implementation calculates both Mean and True South Nodes from their corresponding North Nodes.

#### Mathematical Implementation

```python
# South Node longitude = North Node longitude + 180°
south_longitude = normalize_longitude(north_node_position.longitude + 180.0)

# South Node latitude = -(North Node latitude)
south_latitude = -north_node_position.latitude

# Speed values
south_longitude_speed = north_node_position.longitude_speed  # Same magnitude
south_latitude_speed = -north_node_position.latitude_speed   # Opposite sign
```

#### Swiss Ephemeris Integration

The Swiss Ephemeris provides direct access to North Nodes:
- **Mean Node**: `swe.MEAN_NODE` (SE constant 10)
- **True Node**: `swe.TRUE_NODE` (SE constant 11)

South Nodes are calculated mathematically since they're not separate SE objects.

### 2. Retrograde Motion Detection

Retrograde motion is detected by analyzing the longitude speed from Swiss Ephemeris calculations.

#### Detection Algorithm

```python
def is_retrograde(longitude_speed: float) -> bool:
    """
    Retrograde detection based on longitude speed.
    
    - longitude_speed < 0: Retrograde motion
    - longitude_speed > 0: Direct motion  
    - longitude_speed = 0: Stationary
    """
    return longitude_speed < 0.0
```

#### Motion Classification

- **Retrograde**: `longitude_speed < 0.0` - Planet appears to move backward
- **Direct**: `longitude_speed > 0.0` - Planet moves forward in normal direction
- **Stationary**: `longitude_speed ≈ 0.0` - Planet appears motionless (changing direction)

## Implementation Details

### Core Classes

#### `EnhancedPlanetPosition`

Extends basic planet position with retrograde detection:

```python
@dataclass
class EnhancedPlanetPosition:
    planet_id: int
    name: str
    longitude: float
    latitude: float
    distance: float
    longitude_speed: float
    latitude_speed: float = 0.0
    distance_speed: float = 0.0
    
    @property
    def is_retrograde(self) -> bool:
        """Detect retrograde motion based on longitude speed."""
        return self.longitude_speed < 0.0
    
    @property
    def motion_type(self) -> str:
        """Return motion type as string."""
        if self.longitude_speed < 0.0:
            return "retrograde"
        elif self.longitude_speed > 0.0:
            return "direct"
        else:
            return "stationary"
```

#### `LunarNodeData`

Complete lunar node information:

```python
@dataclass
class LunarNodeData:
    mean_north: EnhancedPlanetPosition
    true_north: EnhancedPlanetPosition
    mean_south: EnhancedPlanetPosition  # Calculated from mean_north
    true_south: EnhancedPlanetPosition  # Calculated from true_north
```

### Key Functions

#### `calculate_south_node_position()`

Calculates South Node from North Node position:

```python
def calculate_south_node_position(
    north_node_position: PlanetPosition,
    calculation_type: str = "mean"
) -> Dict[str, Union[float, str]]:
    """
    Calculate South Node position from North Node.
    
    The South Node is always 180° opposite the North Node.
    Its latitude is the negative of the North Node's latitude.
    Speed values maintain the same magnitude but opposite sign for latitude.
    """
```

#### `get_comprehensive_ephemeris_output()`

Main function implementing "all planets and features output":

```python
def get_comprehensive_ephemeris_output(
    datetime_utc: datetime,
    include_analysis: bool = True,
    include_asteroids: bool = True,
    include_nodes: bool = True,
    include_lilith: bool = True,
    flags: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive ephemeris output with all planets and features.
    
    This implements the complete "all planets and features output from ephemeris"
    as described in the technical documentation.
    """
```

## Swiss Ephemeris Technical Details

### Speed Flag Usage

To get velocity information (required for retrograde detection), the `FLG_SPEED` flag must be included:

```python
flags = swe.FLG_SWIEPH | swe.FLG_SPEED
result, ret_flags = swe.calc_ut(julian_day, planet_id, flags)

# result[3] contains longitude speed (degrees/day)
longitude_speed = result[3]
is_retrograde = longitude_speed < 0.0
```

### Coordinate System

- **Default**: Geocentric tropical coordinates
- **Reference Frame**: J2000.0 ecliptic and equinox
- **Precision**: Arc-second level accuracy
- **Time System**: Universal Time (UT)

### Node Motion Characteristics

Lunar nodes exhibit unique motion patterns:

- **Direction**: Always retrograde (moving backward through zodiac)
- **Mean Motion**: Approximately -0.053°/day (-19.3°/year)
- **Cycle Period**: 18.6 years for complete zodiac circuit
- **Mean vs True**: True nodes oscillate around mean position

## Output Format

### JSON Structure

```json
{
  "calculation_info": {
    "datetime_utc": "2024-01-01T12:00:00+00:00",
    "julian_day": 2460310.0,
    "swiss_ephemeris_version": "2.10.03",
    "coordinate_system": "geocentric_tropical",
    "precision": "arc_second_level"
  },
  "positions": {
    "sun": {
      "planet_id": 0,
      "name": "Sun",
      "longitude": 280.1234,
      "latitude": 0.0,
      "distance": 0.9833,
      "longitude_speed": 0.9856,
      "is_retrograde": false,
      "motion_type": "direct"
    },
    "mercury": {
      "planet_id": 2,
      "name": "Mercury",
      "longitude": 95.4321,
      "latitude": 1.2,
      "distance": 0.4,
      "longitude_speed": -1.2345,
      "is_retrograde": true,
      "motion_type": "retrograde"
    },
    "north_node_mean": {
      "planet_id": 10,
      "name": "North Node (Mean)",
      "longitude": 125.6789,
      "latitude": 0.0,
      "distance": 1.0,
      "longitude_speed": -0.0529,
      "is_retrograde": true,
      "motion_type": "retrograde"
    },
    "south_node_mean": {
      "planet_id": 1010,
      "name": "South Node (Mean)",
      "longitude": 305.6789,
      "latitude": 0.0,
      "distance": 1.0,
      "longitude_speed": -0.0529,
      "is_retrograde": true,
      "motion_type": "retrograde"
    }
  },
  "retrograde_analysis": {
    "total_bodies": 15,
    "retrograde_count": 3,
    "direct_count": 12,
    "stationary_count": 0,
    "retrograde_percentage": 20.0,
    "retrograde_bodies": [
      {
        "name": "mercury",
        "longitude_speed": -1.2345,
        "longitude": 95.4321
      }
    ]
  }
}
```

## Usage Examples

### Basic South Node Calculation

```python
from app.core.ephemeris.tools.enhanced_calculations import calculate_complete_lunar_nodes

# Calculate all lunar nodes for J2000.0
node_data = calculate_complete_lunar_nodes(2451545.0)

print(f"Mean North Node: {node_data.mean_north.longitude:.3f}°")
print(f"Mean South Node: {node_data.mean_south.longitude:.3f}°")
print(f"Nodes are retrograde: {node_data.mean_north.is_retrograde}")
```

### Retrograde Detection

```python
from app.core.ephemeris.tools.enhanced_calculations import get_enhanced_planet_position
from app.core.ephemeris.const import SwePlanets

# Check if Mercury is retrograde
mercury = get_enhanced_planet_position(SwePlanets.MERCURY, 2451545.0)
print(f"Mercury is retrograde: {mercury.is_retrograde}")
print(f"Mercury motion type: {mercury.motion_type}")
print(f"Mercury speed: {mercury.longitude_speed:.4f}°/day")
```

### Comprehensive Output

```python
from datetime import datetime, timezone
from app.core.ephemeris.tools.enhanced_calculations import get_comprehensive_ephemeris_output

# Generate complete ephemeris for current time
result = get_comprehensive_ephemeris_output(
    datetime.now(timezone.utc),
    include_analysis=True,
    include_asteroids=True,
    include_nodes=True,
    include_lilith=True
)

# Access retrograde analysis
analysis = result['retrograde_analysis']
print(f"Currently retrograde: {analysis['retrograde_count']} planets")

# Access specific positions
mercury = result['positions']['mercury']
south_node = result['positions']['south_node_mean']
```

## Error Handling

The implementation includes comprehensive error handling:

- **Swiss Ephemeris Errors**: Caught and re-raised with descriptive messages
- **Invalid Dates**: Handled by Julian Day conversion validation
- **Missing Data**: Graceful degradation with warnings
- **Calculation Failures**: Individual planet failures don't stop entire calculation

## Performance Considerations

- **Caching**: Results cached for 1 hour to improve performance
- **Batch Calculations**: Optimized for calculating multiple objects
- **Memory Usage**: Efficient data structures to minimize memory footprint
- **Calculation Speed**: Direct Swiss Ephemeris calls for maximum speed

## Integration with ACG System

The retrograde detection integrates seamlessly with the Astrocartography system:

```python
# From ACG integration code
retrograde=getattr(planet_pos, 'longitude_speed', 0) < 0
```

This ensures consistent retrograde detection across all system components.

## Validation and Testing

Comprehensive test suite includes:

- **Unit Tests**: Individual function testing
- **Integration Tests**: Swiss Ephemeris integration validation  
- **Accuracy Tests**: Comparison with reference astronomical software
- **Edge Case Tests**: Stationary planets, node oscillations, coordinate boundaries

## Future Enhancements

Potential future improvements:

1. **Station Detection**: Precise calculation of retrograde station points
2. **Speed Profiles**: Detailed speed analysis over time periods
3. **Visual Motion**: Animation of retrograde loops
4. **Historical Analysis**: Retrograde pattern analysis over time
5. **Additional Bodies**: Extended asteroid and comet retrograde detection

## References

- Swiss Ephemeris Programming Interface Documentation
- Meeus, J. "Astronomical Algorithms"
- IAU Standards for Astronomical Coordinates
- Professional astrology software retrograde detection methods

---

*This implementation provides the complete "all planets and features output from ephemeris" capability with enhanced retrograde detection and South Node calculations, maintaining Swiss Ephemeris precision and reliability.*
