"""
Meridian Ephemeris API - Predictive Astrology Schemas

Pydantic schemas for eclipse and transit prediction API endpoints.
Provides comprehensive validation and standardized serialization for
NASA-validated astronomical calculations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum

from .schemas import CoordinateInput, DateTimeInput, TimezoneInput
from ...core.ephemeris.tools.predictive_models import (
    SolarEclipse, LunarEclipse, Transit, SignIngress, 
    EclipseVisibility, GeographicLocation
)


class EclipseTypeEnum(str, Enum):
    """Eclipse types for filtering."""
    TOTAL = "total"
    PARTIAL = "partial"
    ANNULAR = "annular"
    HYBRID = "hybrid"
    PENUMBRAL = "penumbral"


class PlanetEnum(str, Enum):
    """Supported planets for transit calculations."""
    SUN = "Sun"
    MOON = "Moon"
    MERCURY = "Mercury"
    VENUS = "Venus"
    MARS = "Mars"
    JUPITER = "Jupiter"
    SATURN = "Saturn"
    URANUS = "Uranus"
    NEPTUNE = "Neptune"
    PLUTO = "Pluto"


class ZodiacSignEnum(str, Enum):
    """Zodiac signs for ingress calculations."""
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"


# Common Schemas

class LocationInput(BaseModel):
    """Geographic location input for eclipse visibility calculations."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "latitude": {"decimal": 40.7128},
                    "longitude": {"decimal": -74.0060},
                    "elevation": 10.0,
                    "timezone": {"name": "America/New_York"}
                }
            ]
        }
    )
    
    latitude: CoordinateInput = Field(..., description="Geographic latitude")
    longitude: CoordinateInput = Field(..., description="Geographic longitude")
    elevation: Optional[float] = Field(0.0, description="Elevation above sea level in meters")
    timezone: Optional[TimezoneInput] = Field(None, description="Local timezone information")


class PredictiveMetadata(BaseModel):
    """Metadata for predictive calculation responses."""
    
    model_config = ConfigDict(extra="allow")
    
    calculation_type: str = Field(..., description="Type of calculation performed")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    search_range_years: Optional[float] = Field(None, description="Years searched")
    nasa_validated: bool = Field(True, description="NASA validation status")
    accuracy_statement: Optional[str] = Field(None, description="Accuracy information")
    performance_note: Optional[str] = Field(None, description="Performance information")
    cache_status: Optional[str] = Field(None, description="Cache hit/miss status")


class ErrorResponse(BaseModel):
    """Standardized error response."""
    
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# Eclipse Request/Response Schemas

class NextEclipseRequest(BaseModel):
    """Request schema for finding next eclipse."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "start_date": "2024-01-01T00:00:00Z",
                    "eclipse_type": "total",
                    "location": {
                        "latitude": {"decimal": 40.7128},
                        "longitude": {"decimal": -74.0060}
                    }
                }
            ]
        }
    )
    
    start_date: datetime = Field(..., description="Starting date for eclipse search")
    eclipse_type: Optional[EclipseTypeEnum] = Field(None, description="Optional eclipse type filter")
    location: Optional[LocationInput] = Field(None, description="Optional location for visibility filtering")
    
    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v):
        """Validate start date is not too far in the past or future."""
        now = datetime.now()
        if v.year < 1900 or v.year > 2100:
            raise ValueError("Start date must be between years 1900 and 2100")
        return v


class NextEclipseResponse(BaseModel):
    """Response schema for next eclipse search."""
    
    success: bool = Field(..., description="Request success status")
    eclipse: Optional[Union[SolarEclipse, LunarEclipse]] = Field(None, description="Eclipse information")
    message: str = Field(..., description="Response message")
    metadata: PredictiveMetadata = Field(..., description="Calculation metadata")


class EclipseSearchRequest(BaseModel):
    """Request schema for eclipse range search."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2025-01-01T00:00:00Z",
                    "eclipse_types": ["total", "annular"],
                    "location": {
                        "latitude": {"decimal": 40.7128},
                        "longitude": {"decimal": -74.0060}
                    }
                }
            ]
        }
    )
    
    start_date: datetime = Field(..., description="Search range start date")
    end_date: datetime = Field(..., description="Search range end date")
    eclipse_types: Optional[List[EclipseTypeEnum]] = Field(None, description="Eclipse types to include")
    location: Optional[LocationInput] = Field(None, description="Location for visibility filtering")
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_dates(cls, v):
        """Validate dates are within reasonable range."""
        if v.year < 1900 or v.year > 2100:
            raise ValueError("Dates must be between years 1900 and 2100")
        return v
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """Ensure end date is after start date."""
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        
        # Check maximum search range
        years_diff = (self.end_date - self.start_date).days / 365.25
        if years_diff > 10:
            raise ValueError("Maximum search range is 10 years")
        
        return self


class EclipseSearchResponse(BaseModel):
    """Response schema for eclipse range search."""
    
    success: bool = Field(..., description="Request success status")
    eclipses: Dict[str, List[Union[SolarEclipse, LunarEclipse]]] = Field(
        ..., description="Found eclipses grouped by type (solar/lunar)"
    )
    total_count: int = Field(..., description="Total number of eclipses found")
    search_range_years: float = Field(..., description="Years searched")
    metadata: PredictiveMetadata = Field(..., description="Calculation metadata")


class EclipseVisibilityRequest(BaseModel):
    """Request schema for eclipse visibility calculation."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "eclipse_time": "2024-04-08T18:00:00Z",
                    "eclipse_type": "solar",
                    "location": {
                        "latitude": {"decimal": 40.7128},
                        "longitude": {"decimal": -74.0060}
                    }
                }
            ]
        }
    )
    
    eclipse_time: datetime = Field(..., description="Eclipse maximum time")
    eclipse_type: str = Field(..., description="Eclipse type (solar or lunar)")
    location: LocationInput = Field(..., description="Observer location")
    
    @field_validator('eclipse_type')
    @classmethod
    def validate_eclipse_type(cls, v):
        """Validate eclipse type."""
        if v.lower() not in ['solar', 'lunar']:
            raise ValueError("Eclipse type must be 'solar' or 'lunar'")
        return v.lower()


class EclipseVisibilityResponse(BaseModel):
    """Response schema for eclipse visibility calculation."""
    
    success: bool = Field(..., description="Request success status")
    visibility: EclipseVisibility = Field(..., description="Detailed visibility information")
    metadata: PredictiveMetadata = Field(..., description="Calculation metadata")


# Transit Request/Response Schemas

class PlanetTransitRequest(BaseModel):
    """Request schema for planetary transit calculation."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "planet_name": "Mars",
                    "target_degree": 15.5,
                    "start_date": "2024-01-01T00:00:00Z",
                    "max_crossings": 3
                }
            ]
        }
    )
    
    planet_name: PlanetEnum = Field(..., description="Planet name")
    target_degree: float = Field(..., description="Target longitude degree (0-360)")
    start_date: datetime = Field(..., description="Starting date for search")
    max_crossings: Optional[int] = Field(1, description="Maximum crossings to find (for retrograde)")
    
    @field_validator('target_degree')
    @classmethod
    def validate_degree(cls, v):
        """Validate degree is in valid range."""
        if not 0 <= v < 360:
            raise ValueError("Target degree must be between 0 and 360")
        return v
    
    @field_validator('max_crossings')
    @classmethod
    def validate_max_crossings(cls, v):
        """Validate max crossings is reasonable."""
        if v is not None and (v < 1 or v > 10):
            raise ValueError("Max crossings must be between 1 and 10")
        return v


class PlanetTransitResponse(BaseModel):
    """Response schema for planetary transit calculation."""
    
    success: bool = Field(..., description="Request success status")
    transits: List[Transit] = Field(..., description="Found transits")
    total_count: int = Field(..., description="Number of transits found")
    metadata: PredictiveMetadata = Field(..., description="Calculation metadata")


class SignIngressRequest(BaseModel):
    """Request schema for sign ingress calculation."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "planet_names": ["Mars", "Jupiter"],
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2025-01-01T00:00:00Z",
                    "target_sign": "Aries"
                }
            ]
        }
    )
    
    planet_names: Optional[List[PlanetEnum]] = Field(None, description="Specific planets (default: all)")
    start_date: datetime = Field(..., description="Search range start date")
    end_date: Optional[datetime] = Field(None, description="Search range end date (default: +1 year)")
    target_sign: Optional[ZodiacSignEnum] = Field(None, description="Specific sign to search for")
    
    @model_validator(mode='after')
    def set_default_end_date(self):
        """Set default end date if not provided."""
        if self.end_date is None:
            # Default to 1 year from start date
            self.end_date = self.start_date.replace(year=self.start_date.year + 1)
        
        # Validate date range
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        
        # Check maximum search range
        years_diff = (self.end_date - self.start_date).days / 365.25
        if years_diff > 5:
            raise ValueError("Maximum search range is 5 years for sign ingresses")
        
        return self


class SignIngressResponse(BaseModel):
    """Response schema for sign ingress calculation."""
    
    success: bool = Field(..., description="Request success status")
    ingresses: Dict[str, List[SignIngress]] = Field(
        ..., description="Ingresses grouped by planet name"
    )
    total_count: int = Field(..., description="Total number of ingresses found")
    metadata: PredictiveMetadata = Field(..., description="Calculation metadata")


class TransitSearchRequest(BaseModel):
    """Request schema for general transit search."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2025-01-01T00:00:00Z",
                    "planet_names": ["Mars", "Jupiter"],
                    "target_degrees": [0, 90, 180, 270],
                    "search_criteria": {
                        "include_retrograde": True,
                        "orb_degrees": 1.0
                    }
                }
            ]
        }
    )
    
    start_date: datetime = Field(..., description="Search range start date")
    end_date: datetime = Field(..., description="Search range end date")
    planet_names: Optional[List[PlanetEnum]] = Field(None, description="Planets to include")
    target_degrees: Optional[List[float]] = Field(None, description="Specific degrees to search for")
    search_criteria: Optional[Dict[str, Any]] = Field(None, description="Additional search criteria")
    
    @field_validator('target_degrees')
    @classmethod
    def validate_target_degrees(cls, v):
        """Validate target degrees."""
        if v is not None:
            for degree in v:
                if not 0 <= degree < 360:
                    raise ValueError(f"Target degree {degree} must be between 0 and 360")
        return v
    
    @model_validator(mode='after')
    def validate_search_params(self):
        """Validate search parameters."""
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        
        years_diff = (self.end_date - self.start_date).days / 365.25
        if years_diff > 5:
            raise ValueError("Maximum search range is 5 years for general transit search")
        
        return self


class TransitSearchResponse(BaseModel):
    """Response schema for general transit search."""
    
    success: bool = Field(..., description="Request success status")
    results: Dict[str, Any] = Field(..., description="Search results organized by criteria")
    search_range_years: float = Field(..., description="Years searched")
    metadata: PredictiveMetadata = Field(..., description="Calculation metadata")


# Batch Operation Schemas

class BatchEclipseRequest(BaseModel):
    """Request schema for batch eclipse calculations."""
    
    model_config = ConfigDict(extra="forbid")
    
    requests: List[NextEclipseRequest] = Field(..., description="List of eclipse requests")
    max_parallel: Optional[int] = Field(4, description="Maximum parallel calculations")
    
    @field_validator('requests')
    @classmethod
    def validate_batch_size(cls, v):
        """Validate batch size is reasonable."""
        if len(v) > 100:
            raise ValueError("Maximum 100 requests per batch")
        return v


class BatchEclipseResponse(BaseModel):
    """Response schema for batch eclipse calculations."""
    
    success: bool = Field(..., description="Batch operation success status")
    results: List[NextEclipseResponse] = Field(..., description="Individual eclipse results")
    batch_metadata: Dict[str, Any] = Field(..., description="Batch processing metadata")


class BatchTransitRequest(BaseModel):
    """Request schema for batch transit calculations."""
    
    model_config = ConfigDict(extra="forbid")
    
    requests: List[PlanetTransitRequest] = Field(..., description="List of transit requests")
    max_parallel: Optional[int] = Field(4, description="Maximum parallel calculations")
    
    @field_validator('requests')
    @classmethod
    def validate_batch_size(cls, v):
        """Validate batch size."""
        if len(v) > 50:
            raise ValueError("Maximum 50 requests per batch for transits")
        return v


class BatchTransitResponse(BaseModel):
    """Response schema for batch transit calculations."""
    
    success: bool = Field(..., description="Batch operation success status")
    results: List[PlanetTransitResponse] = Field(..., description="Individual transit results")
    batch_metadata: Dict[str, Any] = Field(..., description="Batch processing metadata")


# Advanced Features Schemas

class SolarReturnRequest(BaseModel):
    """Request schema for solar return calculations."""
    
    birth_date: datetime = Field(..., description="Birth date and time")
    return_year: int = Field(..., description="Year for solar return")
    location: LocationInput = Field(..., description="Location for solar return")
    
    @field_validator('return_year')
    @classmethod
    def validate_return_year(cls, v):
        """Validate return year is reasonable."""
        if v < 1900 or v > 2100:
            raise ValueError("Return year must be between 1900 and 2100")
        return v


class LunarReturnRequest(BaseModel):
    """Request schema for lunar return calculations."""
    
    birth_date: datetime = Field(..., description="Birth date and time")
    return_date: datetime = Field(..., description="Approximate date for lunar return")
    location: LocationInput = Field(..., description="Location for lunar return")


class PlanetaryStationRequest(BaseModel):
    """Request schema for planetary station calculations."""
    
    planet_name: PlanetEnum = Field(..., description="Planet name")
    start_date: datetime = Field(..., description="Search start date")
    end_date: datetime = Field(..., description="Search end date")
    station_type: Optional[str] = Field(None, description="Station type filter (direct/retrograde)")
    
    @field_validator('station_type')
    @classmethod
    def validate_station_type(cls, v):
        """Validate station type."""
        if v is not None and v.lower() not in ['direct', 'retrograde', 'both']:
            raise ValueError("Station type must be 'direct', 'retrograde', or 'both'")
        return v.lower() if v else v


# Configuration and Settings Schemas

class PredictiveSettings(BaseModel):
    """Settings for predictive calculations."""
    
    default_search_years: int = Field(5, description="Default search range in years")
    enable_caching: bool = Field(True, description="Enable result caching")
    cache_ttl_hours: int = Field(24, description="Cache TTL in hours")
    max_parallel_calculations: int = Field(4, description="Max parallel calculations")
    nasa_validation_enabled: bool = Field(True, description="Enable NASA cross-validation")
    performance_logging: bool = Field(True, description="Log performance metrics")


class FeatureFlags(BaseModel):
    """Feature flags for predictive functionality."""
    
    eclipse_calculations: bool = Field(True, description="Enable eclipse calculations")
    transit_calculations: bool = Field(True, description="Enable transit calculations")
    batch_processing: bool = Field(True, description="Enable batch processing")
    advanced_features: bool = Field(True, description="Enable advanced features")
    experimental_features: bool = Field(False, description="Enable experimental features")