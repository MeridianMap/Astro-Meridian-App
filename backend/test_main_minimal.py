"""
Minimal test version of main.py for testing basic ephemeris functionality
Excludes ACG and predictive routes that have dependency issues
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

from app.api.routes.ephemeris import router as ephemeris_router
# Skip ACG and predictive routers for now
# from app.api.routes.acg import router as acg_router  
# from app.api.routes.predictive import router as predictive_router
from app.api.models.schemas import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Meridian Ephemeris API (Minimal Test Version)")
    # Skip metrics setup that might need Redis
    # setup_metrics_middleware(app)
    yield
    logger.info("Shutting down Meridian Ephemeris API")


# Create FastAPI application
app = FastAPI(
    title="Meridian Ephemeris API (Test)",
    version="1.0.0",
    description="Professional astrological calculations and ephemeris services (test version)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Meridian Ephemeris Support",
        "email": "support@meridian-ephemeris.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:.4f}")
    return response


# Include routers
app.include_router(ephemeris_router)
# Skip problematic routers for testing
# app.include_router(acg_router)
# app.include_router(predictive_router)


# Root endpoint
@app.get(
    "/",
    summary="API Root",
    description="Root endpoint providing API information and status.",
    tags=["info"]
)
async def root():
    """
    API root endpoint.
    
    Returns:
        Basic API information and status
    """
    return {
        "service": "Meridian Ephemeris API (Test Version)",
        "version": "1.0.0",
        "description": "Professional astrological calculations",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "available_endpoints": [
            "/docs - API Documentation",
            "/ephemeris/* - Ephemeris calculations",
            "/health - Health check"
        ]
    }


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "validation_error",
            "message": "Request validation failed",
            "details": [{"field": err["loc"][-1], "message": err["msg"]} for err in exc.errors()]
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "internal_server_error",
            "message": "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get(
    "/health",
    summary="Global Health Check", 
    description="Basic health check for the API service.",
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
        "service": "meridian-ephemeris-api-test",
        "version": "1.0.0",
        "timestamp": time.time()
    }


if __name__ == "__main__":
    uvicorn.run(
        "test_main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )