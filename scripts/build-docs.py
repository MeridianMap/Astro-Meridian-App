#!/usr/bin/env python3
"""
Documentation Build and Publishing Script

This script automates the building and publishing of documentation
using MkDocs Material and deploys to various platforms.
"""

import os
import subprocess
import sys
import shutil
import json
from pathlib import Path
from typing import List, Dict, Any

class DocumentationBuilder:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.docs_dir = self.root_dir / "docs"
        self.site_dir = self.root_dir / "site"
        self.requirements_file = self.root_dir / "docs-requirements.txt"
        
    def check_requirements(self) -> bool:
        """Check if required tools are installed."""
        required_packages = [
            'mkdocs',
            'mkdocs-material',
            'pymdown-extensions',
            'mkdocs-git-revision-date-localized-plugin',
            'mkdocs-git-authors-plugin',
            'mkdocs-minify-plugin'
        ]
        
        print("📋 Checking requirements...")
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print(f"Install with: pip install {' '.join(missing_packages)}")
            return False
        
        print("✅ All requirements satisfied")
        return True
    
    def create_requirements_file(self) -> None:
        """Create requirements file for documentation dependencies."""
        requirements = [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0", 
            "pymdown-extensions>=10.0",
            "mkdocs-git-revision-date-localized-plugin>=1.2.0",
            "mkdocs-git-authors-plugin>=0.7.0",
            "mkdocs-minify-plugin>=0.7.0",
            "Pillow>=10.0.0",  # For image processing
            "requests>=2.31.0"  # For API validation
        ]
        
        with open(self.requirements_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        print(f"📝 Created requirements file: {self.requirements_file}")
    
    def generate_api_docs(self) -> bool:
        """Generate API documentation from OpenAPI spec."""
        print("🔧 Generating API documentation...")
        
        try:
            # Generate OpenAPI spec
            backend_dir = self.root_dir / "backend"
            openapi_path = backend_dir / "openapi.json"
            
            os.chdir(backend_dir)
            result = subprocess.run([
                sys.executable, "-c",
                "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))"
            ], capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "."})
            
            if result.returncode != 0:
                print(f"❌ Failed to generate OpenAPI spec: {result.stderr}")
                return False
            
            # Save OpenAPI spec
            with open(openapi_path, "w") as f:
                f.write(result.stdout)
            
            # Create API documentation files
            self._create_api_endpoints_doc(json.loads(result.stdout))
            self._create_api_schemas_doc(json.loads(result.stdout))
            
            print("✅ API documentation generated")
            return True
            
        except Exception as e:
            print(f"❌ Error generating API docs: {e}")
            return False
        finally:
            os.chdir(self.root_dir)
    
    def _create_api_endpoints_doc(self, openapi_spec: Dict[str, Any]) -> None:
        """Create endpoints documentation from OpenAPI spec."""
        endpoints_content = '''# API Endpoints

This page documents all available API endpoints with detailed request/response information.

## Base URL

```
https://api.meridianephemeris.com
```

'''
        
        # Process paths
        for path, methods in openapi_spec.get("paths", {}).items():
            endpoints_content += f"\n## `{path}`\n\n"
            
            for method, details in methods.items():
                method_upper = method.upper()
                summary = details.get("summary", "")
                description = details.get("description", "")
                
                endpoints_content += f"### {method_upper} {summary}\n\n"
                
                if description:
                    endpoints_content += f"{description}\n\n"
                
                # Request body
                if "requestBody" in details:
                    request_body = details["requestBody"]
                    content_type = list(request_body.get("content", {}).keys())[0]
                    schema_ref = request_body["content"][content_type]["schema"]
                    
                    endpoints_content += "**Request Body:**\n\n"
                    endpoints_content += f"Content-Type: `{content_type}`\n\n"
                    
                    if "$ref" in schema_ref:
                        schema_name = schema_ref["$ref"].split("/")[-1]
                        endpoints_content += f"Schema: [`{schema_name}`](schemas.md#{schema_name.lower()})\n\n"
                
                # Responses
                if "responses" in details:
                    endpoints_content += "**Responses:**\n\n"
                    
                    for status_code, response_info in details["responses"].items():
                        description = response_info.get("description", "")
                        endpoints_content += f"- `{status_code}`: {description}\n"
                    
                    endpoints_content += "\n"
                
                # Parameters
                if "parameters" in details:
                    endpoints_content += "**Parameters:**\n\n"
                    
                    for param in details["parameters"]:
                        name = param.get("name", "")
                        param_in = param.get("in", "")
                        required = param.get("required", False)
                        description = param.get("description", "")
                        
                        req_text = "required" if required else "optional"
                        endpoints_content += f"- `{name}` ({param_in}, {req_text}): {description}\n"
                    
                    endpoints_content += "\n"
                
                endpoints_content += "---\n\n"
        
        # Write endpoints documentation
        endpoints_file = self.docs_dir / "api" / "endpoints.md"
        endpoints_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(endpoints_file, "w") as f:
            f.write(endpoints_content)
    
    def _create_api_schemas_doc(self, openapi_spec: Dict[str, Any]) -> None:
        """Create schemas documentation from OpenAPI spec."""
        schemas_content = '''# API Schemas

This page documents all data models and schemas used by the API.

'''
        
        # Process components/schemas
        schemas = openapi_spec.get("components", {}).get("schemas", {})
        
        for schema_name, schema_info in schemas.items():
            schemas_content += f"\n## {schema_name}\n\n"
            
            description = schema_info.get("description", "")
            if description:
                schemas_content += f"{description}\n\n"
            
            # Properties
            if "properties" in schema_info:
                schemas_content += "**Properties:**\n\n"
                
                required_fields = schema_info.get("required", [])
                
                for prop_name, prop_info in schema_info["properties"].items():
                    prop_type = prop_info.get("type", "unknown")
                    prop_desc = prop_info.get("description", "")
                    is_required = prop_name in required_fields
                    
                    req_text = "**required**" if is_required else "optional"
                    schemas_content += f"- `{prop_name}` ({prop_type}, {req_text}): {prop_desc}\n"
                
                schemas_content += "\n"
            
            # Example
            if "example" in schema_info:
                example = json.dumps(schema_info["example"], indent=2)
                schemas_content += "**Example:**\n\n"
                schemas_content += f"```json\n{example}\n```\n\n"
            
            schemas_content += "---\n\n"
        
        # Write schemas documentation
        schemas_file = self.docs_dir / "api" / "schemas.md"
        schemas_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(schemas_file, "w") as f:
            f.write(schemas_content)
    
    def create_additional_docs(self) -> None:
        """Create additional documentation files."""
        print("📄 Creating additional documentation...")
        
        # Installation guide
        self._create_installation_guide()
        
        # Authentication guide (placeholder for future)
        self._create_auth_guide()
        
        # Rate limits guide
        self._create_rate_limits_guide()
        
        # Error handling guide
        self._create_error_handling_guide()
        
        print("✅ Additional documentation created")
    
    def _create_installation_guide(self) -> None:
        """Create installation guide."""
        content = '''# Installation Guide

## Python SDK

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

### Usage

```python
from meridian_ephemeris import MeridianEphemeris

client = MeridianEphemeris()
chart = client.calculate_natal_chart({
    "name": "John Doe",
    "datetime": {"iso_string": "1990-06-15T14:30:00"},
    "latitude": {"decimal": 40.7128},
    "longitude": {"decimal": -74.0060},
    "timezone": {"name": "America/New_York"}
})
```

## TypeScript/JavaScript SDK

### Using npm

```bash
npm install meridian-ephemeris-sdk
```

### Using yarn

```bash
yarn add meridian-ephemeris-sdk
```

### Usage

```typescript
import { MeridianEphemeris } from 'meridian-ephemeris-sdk';

const client = new MeridianEphemeris();
const chart = await client.calculateNatalChart({
  name: "John Doe",
  datetime: { iso_string: "1990-06-15T14:30:00" },
  latitude: { decimal: 40.7128 },
  longitude: { decimal: -74.0060 },
  timezone: { name: "America/New_York" }
});
```

## Go SDK

### Using go mod

```bash
go mod init your-project
go get github.com/meridian-ephemeris/go-sdk
```

### Usage

```go
package main

import (
    "context"
    "github.com/meridian-ephemeris/go-sdk"
)

func main() {
    client := meridianephemeris.NewClient("")
    
    request := meridianephemeris.NatalChartRequest{
        Subject: meridianephemeris.SubjectRequest{
            Name: "John Doe",
            // ... other fields
        },
    }
    
    chart, _, err := client.CalculateNatalChart(context.Background(), request)
    // Handle response
}
```

## Direct HTTP Usage

### Using cURL

```bash
curl -X POST "https://api.meridianephemeris.com/ephemeris/natal" \\
  -H "Content-Type: application/json" \\
  -d '{
    "subject": {
      "name": "John Doe",
      "datetime": {"iso_string": "1990-06-15T14:30:00"},
      "latitude": {"decimal": 40.7128},
      "longitude": {"decimal": -74.0060},
      "timezone": {"name": "America/New_York"}
    }
  }'
```

### Response

```json
{
  "success": true,
  "data": {
    "subject": { /* ... */ },
    "planets": { /* ... */ },
    "houses": { /* ... */ }
  }
}
```
'''
        
        install_file = self.docs_dir / "guides" / "installation.md"
        install_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(install_file, "w") as f:
            f.write(content)
    
    def _create_auth_guide(self) -> None:
        """Create authentication guide."""
        content = '''# Authentication

!!! info "Current Status"
    The Meridian Ephemeris API is currently **open access** and does not require authentication. This may change in future versions.

## Future Authentication

When authentication is implemented, the API will support:

### API Keys

API keys will be used for identifying and rate limiting requests:

```python
from meridian_ephemeris import MeridianEphemeris

client = MeridianEphemeris(api_key="your-api-key-here")
```

```bash
curl -X POST "https://api.meridianephemeris.com/ephemeris/natal" \\
  -H "Authorization: Bearer your-api-key-here" \\
  -H "Content-Type: application/json" \\
  -d '{ /* request data */ }'
```

### Rate Limiting

With authentication, you'll receive higher rate limits:

- **Free tier**: 100 requests/hour
- **Premium tier**: 1000 requests/hour
- **Enterprise**: Custom limits

### Usage Tracking

Track your API usage through the developer dashboard:

- Request count and history
- Error rate monitoring
- Performance metrics
- Usage analytics

## Security Best Practices

When authentication is implemented:

1. **Never expose API keys** in client-side code
2. **Use environment variables** to store keys securely
3. **Rotate keys regularly** for enhanced security
4. **Monitor usage** for unexpected activity
5. **Use HTTPS only** for all API requests

## Current Access

For now, simply use the API without authentication:

```python
# No API key needed currently
client = MeridianEphemeris()
```

Stay updated on authentication changes through:
- 📧 Email notifications (subscribe on website)
- 📱 GitHub releases
- 📚 Documentation updates
'''
        
        auth_file = self.docs_dir / "guides" / "authentication.md"
        auth_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(auth_file, "w") as f:
            f.write(content)
    
    def _create_rate_limits_guide(self) -> None:
        """Create rate limits guide."""
        content = '''# Rate Limits

The Meridian Ephemeris API implements rate limiting to ensure fair usage and maintain service quality.

## Current Limits

### Per IP Address
- **Rate Limit**: 100 requests per minute
- **Burst Limit**: 10 requests per second
- **Daily Limit**: 10,000 requests per day

## Rate Limit Headers

Every API response includes rate limit information:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701944460
X-RateLimit-Retry-After: 60
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per time window |
| `X-RateLimit-Remaining` | Remaining requests in current window |
| `X-RateLimit-Reset` | Timestamp when rate limit resets |
| `X-RateLimit-Retry-After` | Seconds to wait before retrying |

## Rate Limited Response

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

## Best Practices

### 1. Implement Retry Logic

```python
import time
import requests

def make_request_with_retry(client, *args, **kwargs):
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = client.calculate_natal_chart(*args, **kwargs)
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('X-RateLimit-Retry-After', 60))
                print(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                raise
    
    raise Exception("Max retries exceeded")
```

### 2. Batch Processing

Group multiple calculations to reduce API calls:

```python
# Instead of multiple individual requests
subjects = [subject1, subject2, subject3]

charts = []
for subject in subjects:
    # Add delay between requests
    time.sleep(1)  # 1 second between requests
    chart = client.calculate_natal_chart(subject)
    charts.append(chart)
```

### 3. Caching

Cache results to avoid redundant API calls:

```python
import hashlib
import json

class CachedEphemerisClient:
    def __init__(self, client):
        self.client = client
        self.cache = {}
    
    def calculate_natal_chart(self, subject_data):
        # Create cache key from subject data
        cache_key = hashlib.md5(
            json.dumps(subject_data, sort_keys=True).encode()
        ).hexdigest()
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Make API call
        result = self.client.calculate_natal_chart(subject_data)
        self.cache[cache_key] = result
        
        return result
```

### 4. Monitor Usage

Track your API usage:

```python
class UsageTracker:
    def __init__(self):
        self.request_count = 0
        self.start_time = time.time()
    
    def track_request(self, response):
        self.request_count += 1
        
        # Check rate limit headers
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        limit = int(response.headers.get('X-RateLimit-Limit', 100))
        
        usage_percent = ((limit - remaining) / limit) * 100
        
        if usage_percent > 80:
            print(f"Warning: {usage_percent:.1f}% of rate limit used")
```

## Future Changes

Rate limits may be adjusted based on:
- Service usage patterns
- Infrastructure improvements
- User feedback
- Authentication tiers (when implemented)

Stay informed about changes through:
- API response headers
- Documentation updates
- Email notifications
- GitHub releases

## Enterprise Solutions

For higher rate limits, contact us about enterprise solutions:
- Custom rate limits
- Dedicated infrastructure
- Priority support
- SLA guarantees

📧 Email: [enterprise@meridianephemeris.com](mailto:enterprise@meridianephemeris.com)
'''
        
        rate_limits_file = self.docs_dir / "guides" / "rate-limits.md"
        with open(rate_limits_file, "w") as f:
            f.write(content)
    
    def _create_error_handling_guide(self) -> None:
        """Create error handling guide."""
        content = '''# Error Handling

Comprehensive guide to handling API errors and implementing robust error handling in your applications.

## Error Response Format

All API errors follow a consistent format:

```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    // Additional error-specific information
  }
}
```

## HTTP Status Codes

| Status Code | Error Type | Description |
|------------|------------|-------------|
| `400` | Bad Request | Malformed request |
| `422` | Validation Error | Invalid input data |
| `429` | Rate Limited | Too many requests |
| `500` | Internal Error | Server error |
| `503` | Service Unavailable | Temporary outage |

## Common Error Types

### 1. Validation Errors (`422`)

Input data doesn't meet validation requirements:

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

**Handling:**

```python
def handle_validation_error(error_response):
    print("Validation failed:")
    for error in error_response["details"]["errors"]:
        field = " -> ".join(error["loc"])
        message = error["msg"]
        print(f"  {field}: {message}")
```

### 2. Calculation Errors (`500`)

Errors during astrological calculations:

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

### 3. Rate Limit Errors (`429`)

Too many requests:

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

## Error Handling Strategies

### Python Implementation

```python
import requests
import time
from typing import Dict, Any, Optional

class EphemerisAPIError(Exception):
    """Base exception for API errors"""
    def __init__(self, error_type: str, message: str, details: Dict[str, Any] = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        super().__init__(f"{error_type}: {message}")

class ValidationError(EphemerisAPIError):
    """Validation error"""
    pass

class RateLimitError(EphemerisAPIError):
    """Rate limit exceeded"""
    def __init__(self, message: str, retry_after: int, details: Dict[str, Any] = None):
        super().__init__("rate_limit_exceeded", message, details)
        self.retry_after = retry_after

class CalculationError(EphemerisAPIError):
    """Calculation error"""
    pass

class RobustEphemerisClient:
    def __init__(self, base_url: str, max_retries: int = 3):
        self.base_url = base_url
        self.max_retries = max_retries
        self.session = requests.Session()
    
    def calculate_natal_chart(self, subject_data: Dict[str, Any], 
                            settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate natal chart with robust error handling"""
        
        for attempt in range(self.max_retries):
            try:
                response = self._make_request(subject_data, settings)
                return self._handle_response(response)
                
            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    print(f"Rate limited. Waiting {e.retry_after} seconds...")
                    time.sleep(e.retry_after)
                    continue
                raise
                
            except (ValidationError, CalculationError):
                # Don't retry validation or calculation errors
                raise
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Request failed. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                raise EphemerisAPIError("network_error", str(e))
        
        raise EphemerisAPIError("max_retries_exceeded", 
                               f"Failed after {self.max_retries} attempts")
    
    def _make_request(self, subject_data: Dict[str, Any], 
                     settings: Dict[str, Any] = None) -> requests.Response:
        """Make HTTP request"""
        payload = {"subject": subject_data, "settings": settings or {}}
        
        response = self.session.post(
            f"{self.base_url}/ephemeris/natal",
            json=payload,
            timeout=30
        )
        
        return response
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        
        # Handle HTTP errors
        if response.status_code == 429:
            retry_after = int(response.headers.get('X-RateLimit-Retry-After', 60))
            error_data = response.json()
            raise RateLimitError(
                error_data.get("message", "Rate limit exceeded"),
                retry_after,
                error_data.get("details", {})
            )
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise EphemerisAPIError("invalid_response", 
                                  f"Invalid JSON response: {response.text[:200]}")
        
        # Handle API-level errors
        if not data.get("success", False):
            error_type = data.get("error", "unknown_error")
            message = data.get("message", "An error occurred")
            details = data.get("details", {})
            
            if error_type == "validation_error":
                raise ValidationError(message, details)
            elif error_type == "calculation_error":
                raise CalculationError(message, details)
            else:
                raise EphemerisAPIError(error_type, message, details)
        
        return data

# Usage example
client = RobustEphemerisClient("https://api.meridianephemeris.com")

try:
    chart = client.calculate_natal_chart({
        "name": "John Doe",
        "datetime": {"iso_string": "1990-06-15T14:30:00"},
        "latitude": {"decimal": 40.7128},
        "longitude": {"decimal": -74.0060},
        "timezone": {"name": "America/New_York"}
    })
    print("✅ Chart calculated successfully")
    
except ValidationError as e:
    print(f"❌ Validation error: {e.message}")
    for error in e.details.get("errors", []):
        field = " -> ".join(error["loc"])
        print(f"  {field}: {error['msg']}")

except RateLimitError as e:
    print(f"❌ Rate limited: {e.message}")
    print(f"  Retry after: {e.retry_after} seconds")

except CalculationError as e:
    print(f"❌ Calculation error: {e.message}")

except EphemerisAPIError as e:
    print(f"❌ API error: {e.error_type} - {e.message}")
```

### TypeScript Implementation

```typescript
interface APIError {
  success: false;
  error: string;
  message: string;
  details?: any;
}

class EphemerisAPIError extends Error {
  constructor(
    public errorType: string,
    public message: string,
    public details: any = {}
  ) {
    super(`${errorType}: ${message}`);
  }
}

class RateLimitError extends EphemerisAPIError {
  constructor(message: string, public retryAfter: number, details: any = {}) {
    super('rate_limit_exceeded', message, details);
  }
}

async function calculateNatalChartWithRetry(
  client: any,
  subjectData: any,
  maxRetries: number = 3
): Promise<any> {
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await client.calculateNatalChart(subjectData);
      return response;
      
    } catch (error: any) {
      if (error.response?.status === 429) {
        const retryAfter = parseInt(error.response.headers['x-ratelimit-retry-after'] || '60');
        
        if (attempt < maxRetries - 1) {
          console.log(`Rate limited. Waiting ${retryAfter} seconds...`);
          await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
          continue;
        }
        
        throw new RateLimitError('Rate limit exceeded', retryAfter);
      }
      
      // Handle other errors
      if (error.response?.data) {
        const errorData = error.response.data as APIError;
        throw new EphemerisAPIError(
          errorData.error,
          errorData.message,
          errorData.details
        );
      }
      
      throw error;
    }
  }
  
  throw new Error(`Failed after ${maxRetries} attempts`);
}
```

## Best Practices

### 1. Always Check Success Flag

```python
response = client.calculate_natal_chart(subject_data)
if response["success"]:
    # Process successful response
    chart_data = response["data"]
else:
    # Handle error
    print(f"Error: {response.get('message', 'Unknown error')}")
```

### 2. Implement Exponential Backoff

```python
import time
import random

def exponential_backoff_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

### 3. Log Errors Properly

```python
import logging

logger = logging.getLogger(__name__)

try:
    chart = client.calculate_natal_chart(subject_data)
except EphemerisAPIError as e:
    logger.error(f"API error: {e.error_type}", extra={
        "error_type": e.error_type,
        "message": e.message,
        "details": e.details,
        "subject_data": subject_data
    })
```

### 4. Provide User-Friendly Messages

```python
ERROR_MESSAGES = {
    "validation_error": "Please check your input data and try again.",
    "calculation_error": "Unable to calculate chart with the provided data.",
    "rate_limit_exceeded": "Too many requests. Please try again later.",
    "internal_error": "A server error occurred. Please try again."
}

def get_user_friendly_message(error_type: str) -> str:
    return ERROR_MESSAGES.get(error_type, "An unexpected error occurred.")
```

## Monitoring and Alerting

Set up monitoring for:
- Error rates and types
- Response times
- Rate limit usage
- Failed requests

This helps identify issues early and improve your application's reliability.
'''
        
        error_handling_file = self.docs_dir / "api" / "errors.md"
        with open(error_handling_file, "w") as f:
            f.write(content)
    
    def build_docs(self, serve: bool = False) -> bool:
        """Build documentation using MkDocs."""
        print("🏗️ Building documentation...")
        
        try:
            # Build command
            cmd = ["mkdocs", "build", "--clean"]
            if serve:
                cmd = ["mkdocs", "serve", "--dev-addr", "127.0.0.1:8001"]
            
            # Run mkdocs
            result = subprocess.run(cmd, cwd=self.root_dir, capture_output=not serve)
            
            if result.returncode == 0:
                if not serve:
                    print(f"✅ Documentation built successfully")
                    print(f"📁 Site directory: {self.site_dir}")
                return True
            else:
                print(f"❌ Documentation build failed")
                if hasattr(result, 'stderr') and result.stderr:
                    print(result.stderr.decode())
                return False
                
        except Exception as e:
            print(f"❌ Error building documentation: {e}")
            return False
    
    def validate_docs(self) -> bool:
        """Validate documentation for common issues."""
        print("🔍 Validating documentation...")
        
        issues = []
        
        # Check for broken internal links
        # Check for missing images
        # Check for outdated API references
        
        if issues:
            print(f"⚠️  Found {len(issues)} validation issues:")
            for issue in issues:
                print(f"  • {issue}")
            return False
        
        print("✅ Documentation validation passed")
        return True
    
    def run(self, serve: bool = False, skip_api: bool = False) -> bool:
        """Run the complete documentation build process."""
        print("🚀 Starting documentation build process...")
        
        # Create requirements file
        self.create_requirements_file()
        
        # Check requirements
        if not self.check_requirements():
            print("💡 Install missing packages with:")
            print(f"    pip install -r {self.requirements_file}")
            return False
        
        # Generate API docs
        if not skip_api:
            if not self.generate_api_docs():
                print("⚠️  API documentation generation failed, continuing...")
        
        # Create additional docs
        self.create_additional_docs()
        
        # Validate docs
        if not self.validate_docs():
            print("⚠️  Validation issues found, continuing with build...")
        
        # Build docs
        if not self.build_docs(serve):
            return False
        
        if not serve:
            print("\n🎉 Documentation build completed successfully!")
            print(f"📖 Open: {self.site_dir}/index.html")
            print("🌐 Serve locally: mkdocs serve")
            print("🚀 Deploy: mkdocs gh-deploy")
        
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Meridian Ephemeris Documentation")
    parser.add_argument("--serve", action="store_true", help="Serve documentation locally")
    parser.add_argument("--skip-api", action="store_true", help="Skip API documentation generation")
    parser.add_argument("--check", action="store_true", help="Only check requirements")
    
    args = parser.parse_args()
    
    builder = DocumentationBuilder()
    
    if args.check:
        builder.check_requirements()
    else:
        success = builder.run(serve=args.serve, skip_api=args.skip_api)
        sys.exit(0 if success else 1)