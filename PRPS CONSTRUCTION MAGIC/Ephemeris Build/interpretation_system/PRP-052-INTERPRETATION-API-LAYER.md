# PRP-052: Interpretation API Layer

## Goal
Implement a comprehensive FastAPI-based interpretation API layer that integrates seamlessly with the existing Meridian ephemeris system, maintaining <100ms response times and following established architectural patterns.

### Feature Goal
Create RESTful interpretation endpoints that transform ephemeris calculation results into structured astrological interpretations, supporting multiple detail levels, traditions, and output formats while maintaining full compatibility with existing API patterns.

### Deliverable
Complete FastAPI router implementation with interpretation endpoints, request/response models, error handling, metrics integration, and comprehensive API documentation.

### Success Definition
- Interpretation API endpoints respond in <100ms median time
- Seamless integration with existing ephemeris endpoints  
- Consistent error handling and response formats
- Comprehensive OpenAPI documentation with examples
- Full metrics integration and performance monitoring
- Support for multiple interpretation traditions and detail levels

---

## Context

### YAML Structure Reference
```yaml
# Existing FastAPI patterns from research
meridian_api_patterns:
  router_organization:
    pattern: "Domain-specific routers with clear prefixes and tags"
    location: "backend/app/api/routes/ephemeris.py"
    structure: |
      router = APIRouter(
        prefix="/ephemeris", 
        tags=["ephemeris"],
        responses={400, 422, 500 error models}
      )
  
  request_models:
    pattern: "Flexible input with multiple format support"
    location: "backend/app/api/models/schemas.py"
    validation: "Pydantic v2 with ConfigDict and model_validator"
    example: "CoordinateInput supports decimal/dms/components"
    
  response_models:
    success_pattern: "success: bool + structured data"
    error_pattern: "ErrorResponse with success/error/message/details"
    headers: "X-Calculation-Time, X-Features-Count for performance"
    
  error_handling:
    global_handlers: "RequestValidationError, calculation errors"
    location: "backend/app/main.py exception handlers"
    format: "Consistent ErrorResponse model with timestamp/path"
    
  monitoring_integration:
    decorators: "@timed_calculation decorator for performance"
    location: "backend/app/core/monitoring/metrics.py"
    manual_recording: "get_metrics().record_calculation() calls"

# Interpretation API specific requirements
interpretation_context:
  input_sources:
    ephemeris_data: "Existing NatalChartResponse structure"
    chart_data: "Planets, houses, angles, aspects from ephemeris"
    user_preferences: "Interpretation level, tradition, format, focus"
    
  integration_points:
    content_system: "backend/app/interpretation/content_loader.py"
    template_engine: "backend/app/interpretation/template_processor.py" 
    service_layer: "backend/app/interpretation/service.py"
    cache_integration: "backend/app/interpretation/cache.py"

# Performance requirements from CLAUDE.md
performance_standards:
  response_time: "<100ms median for interpretation generation"
  cache_integration: "Redis cache hit rate >70%"
  monitoring: "Prometheus metrics for all endpoints"
  error_rate: "<1% under normal load"
```

### External Resources
- **FastAPI Best Practices**: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- **Pydantic V2 Validation**: https://docs.pydantic.dev/latest/concepts/validators/
- **OpenAPI Documentation**: https://spec.openapis.org/oas/v3.0.3#operation-object
- **Async Performance Patterns**: https://fastapi.tiangolo.com/async/
- **Request Validation**: https://fastapi.tiangolo.com/tutorial/request-validation/

---

## Implementation Tasks

### Task 1: Interpretation Router Setup
**Dependency**: None  
**Location**: `backend/app/api/routes/interpretation.py`

Create interpretation router following existing patterns from `routes/ephemeris.py`:

```python
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Response
from app.api.models.schemas import ErrorResponse
from app.interpretation.models import (
    InterpretationRequest, InterpretationResponse,
    InterpretationOptions, ChartInterpretationRequest
)
from app.interpretation.service import InterpretationService
from app.core.monitoring.metrics import timed_calculation, get_metrics

router = APIRouter(
    prefix="/interpretation",
    tags=["interpretation"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid chart data or parameters"},
        422: {"model": ErrorResponse, "description": "Request validation failed"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Interpretation generation failed"},
    }
)

# Initialize service following existing pattern
interpretation_service = InterpretationService()

@router.post(
    "/natal",
    response_model=InterpretationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Natal Chart Interpretation",
    description="""Generate comprehensive astrological interpretation from natal chart data."""
)
@timed_calculation("natal_interpretation")
async def generate_natal_interpretation(
    request: ChartInterpretationRequest,
    response: Response
) -> InterpretationResponse:
    """Generate natal chart interpretation following existing performance patterns."""
    pass
```

### Task 2: Request/Response Models
**Dependency**: Task 1  
**Location**: `backend/app/interpretation/models.py`

Implement Pydantic models following existing patterns in `schemas.py`:

```python
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Dict, Any, List, Union
from enum import Enum

class InterpretationLevel(str, Enum):
    """Interpretation detail levels."""
    BASIC = "basic"           # Level 1-2: Technical + basic meaning
    STANDARD = "standard"     # Level 1-3: + psychological insight
    DETAILED = "detailed"     # Level 1-4: + life expression  
    COMPLETE = "complete"     # Level 1-5: + spiritual context

class InterpretationTradition(str, Enum):
    """Astrological traditions."""
    MODERN = "modern"
    TRADITIONAL = "traditional"
    PSYCHOLOGICAL = "psychological"
    EVOLUTIONARY = "evolutionary"

class InterpretationOptions(BaseModel):
    """Interpretation generation options."""
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "level": "detailed",
                "tradition": "psychological",
                "format": "structured",
                "focus": ["personality", "career"],
                "exclude": ["health", "death"]
            }
        }
    )
    
    level: InterpretationLevel = Field(
        InterpretationLevel.STANDARD,
        description="Detail level for interpretation"
    )
    tradition: InterpretationTradition = Field(
        InterpretationTradition.MODERN,
        description="Astrological tradition to follow"
    )
    format: str = Field("structured", description="Output format")
    focus: Optional[List[str]] = Field(None, description="Life areas to emphasize")
    exclude: Optional[List[str]] = Field(None, description="Topics to avoid")
    include_aspects: bool = Field(True, description="Include aspect interpretations")
    include_patterns: bool = Field(True, description="Include chart pattern analysis")

class ChartInterpretationRequest(BaseModel):
    """Request for chart interpretation following existing validation patterns."""
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "chart_data": {
                    "subject": {"name": "John Doe", "datetime": "1990-06-15T14:30:00-04:00"},
                    "planets": {"Sun": {"sign": "Gemini", "house": 9}},
                    "aspects": [{"object1": "Sun", "object2": "Moon", "aspect": "Square"}]
                },
                "options": {"level": "detailed", "tradition": "psychological"}
            }
        }
    )
    
    chart_data: Dict[str, Any] = Field(
        ...,
        description="Chart data from ephemeris calculation (NatalChartResponse format)"
    )
    options: InterpretationOptions = Field(
        InterpretationOptions(),
        description="Interpretation generation options"
    )
    
    @model_validator(mode='after')
    def validate_chart_data(self):
        """Validate chart data contains required elements."""
        required_keys = ["subject", "planets"]
        if not all(key in self.chart_data for key in required_keys):
            raise ValueError("Chart data must contain subject and planets")
        return self

class InterpretationResponse(BaseModel):
    """Interpretation response following existing success/error pattern."""
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "success": True,
                "interpretation": {
                    "chart_summary": "Overview text...",
                    "planets": {"Sun": {"basic": "...", "detailed": "..."}},
                    "patterns": [{"name": "T-Square", "interpretation": "..."}]
                },
                "metadata": {
                    "processing_time_ms": 45.2,
                    "content_version": "1.0.0",
                    "tradition_used": "psychological"
                }
            }
        }
    )
    
    success: bool = Field(True, description="Request success status")
    interpretation: Dict[str, Any] = Field(..., description="Generated interpretation content")
    metadata: Dict[str, Any] = Field(..., description="Processing and version metadata")
```

### Task 3: Service Integration Layer
**Dependency**: Task 2  
**Location**: `backend/app/interpretation/service.py`

Create service layer following existing patterns from `services/ephemeris_service.py`:

```python
from typing import Dict, Any
from datetime import datetime
from app.interpretation.content_loader import InterpretationContentLoader
from app.interpretation.template_processor import TemplateProcessor
from app.interpretation.cache import InterpretationCache
from app.core.monitoring.metrics import get_metrics
from app.api.models.schemas import ErrorResponse

class InterpretationService:
    """High-level interpretation service following existing service patterns."""
    
    def __init__(self):
        self.content_loader = InterpretationContentLoader()
        self.template_processor = TemplateProcessor()
        self.cache = InterpretationCache()
        self.metrics = get_metrics()
    
    async def generate_chart_interpretation(
        self,
        chart_data: Dict[str, Any],
        options: InterpretationOptions
    ) -> InterpretationResponse:
        """Generate complete chart interpretation with caching and error handling."""
        start_time = datetime.now()
        
        try:
            # Generate cache key from chart data and options
            cache_key = self._generate_cache_key(chart_data, options)
            
            # Try cache first
            cached_result = await self.cache.get_interpretation(cache_key)
            if cached_result:
                return cached_result
            
            # Generate interpretation
            interpretation_content = await self._build_interpretation(chart_data, options)
            
            # Create response
            response = InterpretationResponse(
                success=True,
                interpretation=interpretation_content,
                metadata=self._create_metadata(start_time, options)
            )
            
            # Cache result
            await self.cache.cache_interpretation(cache_key, response)
            
            # Record metrics
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.record_calculation("interpretation_generation", duration, True)
            
            return response
            
        except Exception as e:
            self.metrics.record_calculation("interpretation_generation", 0, False)
            raise InterpretationError(f"Failed to generate interpretation: {str(e)}") from e
    
    def create_error_response(self, exception: Exception) -> ErrorResponse:
        """Create consistent error response following existing pattern."""
        return ErrorResponse(
            success=False,
            error=type(exception).__name__.lower(),
            message=str(exception),
            details={"timestamp": datetime.utcnow().isoformat() + 'Z'}
        )
```

### Task 4: Error Handling Integration
**Dependency**: Task 3  
**Location**: Update `backend/app/main.py`

Add interpretation-specific exception handling following existing patterns:

```python
# Add to existing exception handlers in main.py
from app.interpretation.exceptions import InterpretationError, ContentNotFoundError

@app.exception_handler(InterpretationError)
async def interpretation_exception_handler(request: Request, exc: InterpretationError):
    """Handle interpretation generation errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "interpretation_error",
            "message": str(exc),
            "details": {
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "path": request.url.path
            }
        }
    )

@app.exception_handler(ContentNotFoundError)
async def content_not_found_handler(request: Request, exc: ContentNotFoundError):
    """Handle missing interpretation content."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": "content_not_found",
            "message": str(exc),
            "details": {"content_type": exc.content_type, "identifier": exc.identifier}
        }
    )
```

### Task 5: Additional Specialized Endpoints
**Dependency**: Task 4  
**Location**: `backend/app/api/routes/interpretation.py` (extend)

Add specialized interpretation endpoints:

```python
@router.get(
    "/element/{element_name}",
    response_model=Dict[str, Any],
    summary="Get Element Interpretation",
    description="Get interpretation for a specific astrological element"
)
async def get_element_interpretation(element_name: str) -> Dict[str, Any]:
    """Get element interpretation following existing lookup pattern."""
    pass

@router.post(
    "/aspects",
    response_model=Dict[str, Any], 
    summary="Interpret Aspect List",
    description="Generate interpretations for a list of aspects"
)
async def interpret_aspects(aspects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Interpret aspects following batch processing patterns."""
    pass

@router.get(
    "/patterns/{pattern_name}",
    response_model=Dict[str, Any],
    summary="Get Pattern Interpretation", 
    description="Get interpretation for chart patterns (T-Square, Grand Trine, etc.)"
)
async def get_pattern_interpretation(pattern_name: str) -> Dict[str, Any]:
    """Get chart pattern interpretation."""
    pass
```

### Task 6: API Documentation Enhancement
**Dependency**: Task 5  
**Location**: `backend/app/api/routes/interpretation.py`

Add comprehensive API documentation following existing patterns:

```python
@router.get(
    "/schemas/request",
    summary="Get Interpretation Request Schema",
    description="Get JSON schema and examples for interpretation requests"
)
async def get_interpretation_request_schema():
    """Return request schema with examples following existing documentation pattern."""
    return {
        "schema": ChartInterpretationRequest.model_json_schema(),
        "examples": {
            "basic_request": {
                "chart_data": {"subject": {...}, "planets": {...}},
                "options": {"level": "basic", "tradition": "modern"}
            },
            "detailed_request": {
                "chart_data": {"subject": {...}, "planets": {...}, "aspects": [...]},
                "options": {
                    "level": "complete",
                    "tradition": "psychological",
                    "focus": ["career", "relationships"],
                    "exclude": ["health"]
                }
            }
        }
    }

@router.get(
    "/info/traditions",
    summary="Get Available Traditions",
    description="List all supported astrological traditions"
)
async def get_available_traditions():
    """Return available interpretation traditions."""
    return {
        "traditions": [
            {
                "name": "modern",
                "description": "Modern psychological astrology approach",
                "features": ["psychological insights", "growth orientation"]
            },
            {
                "name": "traditional",
                "description": "Classical astrological methods",
                "features": ["essential dignities", "traditional rulerships"]
            }
        ]
    }
```

### Task 7: Main App Router Registration
**Dependency**: All previous tasks  
**Location**: `backend/app/main.py`

Register interpretation router following existing patterns:

```python
# Add to existing router includes in main.py
from app.api.routes.interpretation import router as interpretation_router

app.include_router(interpretation_router, prefix="/api/v1")

# Update OpenAPI tags
tags_metadata = [
    {
        "name": "interpretation",
        "description": "Astrological interpretation generation endpoints",
        "externalDocs": {
            "description": "Interpretation system documentation",
            "url": "/docs/interpretation"
        }
    },
    # ... existing tags
]
```

---

## Validation Gates

### API Functionality Validation
```bash
# Test all interpretation endpoints
cd backend && python -m pytest tests/api/routes/test_interpretation.py -v
# Verify request/response model validation
# Confirm error handling consistency
```

### Performance Validation
```bash
# Verify <100ms response time standard
python scripts/test_interpretation_api_performance.py
# Confirm metrics integration working
# Test cache hit rate improvements
```

### Integration Validation
```bash
# Test integration with existing ephemeris endpoints
cd backend && python -m pytest tests/integration/test_interpretation_api_integration.py -v
# Verify seamless data flow from ephemeris to interpretation
# Confirm existing API functionality unchanged
```

### Documentation Validation
```bash
# Verify OpenAPI schema generation
curl http://localhost:8000/docs/openapi.json | jq '.paths."/api/v1/interpretation"'
# Check API documentation completeness
# Validate example requests/responses
```

---

## Final Validation Checklist

- [ ] Interpretation router follows existing FastAPI patterns from ephemeris routes
- [ ] Request/response models use consistent Pydantic validation patterns
- [ ] Error handling integrates with existing global exception handlers
- [ ] All endpoints include comprehensive OpenAPI documentation
- [ ] Metrics integration uses existing @timed_calculation decorators
- [ ] Service layer follows established abstraction patterns
- [ ] Cache integration maintains performance standards (<100ms)
- [ ] API responses include performance headers (X-Calculation-Time)
- [ ] Specialized endpoints support multiple interpretation traditions
- [ ] Router registration follows existing main.py patterns

**Confidence Score**: 9/10 for one-pass implementation success

**Critical Dependencies**:
- Interpretation service layer (PRP-055) must be operational
- Content system (PRP-051) must provide interpretation data
- Template processor (PRP-054) must handle content formatting
- Existing FastAPI application must be running with ephemeris routes