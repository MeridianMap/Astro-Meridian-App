# API Reference Overview

The Meridian Ephemeris API is a RESTful web service that provides precise astrological chart calculations using the Swiss Ephemeris. All endpoints return JSON responses and follow standard HTTP status codes.

## Base URL

```
https://api.meridianephemeris.com
```

For local development:
```
http://localhost:8000
```

## Authentication

Currently, the API is open and does not require authentication. Future versions may implement API key authentication for rate limiting and usage tracking.

## Request Headers

All requests should include the following headers:

```
Content-Type: application/json
Accept: application/json
```

## Response Format

All API responses follow a consistent structure:

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data specific to the endpoint
  },
  "metadata": {
    "calculation_time": "2023-12-07T14:30:00Z",
    "api_version": "1.0.0",
    "processing_time_ms": 45
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    // Additional error information
  }
}
```

## HTTP Status Codes

The API uses standard HTTP status codes:

| Status Code | Description | Usage |
|------------|-------------|-------|
| `200 OK` | Success | Request completed successfully |
| `400 Bad Request` | Client Error | Invalid request parameters or format |
| `422 Unprocessable Entity` | Validation Error | Request format is valid but data validation failed |
| `429 Too Many Requests` | Rate Limited | Too many requests in a given time period |
| `500 Internal Server Error` | Server Error | Unexpected server error |
| `503 Service Unavailable` | Service Error | Service temporarily unavailable |

## Error Types

Common error codes returned by the API:

### `validation_error`
Input validation failed. Check the `details.errors` array for specific field validation issues.

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

### `calculation_error`
Error during astrological calculations, often due to invalid ephemeris data or extreme coordinates.

```json
{
  "success": false,
  "error": "calculation_error",
  "message": "Failed to calculate planetary positions",
  "details": {
    "error_type": "ephemeris_error",
    "coordinates": {"latitude": 89.9, "longitude": 0.0}
  }
}
```

### `internal_error`
Unexpected server error. These should be rare and indicate a bug in the API.

```json
{
  "success": false,
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "details": {
    "error_id": "uuid-string-for-tracking"
  }
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Rate Limit**: 100 requests per minute per IP address
- **Burst Limit**: 10 requests per second

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701944460
X-RateLimit-Retry-After: 60
```

When rate limited, you'll receive a `429 Too Many Requests` response:

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

## Pagination

For endpoints that return multiple results (future feature), pagination follows the standard pattern:

```json
{
  "success": true,
  "data": {
    "items": [ /* ... results ... */ ],
    "pagination": {
      "total": 150,
      "page": 1,
      "per_page": 25,
      "total_pages": 6,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## Request/Response Examples

### Successful Chart Calculation

**Request:**
```http
POST /ephemeris/natal HTTP/1.1
Host: api.meridianephemeris.com
Content-Type: application/json

{
  "subject": {
    "name": "John Doe",
    "datetime": {"iso_string": "1990-06-15T14:30:00"},
    "latitude": {"decimal": 40.7128},
    "longitude": {"decimal": -74.0060},
    "timezone": {"name": "America/New_York"}
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Process-Time: 0.045
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99

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
        "longitude": 94.123,
        "latitude": 0.001,
        "distance": 1.0156,
        "longitude_speed": 0.9856,
        "latitude_speed": 0.0001,
        "distance_speed": 0.0,
        "sign": "Gemini",
        "sign_longitude": 4.123,
        "house": 10,
        "retrograde": false
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
    }
  },
  "metadata": {
    "calculation_time": "2023-12-07T14:30:00Z",
    "julian_day": 2448079.1041666665,
    "api_version": "1.0.0",
    "processing_time_ms": 45
  }
}
```

### Validation Error

**Request:**
```http
POST /ephemeris/natal HTTP/1.1
Host: api.meridianephemeris.com
Content-Type: application/json

{
  "subject": {
    "name": "",
    "datetime": {"iso_string": "invalid-date"},
    "latitude": {"decimal": 95.0},
    "longitude": {"decimal": -74.0060}
  }
}
```

**Response:**
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "success": false,
  "error": "validation_error",
  "message": "Request validation failed",
  "details": {
    "errors": [
      {
        "loc": ["subject", "name"],
        "msg": "Name cannot be empty",
        "type": "value_error"
      },
      {
        "loc": ["subject", "datetime", "iso_string"],
        "msg": "Invalid ISO 8601 datetime format",
        "type": "value_error"
      },
      {
        "loc": ["subject", "latitude", "decimal"],
        "msg": "Latitude must be between -90 and 90 degrees",
        "type": "value_error"
      },
      {
        "loc": ["subject"],
        "msg": "Timezone is required when datetime is provided",
        "type": "value_error"
      }
    ]
  }
}
```

## API Versioning

The API follows semantic versioning (SemVer). The current version is included in:

- Response metadata: `"api_version": "1.0.0"`
- OpenAPI specification: `"version": "1.0.0"`
- HTTP header: `X-API-Version: 1.0.0`

Future versions may introduce:
- New endpoints (backward compatible)
- Additional response fields (backward compatible)
- Deprecated fields (with advance notice)
- Breaking changes (new major version)

## OpenAPI Specification

The complete API specification is available in OpenAPI 3.1 format:

- **Interactive Documentation**: [/docs](https://api.meridianephemeris.com/docs)
- **ReDoc Documentation**: [/redoc](https://api.meridianephemeris.com/redoc)
- **OpenAPI JSON**: [/openapi.json](https://api.meridianephemeris.com/openapi.json)

## SDK and Client Libraries

Official SDKs are available for popular programming languages:

- **Python**: [meridian-ephemeris](https://pypi.org/project/meridian-ephemeris/)
- **TypeScript/JavaScript**: [meridian-ephemeris-sdk](https://www.npmjs.com/package/meridian-ephemeris-sdk)
- **Go**: [meridian-ephemeris-go](https://github.com/meridian-ephemeris/go-sdk)

These SDKs provide type-safe interfaces, automatic error handling, and convenient wrapper functions for common operations.

## Testing and Development

For testing and development:

1. **Health Check**: Use `/health` to verify API availability
2. **Validation**: Test input validation with invalid data
3. **Rate Limits**: Implement appropriate retry logic
4. **Error Handling**: Handle all documented error types
5. **Timeout**: Set reasonable request timeouts (30-60 seconds for calculations)

## Performance Considerations

- **Caching**: The API implements intelligent caching for repeated calculations
- **Parallel Requests**: Multiple concurrent requests are supported
- **Response Time**: Typical response times are 10-100ms for cached results, 100-500ms for new calculations
- **Payload Size**: Response sizes range from 2-20KB depending on requested data

## Next Steps

- **[Endpoints](endpoints.md)**: Detailed documentation of all API endpoints
- **[Schemas](schemas.md)**: Complete request/response schema documentation
- **[Error Handling](errors.md)**: Comprehensive error handling guide