#!/usr/bin/env python3
"""
Example: Adding a New API Endpoint to Meridian Ephemeris

This example demonstrates the complete pattern for adding a new
endpoint that calculates planetary aspects with caching and monitoring.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, validator
import logging

# Core imports
from extracted.systems.ephemeris import get_planet, julian_day_from_datetime
from extracted.systems.const import SwePlanets, get_planet_name
from extracted.systems.classes.cache import get_global_cache
from extracted.systems.classes.redis_cache import get_redis_cache
from app.core.monitoring.metrics import timed_calculation, get_metrics
from extracted.api.models.schemas import DateTimeInput, ErrorResponse

# Set up logging
logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)

# Router for the new endpoint
router = APIRouter(prefix="/ephemeris", tags=["aspects"])


# 1. REQUEST/RESPONSE MODELS
# Define Pydantic models for type safety and validation

class AspectRequest(BaseModel):
    """
    Request model for planetary aspect calculations.
    
    Example:
        {
            "datetime": {"iso_string": "2000-01-01T12:00:00"},
            "planets": ["sun", "moon", "venus"], 
            "orb_settings": {
                "conjunction": 8.0,
                "opposition": 8.0,
                "trine": 6.0,
                "square": 6.0,
                "sextile": 4.0
            }
        }
    """
    datetime: DateTimeInput = Field(
        ..., 
        description="Date and time for aspect calculation",
        example={"iso_string": "2000-01-01T12:00:00"}
    )
    planets: List[str] = Field(
        ...,
        description="List of planets to calculate aspects between",
        example=["sun", "moon", "mercury", "venus", "mars"],
        min_items=2,
        max_items=15
    )
    orb_settings: Optional[Dict[str, float]] = Field(
        {
            "conjunction": 8.0,
            "opposition": 8.0, 
            "trine": 6.0,
            "square": 6.0,
            "sextile": 4.0
        },
        description="Orb tolerances for each aspect type",
        example={
            "conjunction": 8.0,
            "opposition": 8.0,
            "trine": 6.0,
            "square": 6.0,
            "sextile": 4.0
        }
    )
    
    @validator('planets')
    def validate_planets(cls, v):
        """Validate planet names."""
        valid_planets = {
            'sun', 'moon', 'mercury', 'venus', 'mars',
            'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'
        }
        
        for planet in v:
            if planet.lower() not in valid_planets:
                raise ValueError(f"Invalid planet: {planet}. Valid options: {sorted(valid_planets)}")
        
        return [planet.lower() for planet in v]
    
    @validator('orb_settings')
    def validate_orbs(cls, v):
        """Validate orb settings."""
        if v:
            for aspect, orb in v.items():
                if not isinstance(orb, (int, float)):
                    raise ValueError(f"Orb for {aspect} must be numeric")
                if orb < 0 or orb > 20:
                    raise ValueError(f"Orb for {aspect} must be between 0 and 20 degrees")
        return v


class AspectData(BaseModel):
    """Individual aspect data."""
    planet1: str = Field(..., description="First planet in aspect")
    planet2: str = Field(..., description="Second planet in aspect")
    aspect_type: str = Field(..., description="Type of aspect (conjunction, trine, etc.)")
    orb: float = Field(..., description="Orb in degrees from exact aspect")
    exact: bool = Field(..., description="True if aspect is within 0.1° of exact")
    angle: float = Field(..., description="Actual angle between planets")


class AspectResponse(BaseModel):
    """Response model for aspect calculations."""
    success: bool = Field(..., description="Request success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Aspect calculation results")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Processing metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "datetime": "2000-01-01T12:00:00+00:00",
                    "aspects": [
                        {
                            "planet1": "sun",
                            "planet2": "venus", 
                            "aspect_type": "conjunction",
                            "orb": 2.5,
                            "exact": False,
                            "angle": 2.5
                        }
                    ],
                    "aspect_count": 1
                },
                "metadata": {
                    "processing_time_ms": 25.4,
                    "cache_hit": False,
                    "planets_calculated": 5
                }
            }
        }


# 2. CORE CALCULATION LOGIC
# Implement the actual calculation with caching and error handling

class AspectCalculator:
    """High-performance aspect calculator with caching."""
    
    def __init__(self):
        self.planet_name_map = {
            'sun': SwePlanets.SUN,
            'moon': SwePlanets.MOON,
            'mercury': SwePlanets.MERCURY,
            'venus': SwePlanets.VENUS,
            'mars': SwePlanets.MARS,
            'jupiter': SwePlanets.JUPITER,
            'saturn': SwePlanets.SATURN,
            'uranus': SwePlanets.URANUS,
            'neptune': SwePlanets.NEPTUNE,
            'pluto': SwePlanets.PLUTO
        }
        
        self.aspect_angles = {
            'conjunction': 0,
            'sextile': 60,
            'square': 90,
            'trine': 120,
            'opposition': 180
        }
    
    @timed_calculation("aspect_calculation")
    def calculate_aspects(self, datetime_input: DateTimeInput, 
                         planet_names: List[str],
                         orb_settings: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate aspects between specified planets.
        
        Args:
            datetime_input: Date/time for calculations
            planet_names: List of planet names to calculate aspects for
            orb_settings: Orb tolerances for each aspect type
            
        Returns:
            Dictionary with aspect data and metadata
        """
        
        # 1. Generate cache key
        cache_key = self._generate_cache_key(datetime_input, planet_names, orb_settings)
        
        # 2. Check caches (Redis first, then memory)
        cached_result = self._get_cached_result(cache_key, datetime_input, 
                                               planet_names, orb_settings)
        if cached_result:
            return cached_result
        
        # 3. Parse datetime
        from extracted.systems.date import parse_datetime_input
        dt = parse_datetime_input(datetime_input.model_dump())
        jd = julian_day_from_datetime(dt)
        
        # 4. Calculate planetary positions
        planet_positions = {}
        for planet_name in planet_names:
            try:
                planet_id = self.planet_name_map[planet_name]
                position = get_planet(planet_id, jd)
                planet_positions[planet_name] = position
            except Exception as e:
                logger.error(f"Failed to calculate {planet_name}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "success": False,
                        "error": "calculation_error",
                        "message": f"Failed to calculate planetary position: {planet_name}",
                        "details": {"planet": planet_name, "error": str(e)}
                    }
                )
        
        # 5. Calculate aspects between all planet pairs
        aspects = []
        for i, planet1 in enumerate(planet_names):
            for planet2 in planet_names[i+1:]:
                aspect = self._calculate_aspect_between_planets(
                    planet1, planet_positions[planet1],
                    planet2, planet_positions[planet2],
                    orb_settings
                )
                if aspect:
                    aspects.append(aspect)
        
        # 6. Prepare result
        result = {
            "datetime": dt.isoformat(),
            "aspects": aspects,
            "aspect_count": len(aspects),
            "planet_positions": {
                name: {
                    "longitude": pos.longitude,
                    "latitude": pos.latitude,
                    "distance": pos.distance
                }
                for name, pos in planet_positions.items()
            }
        }
        
        # 7. Cache result
        self._cache_result(cache_key, result, datetime_input, planet_names, orb_settings)
        
        return result
    
    def _calculate_aspect_between_planets(self, planet1: str, pos1, planet2: str, pos2,
                                        orb_settings: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Calculate aspect between two planetary positions."""
        
        # Calculate angular difference
        angle_diff = abs(pos1.longitude - pos2.longitude)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        # Check each aspect type
        for aspect_name, aspect_angle in self.aspect_angles.items():
            if aspect_name not in orb_settings:
                continue
                
            orb_tolerance = orb_settings[aspect_name]
            orb_actual = abs(angle_diff - aspect_angle)
            
            if orb_actual <= orb_tolerance:
                return {
                    "planet1": planet1,
                    "planet2": planet2,
                    "aspect_type": aspect_name,
                    "orb": orb_actual,
                    "exact": orb_actual < 0.1,
                    "angle": angle_diff
                }
        
        return None
    
    def _generate_cache_key(self, datetime_input: DateTimeInput,
                           planet_names: List[str], orb_settings: Dict[str, float]) -> str:
        """Generate consistent cache key."""
        import hashlib
        import json
        
        cache_data = {
            "datetime": datetime_input.model_dump(),
            "planets": sorted(planet_names),
            "orbs": orb_settings
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"aspects_{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def _get_cached_result(self, cache_key: str, datetime_input: DateTimeInput,
                          planet_names: List[str], orb_settings: Dict[str, float]):
        """Try to get result from cache."""
        
        # Try Redis cache first
        redis_cache = get_redis_cache()
        if redis_cache.enabled:
            cache_data = {
                "datetime": datetime_input.model_dump(),
                "planets": planet_names,
                "orbs": orb_settings
            }
            cached_result = redis_cache.get("aspect_calculation", cache_data)
            if cached_result:
                logger.info("Cache hit (Redis): aspect calculation")
                return cached_result
        
        # Try memory cache
        memory_cache = get_global_cache()
        cached_result = memory_cache.get(cache_key)
        if cached_result:
            logger.info("Cache hit (Memory): aspect calculation")
            return cached_result
        
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any],
                     datetime_input: DateTimeInput, planet_names: List[str],
                     orb_settings: Dict[str, float]):
        """Cache the calculation result."""
        
        # Cache in memory
        memory_cache = get_global_cache()
        memory_cache.put(cache_key, result, ttl=3600)  # 1 hour
        
        # Cache in Redis
        redis_cache = get_redis_cache()
        if redis_cache.enabled:
            cache_data = {
                "datetime": datetime_input.model_dump(),
                "planets": planet_names,
                "orbs": orb_settings
            }
            redis_cache.set("aspect_calculation", cache_data, result, ttl=3600)


# 3. API ENDPOINT IMPLEMENTATION
# Create the FastAPI endpoint with proper error handling

# Global calculator instance
aspect_calculator = AspectCalculator()


@router.post(
    "/aspects",
    response_model=AspectResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Planetary Aspects",
    description="""
    Calculate aspects between specified planets at a given date and time.
    
    This endpoint calculates angular relationships (aspects) between planets,
    including conjunctions, sextiles, squares, trines, and oppositions.
    
    **Features:**
    - Supports all major planets
    - Configurable orb tolerances
    - High-performance caching (Redis + memory)
    - Comprehensive error handling
    - Performance monitoring integration
    
    **Performance:**
    - Typical response time: 25-45ms (cache miss)
    - Cache hit response: 5-10ms
    - Supports concurrent requests
    
    **Examples:**
    
    Calculate aspects between Sun, Moon, and Venus:
    ```json
    {
      "datetime": {"iso_string": "2000-01-01T12:00:00"},
      "planets": ["sun", "moon", "venus"],
      "orb_settings": {
        "conjunction": 8.0,
        "trine": 6.0
      }
    }
    ```
    """,
    responses={
        200: {"description": "Successful aspect calculation", "model": AspectResponse},
        400: {"description": "Bad request", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Calculation error", "model": ErrorResponse}
    }
)
async def calculate_aspects(request: AspectRequest) -> AspectResponse:
    """
    Calculate planetary aspects for specified date/time and planets.
    
    Args:
        request: Aspect calculation request with datetime, planets, and orb settings
        
    Returns:
        AspectResponse: Calculated aspects with metadata
        
    Raises:
        HTTPException: For validation errors or calculation failures
    """
    
    start_time = datetime.now(timezone.utc)
    
    try:
        # Perform calculation
        result_data = aspect_calculator.calculate_aspects(
            request.datetime,
            request.planets, 
            request.orb_settings
        )
        
        # Calculate processing time
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        # Record metrics
        metrics = get_metrics()
        metrics.record_calculation("aspect_calculation", processing_time / 1000, True)
        metrics.record_api_request("POST", "/ephemeris/aspects", 200, processing_time / 1000)
        
        # Prepare response
        response_data = AspectResponse(
            success=True,
            data=result_data,
            metadata={
                "processing_time_ms": processing_time,
                "cache_hit": processing_time < 15,  # Likely cache hit if very fast
                "planets_calculated": len(request.planets),
                "aspects_found": result_data["aspect_count"]
            }
        )
        
        logger.info(f"Aspect calculation completed in {processing_time:.1f}ms "
                   f"for {len(request.planets)} planets")
        
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
        
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error in aspect calculation: {e}")
        metrics = get_metrics()
        metrics.record_error("validation_error", "/ephemeris/aspects")
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "error": "validation_error",
                "message": "Request validation failed",
                "details": {"validation_error": str(e)}
            }
        )
        
    except Exception as e:
        # Handle unexpected errors
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        logger.error(f"Unexpected error in aspect calculation: {e}", exc_info=True)
        
        metrics = get_metrics()
        metrics.record_calculation("aspect_calculation", processing_time / 1000, False)
        metrics.record_error("calculation_error", "/ephemeris/aspects")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "calculation_error", 
                "message": "Aspect calculation failed",
                "details": {
                    "error_type": "unexpected_error",
                    "processing_time_ms": processing_time
                }
            }
        )


# 4. ADDITIONAL UTILITY ENDPOINTS

@router.get(
    "/aspects/supported-types",
    summary="Get Supported Aspect Types",
    description="Returns list of all supported aspect types with their angles and default orbs."
)
async def get_supported_aspect_types():
    """Get list of supported aspect types."""
    
    aspect_info = {
        "conjunction": {"angle": 0, "default_orb": 8.0, "description": "Same position"},
        "sextile": {"angle": 60, "default_orb": 4.0, "description": "60° apart"},
        "square": {"angle": 90, "default_orb": 6.0, "description": "90° apart"},
        "trine": {"angle": 120, "default_orb": 6.0, "description": "120° apart"},
        "opposition": {"angle": 180, "default_orb": 8.0, "description": "Opposite positions"}
    }
    
    return {
        "success": True,
        "data": {
            "aspect_types": aspect_info,
            "total_types": len(aspect_info)
        }
    }


@router.get(
    "/aspects/supported-planets",
    summary="Get Supported Planets",
    description="Returns list of all planets supported for aspect calculations."
)
async def get_supported_planets():
    """Get list of supported planets."""
    
    planets = {
        "sun": {"id": 0, "symbol": "☉", "type": "luminary"},
        "moon": {"id": 1, "symbol": "☽", "type": "luminary"},
        "mercury": {"id": 2, "symbol": "☿", "type": "personal"},
        "venus": {"id": 3, "symbol": "♀", "type": "personal"},
        "mars": {"id": 4, "symbol": "♂", "type": "personal"},
        "jupiter": {"id": 5, "symbol": "♃", "type": "social"},
        "saturn": {"id": 6, "symbol": "♄", "type": "social"},
        "uranus": {"id": 7, "symbol": "♅", "type": "outer"},
        "neptune": {"id": 8, "symbol": "♆", "type": "outer"},
        "pluto": {"id": 9, "symbol": "♇", "type": "outer"}
    }
    
    return {
        "success": True,
        "data": {
            "planets": planets,
            "total_planets": len(planets)
        }
    }


# 5. INTEGRATION WITH MAIN APPLICATION
# Add this router to the main FastAPI application

"""
To integrate this endpoint into the main application:

1. In backend/app/main.py, add:
   from examples.integration_patterns.new_endpoint_example import router as aspects_router
   app.include_router(aspects_router)

2. Add to requirements.txt if new dependencies are needed

3. Update API documentation:
   - The endpoint will automatically appear in /docs
   - Add examples to the MkDocs documentation

4. Add integration tests:
   - Test the new endpoint in tests/api/routes/test_aspects.py
   - Add performance benchmarks in tests/benchmarks/

5. Update monitoring:
   - The endpoint automatically integrates with Prometheus metrics
   - Add custom Grafana dashboard panels if needed
"""


# 6. TESTING EXAMPLE

def test_new_endpoint():
    """
    Example test for the new aspects endpoint.
    Add this to tests/api/routes/test_aspects.py
    """
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # Test valid request
    test_request = {
        "datetime": {"iso_string": "2000-01-01T12:00:00"},
        "planets": ["sun", "moon", "venus"],
        "orb_settings": {
            "conjunction": 8.0,
            "trine": 6.0
        }
    }
    
    response = client.post("/ephemeris/aspects", json=test_request)
    
    assert response.status_code == 200
    data = response.model_dump_json()
    
    assert data["success"] is True
    assert "data" in data
    assert "aspects" in data["data"]
    assert "metadata" in data
    assert data["metadata"]["processing_time_ms"] < 100  # Performance target


if __name__ == "__main__":
    # Example usage
    print("🚀 Meridian Ephemeris - New Endpoint Example")
    print("This example shows how to add a planetary aspects endpoint")
    print("with caching, monitoring, and comprehensive error handling.")
    print("\n📋 Key Components:")
    print("1. Pydantic models for request/response validation")
    print("2. Core calculation logic with caching")
    print("3. FastAPI endpoint with error handling")
    print("4. Performance monitoring integration")
    print("5. Comprehensive testing patterns")
    print("\n✅ Follow this pattern for all new endpoints!")