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


# Enhanced API Models for Aspect Calculations

class NatalChartEnhancedRequest(BaseModel):
    """Enhanced request for natal chart calculation with aspect configuration."""
    
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
                },
                "include_aspects": True,
                "aspect_orb_preset": "traditional",
                "metadata_level": "full",
                "include_arabic_parts": True,
                "include_all_traditional_parts": True
            }
        }
    )
    
    subject: SubjectRequest = Field(..., description="Subject birth data")
    configuration: Optional[ChartConfiguration] = Field(
        ChartConfiguration(),
        description="Chart calculation configuration"
    )
    include_aspects: bool = Field(True, description="Include aspect calculations")
    aspect_orb_preset: str = Field(
        "traditional", 
        description="Orb system preset: 'traditional', 'modern', or 'tight'"
    )
    custom_orb_config: Optional[Dict[str, Dict[str, float]]] = Field(
        None,
        description="Custom orb configuration (overrides preset)"
    )
    metadata_level: str = Field(
        "basic",
        description="Metadata detail level: 'basic', 'full', or 'audit'"
    )
    include_arabic_parts: bool = Field(
        False, 
        description="Include Arabic parts calculations in the chart"
    )
    arabic_parts_selection: Optional[List[str]] = Field(
        None,
        description="Specific Arabic parts to calculate (if None, uses include_all_traditional_parts setting)"
    )
    include_all_traditional_parts: bool = Field(
        False,
        description="Include all 16 traditional Arabic parts when include_arabic_parts is True"
    )
    custom_arabic_formulas: Optional[Dict[str, Dict[str, str]]] = Field(
        None,
        description="Custom Arabic part formulas with day/night variations"
    )

    @field_validator('aspect_orb_preset')
    @classmethod
    def validate_orb_preset(cls, v):
        valid_presets = ['traditional', 'modern', 'tight']
        if v not in valid_presets:
            raise ValueError(f"aspect_orb_preset must be one of {valid_presets}")
        return v
    
    @field_validator('metadata_level')
    @classmethod
    def validate_metadata_level(cls, v):
        valid_levels = ['basic', 'full', 'audit']
        if v not in valid_levels:
            raise ValueError(f"metadata_level must be one of {valid_levels}")
        return v
    
    @field_validator('arabic_parts_selection')
    @classmethod
    def validate_arabic_parts_selection(cls, v, info):
        if v is not None and not isinstance(v, list):
            raise ValueError("arabic_parts_selection must be a list of strings")
        if v is not None and len(v) == 0:
            raise ValueError("arabic_parts_selection cannot be an empty list")
        return v


class AspectMatrixResponse(BaseModel):
    """Aspect matrix summary data."""
    
    model_config = ConfigDict(extra="allow")
    
    total_aspects: int = Field(..., description="Total number of aspects found")
    major_aspects: int = Field(..., description="Number of major aspects")
    minor_aspects: int = Field(..., description="Number of minor aspects")
    orb_config_used: str = Field(..., description="Orb configuration preset used")
    calculation_time_ms: float = Field(..., description="Calculation time in milliseconds")


class EnhancedAspectResponse(BaseModel):
    """Enhanced aspect relationship data with additional metadata."""
    
    model_config = ConfigDict(extra="allow")
    
    object1: str = Field(..., description="First object name")
    object2: str = Field(..., description="Second object name") 
    aspect: str = Field(..., description="Aspect name")
    angle: float = Field(..., description="Exact angle in degrees")
    orb: float = Field(..., description="Orb from exact aspect in degrees")
    applying: Optional[bool] = Field(None, description="Whether aspect is applying")
    strength: float = Field(..., description="Aspect strength (0.0-1.0, where 1.0 is exact)")
    exact_angle: float = Field(..., description="Expected exact angle for this aspect type")
    orb_percentage: float = Field(..., description="Percentage of maximum orb used")


class SectDeterminationResponse(BaseModel):
    """Sect determination data in response."""
    
    model_config = ConfigDict(extra="allow")
    
    sect: str = Field(..., description="Chart sect: 'day' or 'night'")
    is_day_chart: bool = Field(..., description="Whether this is a day chart")
    sun_above_horizon: bool = Field(..., description="Whether sun is above horizon")
    method_used: str = Field(..., description="Method used for sect determination")
    validation_methods: Dict[str, bool] = Field(
        default_factory=dict,
        description="Results from multiple validation methods"
    )
    

class ArabicPartResponse(BaseModel):
    """Arabic part calculation data in response."""
    
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(..., description="Arabic part name identifier")
    display_name: str = Field(..., description="Human-readable display name")
    longitude: float = Field(..., description="Arabic part longitude in degrees")
    sign_name: str = Field(..., description="Zodiac sign name")
    sign_longitude: float = Field(..., description="Longitude within sign (0-29.999...)")
    house_number: int = Field(..., description="House number (1-12)")
    formula_used: str = Field(..., description="Formula used for calculation")
    description: str = Field(..., description="Description of this Arabic part's meaning")
    traditional_source: str = Field(..., description="Traditional astrological source")
    

class ArabicPartsResponse(BaseModel):
    """Complete Arabic parts calculation results."""
    
    model_config = ConfigDict(extra="allow")
    
    sect_determination: SectDeterminationResponse = Field(
        ..., 
        description="Day/night sect determination results"
    )
    arabic_parts: Dict[str, ArabicPartResponse] = Field(
        ..., 
        description="Arabic parts calculations by name"
    )
    formulas_used: List[str] = Field(
        ..., 
        description="List of formula names that were calculated"
    )
    calculation_time_ms: float = Field(
        ..., 
        description="Arabic parts calculation time in milliseconds"
    )
    total_parts_calculated: int = Field(
        ..., 
        description="Total number of Arabic parts calculated"
    )


class CalculationMetadata(BaseModel):
    """Calculation metadata and performance information."""
    
    model_config = ConfigDict(extra="allow")
    
    calculation_time: float = Field(..., description="Total calculation time in seconds")
    aspect_calculation_time_ms: Optional[float] = Field(
        None, 
        description="Aspect calculation time in milliseconds"
    )
    orb_system_used: Optional[str] = Field(None, description="Orb system configuration used")
    features_included: List[str] = Field(
        default_factory=list, 
        description="List of features included in calculation"
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional performance metrics"
    )


class NatalChartEnhancedResponse(BaseModel):
    """Enhanced natal chart response with aspect calculations and metadata."""
    
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
                "aspects": [
                    {
                        "object1": "Sun",
                        "object2": "Moon", 
                        "aspect": "Sextile",
                        "angle": 58.2,
                        "orb": 1.8,
                        "applying": True,
                        "strength": 0.95
                    }
                ],
                "aspect_matrix": {
                    "total_aspects": 15,
                    "major_aspects": 12,
                    "minor_aspects": 3,
                    "orb_config_used": "traditional"
                },
                "calculation_metadata": {
                    "calculation_time": 0.045,
                    "features_included": ["aspects", "retrograde_analysis"]
                }
            }
        }
    )
    
    success: bool = Field(..., description="Whether calculation succeeded")
    subject: SubjectResponse = Field(..., description="Normalized subject data")
    planets: Dict[str, PlanetResponse] = Field(..., description="Planet positions by name")
    houses: HousesResponse = Field(..., description="House system data")
    angles: AnglesResponse = Field(..., description="Chart angles")
    aspects: List[EnhancedAspectResponse] = Field(..., description="Enhanced aspect relationships")
    aspect_matrix: Optional[AspectMatrixResponse] = Field(
        None, 
        description="Aspect matrix summary data"
    )
    calculation_metadata: CalculationMetadata = Field(
        ..., 
        description="Calculation metadata and performance information"
    )
    retrograde_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="Retrograde motion analysis if requested"
    )
    arabic_parts: Optional[ArabicPartsResponse] = Field(
        None,
        description="Arabic parts calculations if requested"
    )
    chart_type: str = Field("natal_enhanced", description="Type of chart")