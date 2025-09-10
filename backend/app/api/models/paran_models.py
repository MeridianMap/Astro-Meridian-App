"""
Pydantic models for ACG Paran API endpoints.

Provides comprehensive request/response models for Jim Lewis ACG paran
calculations with professional validation and documentation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator

from extracted.api.models.schemas import DateTimeInput, CoordinateInput
from extracted.systems.acg_engine.paran_models import (
    ACGEventType,
    ACGVisibilityMode,
    HorizonConvention,
    ParanCalculationMethod,
    ParanPrecisionLevel
)


class ParanVisibilityFilter(str, Enum):
    """Visibility filtering options for paran calculations."""
    ALL = "all"
    BOTH_VISIBLE = "both_visible"
    MERIDIAN_VISIBLE_ONLY = "meridian_visible_only"


class ParanPrecisionMode(str, Enum):
    """Precision modes for paran calculations."""
    FAST = "fast"
    STANDARD = "standard"
    HIGH = "high"
    ULTRA_HIGH = "ultra_high"


class PlanetPairRequest(BaseModel):
    """Request model for a single planet pair paran calculation."""
    
    planet_a: str = Field(
        ...,
        description="First planet name",
        example="Mars"
    )
    
    planet_b: str = Field(
        ...,
        description="Second planet name", 
        example="Jupiter"
    )
    
    @validator('planet_a', 'planet_b')
    def validate_planet_names(cls, v):
        valid_planets = {
            "Sun", "Moon", "Mercury", "Venus", "Mars",
            "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
        }
        if v not in valid_planets:
            raise ValueError(f"Invalid planet name: {v}")
        return v


class ACGEventCombination(BaseModel):
    """ACG event combination for paran calculations."""
    
    event_a: ACGEventType = Field(
        ...,
        description="ACG event for first planet (MC, IC, R, S)"
    )
    
    event_b: ACGEventType = Field(
        ...,
        description="ACG event for second planet (MC, IC, R, S)"
    )


class ParanCalculationRequest(BaseModel):
    """
    Request for ACG paran calculations.
    
    Example:
        {
            "datetime": {"iso_string": "2000-01-01T12:00:00Z"},
            "planet_pairs": [
                {"planet_a": "Mars", "planet_b": "Jupiter"}
            ],
            "event_combinations": [
                {"event_a": "MC", "event_b": "R"}
            ],
            "latitude_range": [-90, 90],
            "visibility_filter": "both_visible",
            "precision_mode": "high"
        }
    """
    
    datetime: DateTimeInput = Field(
        ...,
        description="Calculation date and time",
        example={"iso_string": "2000-01-01T12:00:00Z"}
    )
    
    planet_pairs: List[PlanetPairRequest] = Field(
        ...,
        description="List of planet pairs to calculate parans for",
        min_items=1,
        max_items=50
    )
    
    event_combinations: Optional[List[ACGEventCombination]] = Field(
        None,
        description="Specific event combinations (default: all combinations)",
        max_items=16
    )
    
    latitude_range: List[float] = Field(
        [-90, 90],
        description="Latitude search range in degrees",
        min_items=2,
        max_items=2
    )
    
    longitude_constraints: Optional[List[float]] = Field(
        None,
        description="Optional longitude constraints in degrees",
        max_items=10
    )
    
    visibility_filter: ParanVisibilityFilter = Field(
        ParanVisibilityFilter.ALL,
        description="Visibility filtering mode"
    )
    
    horizon_convention: HorizonConvention = Field(
        HorizonConvention.GEOMETRIC,
        description="Horizon convention for visibility calculations"
    )
    
    precision_mode: ParanPrecisionMode = Field(
        ParanPrecisionMode.HIGH,
        description="Calculation precision level"
    )
    
    exclude_degenerate: bool = Field(
        True,
        description="Exclude degenerate cases (both planets on meridian)"
    )
    
    include_metadata: bool = Field(
        True,
        description="Include calculation metadata in response"
    )
    
    @validator('latitude_range')
    def validate_latitude_range(cls, v):
        if len(v) != 2:
            raise ValueError("Latitude range must have exactly 2 values")
        if not (-90 <= v[0] <= v[1] <= 90):
            raise ValueError("Invalid latitude range")
        return v
    
    @validator('longitude_constraints')
    def validate_longitude_constraints(cls, v):
        if v is not None:
            for lon in v:
                if not (-180 <= lon <= 180):
                    raise ValueError(f"Invalid longitude: {lon}")
        return v


class ParanLineResponse(BaseModel):
    """Response model for a single paran line."""
    
    planet_a: str = Field(..., description="First planet name")
    planet_b: str = Field(..., description="Second planet name")
    event_a: ACGEventType = Field(..., description="First planet's ACG event")
    event_b: ACGEventType = Field(..., description="Second planet's ACG event")
    
    latitude_deg: float = Field(
        ...,
        description="Paran latitude in degrees",
        ge=-90,
        le=90
    )
    
    longitude_deg: Optional[float] = Field(
        None,
        description="Representative longitude in degrees",
        ge=-180,
        le=180
    )
    
    is_valid: bool = Field(..., description="Whether paran calculation succeeded")
    
    calculation_method: ParanCalculationMethod = Field(
        ...,
        description="Method used for calculation"
    )
    
    precision_achieved: float = Field(
        ...,
        description="Achieved precision in degrees",
        ge=0
    )
    
    visibility_status: ACGVisibilityMode = Field(
        ...,
        description="Visibility status of the paran"
    )
    
    failure_reason: Optional[str] = Field(
        None,
        description="Reason for calculation failure (if any)"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional calculation metadata"
    )


class ParanCalculationResponse(BaseModel):
    """
    Response for ACG paran calculations.
    
    Example:
        {
            "success": true,
            "total_parans_calculated": 16,
            "valid_parans_found": 12,
            "calculation_date": "2000-01-01T12:00:00Z",
            "paran_lines": [...],
            "performance_metrics": {
                "total_time_ms": 245.6,
                "average_precision": 0.012,
                "meets_jim_lewis_standard": true
            }
        }
    """
    
    success: bool = Field(..., description="Whether calculation succeeded")
    
    total_parans_calculated: int = Field(
        ...,
        description="Total number of paran calculations attempted",
        ge=0
    )
    
    valid_parans_found: int = Field(
        ...,
        description="Number of valid paran lines found",
        ge=0
    )
    
    calculation_date: datetime = Field(
        ...,
        description="Date used for calculations"
    )
    
    paran_lines: List[ParanLineResponse] = Field(
        ...,
        description="List of calculated paran lines"
    )
    
    performance_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Calculation performance statistics"
    )
    
    configuration_used: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration parameters used"
    )
    
    errors: Optional[List[str]] = Field(
        None,
        description="Any errors encountered during calculation"
    )


class GlobalParanSearchRequest(BaseModel):
    """
    Request for global paran line search across multiple locations.
    
    For generating complete paran line maps for astrocartography visualization.
    """
    
    datetime: DateTimeInput = Field(
        ...,
        description="Calculation date and time"
    )
    
    planet_pairs: List[PlanetPairRequest] = Field(
        ...,
        description="Planet pairs for global search",
        min_items=1,
        max_items=20
    )
    
    event_combinations: Optional[List[ACGEventCombination]] = Field(
        None,
        description="Specific event combinations to search"
    )
    
    geographic_bounds: Optional[Dict[str, float]] = Field(
        None,
        description="Geographic search bounds (min_lat, max_lat, min_lon, max_lon)"
    )
    
    resolution_deg: float = Field(
        1.0,
        description="Search resolution in degrees",
        gt=0,
        le=10
    )
    
    visibility_filter: ParanVisibilityFilter = Field(
        ParanVisibilityFilter.BOTH_VISIBLE,
        description="Visibility filtering for global search"
    )
    
    precision_mode: ParanPrecisionMode = Field(
        ParanPrecisionMode.STANDARD,
        description="Precision vs speed tradeoff for global search"
    )
    
    max_results_per_pair: int = Field(
        100,
        description="Maximum results per planet pair",
        gt=0,
        le=1000
    )
    
    include_geojson: bool = Field(
        False,
        description="Include GeoJSON format for mapping"
    )
    
    @validator('geographic_bounds')
    def validate_geographic_bounds(cls, v):
        if v is not None:
            required_keys = {'min_lat', 'max_lat', 'min_lon', 'max_lon'}
            if not all(key in v for key in required_keys):
                raise ValueError("Geographic bounds must include min_lat, max_lat, min_lon, max_lon")
            
            if not (-90 <= v['min_lat'] <= v['max_lat'] <= 90):
                raise ValueError("Invalid latitude bounds")
            
            if not (-180 <= v['min_lon'] <= v['max_lon'] <= 180):
                raise ValueError("Invalid longitude bounds")
        return v


class GlobalParanPoint(BaseModel):
    """Geographic point for global paran search results."""
    
    latitude_deg: float = Field(..., description="Latitude in degrees")
    longitude_deg: float = Field(..., description="Longitude in degrees")
    precision_deg: float = Field(..., description="Calculation precision")
    calculation_method: ParanCalculationMethod = Field(..., description="Method used")


class GlobalParanLine(BaseModel):
    """Global paran line result."""
    
    planet_a: str = Field(..., description="First planet")
    planet_b: str = Field(..., description="Second planet")
    event_a: ACGEventType = Field(..., description="First planet event")
    event_b: ACGEventType = Field(..., description="Second planet event")
    
    points: List[GlobalParanPoint] = Field(
        ...,
        description="Geographic points where paran occurs"
    )
    
    line_type: str = Field(
        ...,
        description="Type of paran line (meridian-horizon, horizon-horizon, etc.)"
    )
    
    quality_score: float = Field(
        ...,
        description="Solution quality score (0-1)",
        ge=0,
        le=1
    )
    
    geojson: Optional[Dict[str, Any]] = Field(
        None,
        description="GeoJSON representation for mapping"
    )


class GlobalParanSearchResponse(BaseModel):
    """
    Response for global paran search.
    
    Contains comprehensive paran line mapping data for astrocartography.
    """
    
    success: bool = Field(..., description="Search success status")
    
    calculation_date: datetime = Field(
        ...,
        description="Date used for calculations"
    )
    
    total_lines_calculated: int = Field(
        ...,
        description="Total paran lines calculated",
        ge=0
    )
    
    valid_lines_found: int = Field(
        ...,
        description="Number of valid paran lines found",
        ge=0
    )
    
    paran_lines: List[GlobalParanLine] = Field(
        ...,
        description="Global paran line results"
    )
    
    geographic_coverage: Dict[str, float] = Field(
        ...,
        description="Geographic coverage statistics"
    )
    
    performance_metrics: Dict[str, Any] = Field(
        ...,
        description="Global search performance metrics"
    )
    
    search_configuration: Dict[str, Any] = Field(
        ...,
        description="Configuration used for global search"
    )


class ParanValidationRequest(BaseModel):
    """Request for validating paran calculations against reference data."""
    
    datetime: DateTimeInput = Field(
        ...,
        description="Reference calculation date"
    )
    
    reference_parans: List[ParanLineResponse] = Field(
        ...,
        description="Reference paran data for validation",
        min_items=1
    )
    
    tolerance_deg: float = Field(
        0.03,
        description="Validation tolerance in degrees",
        gt=0,
        le=1
    )
    
    precision_mode: ParanPrecisionMode = Field(
        ParanPrecisionMode.ULTRA_HIGH,
        description="Precision mode for validation calculations"
    )


class ParanValidationResponse(BaseModel):
    """Response for paran validation."""
    
    success: bool = Field(..., description="Validation success status")
    
    total_validated: int = Field(
        ...,
        description="Total parans validated",
        ge=0
    )
    
    validation_passed: int = Field(
        ...,
        description="Number of validations that passed",
        ge=0
    )
    
    validation_rate: float = Field(
        ...,
        description="Validation success rate (0-1)",
        ge=0,
        le=1
    )
    
    meets_jim_lewis_standard: bool = Field(
        ...,
        description="Whether results meet Jim Lewis ACG precision standards"
    )
    
    validation_details: List[Dict[str, Any]] = Field(
        ...,
        description="Detailed validation results for each paran"
    )
    
    performance_comparison: Dict[str, Any] = Field(
        ...,
        description="Performance comparison with reference system"
    )


# Error response models
class ParanCalculationError(BaseModel):
    """Error response for paran calculations."""
    
    success: bool = Field(False, description="Always false for error responses")
    
    error_type: str = Field(
        ...,
        description="Type of error encountered"
    )
    
    error_message: str = Field(
        ...,
        description="Detailed error description"
    )
    
    failed_planet_pairs: Optional[List[PlanetPairRequest]] = Field(
        None,
        description="Planet pairs that failed calculation"
    )
    
    partial_results: Optional[List[ParanLineResponse]] = Field(
        None,
        description="Any partial results calculated before failure"
    )
    
    troubleshooting_hints: Optional[List[str]] = Field(
        None,
        description="Suggestions for resolving the error"
    )