# Quick Start Guide

Get up and running with the Meridian Ephemeris API in less than 5 minutes!

## Step 1: Verify API Access

First, let's check that the API is accessible:

=== "cURL"

    ```bash
    curl https://api.meridianephemeris.com/health
    ```

=== "Python"

    ```python
    import requests
    
    response = requests.get("https://api.meridianephemeris.com/health")
    print(response.json())
    ```

=== "TypeScript"

    ```typescript
    const response = await fetch("https://api.meridianephemeris.com/health");
    const health = await response.json();
    console.log(health);
    ```

You should receive a response like:

```json
{
  "status": "healthy",
  "service": "meridian-ephemeris-api",
  "version": "1.0.0",
  "timestamp": 1701944400.0
}
```

## Step 2: Your First Chart Calculation

Let's calculate a basic natal chart for someone born on June 15, 1990, at 2:30 PM in New York City:

=== "cURL"

    ```bash
    curl -X POST "https://api.meridianephemeris.com/ephemeris/natal" \
      -H "Content-Type: application/json" \
      -d '{
        "subject": {
          "name": "Sample Chart",
          "datetime": {"iso_string": "1990-06-15T14:30:00"},
          "latitude": {"decimal": 40.7128},
          "longitude": {"decimal": -74.0060},
          "timezone": {"name": "America/New_York"}
        }
      }'
    ```

=== "Python"

    ```python
    import requests
    
    # Define the chart request
    chart_request = {
        "subject": {
            "name": "Sample Chart",
            "datetime": {"iso_string": "1990-06-15T14:30:00"},
            "latitude": {"decimal": 40.7128},
            "longitude": {"decimal": -74.0060},
            "timezone": {"name": "America/New_York"}
        }
    }
    
    # Make the request
    response = requests.post(
        "https://api.meridianephemeris.com/ephemeris/natal",
        json=chart_request
    )
    
    # Parse the response
    chart = response.json()
    
    if chart["success"]:
        sun_pos = chart["data"]["planets"]["sun"]["longitude"]
        asc_pos = chart["data"]["houses"]["angles"]["ascendant"]
        print(f"Sun position: {sun_pos:.2f}°")
        print(f"Ascendant: {asc_pos:.2f}°")
    else:
        print(f"Error: {chart['message']}")
    ```

=== "TypeScript"

    ```typescript
    interface ChartRequest {
      subject: {
        name: string;
        datetime: { iso_string: string };
        latitude: { decimal: number };
        longitude: { decimal: number };
        timezone: { name: string };
      };
    }
    
    const chartRequest: ChartRequest = {
      subject: {
        name: "Sample Chart",
        datetime: { iso_string: "1990-06-15T14:30:00" },
        latitude: { decimal: 40.7128 },
        longitude: { decimal: -74.0060 },
        timezone: { name: "America/New_York" }
      }
    };
    
    const response = await fetch("https://api.meridianephemeris.com/ephemeris/natal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(chartRequest)
    });
    
    const chart = await response.json();
    
    if (chart.success) {
      const sunPos = chart.data.planets.sun.longitude;
      const ascPos = chart.data.houses.angles.ascendant;
      console.log(`Sun position: ${sunPos.toFixed(2)}°`);
      console.log(`Ascendant: ${ascPos.toFixed(2)}°`);
    } else {
      console.error(`Error: ${chart.message}`);
    }
    ```

## Step 3: Understanding the Response

The response contains comprehensive astrological data:

```json
{
  "success": true,
  "data": {
    "subject": {
      "name": "Sample Chart",
      "datetime": "1990-06-15T14:30:00-04:00",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "timezone": "America/New_York"
    },
    "planets": {
      "sun": {
        "longitude": 94.123,
        "latitude": 0.001,
        "distance": 1.0156,
        "longitude_speed": 0.9856,
        "sign": "Gemini",
        "house": 10
      },
      "moon": {
        "longitude": 180.456,
        "latitude": -2.345,
        "distance": 0.00257,
        "longitude_speed": 13.1764,
        "sign": "Libra",
        "house": 2
      }
      // ... more planets
    },
    "houses": {
      "system": "placidus",
      "cusps": [15.123, 45.678, 75.901, 105.234, 135.567, 165.890, 195.123, 225.456, 255.789, 285.012, 315.345, 345.678],
      "angles": {
        "ascendant": 15.123,
        "midheaven": 105.234,
        "descendant": 195.123,
        "imum_coeli": 285.012
      }
    },
    "calculation_time": "2023-12-07T14:30:00Z",
    "julian_day": 2448079.1041666665
  }
}
```

## Step 4: Exploring Different Input Formats

The API supports multiple input formats for flexibility:

### Coordinate Formats

=== "Decimal Degrees"

    ```json
    {
      "latitude": {"decimal": 40.7128},
      "longitude": {"decimal": -74.0060}
    }
    ```

=== "DMS String"

    ```json
    {
      "latitude": {"dms_string": "40°42'46\"N"},
      "longitude": {"dms_string": "74°00'22\"W"}
    }
    ```

=== "Component Object"

    ```json
    {
      "latitude": {
        "degrees": 40,
        "minutes": 42,
        "seconds": 46,
        "direction": "N"
      },
      "longitude": {
        "degrees": 74,
        "minutes": 0,
        "seconds": 22,
        "direction": "W"
      }
    }
    ```

### DateTime Formats

=== "ISO String"

    ```json
    {"datetime": {"iso_string": "1990-06-15T14:30:00"}}
    ```

=== "Julian Day"

    ```json
    {"datetime": {"julian_day": 2448079.1041666665}}
    ```

=== "Component Object"

    ```json
    {
      "datetime": {
        "year": 1990,
        "month": 6,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "second": 0
      }
    }
    ```

### Timezone Formats

=== "IANA Name"

    ```json
    {"timezone": {"name": "America/New_York"}}
    ```

=== "UTC Offset"

    ```json
    {"timezone": {"utc_offset": -4.0}}
    ```

=== "Auto-Detection"

    ```json
    {"timezone": {"auto_detect": true}}
    ```

## Step 5: Different House Systems

You can specify different house systems in your calculations:

```python
chart_request = {
    "subject": {
        "name": "Koch System Chart",
        "datetime": {"iso_string": "1990-06-15T14:30:00"},
        "latitude": {"decimal": 40.7128},
        "longitude": {"decimal": -74.0060},
        "timezone": {"name": "America/New_York"}
    },
    "settings": {
        "house_system": "koch"  # Options: placidus, koch, equal, whole_sign, campanus, regiomontanus
    }
}
```

## Error Handling

The API provides clear error messages for invalid input:

```python
# Example with invalid coordinates
bad_request = {
    "subject": {
        "name": "Bad Coordinates",
        "datetime": {"iso_string": "1990-06-15T14:30:00"},
        "latitude": {"decimal": 95.0},  # Invalid: > 90°
        "longitude": {"decimal": -74.0060},
        "timezone": {"name": "America/New_York"}
    }
}

response = requests.post(
    "https://api.meridianephemeris.com/ephemeris/natal",
    json=bad_request
)

error_response = response.json()
# {
#   "success": false,
#   "error": "validation_error",
#   "message": "Request validation failed",
#   "details": {
#     "errors": [
#       {
#         "loc": ["subject", "latitude", "decimal"],
#         "msg": "Latitude must be between -90 and 90 degrees",
#         "type": "value_error"
#       }
#     ]
#   }
# }
```

## Next Steps

Now that you've made your first successful chart calculation, explore these advanced features:

- 🏠 **[House Systems](../tutorials/house-systems.md)**: Learn about different house calculation methods
- ⏰ **[Date & Time Handling](../tutorials/datetime.md)**: Master complex timezone and datetime scenarios
- 📍 **[Coordinate Systems](../tutorials/coordinates.md)**: Work with various coordinate input formats
- 🔧 **[Advanced Features](../tutorials/advanced.md)**: Aspects, fixed stars, and more

## Common Use Cases

### Batch Chart Calculations

```python
import requests
from concurrent.futures import ThreadPoolExecutor
import json

def calculate_chart(person_data):
    """Calculate chart for a single person"""
    response = requests.post(
        "https://api.meridianephemeris.com/ephemeris/natal",
        json={"subject": person_data}
    )
    return response.json()

# List of people to calculate charts for
people = [
    {
        "name": "Person 1",
        "datetime": {"iso_string": "1985-03-20T12:00:00"},
        "latitude": {"decimal": 51.5074},
        "longitude": {"decimal": -0.1278},
        "timezone": {"name": "Europe/London"}
    },
    {
        "name": "Person 2",
        "datetime": {"iso_string": "1992-07-04T15:30:00"},
        "latitude": {"decimal": 34.0522},
        "longitude": {"decimal": -118.2437},
        "timezone": {"name": "America/Los_Angeles"}
    }
]

# Calculate charts in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    charts = list(executor.map(calculate_chart, people))

# Process results
for chart in charts:
    if chart["success"]:
        name = chart["data"]["subject"]["name"]
        sun_sign = chart["data"]["planets"]["sun"]["sign"]
        print(f"{name}: Sun in {sun_sign}")
```

### Chart Comparison

```python
def compare_charts(chart1, chart2):
    """Compare two natal charts"""
    if not (chart1["success"] and chart2["success"]):
        return "Error: Both charts must be calculated successfully"
    
    planets1 = chart1["data"]["planets"]
    planets2 = chart2["data"]["planets"]
    
    # Calculate Sun-Sun aspect
    sun1_long = planets1["sun"]["longitude"]
    sun2_long = planets2["sun"]["longitude"]
    
    aspect_angle = abs(sun1_long - sun2_long)
    if aspect_angle > 180:
        aspect_angle = 360 - aspect_angle
    
    # Determine aspect type
    if aspect_angle < 8:
        aspect = "Conjunction"
    elif 52 < aspect_angle < 68:
        aspect = "Sextile"
    elif 82 < aspect_angle < 98:
        aspect = "Square"
    elif 112 < aspect_angle < 128:
        aspect = "Trine"
    elif aspect_angle > 172:
        aspect = "Opposition"
    else:
        aspect = f"Minor aspect ({aspect_angle:.1f}°)"
    
    return f"Sun-Sun aspect: {aspect} ({aspect_angle:.1f}°)"

# Example usage
chart1 = calculate_chart(people[0])
chart2 = calculate_chart(people[1])
print(compare_charts(chart1, chart2))
```

You're now ready to build amazing astrological applications with the Meridian Ephemeris API! 🌟