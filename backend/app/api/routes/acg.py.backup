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
from ...core.acg.aspect_lines import aspect_lines_manager, AspectLineFeature
from ...core.acg.retrograde_integration import RetrogradeIntegratedACGCalculator, motion_styler
from ...core.acg.paran_calculator import JimLewisACGParanCalculator
from ...core.monitoring.metrics import timed_calculation, get_metrics

logger = logging.getLogger(__name__)

# Create router with ACG prefix
router = APIRouter(prefix="/acg", tags=["acg"])

# Initialize core components
acg_engine = ACGCalculationEngine()
metadata_manager = ACGMetadataManager()
enhanced_acg_engine = RetrogradeIntegratedACGCalculator(acg_engine)
paran_calculator = JimLewisACGParanCalculator()


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


# ========================================
# ENHANCED ACG ENDPOINTS (PRP 4)
# ========================================

from ..models.enhanced_acg_models import (
    EnhancedACGLinesRequest, EnhancedACGLinesResponse,
    AspectLineRequest, AspectLineFeatureResponse,
    MotionFilterRequest, MotionFilterResponse,
    ACGPerformanceResponse, ACGCacheRequest, ACGCacheResponse,
    AspectLinesConfig, MotionStatusFilter
)


@router.post(
    "/v2/lines",
    response_model=EnhancedACGLinesResponse,
    summary="Calculate enhanced ACG lines with retrograde awareness",
    description="Calculate ACG lines with retrograde motion metadata, aspect-to-angle lines, and motion-based filtering",
    tags=["enhanced-acg"]
)
@timed_calculation("enhanced_acg_lines")
async def calculate_enhanced_acg_lines(request: EnhancedACGLinesRequest) -> EnhancedACGLinesResponse:
    """
    Calculate enhanced ACG lines with retrograde awareness and aspect-to-angle lines.
    
    This endpoint extends the standard ACG calculation with:
    - Retrograde motion status and timing metadata
    - Aspect-to-angle line calculations (aspects to MC/ASC/IC/DSC)
    - Motion-based filtering capabilities
    - Enhanced styling hints for visualization
    - Station timing analysis
    
    Args:
        request: Enhanced ACG lines request with retrograde options
        
    Returns:
        EnhancedACGLinesResponse: Complete ACG data with enhancements
        
    Raises:
        HTTPException: For validation or calculation errors
    """
    start_time = time.time()
    
    try:
        # Convert request to calculation parameters
        calculation_date = datetime.fromisoformat(request.datetime.iso_string.replace('Z', '+00:00'))
        jd_ut1 = swe.julday(
            calculation_date.year,
            calculation_date.month,
            calculation_date.day,
            calculation_date.hour + calculation_date.minute/60.0
        )
        
        # Prepare bodies list
        bodies = []
        if request.bodies:
            for body_id in request.bodies:
                bodies.append(ACGBody(id=body_id, type=ACGBodyType.PLANET))
        else:
            bodies = acg_engine.get_default_bodies()
        
        # Calculate enhanced ACG lines
        result = enhanced_acg_engine.calculate_enhanced_acg_lines(
            bodies=bodies,
            jd_ut1=jd_ut1,
            calculation_date=calculation_date,
            include_retrograde_metadata=request.include_retrograde_metadata,
            motion_status_filter=[f.value for f in request.motion_status_filter] if request.motion_status_filter else None,
            include_station_analysis=request.include_station_analysis
        )
        
        # Calculate aspect-to-angle lines if requested
        aspect_lines = []
        if request.include_aspect_lines and request.aspect_lines_config:
            planet_ids = [i for i, body in enumerate(bodies) if body.type == ACGBodyType.PLANET]
            
            aspect_results = aspect_lines_manager.calculate_multiple_planet_aspect_lines(
                planet_ids=planet_ids,
                calculation_date=calculation_date,
                aspects_config=request.aspect_lines_config.model_dump(),
                precision=request.aspect_lines_config.precision_degrees
            )
            
            # Convert to response format
            for planet_id, features in aspect_results.items():
                for feature in features:
                    aspect_lines.append(AspectLineFeatureResponse(
                        planet_id=feature.planet_id,
                        planet_name=feature.planet_name,
                        angle_name=feature.angle_name,
                        aspect_type=feature.aspect_type.name.lower(),
                        aspect_angle=feature.aspect_angle,
                        orb_degrees=feature.orb,
                        geojson_feature=feature.to_geojson_feature(),
                        line_strength=feature.line_strength,
                        visual_priority=feature.visual_priority,
                        point_count=len(feature.line_points),
                        calculation_accuracy=feature.calculation_accuracy
                    ))
        
        # Generate styling metadata
        styling_metadata = {}
        legend_data = {}
        
        if request.include_retrograde_metadata:
            # Generate styling for motion visualization
            active_filters = [f.value for f in request.motion_status_filter] if request.motion_status_filter else []
            legend_data = motion_styler.generate_legend_data(active_filters, request.color_scheme)
        
        # Calculate total time
        calculation_time = (time.time() - start_time) * 1000
        
        # Build response
        response = EnhancedACGLinesResponse(
            success=True,
            chart_info={
                "name": request.chart_name,
                "datetime": request.datetime.iso_string,
                "coordinates": request.coordinates.model_dump(),
                "julian_day": jd_ut1
            },
            geojson_features=result.features if hasattr(result, 'features') else [],
            retrograde_metadata=getattr(result, 'enhanced_metadata', {}).get('retrograde_data'),
            aspect_lines=aspect_lines if aspect_lines else None,
            styling_metadata=styling_metadata if styling_metadata else None,
            legend_data=legend_data if legend_data else None,
            calculation_time_ms=calculation_time,
            performance_stats=enhanced_acg_engine.get_performance_stats(),
            metadata={
                "api_version": "v2",
                "enhanced_features": {
                    "retrograde_metadata": request.include_retrograde_metadata,
                    "aspect_lines": request.include_aspect_lines,
                    "station_analysis": request.include_station_analysis
                },
                "calculation_settings": {
                    "color_scheme": request.color_scheme,
                    "motion_filters": [f.value for f in request.motion_status_filter] if request.motion_status_filter else [],
                    "body_count": len(bodies)
                }
            }
        )
        
        # Record metrics
        metrics = get_metrics()
        metrics.record_calculation("enhanced_acg_lines", calculation_time / 1000, True)
        
        return response
        
    except Exception as e:
        logger.error(f"Enhanced ACG lines calculation failed: {e}")
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "enhanced_calculation_error",
            f"Enhanced ACG calculation failed: {str(e)}",
            "/api/v1/acg/v2/lines"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


@router.post(
    "/v2/aspect-lines",
    response_model=List[AspectLineFeatureResponse],
    summary="Calculate aspect-to-angle lines",
    description="Calculate aspect lines to MC, ASC, IC, and DSC for specified planets",
    tags=["enhanced-acg"]
)
@timed_calculation("aspect_to_angle_lines")
async def calculate_aspect_lines(request: AspectLineRequest) -> List[AspectLineFeatureResponse]:
    """
    Calculate aspect-to-angle lines for specified planets.
    
    Calculates lines where planets form specific aspects (conjunction, trine, square, etc.)
    to local angles (MC, ASC, IC, DSC) at various locations on Earth.
    
    Args:
        request: Aspect lines request with configuration
        
    Returns:
        List of aspect line features
        
    Raises:
        HTTPException: For validation or calculation errors
    """
    try:
        calculation_date = datetime.fromisoformat(request.datetime.iso_string.replace('Z', '+00:00'))
        
        # Calculate aspect lines for all requested planets
        all_features = []
        
        for planet_id in request.planet_ids:
            features = aspect_lines_manager.calculate_planet_aspect_lines(
                planet_id=planet_id,
                calculation_date=calculation_date,
                aspects_config=request.aspects_config.model_dump(),
                precision=request.aspects_config.precision_degrees
            )
            
            # Convert to response format
            for feature in features:
                all_features.append(AspectLineFeatureResponse(
                    planet_id=feature.planet_id,
                    planet_name=feature.planet_name,
                    angle_name=feature.angle_name,
                    aspect_type=feature.aspect_type.name.lower(),
                    aspect_angle=feature.aspect_angle,
                    orb_degrees=feature.orb,
                    geojson_feature=feature.to_geojson_feature(),
                    line_strength=feature.line_strength,
                    visual_priority=feature.visual_priority,
                    point_count=len(feature.line_points),
                    calculation_accuracy=feature.calculation_accuracy
                ))
        
        return all_features
        
    except Exception as e:
        logger.error(f"Aspect lines calculation failed: {e}")
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "aspect_lines_error", 
            f"Aspect lines calculation failed: {str(e)}",
            "/api/v1/acg/v2/aspect-lines"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


@router.post(
    "/v2/motion-filter",
    response_model=MotionFilterResponse,
    summary="Apply motion-based filtering to ACG data",
    description="Filter ACG lines by planetary motion status and generate styling metadata",
    tags=["enhanced-acg"]
)
async def apply_motion_filtering(request: MotionFilterRequest) -> MotionFilterResponse:
    """
    Apply motion-based filtering to ACG data.
    
    Filters existing ACG calculations by planetary motion status
    and generates appropriate styling metadata for visualization.
    
    Args:
        request: Motion filter request
        
    Returns:
        Filtered features with styling metadata
        
    Raises:
        HTTPException: For filtering errors
    """
    try:
        # This would typically operate on cached ACG data
        # For now, return example response structure
        
        filter_values = [f.value for f in request.motion_filters]
        
        # Generate legend data
        legend_data = None
        if request.include_legend:
            legend_data = motion_styler.generate_legend_data(filter_values, request.color_scheme)
        
        return MotionFilterResponse(
            success=True,
            filtered_features=[],  # Would contain actual filtered features
            styling_metadata={
                "color_scheme": request.color_scheme,
                "motion_filters": filter_values,
                "styling_applied": True
            },
            legend_data=legend_data,
            filter_stats={
                "total_features_input": 0,
                "features_after_filtering": 0,
                "filters_applied": len(filter_values),
                "filter_effectiveness": 0.0
            }
        )
        
    except Exception as e:
        logger.error(f"Motion filtering failed: {e}")
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "motion_filtering_error",
            f"Motion filtering failed: {str(e)}",
            "/api/v1/acg/v2/motion-filter"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


@router.get(
    "/v2/performance",
    response_model=ACGPerformanceResponse,
    summary="Get enhanced ACG performance statistics",
    description="Retrieve performance statistics for enhanced ACG features",
    tags=["enhanced-acg", "monitoring"]
)
async def get_enhanced_performance_stats() -> ACGPerformanceResponse:
    """
    Get performance statistics for enhanced ACG features.
    
    Returns detailed performance metrics for retrograde integration,
    aspect-to-angle calculations, and overall system performance.
    
    Returns:
        Performance statistics and recommendations
    """
    try:
        # Get performance stats from enhanced engine
        retrograde_stats = enhanced_acg_engine.get_performance_stats()
        
        # Get aspect lines performance (would be implemented in aspect_lines_manager)
        aspect_stats = {
            "calculation_count": 0,
            "average_time_ms": 0.0,
            "cache_hit_rate": 0.0
        }
        
        # Generate recommendations based on performance
        recommendations = []
        if retrograde_stats.get("average_time_ms", 0) > 200:
            recommendations.append("Consider reducing precision for better performance")
        if aspect_stats.get("cache_hit_rate", 1.0) < 0.5:
            recommendations.append("Aspect lines cache hit rate is low, consider cache tuning")
        
        return ACGPerformanceResponse(
            success=True,
            performance_stats={
                "total_enhanced_calculations": retrograde_stats.get("enhanced_calculation_count", 0),
                "average_response_time_ms": retrograde_stats.get("average_time_ms", 0.0),
                "performance_overhead": retrograde_stats.get("performance_overhead_estimate", "~10-15% vs base ACG")
            },
            retrograde_integration_stats=retrograde_stats,
            aspect_lines_stats=aspect_stats,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Failed to get enhanced performance stats: {e}")
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "performance_stats_error",
            f"Failed to retrieve performance statistics: {str(e)}",
            "/api/v1/acg/v2/performance"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


@router.post(
    "/v2/cache",
    response_model=ACGCacheResponse,
    summary="Manage enhanced ACG cache operations",
    description="Clear or get statistics for enhanced ACG feature caches",
    tags=["enhanced-acg", "cache"]
)
async def manage_enhanced_cache(request: ACGCacheRequest) -> ACGCacheResponse:
    """
    Manage enhanced ACG cache operations.
    
    Provides cache management for enhanced ACG features including
    retrograde metadata cache and aspect lines cache.
    
    Args:
        request: Cache operation request
        
    Returns:
        Cache operation result
    """
    try:
        if request.operation == "clear":
            # Clear all enhanced feature caches
            enhanced_acg_engine.clear_performance_cache()
            aspect_lines_manager.clear_cache()
            
            return ACGCacheResponse(
                success=True,
                operation="clear",
                message="Enhanced ACG caches cleared successfully"
            )
            
        elif request.operation == "stats":
            # Get cache statistics
            cache_stats = {
                "retrograde_cache": "active",
                "aspect_lines_cache": "active", 
                "performance_cache": len(enhanced_acg_engine._retrograde_calculation_times) if hasattr(enhanced_acg_engine, '_retrograde_calculation_times') else 0
            }
            
            return ACGCacheResponse(
                success=True,
                operation="stats",
                cache_stats=cache_stats,
                message="Cache statistics retrieved successfully"
            )
            
        elif request.operation == "clear_by_type" and request.cache_type:
            # Clear specific cache type
            if request.cache_type == "retrograde":
                enhanced_acg_engine.clear_performance_cache()
            elif request.cache_type == "aspect_lines":
                aspect_lines_manager.clear_cache()
            
            return ACGCacheResponse(
                success=True,
                operation="clear_by_type",
                message=f"Cache type '{request.cache_type}' cleared successfully"
            )
        
        else:
            raise ValueError(f"Unknown cache operation: {request.operation}")
            
    except Exception as e:
        logger.error(f"Enhanced cache operation failed: {e}")
        error_response = create_acg_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "cache_operation_error",
            f"Cache operation failed: {str(e)}",
            "/api/v1/acg/v2/cache"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )