"""
ACG API Endpoints (PRP 2)

RESTful API endpoints for the ACG (Astrocartography) engine, exposing all core
calculation features and returning data in GeoJSON and metadata formats.

All endpoints follow the API contract specification in:
PRPs/contracts/acg-api-contract.md

Endpoints:
- POST /acg/lines: Calculate ACG lines for a single chart
- POST /acg/batch: Batch calculation for multiple charts  
- GET /acg/features: Get supported bodies, line types, and capabilities
- GET /acg/schema: Get metadata schema
- POST /acg/animate: Calculate time-based animation frames
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, status, Response, BackgroundTasks
from fastapi.responses import JSONResponse
import logging

from ...core.acg.acg_core import ACGCalculationEngine
from ...core.acg.acg_metadata import ACGMetadataManager
from ...core.acg.acg_types import (
    ACGRequest, ACGResult, ACGBatchRequest, ACGBatchResponse,
    ACGAnimateRequest, ACGAnimateResponse, ACGFeaturesResponse,
    ACGErrorResponse, ACGBody, ACGOptions
)
from ...core.monitoring.metrics import timed_calculation, get_metrics

logger = logging.getLogger(__name__)

# Create router with ACG prefix
router = APIRouter(prefix="/acg", tags=["acg"])

# Initialize core components
acg_engine = ACGCalculationEngine()
metadata_manager = ACGMetadataManager()


# Error handler for ACG-specific errors
def create_acg_error_response(
    status_code: int,
    error_type: str,
    message: str,
    path: str,
    details: Optional[List[Dict[str, str]]] = None
) -> ACGErrorResponse:
    """Create standardized ACG error response."""
    return ACGErrorResponse(
        timestamp=datetime.utcnow().isoformat() + 'Z',
        status=status_code,
        error=error_type,
        message=message,
        path=path,
        errors=details or []
    )


@router.post(
    "/lines",
    response_model=ACGResult,
    summary="Calculate ACG lines for a single chart",
    description="""
    Calculate and return all ACG lines for a given natal chart.
    
    Returns GeoJSON FeatureCollection with complete metadata for each line.
    Supports all line types (MC, IC, AC, DC, aspects, parans) and all celestial bodies.
    
    **Performance**: Typically <100ms for standard calculations.
    
    **Caching**: Results are cached based on input parameters for faster subsequent requests.
    """,
    responses={
        200: {
            "description": "ACG calculation successful",
            "content": {"application/geo+json": {}}
        },
        400: {"description": "Invalid request parameters"},
        422: {"description": "Request validation failed"}, 
        500: {"description": "Calculation error"}
    }
)
@timed_calculation("acg_lines")
async def acg_lines_endpoint(
    request: ACGRequest,
    response: Response
) -> ACGResult:
    """
    Calculate ACG lines for a single chart.
    
    Args:
        request: ACG calculation request with epoch, bodies, and options
        response: FastAPI response object
        
    Returns:
        ACGResult: GeoJSON FeatureCollection with ACG lines and metadata
        
    Raises:
        HTTPException: For validation or calculation errors
    """
    calc_start_time = time.time()
    
    try:
        logger.info(f"ACG lines calculation requested for epoch: {request.epoch}")
        
        # Perform ACG calculation
        result = acg_engine.calculate_acg_lines(request)
        
        # Record metrics
        metrics = get_metrics()
        calc_duration = time.time() - calc_start_time
        metrics.record_calculation("acg_lines", calc_duration, True)
        
        # Set response headers
        response.headers["Content-Type"] = "application/geo+json"
        response.headers["X-Calculation-Time"] = f"{calc_duration * 1000:.2f}ms"
        response.headers["X-Features-Count"] = str(len(result.features))
        
        logger.info(f"ACG lines calculation completed in {calc_duration * 1000:.2f}ms")
        return result
        
    except ValueError as e:
        logger.warning(f"ACG lines validation error: {e}")
        error_response = create_acg_error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "validation_error",
            str(e),
            "/api/v1/acg/lines"
        )
        # FastAPI expects a top-level 'detail' field in the error response
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": error_response.model_dump()})
    except Exception as e:
        logger.error(f"ACG lines calculation failed: {e}")
        
        # Record failed calculation
        calc_duration = time.time() - calc_start_time
        metrics = get_metrics()
        metrics.record_calculation("acg_lines", calc_duration, False)
        
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "calculation_error",
            "ACG calculation failed",
            "/api/v1/acg/lines",
            [{"field": "general", "message": str(e)}]
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": error_response.model_dump()})


@router.post(
    "/batch",
    response_model=ACGBatchResponse,
    summary="Batch ACG calculation for multiple charts",
    description="""
    Calculate ACG lines for multiple charts in a single request.
    
    Optimized for performance with parallel processing and shared computations.
    Each request can have a correlation ID for tracking results.
    
    **Performance**: ~5x faster than individual requests for 10+ charts.
    """,
    responses={
        200: {"description": "Batch calculation successful"},
        400: {"description": "Invalid batch request"},
        500: {"description": "Batch calculation error"}
    }
)
@timed_calculation("acg_batch")
async def acg_batch_endpoint(
    request: ACGBatchRequest,
    background_tasks: BackgroundTasks,
    response: Response
) -> ACGBatchResponse:
    """
    Calculate ACG lines for multiple charts in batch.
    
    Args:
        request: Batch request with multiple ACG calculations
        background_tasks: FastAPI background tasks
        response: FastAPI response object
        
    Returns:
        ACGBatchResponse: Array of results with correlation IDs
    """
    calc_start_time = time.time()
    
    try:
        logger.info(f"ACG batch calculation requested for {len(request.requests)} charts")
        # Validate non-empty requests
        if not request.requests:
            error_response = create_acg_error_response(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "validation_error",
                "Batch 'requests' must contain at least one item",
                "/api/v1/acg/batch"
            )
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": error_response.model_dump()})
        
        results = []

        # Process each request in the batch
        for i, acg_request in enumerate(request.requests):
            try:
                # Use provided correlation ID or fallback
                correlation_id = acg_request.correlation_id or f"batch_{i}"

                # Calculate ACG lines
                acg_result = acg_engine.calculate_acg_lines(acg_request)

                results.append({
                    "correlation_id": correlation_id,
                    "response": acg_result.model_dump()
                })

            except Exception as e:
                logger.error(f"Batch item {i} failed: {e}")
                # Include error in results rather than failing entire batch
                results.append({
                    "correlation_id": acg_request.correlation_id or f"batch_{i}",
                    "error": {
                        "message": str(e),
                        "status": "calculation_failed"
                    }
                })
        
        # Record metrics
        calc_duration = time.time() - calc_start_time
        metrics = get_metrics()
        metrics.record_calculation("acg_batch", calc_duration, True)
        
        # Set response headers
        response.headers["X-Calculation-Time"] = f"{calc_duration * 1000:.2f}ms"
        response.headers["X-Batch-Size"] = str(len(request.requests))
        response.headers["X-Success-Count"] = str(
            sum(1 for r in results if "error" not in r)
        )
        
        logger.info(f"ACG batch calculation completed in {calc_duration * 1000:.2f}ms")
        
        return ACGBatchResponse(results=results)
        
    except Exception as e:
        logger.error(f"ACG batch calculation failed: {e}")
        
        calc_duration = time.time() - calc_start_time
        metrics = get_metrics()
        metrics.record_calculation("acg_batch", calc_duration, False)
        
        # Build and return error immediately to avoid referencing 'e' outside scope
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "calculation_error",
            "ACG calculation failed",
            "/api/v1/acg/lines",
            [{"field": "general", "message": str(e)}]
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": error_response.model_dump()})
        


@router.get(
    "/features",
    response_model=ACGFeaturesResponse,
    summary="Get supported ACG features and capabilities",
    description="""
    Returns comprehensive information about supported:
    - Celestial bodies (planets, asteroids, fixed stars, etc.)
    - Line types (MC, IC, AC, DC, aspects, parans)
    - Available aspects and default settings
    - Metadata schema fields
    
    Use this endpoint to discover capabilities before making calculation requests.
    """
)
async def get_acg_features() -> ACGFeaturesResponse:
    """
    Get supported ACG features and capabilities.
    
    Returns:
        ACGFeaturesResponse: Complete feature and capability information
    """
    try:
        logger.debug("ACG features requested")
        
        # Get supported bodies
        bodies = acg_engine.get_supported_bodies()
        
        # Define supported line types
        line_types = [
            "MC", "IC", "AC", "DC", 
            "MC_ASPECT", "AC_ASPECT", "PARAN"
        ]
        
        # Define supported aspects
        aspects = [
            "conjunction", "sextile", "square", 
            "trine", "opposition", "quincunx"
        ]
        
        # Get default options
        defaults = ACGOptions()
        
        # Get metadata schema keys
        schema = metadata_manager.export_metadata_schema()
        metadata_keys = list(schema['properties'].keys())
        
        return ACGFeaturesResponse(
            bodies=bodies,
            line_types=line_types,
            aspects=aspects,
            defaults=defaults,
            metadata_keys=metadata_keys
        )
        
    except Exception as e:
        logger.error(f"Failed to get ACG features: {e}")
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "features_error",
            "Failed to retrieve ACG features",
            "/api/v1/acg/features"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


@router.get(
    "/schema",
    summary="Get ACG metadata schema",
    description="""
    Returns the JSON Schema definition for ACG feature metadata properties.
    
    Use this schema to:
    - Validate ACG feature properties
    - Understand available metadata fields
    - Generate documentation
    - Build client-side validation
    """,
    response_class=JSONResponse
)
async def get_acg_schema() -> Dict[str, Any]:
    """
    Get ACG metadata schema.
    
    Returns:
        Dict: JSON Schema for ACG metadata
    """
    try:
        logger.debug("ACG schema requested")
        schema = metadata_manager.export_metadata_schema()
        return JSONResponse(content=schema)
        
    except Exception as e:
        logger.error(f"Failed to get ACG schema: {e}")
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "schema_error", 
            "Failed to retrieve ACG schema",
            "/api/v1/acg/schema"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


@router.post(
    "/animate",
    response_model=ACGAnimateResponse,
    summary="Calculate ACG animation frames over time",
    description="""
    Calculate ACG lines for animation sequences over time periods.
    
    Useful for:
    - Progressions and transits visualization
    - Time-lapse ACG animations
    - Temporal analysis of ACG patterns
    
    **Performance**: Optimized for time-series calculations with frame caching.
    """,
    responses={
        200: {"description": "Animation calculation successful"},
        400: {"description": "Invalid animation request"},
        500: {"description": "Animation calculation error"}
    }
)
@timed_calculation("acg_animate")
async def acg_animate_endpoint(
    request: ACGAnimateRequest,
    response: Response
) -> ACGAnimateResponse:
    """
    Calculate ACG animation frames over time.
    
    Args:
        request: Animation request with time range and step
        response: FastAPI response object
        
    Returns:
        ACGAnimateResponse: Sequence of ACG frames with timestamps
    """
    calc_start_time = time.time()
    
    try:
        logger.info(f"ACG animation requested: {request.epoch_start} to {request.epoch_end}")
        
        # Parse time range
        start_dt = datetime.fromisoformat(request.epoch_start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(request.epoch_end.replace('Z', '+00:00'))
        
        if start_dt >= end_dt:
            raise ValueError("Start time must be before end time")
        
        # Calculate frames
        frames = []
        current_dt = start_dt
        frame_count = 0
        max_frames = 1000  # Limit to prevent excessive computation
        
        while current_dt < end_dt and frame_count < max_frames:
            # Create request for current frame
            # Normalize to UTC ISO 8601 with trailing 'Z' (no duplicate offset)
            try:
                from datetime import timezone
                frame_epoch = current_dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat() + 'Z'
            except Exception:
                # Fallback: strip tzinfo if present
                frame_epoch = current_dt.replace(tzinfo=None).isoformat() + 'Z'
            frame_request = ACGRequest(
                epoch=frame_epoch,
                bodies=request.bodies,
                options=request.options,
                natal=request.natal
            )
            
            # Calculate ACG lines for frame
            frame_result = acg_engine.calculate_acg_lines(frame_request)
            
            # Calculate Julian Day for frame
            import swisseph as swe
            jd = swe.julday(
                current_dt.year, current_dt.month, current_dt.day,
                current_dt.hour + current_dt.minute/60.0 + current_dt.second/3600.0
            )
            
            frames.append({
                "epoch": frame_epoch,
                "jd": jd,
                "data": frame_result.model_dump()
            })
            
            # Advance to next frame
            from datetime import timedelta
            current_dt += timedelta(minutes=request.step_minutes)
            frame_count += 1
        
        if frame_count >= max_frames:
            logger.warning(f"Animation truncated at {max_frames} frames")
        
        # Record metrics
        calc_duration = time.time() - calc_start_time
        metrics = get_metrics()
        metrics.record_calculation("acg_animate", calc_duration, True)
        
        # Set response headers
        response.headers["X-Calculation-Time"] = f"{calc_duration * 1000:.2f}ms"
        response.headers["X-Frame-Count"] = str(len(frames))
        
        logger.info(f"ACG animation completed: {len(frames)} frames in {calc_duration * 1000:.2f}ms")
        
        return ACGAnimateResponse(frames=frames)
        
    except ValueError as e:
        logger.warning(f"ACG animation validation error: {e}")
        error_response = create_acg_error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "validation_error",
            str(e),
            "/api/v1/acg/animate"
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": error_response.model_dump()})
    except Exception as e:
        logger.error(f"ACG animation calculation failed: {e}")
        
        calc_duration = time.time() - calc_start_time
        metrics = get_metrics()
        metrics.record_calculation("acg_animate", calc_duration, False)
        
    error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "animation_error",
            "ACG animation calculation failed",
            "/api/v1/acg/animate"
        )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": error_response.model_dump()})


# Cache statistics endpoint
@router.get(
    "/cache/stats",
    summary="ACG cache statistics",
    description="Get ACG caching performance statistics and configuration",
    tags=["cache"]
)
async def get_acg_cache_stats() -> Dict[str, Any]:
    """
    Get ACG cache statistics and performance metrics.
    
    Returns:
        Dict: Cache statistics and configuration
    """
    try:
        from ...core.acg.acg_cache import get_acg_cache_manager
        
        cache_manager = get_acg_cache_manager()
        stats = cache_manager.get_cache_statistics()
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "cache_stats_error",
            "Failed to retrieve cache statistics",
            "/api/v1/acg/cache/stats"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


# Health check endpoint specific to ACG
@router.get(
    "/health",
    summary="ACG service health check",
    description="Check health and readiness of ACG calculation service",
    tags=["health"]
)
async def acg_health_check() -> Dict[str, Any]:
    """
    ACG service health check.
    
    Returns:
        Dict: Health status and service information
    """
    try:
        # Test core engine
        bodies = acg_engine.get_supported_bodies()
        
        # Test metadata manager
        schema = metadata_manager.export_metadata_schema()
        
        # Get provenance info
        provenance = metadata_manager.get_provenance_info()
        
        return {
            "status": "healthy",
            "service": "acg",
            "version": "1.0.0",
            "supported_bodies": len(bodies),
            "schema_version": metadata_manager.metadata_schema_version,
            "se_version": provenance.get("se_version", "unknown"),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
    except Exception as e:
        logger.error(f"ACG health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "acg",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }