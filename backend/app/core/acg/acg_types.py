"""
ACG Types - Data models and type definitions for Astrocartography

Defines all data structures for ACG calculations, requests, and responses,
following the metadata schema from ACG_FEATURE_MASTER_CONTEXT.md.

All models use snake_case for JSON keys and include comprehensive validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Literal
from pydantic import BaseModel, Field, ConfigDict
from pydantic import model_validator
from enum import Enum


class ACGBodyType(str, Enum):
    """Types of celestial bodies supported in ACG calculations."""
    PLANET = "planet"
    ASTEROID = "asteroid" 
    LOT = "lot"
    NODE = "node"
    FIXED_STAR = "fixed_star"
    POINT = "point"
    DWARF = "dwarf"


class ACGLineType(str, Enum):
    """Types of ACG lines that can be calculated."""
    MC = "MC"
    IC = "IC"
    AC = "AC"
    DC = "DC"
    MC_ASPECT = "MC_ASPECT"
    AC_ASPECT = "AC_ASPECT"
    PARAN = "PARAN"


class ACGAspectType(str, Enum):
    """Aspect types for ACG lines."""
    CONJUNCTION = "conjunction"
    SEXTILE = "sextile"
    SQUARE = "square"
    TRINE = "trine"
    OPPOSITION = "opposition"
    QUINCUNX = "quincunx"


@dataclass(frozen=True)
class ACGCoordinates:
    """Celestial body coordinates for ACG calculations."""
    ra: float = field(metadata={"description": "Right ascension in degrees"})
    dec: float = field(metadata={"description": "Declination in degrees"})
    lambda_: float = field(metadata={"description": "Ecliptic longitude in degrees"})
    beta: float = field(metadata={"description": "Ecliptic latitude in degrees"})
    distance: Optional[float] = field(default=None, metadata={"description": "Distance from Earth in AU"})
    speed: Optional[float] = field(default=None, metadata={"description": "Longitude speed in degrees/day"})


@dataclass(frozen=True) 
class ACGLineInfo:
    """Line-specific information for ACG features."""
    angle: Union[float, str] = field(metadata={"description": "Angle type (MC, AC, etc.) or degree value"})
    line_type: str = field(metadata={"description": "Line type (MC, IC, AC, DC, etc.)"})
    method: str = field(metadata={"description": "Calculation method and settings"})
    aspect: Optional[str] = field(default=None, metadata={"description": "Aspect name if applicable"})
    segment_id: Optional[str] = field(default=None, metadata={"description": "Segment identifier for multi-part lines"})
    orb: Optional[float] = field(default=None, metadata={"description": "Orb tolerance in degrees"})


@dataclass(frozen=True)
class ACGNatalInfo:
    """Natal chart information attached to ACG features."""
    dignity: Optional[str] = field(default=None, metadata={"description": "Essential dignity"})
    house: Optional[Union[str, int]] = field(default=None, metadata={"description": "House position"})
    retrograde: Optional[bool] = field(default=None, metadata={"description": "Retrograde status"})
    sign: Optional[str] = field(default=None, metadata={"description": "Zodiac sign"})
    element: Optional[str] = field(default=None, metadata={"description": "Element (Fire, Earth, Air, Water)"})
    modality: Optional[str] = field(default=None, metadata={"description": "Modality (Cardinal, Fixed, Mutable)"})
    aspects: Optional[List[Dict[str, Any]]] = field(default=None, metadata={"description": "Aspect relationships"})


@dataclass
class ACGMetadata:
    """Complete metadata for ACG features following the master context schema."""
    id: str = field(metadata={"description": "Body identifier (e.g., 'Sun', 'Venus', 'Regulus')"})
    type: str = field(metadata={"description": "Feature type (body, line, paran, etc.)"})
    kind: ACGBodyType = field(metadata={"description": "Body kind (planet, asteroid, lot, etc.)"})
    epoch: str = field(metadata={"description": "ISO UTC timestamp"})
    jd: float = field(metadata={"description": "Julian Day"})
    gmst: float = field(metadata={"description": "Greenwich Mean Sidereal Time in degrees"})
    obliquity: float = field(metadata={"description": "True obliquity in degrees"})
    coords: ACGCoordinates = field(metadata={"description": "Celestial coordinates"})
    line: ACGLineInfo = field(metadata={"description": "Line-specific information"})
    calculation_time_ms: float = field(metadata={"description": "Calculation time in milliseconds"})
    number: Optional[int] = field(default=None, metadata={"description": "Swiss Ephemeris or internal index"})
    natal: Optional[ACGNatalInfo] = field(default=None, metadata={"description": "Natal chart context"})
    flags: Optional[int] = field(default=None, metadata={"description": "Swiss Ephemeris calculation flags"})
    se_version: Optional[str] = field(default=None, metadata={"description": "Swiss Ephemeris version"})
    source: str = field(default="Meridian-ACG", metadata={"description": "Calculation source"})
    color: Optional[str] = field(default=None, metadata={"description": "Display color for frontend"})
    style: Optional[str] = field(default=None, metadata={"description": "Display style for frontend"})
    z_index: Optional[int] = field(default=None, metadata={"description": "Z-index for layering"})
    hit_radius: Optional[float] = field(default=None, metadata={"description": "Hit test radius in degrees"})
    custom: Optional[Dict[str, Any]] = field(default=None, metadata={"description": "Custom metadata fields"})


class ACGBody(BaseModel):
    """ACG celestial body definition matching API contract."""
    
    model_config = ConfigDict(extra="forbid")
    
    id: str = Field(..., description="Body identifier (e.g., 'Sun', 'Venus', 'Regulus')")
    type: ACGBodyType = Field(..., description="Body type")
    number: Optional[int] = Field(None, description="Swiss Ephemeris index if applicable")


class ACGOptions(BaseModel):
    """ACG calculation options matching API contract."""
    
    model_config = ConfigDict(extra="forbid")
    
    line_types: Optional[List[ACGLineType]] = Field(
        None, 
        description="Line types to calculate (defaults to all)"
    )
    aspects: Optional[List[ACGAspectType]] = Field(
        None,
        description="Aspects to AC/MC lines (defaults to major aspects)"
    )
    include_parans: bool = Field(True, description="Include paran calculations")
    include_fixed_stars: bool = Field(False, description="Include fixed stars")
    orb_deg: float = Field(1.0, ge=0.0, le=5.0, description="Orb tolerance in degrees")
    flags: Optional[int] = Field(None, description="Swiss Ephemeris calculation flags")


class ACGNatalData(BaseModel):
    """Natal chart data for ACG context matching API contract."""
    
    model_config = ConfigDict(extra="forbid")
    
    birthplace_lat: Optional[float] = Field(
        None,
        description="Birth latitude (-90 to 90)"
    )
    birthplace_lon: Optional[float] = Field(
        None,
        description="Birth longitude (-180 to 180)"
    )
    birthplace_alt_m: Optional[float] = Field(
        None,
        description="Birth altitude in meters"
    )
    houses_system: Optional[str] = Field(
        "placidus",
        description="House system code"
    )


class ACGRequest(BaseModel):
    """ACG calculation request matching API contract."""
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "epoch": "2000-01-01T12:00:00Z",
                "jd": 2451545.0,
                "bodies": [
                    {"id": "Sun", "type": "planet"},
                    {"id": "Moon", "type": "planet"},
                    {"id": "Venus", "type": "planet"}
                ],
                "options": {
                    "line_types": ["MC", "IC", "AC", "DC"],
                    "aspects": ["square", "trine"],
                    "include_parans": True
                },
                "natal": {
                    "birthplace_lat": 40.7128,
                    "birthplace_lon": -74.0060
                }
            }
        }
    )
    
    epoch: str = Field(..., description="ISO 8601 UTC timestamp")
    jd: Optional[float] = Field(None, description="Optional Julian Day override")
    bodies: Optional[List[ACGBody]] = Field(None, description="Bodies to calculate (defaults to standard set)")
    options: Optional[ACGOptions] = Field(None, description="Calculation options")
    natal: Optional[ACGNatalData] = Field(None, description="Natal chart context")
    correlation_id: Optional[str] = Field(None, description="Optional correlation ID for batch operations")

    # Conditional epoch validation: enforce ISO 8601 when request has actionable fields
    @model_validator(mode="after")
    def _validate_epoch_format(self):
        # Only enforce strict epoch validation when bodies/options/natal are provided.
        # This keeps simple constructions (epoch only) available for downstream validators.
        needs_strict = any([
            self.bodies is not None,
            self.options is not None,
            self.natal is not None,
        ])
        if self.epoch and needs_strict:
            try:
                # Accept 'Z' or explicit offset
                _ = datetime.fromisoformat(self.epoch.replace('Z', '+00:00'))
            except Exception:
                raise ValueError("epoch must be a valid ISO 8601 timestamp")
        return self


class ACGBatchRequest(BaseModel):
    """Batch ACG calculation request matching API contract."""
    
    model_config = ConfigDict(extra="forbid")
    
    requests: List[ACGRequest] = Field(
        ...,
        description="Individual ACG requests",
        min_length=1  # Ensure at least one request is provided
    )
    
    # Add correlation_id to each request for tracking
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure each request has a correlation_id
        for i, req in enumerate(self.requests):
            if getattr(req, 'correlation_id', None) is None:
                # Safe to set since field exists on model
                req.correlation_id = f"req_{i}"


class ACGAnimateRequest(BaseModel):
    """ACG animation request matching API contract."""
    
    model_config = ConfigDict(extra="forbid")
    
    epoch_start: str = Field(..., description="Animation start time (ISO 8601 UTC)")
    epoch_end: str = Field(..., description="Animation end time (ISO 8601 UTC)")
    step_minutes: int = Field(..., ge=1, le=43200, description="Time step in minutes")
    bodies: Optional[List[ACGBody]] = Field(None, description="Bodies to animate")
    options: Optional[ACGOptions] = Field(None, description="Calculation options")
    natal: Optional[ACGNatalData] = Field(None, description="Natal chart context")


@dataclass
class ACGBodyData:
    """Runtime body data with calculated positions."""
    body: ACGBody
    coordinates: ACGCoordinates
    natal_info: Optional[ACGNatalInfo] = None
    calculation_time_ms: float = 0.0


@dataclass
class ACGLineData:
    """Runtime line data with geometry."""
    line_type: ACGLineType
    geometry: Dict[str, Any]  # GeoJSON geometry
    body_data: ACGBodyData
    metadata: ACGMetadata
    

class ACGResult(BaseModel):
    """ACG calculation result as GeoJSON FeatureCollection."""
    
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[-180.0, -89.9], [180.0, 89.9]]
                        },
                        "properties": {
                            "id": "Sun",
                            "type": "body",
                            "kind": "planet",
                            "line": {
                                "angle": "MC",
                                "line_type": "MC"
                            },
                            "source": "Meridian-ACG"
                        }
                    }
                ]
            }
        }
    )
    
    type: Literal["FeatureCollection"] = Field("FeatureCollection", description="GeoJSON type")
    features: List[Dict[str, Any]] = Field(..., description="GeoJSON features with ACG metadata")


class ACGBatchResponse(BaseModel):
    """Batch ACG calculation response."""
    
    model_config = ConfigDict(extra="forbid")
    
    results: List[Dict[str, Any]] = Field(
        ..., 
        description="Array of results with correlation IDs"
    )


class ACGAnimateResponse(BaseModel):
    """ACG animation response."""
    
    model_config = ConfigDict(extra="forbid")
    
    frames: List[Dict[str, Any]] = Field(
        ...,
        description="Array of animation frames with timestamp and data"
    )


class ACGFeaturesResponse(BaseModel):
    """ACG features and capabilities response."""
    
    model_config = ConfigDict(extra="forbid")
    
    bodies: List[ACGBody] = Field(..., description="Supported celestial bodies")
    line_types: List[str] = Field(..., description="Supported line types")
    aspects: List[str] = Field(..., description="Supported aspects")
    defaults: ACGOptions = Field(..., description="Default calculation options")
    metadata_keys: List[str] = Field(..., description="Available metadata property keys")


class ACGErrorResponse(BaseModel):
    """ACG-specific error response."""
    
    model_config = ConfigDict(extra="forbid")
    
    timestamp: str = Field(..., description="Error timestamp")
    status: int = Field(..., description="HTTP status code")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    path: str = Field(..., description="Request path")
    errors: Optional[List[Dict[str, str]]] = Field(None, description="Detailed validation errors")