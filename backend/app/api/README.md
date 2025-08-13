# Meridian Ephemeris API Documentation

## 🏗️ API Architecture Overview

The Meridian Ephemeris API is built using FastAPI with a modular, performance-first architecture designed for high-throughput astrological calculations.

### Directory Structure
```
backend/app/api/
├── models/
│   └── schemas.py          # Pydantic models for request/response validation
├── routes/
│   └── ephemeris.py        # Main API endpoints
└── README.md              # This file
```

## 🌟 Core API Features

- **High Performance**: <100ms median response times
- **Comprehensive Validation**: Pydantic models with detailed error handling
- **Multiple Input Formats**: Flexible coordinate, datetime, and timezone inputs
- **Intelligent Caching**: Redis + memory caching for optimal performance
- **Production Monitoring**: Prometheus metrics integration
- **Auto-Generated Documentation**: OpenAPI 3.1 with interactive docs

## 📋 API Endpoints Overview

### Health & Status Endpoints

#### `GET /health`
Global API health check
- **Response Time**: <10ms
- **Returns**: Basic service status
- **Use Case**: Load balancer health checks

#### `GET /ephemeris/health`
Detailed ephemeris system health
- **Response Time**: <50ms  
- **Returns**: Swiss Ephemeris status, cache health, file availability
- **Use Case**: System monitoring and diagnostics

### Calculation Endpoints

#### `POST /ephemeris/natal`
**Primary natal chart calculation endpoint**

**Request Model**: `NatalChartRequest`
```json
{
  "subject": {
    "name": "John Doe",
    "datetime": {"iso_string": "1990-06-15T14:30:00"},
    "latitude": {"decimal": 40.7128},
    "longitude": {"decimal": -74.0060},
    "timezone": {"name": "America/New_York"}
  },
  "settings": {
    "house_system": "placidus",
    "include_aspects": true,
    "orb_settings": {
      "conjunction": 8.0,
      "opposition": 8.0
    }
  }
}
```

**Response Model**: `NatalChartResponse`
```json
{
  "success": true,
  "data": {
    "subject": {
      "name": "John Doe",
      "datetime": "1990-06-15T14:30:00-04:00",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "timezone": "America/New_York"
    },
    "planets": {
      "sun": {
        "longitude": 24.123,
        "latitude": 0.0002,
        "distance": 1.0145,
        "longitude_speed": 0.9583,
        "sign": "gemini",
        "house": 10,
        "retrograde": false
      }
    },
    "houses": {
      "system": "placidus",
      "cusps": [12.34, 45.67, ...],
      "angles": {
        "ascendant": 12.34,
        "midheaven": 102.45,
        "descendant": 192.34,
        "imum_coeli": 282.45
      }
    },
    "aspects": [
      {
        "planet1": "sun",
        "planet2": "moon", 
        "type": "trine",
        "orb": 2.15,
        "exact": false
      }
    ]
  },
  "metadata": {
    "processing_time_ms": 45.2,
    "cache_hit": false,
    "calculation_engine": "swiss_ephemeris_2.10"
  }
}
```

**Performance Characteristics**:
- **Median Response Time**: 35-65ms (cache miss)
- **Cache Hit Response**: 5-15ms  
- **P95 Response Time**: <100ms
- **Throughput**: 500+ requests/second

#### `POST /ephemeris/batch`
**Batch natal chart processing for high-performance applications**

**Request Model**: `BatchNatalRequest`
```json
{
  "subjects": [
    {
      "name": "Subject 1", 
      "datetime": {"iso_string": "1990-01-01T12:00:00"},
      "latitude": {"decimal": 40.7128},
      "longitude": {"decimal": -74.0060},
      "timezone": {"name": "UTC"}
    },
    {
      "name": "Subject 2",
      "datetime": {"iso_string": "1991-01-01T12:00:00"}, 
      "latitude": {"decimal": 51.5074},
      "longitude": {"decimal": -0.1278},
      "timezone": {"name": "Europe/London"}
    }
  ],
  "settings": {
    "house_system": "placidus"
  }
}
```

**Performance Characteristics**:
- **10x+ Performance Improvement** over individual requests
- **Optimal Batch Size**: 50-200 subjects
- **Maximum Batch Size**: 1000 subjects
- **Throughput**: 2000+ charts/second

### Reference & Schema Endpoints

#### `GET /ephemeris/house-systems`
Lists all supported house systems with descriptions

#### `GET /ephemeris/supported-objects` 
Lists all calculable celestial objects

#### `GET /ephemeris/schemas/natal-request`
Returns the complete JSON schema for natal chart requests

#### `GET /ephemeris/schemas/natal-response`
Returns the complete JSON schema for natal chart responses

## 🔧 Input Format Documentation

### Coordinate Input Formats

The API accepts coordinates in three flexible formats:

#### 1. Decimal Degrees (Recommended)
```json
{
  "latitude": {"decimal": 40.7128},
  "longitude": {"decimal": -74.0060}
}
```
- **Range**: Latitude [-90, 90], Longitude [-180, 180]
- **Precision**: Up to 6 decimal places (≈0.1 meter accuracy)

#### 2. DMS String Format
```json
{
  "latitude": {"dms_string": "40°42'46\"N"},
  "longitude": {"dms_string": "74°00'22\"W"}
}
```
- **Formats Accepted**: 
  - `40°42'46"N` (degrees, minutes, seconds with direction)
  - `40d42m46sN` (alternative notation)
  - `40 42 46 N` (space-separated)

#### 3. Component Format
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
- **Direction**: "N", "S" for latitude; "E", "W" for longitude
- **Validation**: Automatic bounds checking and direction consistency

### DateTime Input Formats

#### 1. ISO 8601 String (Recommended)
```json
{
  "datetime": {"iso_string": "1990-06-15T14:30:00"}
}
```
- **With Timezone**: `"1990-06-15T14:30:00-05:00"`
- **UTC**: `"1990-06-15T14:30:00Z"`

#### 2. Julian Day Number
```json
{
  "datetime": {"julian_day": 2448079.1041666665}
}
```
- **Precision**: Astronomical standard precision
- **Use Case**: Precise historical calculations

#### 3. Component Format
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

### Timezone Input Formats

#### 1. IANA Timezone Names (Recommended)
```json
{
  "timezone": {"name": "America/New_York"}
}
```
- **Examples**: `"Europe/London"`, `"Asia/Tokyo"`, `"UTC"`
- **Automatic DST**: Handles daylight saving time transitions

#### 2. UTC Offset
```json
{
  "timezone": {"utc_offset": -5.0}
}
```
- **Range**: [-12.0, +14.0] hours
- **Note**: Does not handle DST automatically

#### 3. Auto-Detection (Beta)
```json
{
  "timezone": {"auto_detect": true}
}
```
- **Uses**: Coordinates to estimate timezone
- **Accuracy**: ~95% for major populated areas

## ⚡ Performance Optimization Guidelines

### Request Optimization

#### 1. Use Batch Endpoints
```python
# Inefficient: Multiple individual requests
for subject in subjects:
    response = requests.post("/ephemeris/natal", json={"subject": subject})

# Efficient: Single batch request (10x+ faster)  
response = requests.post("/ephemeris/batch", json={"subjects": subjects})
```

#### 2. Leverage Caching
```python
# Identical requests within 1 hour are cached
# First request: 65ms (cache miss)
# Subsequent requests: 8ms (cache hit)
```

#### 3. Optimize Input Formats
```python
# Fastest: Decimal degrees + ISO strings
request = {
  "subject": {
    "datetime": {"iso_string": "1990-06-15T14:30:00"},
    "latitude": {"decimal": 40.7128},
    "longitude": {"decimal": -74.0060}
  }
}

# Slower: Component formats (additional parsing)
request = {
  "subject": {
    "datetime": {"year": 1990, "month": 6, "day": 15},
    "latitude": {"degrees": 40, "minutes": 42, "seconds": 46, "direction": "N"}
  }
}
```

### Response Optimization

#### 1. Request Only Needed Data
```json
{
  "settings": {
    "include_aspects": false,     // Skip if not needed
    "include_fixed_stars": false, // Skip if not needed  
    "precision": "standard"       // vs "high" precision
  }
}
```

#### 2. Use Appropriate House Systems
```json
{
  "settings": {
    "house_system": "equal"       // Faster than "placidus"
  }
}
```

## 🛡️ Error Handling

### Error Response Format
All errors follow a consistent structure:

```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable error description", 
  "details": {
    "field_errors": [...],
    "error_context": {...}
  }
}
```

### Error Types & Status Codes

#### 400 - Bad Request
```json
{
  "success": false,
  "error": "bad_request",
  "message": "Invalid request format",
  "details": {"issue": "Missing required field"}
}
```

#### 422 - Validation Error  
```json
{
  "success": false,
  "error": "validation_error",
  "message": "Request validation failed",
  "details": {
    "errors": [
      {
        "loc": ["subject", "latitude", "decimal"],
        "msg": "Latitude must be between -90 and 90 degrees", 
        "type": "value_error"
      }
    ]
  }
}
```

#### 429 - Rate Limited
```json
{
  "success": false,
  "error": "rate_limit_exceeded", 
  "message": "Rate limit exceeded",
  "details": {
    "limit": 100,
    "window": "1 minute",
    "retry_after": 60
  }
}
```

#### 500 - Calculation Error
```json
{
  "success": false,
  "error": "calculation_error",
  "message": "Swiss Ephemeris calculation failed",
  "details": {
    "error_type": "ephemeris_file_missing",
    "coordinates": {"latitude": 85.0, "longitude": 0.0}
  }
}
```

## 🔄 API Versioning

### Current Version: v1.0
- **Base URL**: `/ephemeris/`
- **Stability**: Production-ready
- **Backwards Compatibility**: Guaranteed for v1.x

### Future Versioning Strategy
- **Breaking Changes**: New major version (v2.0)
- **New Features**: Minor version increments (v1.1)
- **Bug Fixes**: Patch versions (v1.0.1)

## 📊 Monitoring & Metrics

### Response Headers
Every API response includes performance metrics:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Process-Time: 0.045
X-Cache-Status: miss
X-Calculation-Engine: swiss_ephemeris_2.10
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701944460
```

### Prometheus Metrics
Available at `/metrics` endpoint:

- `meridian_api_requests_total` - Total request count by endpoint/status
- `meridian_api_request_duration_seconds` - Response time distributions
- `meridian_calculations_total` - Calculation count by type/success
- `meridian_cache_hit_rate` - Cache performance metrics

## 🧪 Testing Your Integration

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
# Expected: {"status": "healthy", "service": "meridian-ephemeris-api"}
```

### Simple Calculation
```bash
curl -X POST "http://localhost:8000/ephemeris/natal" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": {
      "name": "Test User",
      "datetime": {"iso_string": "2000-01-01T12:00:00"},
      "latitude": {"decimal": 0.0},
      "longitude": {"decimal": 0.0},
      "timezone": {"name": "UTC"}
    }
  }'
```

### Performance Test
```bash
# Test batch endpoint with multiple subjects
curl -X POST "http://localhost:8000/ephemeris/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "subjects": [
      {"name": "Test 1", "datetime": {"iso_string": "2000-01-01T12:00:00"}, 
       "latitude": {"decimal": 40.7128}, "longitude": {"decimal": -74.0060},
       "timezone": {"name": "America/New_York"}},
      {"name": "Test 2", "datetime": {"iso_string": "2001-01-01T12:00:00"},
       "latitude": {"decimal": 51.5074}, "longitude": {"decimal": -0.1278}, 
       "timezone": {"name": "Europe/London"}}
    ]
  }'
```

## 🔗 Related Resources

- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **Metrics Endpoint**: `http://localhost:8000/metrics`
- **Performance Validation**: `python scripts/validate-performance.py`

## 🚀 Best Practices for Integration

1. **Always validate responses** - Check the `success` field
2. **Implement retry logic** - Handle rate limits gracefully
3. **Use batch endpoints** - For multiple calculations
4. **Cache aggressively** - Identical requests return cached results
5. **Monitor performance** - Track response times and error rates
6. **Handle all error types** - Implement comprehensive error handling
7. **Test edge cases** - Extreme coordinates, historical dates
8. **Use appropriate precision** - Balance accuracy vs performance

## 📞 Support & Troubleshooting

### Common Issues

**Slow Response Times**
- Use batch endpoints for multiple calculations
- Check if Swiss Ephemeris files are properly installed
- Monitor cache hit rates

**Validation Errors**  
- Verify coordinate ranges: lat[-90,90], lng[-180,180]
- Check datetime format compatibility
- Ensure timezone names are valid IANA identifiers

**Rate Limiting**
- Implement exponential backoff retry logic
- Use batch processing to reduce request count
- Monitor rate limit headers

### Debug Mode
Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

The Meridian Ephemeris API is designed for high-performance, production-grade astrological calculations. Follow these patterns for optimal integration! 🌟