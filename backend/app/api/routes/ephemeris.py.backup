"""
Meridian Ephemeris API - Ephemeris Routes

FastAPI routes for ephemeris calculations and chart generation.
Provides standardized REST endpoints with comprehensive input validation.
"""

from typing import Union
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ..models.schemas import (
    NatalChartRequest, NatalChartResponse, ErrorResponse, HealthResponse,
    NatalChartEnhancedRequest, NatalChartEnhancedResponse, CalculationMetadata,
    AspectMatrixResponse, EnhancedAspectResponse, ArabicPartsResponse,
    SectDeterminationResponse, ArabicPartResponse
)
from ...services.ephemeris_service import (
    ephemeris_service, EphemerisServiceError, InputValidationError, CalculationError
)

# Create router
router = APIRouter(
    prefix="/ephemeris",
    tags=["ephemeris"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Input validation failed"},
        422: {"model": ErrorResponse, "description": "Unprocessable Entity - Invalid input format"},
        500: {"model": ErrorResponse, "description": "Internal Server Error - Calculation failed"},
    }
)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the ephemeris service and verify ephemeris data availability."
)
async def health_check() -> HealthResponse:
    """
    Get service health status.
    
    Returns:
        HealthResponse: Service health information including ephemeris file availability
    """
    try:
        return ephemeris_service.get_health_status()
    except Exception as e:
        # Health check should not fail, but if it does, return basic status
        return HealthResponse(
            status="error",
            version="1.0.0",
            ephemeris_available=False,
            uptime=0.0
        )


@router.post(
    "/natal",
    response_model=NatalChartResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Natal Chart",
    description="""
    Calculate a complete natal chart for the given birth data.
    
    Supports multiple input formats:
    - Coordinates: decimal degrees, DMS strings, or component objects
    - DateTime: ISO strings, Julian Day numbers, or component objects  
    - Timezone: IANA names, UTC offsets, or auto-detection from coordinates
    
    Returns comprehensive chart data including:
    - Normalized subject birth data
    - All planetary positions with zodiac and house information
    - House system cusps and angles
    - Major aspects with orbs and applying/separating status
    """,
    responses={
        200: {
            "model": NatalChartResponse,
            "description": "Successful chart calculation"
        },
        400: {
            "model": ErrorResponse,
            "description": "Input validation error"
        },
        500: {
            "model": ErrorResponse,
            "description": "Chart calculation error"
        }
    }
)
async def calculate_natal_chart(
    request: NatalChartRequest
) -> Union[NatalChartResponse, JSONResponse]:
    """
    Calculate natal chart from birth data.
    
    Args:
        request: Natal chart calculation request
        
    Returns:
        Complete natal chart response with all calculated data
        
    Raises:
        HTTPException: For validation or calculation errors
    """
    try:
        # Calculate chart using service
        result = ephemeris_service.calculate_natal_chart(request)
        return result
        
    except InputValidationError as e:
        # Input validation errors (400 Bad Request)
        error_response = ephemeris_service.create_error_response(e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump()
        )
        
    except CalculationError as e:
        # Calculation errors (500 Internal Server Error)
        error_response = ephemeris_service.create_error_response(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )
        
    except Exception as e:
        # Unexpected errors (500 Internal Server Error)
        error_response = ephemeris_service.create_error_response(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )


@router.post(
    "/v2/natal-enhanced",
    response_model=NatalChartEnhancedResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Enhanced Natal Chart",
    description="""
    Calculate a comprehensive natal chart with enhanced features including configurable aspects and Arabic parts.
    
    Enhanced features include:
    - Professional aspect calculations with configurable orb systems
    - Traditional, Modern, or Tight orb presets
    - Custom orb configuration support
    - Applying/separating aspect detection
    - Aspect strength and exactitude calculations
    - Arabic parts calculations with sect determination
    - Traditional 16 Hermetic lots with day/night formula variations
    - Custom Arabic parts formula support
    - Retrograde motion analysis
    - Comprehensive calculation metadata
    
    Supports all input formats from the standard natal endpoint plus:
    - Aspect orb preset selection (traditional, modern, tight)
    - Custom orb configuration overrides
    - Arabic parts calculation with traditional lots
    - Custom Arabic parts formulas
    - Metadata detail level control
    
    Performance: Aspect calculations typically complete in <50ms, Arabic parts in <40ms for 16 traditional lots.
    """,
    responses={
        200: {
            "model": NatalChartEnhancedResponse,
            "description": "Successful enhanced chart calculation"
        },
        400: {
            "model": ErrorResponse,
            "description": "Input validation error"
        },
        500: {
            "model": ErrorResponse,
            "description": "Chart calculation error"
        }
    }
)
async def calculate_natal_chart_enhanced(
    request: NatalChartEnhancedRequest
) -> Union[NatalChartEnhancedResponse, JSONResponse]:
    """
    Calculate enhanced natal chart with aspect calculations and additional features.
    
    Args:
        request: Enhanced natal chart calculation request
        
    Returns:
        Complete enhanced natal chart response with aspects and metadata
        
    Raises:
        HTTPException: For validation or calculation errors
    """
    try:
        # Convert enhanced request to standard request for service
        standard_request = NatalChartRequest(
            subject=request.subject,
            configuration=request.configuration
        )
        
        # Calculate enhanced chart using service
        result_dict = ephemeris_service.calculate_natal_chart_enhanced(
            request=standard_request,
            include_aspects=request.include_aspects,
            aspect_orb_preset=request.aspect_orb_preset,
            custom_orb_config=request.custom_orb_config,
            include_south_nodes=True,  # Always include for enhanced
            include_retrograde_analysis=True,  # Always include for enhanced
            include_arabic_parts=request.include_arabic_parts,
            arabic_parts_selection=request.arabic_parts_selection,
            include_all_traditional_parts=request.include_all_traditional_parts,
            custom_arabic_formulas=request.custom_arabic_formulas,
            include_dignities=request.include_dignities
        )
        
        # Format response according to enhanced schema
        enhanced_response = _format_enhanced_response(result_dict, request.metadata_level)
        
        return enhanced_response
        
    except InputValidationError as e:
        # Input validation errors (400 Bad Request)
        error_response = ephemeris_service.create_error_response(e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump()
        )
        
    except CalculationError as e:
        # Calculation errors (500 Internal Server Error)
        error_response = ephemeris_service.create_error_response(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )
        
    except Exception as e:
        # Unexpected errors (500 Internal Server Error)
        error_response = ephemeris_service.create_error_response(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )


def _format_enhanced_response(result_dict: dict, metadata_level: str) -> NatalChartEnhancedResponse:
    """
    Format the enhanced chart calculation result into the proper response schema.
    
    Args:
        result_dict: Raw result dictionary from service
        metadata_level: Level of metadata detail to include
        
    Returns:
        Formatted enhanced response
    """
    # Extract calculation metadata
    calculation_time = result_dict.get('calculation_time', 0.0)
    aspect_matrix_data = result_dict.get('aspect_matrix', {})
    
    # Determine features included
    features_included = []
    if result_dict.get('aspects'):
        features_included.append('aspects')
    if result_dict.get('retrograde_analysis'):
        features_included.append('retrograde_analysis')
    if result_dict.get('arabic_parts'):
        features_included.append('arabic_parts')
    
    # Create calculation metadata based on level
    metadata_fields = {
        'calculation_time': calculation_time,
        'features_included': features_included
    }
    
    if metadata_level in ['full', 'audit']:
        metadata_fields.update({
            'aspect_calculation_time_ms': aspect_matrix_data.get('calculation_time_ms'),
            'orb_system_used': aspect_matrix_data.get('orb_config_used')
        })
    
    if metadata_level == 'audit':
        metadata_fields['performance_metrics'] = {
            'total_aspects_calculated': aspect_matrix_data.get('total_aspects', 0),
            'aspect_breakdown': {
                'major': aspect_matrix_data.get('major_aspects', 0),
                'minor': aspect_matrix_data.get('minor_aspects', 0)
            }
        }
    
    calculation_metadata = CalculationMetadata(**metadata_fields)
    
    # Format enhanced aspects
    enhanced_aspects = []
    for aspect in result_dict.get('aspects', []):
        enhanced_aspect = EnhancedAspectResponse(
            object1=aspect.get('object1', ''),
            object2=aspect.get('object2', ''),
            aspect=aspect.get('aspect', ''),
            angle=aspect.get('angle', 0.0),
            orb=aspect.get('orb', 0.0),
            applying=aspect.get('applying'),
            strength=aspect.get('strength', 0.0),
            exact_angle=aspect.get('exact_angle', 0.0),
            orb_percentage=aspect.get('orb_percentage', 0.0)
        )
        enhanced_aspects.append(enhanced_aspect)
    
    # Create aspect matrix response if data available
    aspect_matrix_response = None
    if aspect_matrix_data:
        aspect_matrix_response = AspectMatrixResponse(**aspect_matrix_data)
    
    # Create Arabic parts response if data available
    arabic_parts_response = None
    if result_dict.get('arabic_parts'):
        arabic_parts_data = result_dict['arabic_parts']
        
        # Format sect determination
        sect_data = arabic_parts_data.get('sect_determination', {})
        sect_response = SectDeterminationResponse(
            sect=sect_data.get('sect', 'unknown'),
            is_day_chart=sect_data.get('is_day_chart', False),
            sun_above_horizon=sect_data.get('sun_above_horizon', False),
            method_used=sect_data.get('method_used', 'unknown'),
            validation_methods=sect_data.get('validation_methods', {})
        )
        
        # Format individual Arabic parts
        formatted_parts = {}
        for name, part_data in arabic_parts_data.get('arabic_parts', {}).items():
            formatted_parts[name] = ArabicPartResponse(
                name=part_data.get('name', name),
                display_name=part_data.get('display_name', name.title()),
                longitude=part_data.get('longitude', 0.0),
                sign_name=part_data.get('sign_name', ''),
                sign_longitude=part_data.get('sign_longitude', 0.0),
                house_number=part_data.get('house_number', 1),
                formula_used=part_data.get('formula_used', ''),
                description=part_data.get('description', ''),
                traditional_source=part_data.get('traditional_source', '')
            )
        
        # Convert formulas_used from dict to list (schema expects list)
        formulas_used_dict = arabic_parts_data.get('formulas_used', {})
        formulas_used_list = list(formulas_used_dict.keys()) if isinstance(formulas_used_dict, dict) else []
        
        arabic_parts_response = ArabicPartsResponse(
            sect_determination=sect_response,
            arabic_parts=formatted_parts,
            formulas_used=formulas_used_list,
            calculation_time_ms=arabic_parts_data.get('calculation_time_ms', 0.0),
            total_parts_calculated=arabic_parts_data.get('total_parts_calculated', 0)
        )
    
    # Format planets properly with enhanced data
    from ..api.models.schemas import PlanetResponse, EssentialDignityInfo
    formatted_planets = {}
    
    for planet_name, planet_data in result_dict.get('planets', {}).items():
        # Create essential dignity info if present
        dignity_info = None
        if 'essential_dignities' in planet_data and planet_data['essential_dignities']:
            dignity_info = EssentialDignityInfo(**planet_data['essential_dignities'])
        
        # Create properly formatted planet response
        formatted_planet = PlanetResponse(
            name=planet_data.get('name', planet_name),
            longitude=planet_data.get('longitude'),
            latitude=planet_data.get('latitude'),
            distance=planet_data.get('distance'),
            longitude_speed=planet_data.get('longitude_speed'),
            is_retrograde=planet_data.get('is_retrograde', False),
            motion_type=planet_data.get('motion_type', 'direct'),
            sign_name=planet_data.get('sign_name'),
            sign_longitude=planet_data.get('sign_longitude'),
            house_number=planet_data.get('house_number'),
            element=planet_data.get('element'),
            modality=planet_data.get('modality'),
            essential_dignities=dignity_info
        )
        formatted_planets[planet_name] = formatted_planet

    # Build enhanced response
    enhanced_response = NatalChartEnhancedResponse(
        success=result_dict.get('success', True),
        subject=result_dict['subject'],
        planets=formatted_planets,
        houses=result_dict['houses'],
        angles=result_dict['angles'],
        aspects=enhanced_aspects,
        aspect_matrix=aspect_matrix_response,
        calculation_metadata=calculation_metadata,
        retrograde_analysis=result_dict.get('retrograde_analysis'),
        arabic_parts=arabic_parts_response,
        chart_type="natal_enhanced"
    )
    
    return enhanced_response


@router.get(
    "/schemas/natal-request",
    summary="Get Natal Chart Request Schema",
    description="Get the JSON schema for natal chart request format with examples."
)
async def get_natal_request_schema():
    """
    Get the JSON schema for natal chart requests.
    
    Returns:
        JSON schema with validation rules and examples
    """
    return {
        "schema": NatalChartRequest.model_json_schema(),
        "examples": {
            "basic": {
                "subject": {
                    "name": "John Doe",
                    "datetime": {"iso_string": "1990-06-15T14:30:00"},
                    "latitude": {"decimal": 40.7128},
                    "longitude": {"decimal": -74.0060},
                    "timezone": {"name": "America/New_York"}
                }
            },
            "dms_coordinates": {
                "subject": {
                    "name": "Jane Smith",
                    "datetime": {"iso_string": "1985-03-21T09:15:00Z"},
                    "latitude": {"dms": "51°30'26\"N"},
                    "longitude": {"dms": "0°7'39\"W"},
                    "timezone": {"name": "Europe/London"}
                },
                "configuration": {
                    "house_system": "K",
                    "include_asteroids": False
                }
            },
            "component_format": {
                "subject": {
                    "name": "Test Subject",
                    "datetime": {
                        "components": {
                            "year": 2000,
                            "month": 12,
                            "day": 25,
                            "hour": 18,
                            "minute": 30
                        }
                    },
                    "latitude": {
                        "components": {
                            "degrees": 34,
                            "minutes": 3,
                            "seconds": 8,
                            "direction": "N"
                        }
                    },
                    "longitude": {
                        "components": {
                            "degrees": 118,
                            "minutes": 14,
                            "seconds": 37,
                            "direction": "W"
                        }
                    },
                    "timezone": {"utc_offset": -8.0}
                }
            },
            "julian_day": {
                "subject": {
                    "name": "Historical Figure",
                    "datetime": {"julian_day": 2451545.0},
                    "latitude": {"decimal": 48.8566},
                    "longitude": {"decimal": 2.3522},
                    "timezone": {"name": "Europe/Paris"}
                },
                "configuration": {
                    "house_system": "P",
                    "aspect_orbs": {
                        "Conjunction": 10.0,
                        "Opposition": 10.0,
                        "Trine": 8.0,
                        "Square": 8.0,
                        "Sextile": 6.0
                    }
                }
            }
        }
    }


@router.get(
    "/schemas/natal-response", 
    summary="Get Natal Chart Response Schema",
    description="Get the JSON schema for natal chart response format."
)
async def get_natal_response_schema():
    """
    Get the JSON schema for natal chart responses.
    
    Returns:
        JSON schema describing the response format
    """
    return {
        "schema": NatalChartResponse.model_json_schema(),
        "description": "Complete natal chart data with all calculated positions and relationships"
    }


# Additional utility endpoints for development/debugging

@router.get(
    "/house-systems",
    summary="Get Supported House Systems",
    description="Get list of supported house systems with their codes and names."
)
async def get_supported_house_systems():
    """
    Get list of supported house systems.
    
    Returns:
        Dictionary of house system codes and names
    """
    return {
        "house_systems": {
            "P": "Placidus",
            "K": "Koch", 
            "O": "Porphyry",
            "R": "Regiomontanus",
            "C": "Campanus",
            "E": "Equal House",
            "W": "Whole Sign"
        },
        "default": "P",
        "description": "Supported house calculation systems"
    }


@router.get(
    "/supported-objects",
    summary="Get Supported Celestial Objects",
    description="Get list of celestial objects included in chart calculations."
)
async def get_supported_objects():
    """
    Get list of supported celestial objects.
    
    Returns:
        Dictionary of object categories and their members
    """
    from ...core.ephemeris.const import MODERN_PLANETS, MAJOR_ASTEROIDS, LUNAR_NODES, LILITH_POINTS, PLANET_NAMES
    
    return {
        "planets": {
            "ids": MODERN_PLANETS,
            "names": [PLANET_NAMES.get(pid, f"Object {pid}") for pid in MODERN_PLANETS]
        },
        "asteroids": {
            "ids": MAJOR_ASTEROIDS,
            "names": [PLANET_NAMES.get(aid, f"Asteroid {aid}") for aid in MAJOR_ASTEROIDS]
        },
        "nodes": {
            "ids": LUNAR_NODES,
            "names": [PLANET_NAMES.get(nid, f"Node {nid}") for nid in LUNAR_NODES]
        },
        "lilith": {
            "ids": LILITH_POINTS,
            "names": [PLANET_NAMES.get(lid, f"Lilith {lid}") for lid in LILITH_POINTS]
        },
        "configuration": {
            "default_includes": {
                "planets": True,
                "asteroids": True,
                "nodes": True,
                "lilith": True
            }
        }
    }


def _format_enhanced_response(result_dict: dict, metadata_level: str) -> NatalChartEnhancedResponse:
    """
    Format the enhanced chart calculation result into the proper response schema.
    
    Args:
        result_dict: Raw result dictionary from service
        metadata_level: Level of metadata detail to include
        
    Returns:
        Formatted enhanced response
    """
    # Extract base natal chart data
    success = result_dict.get('success', True)
    subject = result_dict.get('subject', {})
    planets = result_dict.get('planets', {})
    houses = result_dict.get('houses', {})
    angles = result_dict.get('angles', {})
    aspects = result_dict.get('aspects', [])
    
    # Extract enhanced features
    arabic_parts_data = result_dict.get('arabic_parts', {})
    
    # Extract calculation metadata
    calculation_time = result_dict.get('calculation_time')
    aspect_matrix_data = result_dict.get('aspect_matrix', {})
    
    # Determine features included based on what's in the result
    features_included = []
    if aspects:
        features_included.append('aspects')
    if arabic_parts_data:
        features_included.append('arabic_parts')
    if result_dict.get('include_dignities'):
        features_included.append('dignities')
    if result_dict.get('include_retrograde_analysis'):
        features_included.append('retrograde_analysis')
    
    # Format Arabic parts data into proper response structure or None
    arabic_parts = None
    if arabic_parts_data and isinstance(arabic_parts_data, dict):
        # If there's Arabic parts data, try to format it properly
        # For now, if we don't have proper sect determination data, set to None
        if 'sect_determination' in arabic_parts_data and 'arabic_parts' in arabic_parts_data:
            try:
                arabic_parts = ArabicPartsResponse(**arabic_parts_data)
            except Exception:
                # If validation fails, set to None rather than crash
                arabic_parts = None
    
    # Create calculation metadata based on level
    metadata = CalculationMetadata(
        calculation_time=calculation_time,
        features_included=features_included
    )
    
    # Add additional metadata based on level
    if metadata_level in ['full', 'audit']:
        metadata.aspect_calculation_time_ms = aspect_matrix_data.get('calculation_time_ms')
        metadata.orb_system_used = aspect_matrix_data.get('orb_config_used')
        
    if metadata_level == 'audit':
        # Add comprehensive performance metrics for audit level
        metadata.performance_metrics = {
            'total_calculation_time_ms': (calculation_time or 0) * 1000,
            'aspect_count': len(aspects),
            'arabic_parts_count': len(arabic_parts_data) if isinstance(arabic_parts_data, dict) and 'arabic_parts' in arabic_parts_data else 0
        }
    
    # Create aspect matrix response if available
    aspect_matrix = None
    if aspect_matrix_data:
        aspect_matrix = AspectMatrixResponse(
            total_aspects=aspect_matrix_data.get('total_aspects', len(aspects)),
            major_aspects=aspect_matrix_data.get('major_aspects', 0),
            minor_aspects=aspect_matrix_data.get('minor_aspects', 0),
            orb_config_used=aspect_matrix_data.get('orb_config_used', 'unknown'),
            calculation_time_ms=aspect_matrix_data.get('calculation_time_ms', 0.0)
        )
    
    # Create enhanced response
    return NatalChartEnhancedResponse(
        success=success,
        subject=subject,
        planets=planets,
        houses=houses,
        angles=angles,
        aspects=aspects,
        aspect_matrix=aspect_matrix,
        arabic_parts=arabic_parts,
        calculation_metadata=metadata,
        chart_type="natal_enhanced"
    )


# Note: Exception handlers are defined in main.py for the full application