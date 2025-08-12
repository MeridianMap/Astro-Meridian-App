"""
Meridian Ephemeris API - Pydantic Schemas

Defines the API input and output models for the ephemeris service endpoints.
Provides comprehensive validation and standardized serialization.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum


class HouseSystemEnum(str, Enum):
    """Supported house systems."""
    PLACIDUS = "P"
    KOCH = "K"
    PORPHYRY = "O"
    REGIOMONTANUS = "R"
    CAMPANUS = "C"
    EQUAL = "E"
    WHOLE_SIGN = "W"


class CoordinateInput(BaseModel):
    """Flexible coordinate input supporting multiple formats."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {"decimal": 40.7128},
                {"dms": "40°42'46\"N"},
                {"components": {"degrees": 40, "minutes": 42, "seconds": 46, "direction": "N"}}
            ]
        }
    )
    
    decimal: Optional[float] = Field(None, description="Decimal degrees (-90 to 90 for lat, -180 to 180 for lon)")
    dms: Optional[str] = Field(None, description="Degrees, minutes, seconds string (e.g., '40°42'46\"N')")
    components: Optional[Dict[str, Union[int, float, str]]] = Field(
        None, 
        description="Separate degree components with direction"
    )
    
    @model_validator(mode='after')
    def validate_coordinate_input(self):
        """Ensure exactly one coordinate format is provided."""
        values = self.__dict__
        provided_formats = [f for f in ['decimal', 'dms', 'components'] if values.get(f) is not None]
        
        if len(provided_formats) != 1:
            raise ValueError("Exactly one coordinate format must be provided (decimal, dms, or components)")
        
        return self


class DateTimeInput(BaseModel):
    """Flexible datetime input supporting multiple formats."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {"iso_string": "2000-01-01T12:00:00"},
                {"iso_string": "2000-01-01T12:00:00Z"},
                {"julian_day": 2451545.0},
                {"components": {"year": 2000, "month": 1, "day": 1, "hour": 12, "minute": 0, "second": 0}}
            ]
        }
    )
    
    iso_string: Optional[str] = Field(None, description="ISO 8601 datetime string")
    julian_day: Optional[float] = Field(None, description="Julian Day Number")
    components: Optional[Dict[str, int]] = Field(None, description="Separate datetime components")
    
    @model_validator(mode='after')
    def validate_datetime_input(self):
        """Ensure exactly one datetime format is provided."""
        values = self.__dict__
        provided_formats = [f for f in ['iso_string', 'julian_day', 'components'] if values.get(f) is not None]
        
        if len(provided_formats) != 1:
            raise ValueError("Exactly one datetime format must be provided (iso_string, julian_day, or components)")
        
        return self


class TimezoneInput(BaseModel):
    """Flexible timezone input supporting multiple formats."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {"name": "America/New_York"},
                {"utc_offset": -5.0},
                {"auto_detect": True}
            ]
        }
    )
    
    name: Optional[str] = Field(None, description="IANA timezone name (e.g., 'America/New_York')")
    utc_offset: Optional[float] = Field(None, description="UTC offset in hours (e.g., -5.0)")
    auto_detect: Optional[bool] = Field(False, description="Auto-detect timezone from coordinates")


class SubjectRequest(BaseModel):
    """Request model for subject birth data."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "datetime": {"iso_string": "1990-06-15T14:30:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "altitude": 100.0,
                "timezone": {"name": "America/New_York"}
            }
        }
    )
    
    name: str = Field(..., min_length=1, max_length=255, description="Subject name or identifier")
    datetime: DateTimeInput = Field(..., description="Birth datetime in various formats")
    latitude: CoordinateInput = Field(..., description="Birth latitude")
    longitude: CoordinateInput = Field(..., description="Birth longitude") 
    altitude: Optional[float] = Field(0.0, description="Altitude in meters above sea level")
    timezone: Optional[TimezoneInput] = Field(None, description="Timezone information")


class ChartConfiguration(BaseModel):
    """Configuration options for chart calculation."""
    
    model_config = ConfigDict(extra="forbid")
    
    house_system: HouseSystemEnum = Field(
        HouseSystemEnum.PLACIDUS,
        description="House system to use for calculations"
    )
    include_asteroids: bool = Field(True, description="Include major asteroids")
    include_nodes: bool = Field(True, description="Include lunar nodes")
    include_lilith: bool = Field(True, description="Include Lilith points")
    parallel_processing: bool = Field(True, description="Use parallel processing for performance")
    aspect_orbs: Optional[Dict[str, float]] = Field(
        None,
        description="Custom aspect orb settings in degrees"
    )


class NatalChartRequest(BaseModel):
    """Complete request for natal chart calculation."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "subject": {
                    "name": "John Doe",
                    "datetime": {"iso_string": "1990-06-15T14:30:00"},
                    "latitude": {"decimal": 40.7128},
                    "longitude": {"decimal": -74.0060},
                    "timezone": {"name": "America/New_York"}
                },
                "configuration": {
                    "house_system": "P",
                    "include_asteroids": True
                }
            }
        }
    )
    
    subject: SubjectRequest = Field(..., description="Subject birth data")
    configuration: Optional[ChartConfiguration] = Field(
        ChartConfiguration(),
        description="Chart calculation configuration"
    )


# Response Models

class SubjectResponse(BaseModel):
    """Normalized subject data in response."""
    
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(..., description="Subject name")
    datetime: str = Field(..., description="ISO format datetime")
    julian_day: float = Field(..., description="Julian Day Number")
    latitude: float = Field(..., description="Latitude in decimal degrees")
    longitude: float = Field(..., description="Longitude in decimal degrees")
    altitude: float = Field(..., description="Altitude in meters")
    timezone_name: Optional[str] = Field(None, description="Timezone name if available")
    utc_offset: Optional[float] = Field(None, description="UTC offset in hours")


class PlanetResponse(BaseModel):
    """Planet position data in response."""
    
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(..., description="Planet name")
    longitude: float = Field(..., description="Ecliptic longitude in degrees")
    latitude: float = Field(..., description="Ecliptic latitude in degrees")
    distance: float = Field(..., description="Distance from Earth")
    longitude_speed: Optional[float] = Field(None, description="Longitude speed in degrees/day")
    sign_name: Optional[str] = Field(None, description="Zodiac sign name")
    sign_longitude: Optional[float] = Field(None, description="Longitude within sign")
    house_number: Optional[int] = Field(None, description="House number (1-12)")
    element: Optional[str] = Field(None, description="Element (Fire, Earth, Air, Water)")
    modality: Optional[str] = Field(None, description="Modality (Cardinal, Fixed, Mutable)")


class HousesResponse(BaseModel):
    """House system data in response."""
    
    model_config = ConfigDict(extra="allow")
    
    system: str = Field(..., description="House system code")
    cusps: List[float] = Field(..., description="House cusp longitudes in degrees")


class AnglesResponse(BaseModel):
    """Chart angles data in response."""
    
    model_config = ConfigDict(extra="allow")
    
    ascendant: float = Field(..., description="Ascendant longitude in degrees")
    midheaven: float = Field(..., description="Midheaven longitude in degrees") 
    descendant: float = Field(..., description="Descendant longitude in degrees")
    imum_coeli: float = Field(..., description="Imum Coeli longitude in degrees")


class AspectResponse(BaseModel):
    """Aspect relationship data in response."""
    
    model_config = ConfigDict(extra="allow")
    
    object1: str = Field(..., description="First object name")
    object2: str = Field(..., description="Second object name")
    aspect: str = Field(..., description="Aspect name")
    angle: float = Field(..., description="Exact angle in degrees")
    orb: float = Field(..., description="Orb from exact aspect")
    applying: Optional[bool] = Field(None, description="Whether aspect is applying")


class NatalChartResponse(BaseModel):
    """Complete natal chart response."""
    
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "success": True,
                "subject": {
                    "name": "John Doe",
                    "datetime": "1990-06-15T14:30:00-04:00",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "planets": {
                    "Sun": {
                        "longitude": 84.5,
                        "sign_name": "Gemini",
                        "house_number": 10
                    }
                },
                "calculation_time": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    success: bool = Field(..., description="Whether calculation succeeded")
    subject: SubjectResponse = Field(..., description="Normalized subject data")
    planets: Dict[str, PlanetResponse] = Field(..., description="Planet positions by name")
    houses: HousesResponse = Field(..., description="House system data")
    angles: AnglesResponse = Field(..., description="Chart angles")
    aspects: List[AspectResponse] = Field(..., description="Aspect relationships")
    calculation_time: str = Field(..., description="When calculation was performed")
    chart_type: str = Field("natal", description="Type of chart")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    model_config = ConfigDict(extra="forbid")
    
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response."""
    
    model_config = ConfigDict(extra="forbid")
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    ephemeris_available: bool = Field(..., description="Whether ephemeris files are available")
    uptime: float = Field(..., description="Service uptime in seconds")