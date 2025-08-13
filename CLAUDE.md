# Meridian Ephemeris Development Guide for AI Agents

## 🎯 Project Philosophy & Standards

### Core Principles
- **Swiss Ephemeris as Gold Standard**: All astronomical calculations must use Swiss Ephemeris as the authoritative source
- **Performance-First Architecture**: Sub-100ms median response times, 10x batch processing improvements
- **Production-Ready Code**: Comprehensive error handling, monitoring integration, and validation
- **Backwards Compatibility**: Maintain API compatibility while adding new features
- **Test-Driven Development**: >90% test coverage with performance benchmarks

### Quality Gates
Before any code integration, ensure:
- [ ] All tests pass (`pytest backend/tests/`)
- [ ] Performance benchmarks meet targets (`pytest backend/tests/benchmarks/`)
- [ ] API documentation is auto-generated and accurate
- [ ] Monitoring metrics are properly instrumented
- [ ] Error handling follows established patterns

## 🏗️ Architecture Overview

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │────│  Core Engine     │────│ Swiss Ephemeris │
│   (REST API)    │    │  (Calculations)  │    │  (Calculations) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       
         │              ┌──────────────────┐             
         └──────────────│  Redis Cache     │             
                        │  (Performance)   │             
                        └──────────────────┘             
                                 │                       
                        ┌──────────────────┐             
                        │  Prometheus      │             
                        │  (Monitoring)    │             
                        └──────────────────┘             
```

### Key Directories
- `backend/app/api/` - FastAPI routes and request/response models
- `backend/app/core/ephemeris/` - Core calculation engine
- `backend/app/core/performance/` - Performance optimizations
- `backend/app/core/monitoring/` - Metrics and monitoring
- `backend/tests/` - Test suites and benchmarks
- `docs/` - MkDocs documentation site

## 🚀 Development Patterns

### 1. Adding New API Endpoints

**Template Pattern:**
```python
from fastapi import APIRouter, HTTPException, status
from app.api.models.schemas import YourRequestModel, YourResponseModel
from app.core.monitoring.metrics import timed_calculation, get_metrics

router = APIRouter(prefix="/ephemeris", tags=["ephemeris"])

@router.post(
    "/your-endpoint", 
    response_model=YourResponseModel,
    summary="Brief description",
    description="Detailed description with examples"
)
@timed_calculation("your_calculation_type")
async def your_endpoint(request: YourRequestModel):
    """
    Calculate [description]
    
    Args:
        request: Your request model with validation
        
    Returns:
        YourResponseModel: Calculated results
        
    Raises:
        HTTPException: For validation or calculation errors
    """
    try:
        # Input validation
        validated_data = request.dict()
        
        # Perform calculation
        result = perform_your_calculation(validated_data)
        
        # Record metrics
        metrics = get_metrics()
        metrics.record_calculation("your_calculation_type", duration, True)
        
        return YourResponseModel(
            success=True,
            data=result,
            metadata={
                "calculation_type": "your_calculation_type",
                "processing_time_ms": duration * 1000
            }
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "validation_error", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"Calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "calculation_error", "message": "Calculation failed"}
        )
```

### 2. Core Calculation Pattern

**All calculations must follow this pattern:**
```python
from app.core.ephemeris.classes.cache import get_global_cache
from app.core.ephemeris.classes.redis_cache import get_redis_cache
from app.core.monitoring.metrics import timed_calculation

@timed_calculation("calculation_type")
def calculate_something(input_data: dict) -> dict:
    """
    Perform astrological calculation with caching and error handling.
    """
    # 1. Generate cache key
    cache_key = generate_cache_key(input_data)
    
    # 2. Try Redis cache first
    redis_cache = get_redis_cache()
    cached_result = redis_cache.get("calculation_type", input_data)
    if cached_result:
        return cached_result
    
    # 3. Try memory cache
    memory_cache = get_global_cache()
    cached_result = memory_cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # 4. Perform calculation using Swiss Ephemeris
    try:
        result = perform_swiss_ephemeris_calculation(input_data)
        
        # 5. Cache results
        memory_cache.put(cache_key, result, ttl=3600)
        redis_cache.set("calculation_type", input_data, result, ttl=3600)
        
        return result
        
    except Exception as e:
        logger.error(f"Swiss Ephemeris calculation failed: {e}")
        raise CalculationError(f"Failed to calculate: {e}")
```

### 3. Performance Optimization Requirements

**Batch Processing:**
```python
# Always implement batch versions for multiple calculations
def calculate_multiple_charts(requests: List[ChartRequest]) -> List[ChartResult]:
    """Use BatchCalculator for 10x+ performance improvement."""
    from app.core.ephemeris.tools.batch import BatchCalculator
    
    calculator = BatchCalculator()
    return calculator.calculate_batch_positions(requests)
```

**Memory Optimization:**
```python
# Use structure-of-arrays for large datasets
from app.core.performance.optimizations import MemoryOptimizations

def process_large_dataset(data: List[Dict]) -> Dict[str, np.ndarray]:
    return MemoryOptimizations.optimize_array_operations(data)
```

### 4. Error Handling Standards

**Use consistent error patterns:**
```python
from app.api.models.schemas import ErrorResponse

# Validation errors
raise HTTPException(
    status_code=422,
    detail={
        "success": False,
        "error": "validation_error",
        "message": "Request validation failed",
        "details": {"field": "specific_issue"}
    }
)

# Calculation errors
raise HTTPException(
    status_code=500,
    detail={
        "success": False,
        "error": "calculation_error", 
        "message": "Ephemeris calculation failed",
        "details": {"error_type": "swiss_ephemeris_error"}
    }
)

# Rate limiting
raise HTTPException(
    status_code=429,
    detail={
        "success": False,
        "error": "rate_limit_exceeded",
        "message": "Rate limit exceeded",
        "details": {"retry_after": 60}
    }
)
```

## 🧪 Testing Requirements

### 1. Unit Tests (Required)
```python
import pytest
from app.core.ephemeris.your_module import your_function

class TestYourModule:
    def test_valid_input(self):
        """Test with valid input data."""
        result = your_function(valid_input)
        assert result is not None
        assert result["success"] is True
    
    def test_invalid_input(self):
        """Test error handling with invalid input."""
        with pytest.raises(ValidationError):
            your_function(invalid_input)
    
    def test_edge_cases(self):
        """Test boundary conditions and edge cases."""
        # Test extreme coordinates, dates, etc.
        pass
```

### 2. Performance Benchmarks (Required)
```python
import pytest

class TestYourModulePerformance:
    @pytest.mark.benchmark(group="your_module")
    def test_calculation_performance(self, benchmark):
        """Benchmark must show reasonable performance."""
        result = benchmark(your_function, test_input)
        assert result is not None
    
    def test_batch_performance_improvement(self):
        """Batch operations must be 5x+ faster."""
        # Test individual vs batch processing
        individual_time = time_individual_processing()
        batch_time = time_batch_processing()
        
        improvement = individual_time / batch_time
        assert improvement >= 5.0  # Minimum 5x improvement
```

### 3. Integration Tests (Required for API endpoints)
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_your_endpoint():
    """Test complete API workflow."""
    response = client.post("/ephemeris/your-endpoint", json=test_data)
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "data" in response.json()
```

## 📊 Monitoring Integration

### Required Metrics
Every new feature must include metrics:

```python
from app.core.monitoring.metrics import get_metrics

# Record all calculations
metrics = get_metrics()
metrics.record_calculation("calculation_type", duration, success)

# Record API operations  
metrics.record_api_request(method, endpoint, status_code, duration)

# Record cache operations
metrics.record_cache_operation(operation, cache_type, result)

# Update system health
metrics.update_system_health("component_name", healthy)
```

## 🔄 Data Models & Schemas

### Pydantic Model Standards
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Union, List
from datetime import datetime

class YourRequestModel(BaseModel):
    """
    Request model with comprehensive validation.
    
    Example:
        {
            "name": "John Doe",
            "datetime": {"iso_string": "2000-01-01T12:00:00"},
            "coordinates": {"latitude": 40.7128, "longitude": -74.0060}
        }
    """
    name: str = Field(..., description="Subject name", example="John Doe")
    datetime: DateTimeInput = Field(..., description="Birth datetime")
    coordinates: CoordinateInput = Field(..., description="Birth coordinates")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class YourResponseModel(BaseModel):
    """Response model with complete data structure."""
    success: bool = Field(..., description="Request success status")
    data: Optional[dict] = Field(None, description="Calculation results")
    metadata: Optional[dict] = Field(None, description="Processing metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {"result": "calculation_data"},
                "metadata": {"processing_time_ms": 45.2}
            }
        }
```

## 🚨 Critical Requirements

### Before Submitting Any Code:

1. **Performance Validation**
   ```bash
   # Run performance validation
   python scripts/validate-performance.py
   ```

2. **Complete Test Suite**
   ```bash
   # All tests must pass
   cd backend && python -m pytest tests/ -v
   
   # Benchmarks must meet targets
   python -m pytest tests/benchmarks/ --benchmark-only
   ```

3. **API Documentation**
   ```bash
   # Generate updated API docs
   python scripts/build-docs.py
   ```

4. **Code Quality**
   ```bash
   # Linting and formatting
   ruff check backend/
   ruff format backend/
   
   # Type checking
   mypy backend/app/
   ```

## 🎯 Performance Targets (Non-Negotiable)

- **API Response Time**: <100ms median for all endpoints
- **Batch Performance**: 5x+ improvement over individual processing
- **Cache Hit Rate**: >70% under realistic load
- **Memory Efficiency**: <1MB per calculation
- **Test Coverage**: >90% for all new code
- **Error Rate**: <1% under normal load

## 📋 Common Pitfalls to Avoid

1. **Don't bypass caching** - Always implement Redis + memory caching
2. **Don't ignore error handling** - Follow established error patterns
3. **Don't skip performance tests** - Benchmark every calculation
4. **Don't break backwards compatibility** - Maintain existing API contracts
5. **Don't forget monitoring** - Instrument all new functionality
6. **Don't hardcode values** - Use configuration and environment variables

## 🔗 Key Files to Study

**Before implementing new features, review:**
- `backend/app/api/routes/ephemeris.py` - API pattern examples
- `backend/app/core/ephemeris/charts/natal.py` - Calculation patterns
- `backend/app/core/monitoring/metrics.py` - Monitoring integration
- `backend/tests/api/routes/test_ephemeris.py` - Testing patterns
- `backend/app/core/performance/optimizations.py` - Performance patterns

## 🆘 Getting Help

When in doubt:
1. **Follow existing patterns** in the codebase
2. **Maintain performance standards** - never compromise on speed
3. **Test comprehensively** - unit, integration, and performance tests
4. **Document thoroughly** - update API docs and examples
5. **Monitor everything** - add metrics for observability

Remember: The goal is to maintain the high performance and reliability standards while adding powerful new capabilities to the Meridian Ephemeris system! 🚀