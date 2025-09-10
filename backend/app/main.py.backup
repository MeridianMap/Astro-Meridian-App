"""
Meridian Ephemeris API - Main Application

FastAPI application entry point with routing, middleware, and configuration.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request, Response, status
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

from .api.routes.ephemeris import router as ephemeris_router
# from .api.routes.acg import router as acg_router  # Temporarily disabled for testing
from .api.routes.predictive import router as predictive_router
from .api.models.schemas import ErrorResponse
from .core.ephemeris.settings import settings
from .core.monitoring.metrics import setup_metrics_middleware, get_metrics, update_health_metrics


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting Meridian Ephemeris API")
    logger.info(f"📊 Using ephemeris data path: {settings.ephemeris_path}")
    
    # Initialize performance optimizations
    try:
        from .core.performance.optimizations import get_performance_optimizer
        from .core.performance.production_optimization import get_production_optimizer
        
        optimizer = get_performance_optimizer()
        production_optimizer = get_production_optimizer()
        await production_optimizer.initialize()
        
        logger.info("⚡ Performance optimizer initialized")
        logger.info("🏭 Production optimizer initialized")
    except Exception as e:
        logger.warning(f"⚠️  Performance optimizer initialization failed: {e}")
    
    # Initialize Redis cache
    try:
        from .core.ephemeris.classes.redis_cache import get_redis_cache, get_cache_warmer
        redis_cache = get_redis_cache()
        if redis_cache.enabled:
            logger.info("🗄️  Redis cache initialized")
            # Warm cache with common calculations
            cache_warmer = get_cache_warmer()
            # Note: Actual cache warming would be done in background
        else:
            logger.info("🗄️  Redis cache disabled, using in-memory cache only")
    except Exception as e:
        logger.warning(f"⚠️  Redis cache initialization failed: {e}")
    
    # Validate ephemeris files on startup
    try:
        from .core.ephemeris.tools.ephemeris import validate_ephemeris_files
        validation_results = validate_ephemeris_files()
        available_files = sum(validation_results.values())
        total_files = len(validation_results)
        
        if available_files == total_files:
            logger.info(f"✅ All {total_files} ephemeris files validated successfully")
        else:
            logger.warning(f"⚠️  {available_files}/{total_files} ephemeris files available")
            logger.warning("Some calculations may not work properly")
            
    except Exception as e:
        logger.error(f"❌ Failed to validate ephemeris files: {e}")
    
    # Initialize monitoring and metrics
    try:
        metrics = get_metrics()
        metrics.set_app_info({
            "version": "1.0.0",
            "name": "meridian-ephemeris-api",
            "environment": "production"
        })
        logger.info("📈 Metrics collection initialized")
        update_health_metrics()
    except Exception as e:
        logger.warning(f"⚠️  Metrics initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Meridian Ephemeris API")
    
    # Clean shutdown of production optimizer
    try:
        from .core.performance.production_optimization import get_production_optimizer
        production_optimizer = get_production_optimizer()
        await production_optimizer.shutdown()
        logger.info("🏭 Production optimizer shut down cleanly")
    except Exception as e:
        logger.warning(f"⚠️  Production optimizer shutdown failed: {e}")


# Create FastAPI application
app = FastAPI(
    title="Meridian Ephemeris API",
    description="""
    **Meridian Ephemeris Engine** - Professional Astrological Calculations
    
    A high-performance REST API for precise astrological chart calculations using the Swiss Ephemeris.
    
    ## Features
    
    - 🎯 **Precise Calculations**: Swiss Ephemeris backend for astronomical accuracy
    - 🏗️ **Flexible Input Formats**: Support for multiple coordinate, datetime, and timezone formats
    - 🏠 **Multiple House Systems**: Placidus, Koch, Equal House, Whole Sign, and more
    - ⚡ **High Performance**: Parallel processing and intelligent caching
    - 📊 **Comprehensive Data**: Complete natal charts with planets, houses, angles, and aspects
    - 🔒 **Input Validation**: Robust validation with clear error messages
    - 📖 **OpenAPI Documentation**: Interactive API documentation and schema validation
    - 🌙 **Eclipse Predictions**: NASA-validated eclipse calculations with ±1 minute accuracy
    - 🪐 **Transit Calculations**: Precise planetary transit timing with retrograde support
    - 📅 **Predictive Features**: Solar/lunar returns, sign ingresses, and future transits
    
    ## Supported Formats
    
    ### Coordinates
    - **Decimal degrees**: `40.7128, -74.0060`
    - **DMS strings**: `"40°42'46\\"N", "74°00'22\\"W"`
    - **Component objects**: `{"degrees": 40, "minutes": 42, "seconds": 46, "direction": "N"}`
    
    ### DateTime
    - **ISO 8601 strings**: `"2000-01-01T12:00:00"`, `"2000-01-01T12:00:00-05:00"`
    - **Julian Day numbers**: `2451545.0`
    - **Component objects**: `{"year": 2000, "month": 1, "day": 1, "hour": 12}`
    
    ### Timezones
    - **IANA names**: `"America/New_York"`, `"Europe/London"`
    - **UTC offsets**: `-5.0`, `+1.0`
    - **Auto-detection**: Based on coordinates
    
    ## Usage Examples
    
    Calculate a natal chart with basic decimal coordinates:
    ```json
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
    """,
    version="1.0.0",
    contact={
        "name": "Meridian Ephemeris Support",
        "email": "support@meridianephemeris.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Set up Prometheus metrics middleware
setup_metrics_middleware(app)

# Add production optimization middleware
try:
    from .core.performance.production_optimization import setup_production_middleware
    setup_production_middleware(app)
    logger.info("🏭 Production optimization middleware configured")
except ImportError as e:
    logger.warning(f"⚠️  Production optimization middleware not available: {e}")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()
    
    # Log request
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"📥 {request.method} {request.url.path} from {client_ip}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"📤 {response.status_code} in {process_time:.3f}s")
    
    return response


# Include routers
app.include_router(ephemeris_router)
# app.include_router(acg_router)  # Temporarily disabled for testing
app.include_router(predictive_router)


# Root endpoint
@app.get(
    "/",
    summary="API Root",
    description="Welcome endpoint with API information and links to documentation.",
    response_model=Dict[str, Any],
    tags=["root"]
)
async def root():
    """
    API root endpoint.
    
    Returns:
        Welcome message with API information
    """
    return {
        "message": "Welcome to Meridian Ephemeris API",
        "version": "1.0.0",
        "description": "Professional astrological calculations using Swiss Ephemeris",
        "documentation": {
            "interactive": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": "/ephemeris/health",
            "natal_chart": "/ephemeris/natal",
            "acg": {
                "health": "/acg/health",
                "lines": "/acg/lines",
                "batch": "/acg/batch",
                "animate": "/acg/animate",
                "features": "/acg/features",
                "schema": "/acg/schema"
            },
            "predictive": {
                "health": "/v2/health",
                "next_solar_eclipse": "/v2/eclipses/next-solar",
                "next_lunar_eclipse": "/v2/eclipses/next-lunar",
                "search_eclipses": "/v2/eclipses/search",
                "eclipse_visibility": "/v2/eclipses/visibility",
                "planet_transits": "/v2/transits/planet-to-degree",
                "sign_ingresses": "/v2/transits/sign-ingresses",
                "transit_search": "/v2/transits/search",
                "rate_limits": "/v2/rate-limits"
            },
            "schemas": {
                "natal_request": "/ephemeris/schemas/natal-request",
                "natal_response": "/ephemeris/schemas/natal-response"
            },
            "reference": {
                "house_systems": "/ephemeris/house-systems",
                "supported_objects": "/ephemeris/supported-objects"
            }
        },
        "status": "operational"
    }


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error on {request.url.path}: {exc}")
    
    # Build standardized error payload
    details = {
        "errors": [{"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]} for error in exc.errors()],
        "body": str(exc.body) if getattr(exc, "body", None) else None
    }
    legacy = {
        "success": False,
        "error": "validation_error",
        "message": "Request validation failed",
        "details": details
    }
    # FastAPI-compatible top-level 'detail'
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": {
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "error": "validation_error",
                "message": "Request validation failed",
                "path": request.url.path,
                "errors": details.get("errors", [])
            },
            **legacy
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    
    payload = {
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "error": "internal_error",
        "message": "An unexpected error occurred",
        "path": request.url.path
    }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": payload,
            "success": False,
            "error": payload["error"],
            "message": payload["message"],
            "details": {"type": "unhandled_exception"}
        }
    )


# Health check endpoint (additional to the one in ephemeris router)
@app.get(
    "/health",
    summary="Global Health Check", 
    description="Basic health check for the entire API service.",
    tags=["health"]
)
async def global_health_check():
    """
    Global health check endpoint.
    
    Returns:
        Basic health status
    """
    return {
        "status": "healthy",
        "service": "meridian-ephemeris-api",
        "version": "1.0.0",
        "timestamp": time.time()
    }


# Configuration for running the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )