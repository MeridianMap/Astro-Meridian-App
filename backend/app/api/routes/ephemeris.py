"""
Meridian Ephemeris API - Ephemeris Routes

FastAPI routes for ephemeris calculations and chart generation.
Provides standardized REST endpoints with comprehensive input validation.
"""

from typing import Union
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ..models.schemas import (
    NatalChartRequest, NatalChartResponse, ErrorResponse, HealthResponse
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


# Note: Exception handlers are defined in main.py for the full application