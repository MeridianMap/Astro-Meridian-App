# Python SDK

The official Python SDK for the Meridian Ephemeris API provides a convenient, type-safe interface for calculating astrological charts.

## Installation

### Using pip

```bash
pip install meridian-ephemeris
```

### From source

```bash
git clone https://github.com/meridian-ephemeris/python-sdk.git
cd python-sdk
pip install -e .
```

### Development installation

```bash
git clone https://github.com/meridian-ephemeris/python-sdk.git
cd python-sdk
pip install -e ".[dev]"
```

## Quick Start

```python
from meridian_ephemeris import MeridianEphemeris

# Initialize the client
client = MeridianEphemeris()

# Calculate a natal chart
chart = client.calculate_natal_chart({
    "name": "John Doe",
    "datetime": {"iso_string": "1990-06-15T14:30:00"},
    "latitude": {"decimal": 40.7128},
    "longitude": {"decimal": -74.0060},
    "timezone": {"name": "America/New_York"}
})

print(f"Sun position: {chart['data']['planets']['sun']['longitude']}°")
```

## API Reference

### MeridianEphemeris Class

The main client class for interacting with the API.

#### Constructor

```python
MeridianEphemeris(base_url: str = "https://api.meridianephemeris.com")
```

**Parameters:**
- `base_url` (str): The base URL of the API (default: production URL)

**Example:**
```python
# Production
client = MeridianEphemeris()

# Local development
client = MeridianEphemeris("http://localhost:8000")

# Custom deployment
client = MeridianEphemeris("https://your-api.example.com")
```

#### Methods

##### `calculate_natal_chart(subject_data, settings=None)`

Calculate a natal chart for the given birth data.

**Parameters:**
- `subject_data` (dict): Birth information
- `settings` (dict, optional): Calculation settings

**Returns:**
- `dict`: Complete chart data

**Example:**
```python
subject = {
    "name": "Jane Smith",
    "datetime": {"iso_string": "1985-03-20T08:45:00"},
    "latitude": {"decimal": 51.5074},
    "longitude": {"decimal": -0.1278},
    "timezone": {"name": "Europe/London"}
}

settings = {
    "house_system": "koch"
}

chart = client.calculate_natal_chart(subject, settings)
```

##### `health_check()`

Check the health status of the API.

**Returns:**
- `dict`: Health status information

**Example:**
```python
health = client.health_check()
print(f"API Status: {health['status']}")
```

### Data Models

The SDK includes comprehensive data models for type safety and autocompletion.

#### SubjectData

```python
from meridian_ephemeris.models import SubjectData, DateTimeInput, CoordinateInput, TimezoneInput

subject = SubjectData(
    name="John Doe",
    datetime=DateTimeInput(iso_string="1990-06-15T14:30:00"),
    latitude=CoordinateInput(decimal=40.7128),
    longitude=CoordinateInput(decimal=-74.0060),
    timezone=TimezoneInput(name="America/New_York")
)
```

#### ChartSettings

```python
from meridian_ephemeris.models import ChartSettings

settings = ChartSettings(
    house_system="placidus",
    include_aspects=True,
    aspect_orbs={
        "conjunction": 8.0,
        "opposition": 8.0,
        "trine": 6.0,
        "square": 6.0,
        "sextile": 4.0
    }
)
```

## Input Formats

The SDK supports multiple input formats for flexibility.

### Coordinates

```python
# Decimal degrees
latitude = {"decimal": 40.7128}

# DMS string
latitude = {"dms_string": "40°42'46\"N"}

# Component format
latitude = {
    "degrees": 40,
    "minutes": 42,
    "seconds": 46,
    "direction": "N"
}
```

### Date & Time

```python
# ISO string
datetime = {"iso_string": "1990-06-15T14:30:00"}

# Julian day
datetime = {"julian_day": 2448079.1041666665}

# Component format
datetime = {
    "year": 1990,
    "month": 6,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "second": 0
}
```

### Timezones

```python
# IANA timezone name
timezone = {"name": "America/New_York"}

# UTC offset
timezone = {"utc_offset": -4.0}

# Auto-detect from coordinates
timezone = {"auto_detect": True}
```

## Error Handling

The SDK provides structured error handling for robust applications.

### Exception Hierarchy

```python
from meridian_ephemeris.exceptions import (
    MeridianEphemerisError,      # Base exception
    ValidationError,             # Input validation failed
    CalculationError,           # Chart calculation failed
    RateLimitError,             # Rate limit exceeded
    NetworkError                # Network/connection issues
)
```

### Example Error Handling

```python
try:
    chart = client.calculate_natal_chart(subject_data)
    
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    for error in e.validation_errors:
        field = " -> ".join(error["loc"])
        print(f"  {field}: {error['msg']}")

except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    time.sleep(e.retry_after)
    
except CalculationError as e:
    print(f"Calculation failed: {e.message}")
    
except NetworkError as e:
    print(f"Network error: {e.message}")
    
except MeridianEphemerisError as e:
    print(f"API error: {e.message}")
```

## Advanced Features

### Automatic Retry

```python
from meridian_ephemeris import MeridianEphemeris
from meridian_ephemeris.retry import RetryConfig

# Configure automatic retry
retry_config = RetryConfig(
    max_retries=3,
    backoff_factor=2.0,
    retry_on_rate_limit=True
)

client = MeridianEphemeris(retry_config=retry_config)
```

### Response Caching

```python
from meridian_ephemeris.cache import MemoryCache

# Enable response caching
cache = MemoryCache(max_size=1000, ttl=3600)  # 1 hour TTL
client = MeridianEphemeris(cache=cache)
```

### Custom HTTP Session

```python
import requests
from meridian_ephemeris import MeridianEphemeris

# Use custom session for proxy, auth, etc.
session = requests.Session()
session.proxies = {"https": "http://proxy.example.com:8080"}

client = MeridianEphemeris(session=session)
```

## Batch Processing

Efficiently process multiple charts:

```python
from meridian_ephemeris.batch import BatchProcessor
import asyncio

async def batch_calculate():
    subjects = [
        {"name": "Person 1", "datetime": {"iso_string": "1990-01-01T12:00:00"}, ...},
        {"name": "Person 2", "datetime": {"iso_string": "1991-01-01T12:00:00"}, ...},
        # ... more subjects
    ]
    
    processor = BatchProcessor(client, max_concurrent=5)
    results = await processor.calculate_charts(subjects)
    
    for result in results:
        if result["success"]:
            print(f"Chart for {result['subject']['name']}: ✅")
        else:
            print(f"Failed for {result['subject']['name']}: {result['error']}")

# Run batch processing
asyncio.run(batch_calculate())
```

## Data Analysis Helpers

Built-in helpers for common analysis tasks:

```python
from meridian_ephemeris.analysis import ChartAnalyzer

analyzer = ChartAnalyzer(chart)

# Get planetary positions
positions = analyzer.get_planetary_positions()
print(f"Sun in {positions['sun']['sign']} at {positions['sun']['longitude']:.2f}°")

# Element distribution
elements = analyzer.get_element_distribution()
print(f"Fire: {elements['fire']}, Earth: {elements['earth']}")

# Aspect patterns
aspects = analyzer.get_major_aspects()
for aspect in aspects:
    print(f"{aspect['planet1']} {aspect['type']} {aspect['planet2']} ({aspect['orb']:.1f}°)")

# House analysis
house_analysis = analyzer.get_house_analysis()
print(f"Most emphasized house: {house_analysis['strongest_house']}")
```

## Configuration

### Environment Variables

```bash
# API endpoint
export MERIDIAN_EPHEMERIS_API_URL="https://api.meridianephemeris.com"

# API key (when authentication is implemented)
export MERIDIAN_EPHEMERIS_API_KEY="your-api-key"

# Timeout settings
export MERIDIAN_EPHEMERIS_TIMEOUT=30

# Retry settings
export MERIDIAN_EPHEMERIS_MAX_RETRIES=3
```

### Configuration File

Create `.meridian_ephemeris.yml`:

```yaml
api:
  base_url: "https://api.meridianephemeris.com"
  timeout: 30
  
retry:
  max_retries: 3
  backoff_factor: 2.0
  retry_on_rate_limit: true
  
cache:
  enabled: true
  max_size: 1000
  ttl: 3600
```

Load configuration:

```python
from meridian_ephemeris.config import load_config

config = load_config(".meridian_ephemeris.yml")
client = MeridianEphemeris.from_config(config)
```

## Logging

Enable detailed logging:

```python
import logging

# Enable SDK logging
logging.getLogger('meridian_ephemeris').setLevel(logging.DEBUG)

# Configure handler
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger('meridian_ephemeris').addHandler(handler)
```

## Testing

The SDK includes utilities for testing:

```python
from meridian_ephemeris.testing import MockClient

# Use mock client for testing
mock_client = MockClient()
mock_client.add_response("natal_chart", {
    "success": True,
    "data": {
        "planets": {"sun": {"longitude": 120.5}},
        # ... mock data
    }
})

# Test your code with mock client
def test_my_function():
    result = my_function(mock_client)
    assert result is not None
```

## Performance Tips

1. **Use caching** for repeated calculations
2. **Batch requests** when processing multiple charts  
3. **Implement proper retry logic** for rate limits
4. **Reuse client instances** to leverage connection pooling
5. **Use async batch processing** for large datasets

## Migration Guide

### From Direct HTTP Calls

```python
# Before (direct HTTP)
import requests

response = requests.post("https://api.meridianephemeris.com/ephemeris/natal", json={
    "subject": {...}
})
chart = response.json()

# After (SDK)
from meridian_ephemeris import MeridianEphemeris

client = MeridianEphemeris()
chart = client.calculate_natal_chart({...})
```

### From Version 0.x

```python
# Version 0.x
from meridian_ephemeris import EphemerisClient
client = EphemerisClient(api_url="...")

# Version 1.x
from meridian_ephemeris import MeridianEphemeris  
client = MeridianEphemeris(base_url="...")
```

## Examples

Complete examples are available in the [GitHub repository](https://github.com/meridian-ephemeris/python-sdk/tree/main/examples):

- **Basic Usage**: Simple chart calculation
- **Batch Processing**: Multiple charts efficiently
- **Web Application**: Flask integration
- **Data Analysis**: Statistical analysis of charts
- **Custom Client**: Advanced configuration

## Support

- 📧 **Email**: [python-sdk@meridianephemeris.com](mailto:python-sdk@meridianephemeris.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/meridian-ephemeris/python-sdk/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/meridian-ephemeris/python-sdk/discussions)
- 📚 **Documentation**: [API Reference](../api/overview.md)

## Contributing

We welcome contributions! See the [Contributing Guide](https://github.com/meridian-ephemeris/python-sdk/blob/main/CONTRIBUTING.md) for details.

---

**Next**: [TypeScript SDK](typescript-sdk.md) | **Up**: [Client SDKs](../examples/code-samples.md)