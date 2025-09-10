"""
Enhanced ACG API Models - Pydantic models for retrograde-aware ACG endpoints

This module defines request/response models for the enhanced ACG API endpoints
including aspect-to-angle lines and motion-based filtering functionality.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from extracted.systems.models.common import DateTimeInput, CoordinateInput


class AspectLineType(str, Enum):
    """Supported aspect types for aspect-to-angle lines."""
    CONJUNCTION = "conjunction"
    SEXTILE = "sextile" 
    SQUARE = "square"
    TRINE = "trine"
    OPPOSITION = "opposition"
    SEMI_SEXTILE = "semi_sextile"
    QUINCUNX = "quincunx"


class AngleType(str, Enum):
    """Supported angle types for aspect-to-angle lines."""
    MC = "MC"  # Midheaven
    ASC = "ASC"  # Ascendant
    IC = "IC"  # Imum Coeli
    DSC = "DSC"  # Descendant


class MotionStatusFilter(str, Enum):
    """Motion status filters for ACG lines."""
    DIRECT = "direct"
    RETROGRADE = "retrograde" 
    STATIONARY = "stationary"
    ALL = "all"


class AspectLinesConfig(BaseModel):
    """Configuration for aspect-to-angle line calculations."""
    
    aspects: List[AspectLineType] = Field(
        default=[AspectLineType.CONJUNCTION, AspectLineType.OPPOSITION, 
                AspectLineType.TRINE, AspectLineType.SQUARE],
        description="List of aspects to calculate"
    )
    
    angles: List[AngleType] = Field(
        default=[AngleType.MC, AngleType.ASC],
        description="List of angles to calculate aspects to"
    )
    
    orb_preset: str = Field(
        default="traditional",
        description="Orb preset system to use"
    )
    
    custom_orbs: Optional[Dict[str, float]] = Field(
        default=None,
        description="Custom orb values for specific aspects"
    )
    
    include_minor_aspects: bool = Field(
        default=False,
        description="Include minor aspects (semi-sextile, quincunx)"
    )
    
    precision_degrees: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        description="Calculation precision in degrees"
    )


class EnhancedACGLinesRequest(BaseModel):
    """Enhanced request for ACG lines with retrograde and aspect-to-angle features."""
    
    # Standard ACG request fields
    chart_name: str = Field(..., description="Chart identifier")
    datetime: DateTimeInput = Field(..., description="Chart datetime")
    coordinates: CoordinateInput = Field(..., description="Chart coordinates")
    
    # Body selection
    bodies: Optional[List[str]] = Field(
        default=None,
        description="List of bodies to calculate (default: all planets)"
    )
    
    # Enhanced features
    include_retrograde_metadata: bool = Field(
        default=True,
        description="Include retrograde motion metadata"
    )
    
    motion_status_filter: Optional[List[MotionStatusFilter]] = Field(
        default=None,
        description="Filter lines by motion status"
    )
    
    include_aspect_lines: bool = Field(
        default=False,
        description="Include aspect-to-angle lines"
    )
    
    aspect_lines_config: Optional[AspectLinesConfig] = Field(
        default=None,
        description="Configuration for aspect-to-angle lines"
    )
    
    include_station_analysis: bool = Field(
        default=True,
        description="Include station timing analysis"
    )
    
    # Styling and visualization
    color_scheme: str = Field(
        default="default",
        description="Color scheme for motion-based styling"
    )
    
    include_animation_hints: bool = Field(
        default=False,
        description="Include animation metadata for time-based visualization"
    )


class AspectLineRequest(BaseModel):
    """Request for calculating aspect-to-angle lines only."""
    
    chart_name: str = Field(..., description="Chart identifier")
    datetime: DateTimeInput = Field(..., description="Chart datetime")
    
    planet_ids: List[int] = Field(
        ...,
        description="List of Swiss Ephemeris planet IDs"
    )
    
    aspects_config: AspectLinesConfig = Field(
        ...,
        description="Aspect calculation configuration"
    )
    
    latitude_range: Optional[List[float]] = Field(
        default=[-89.0, 89.0],
        description="Latitude range for calculations [min, max]"
    )
    
    point_density: int = Field(
        default=180,
        ge=90,
        le=720,
        description="Number of points per line"
    )


class AspectLineFeatureResponse(BaseModel):
    """Response model for a single aspect-to-angle line feature."""
    
    planet_id: int = Field(..., description="Swiss Ephemeris planet ID")
    planet_name: str = Field(..., description="Planet name")
    angle_name: str = Field(..., description="Angle name (MC, ASC, etc.)")
    aspect_type: str = Field(..., description="Aspect type")
    aspect_angle: float = Field(..., description="Aspect angle in degrees")
    orb_degrees: float = Field(..., description="Orb allowance in degrees")
    
    # GeoJSON geometry
    geojson_feature: Dict[str, Any] = Field(..., description="GeoJSON feature")
    
    # Metadata
    line_strength: float = Field(..., description="Line strength (0-1)")
    visual_priority: int = Field(..., description="Visual priority (1-5)")
    point_count: int = Field(..., description="Number of points in line")
    calculation_accuracy: float = Field(..., description="Calculation accuracy")


class EnhancedACGLinesResponse(BaseModel):
    """Enhanced response for ACG lines with retrograde and aspect features."""
    
    success: bool = Field(..., description="Request success status")
    
    # Standard ACG response data
    chart_info: Dict[str, Any] = Field(..., description="Chart information")
    geojson_features: List[Dict[str, Any]] = Field(..., description="GeoJSON features")
    
    # Enhanced metadata
    retrograde_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Retrograde motion metadata by planet"
    )
    
    aspect_lines: Optional[List[AspectLineFeatureResponse]] = Field(
        default=None,
        description="Aspect-to-angle line features"
    )
    
    # Styling and visualization
    styling_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Styling hints for visualization"
    )
    
    legend_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Legend data for motion-based visualization"
    )
    
    # Performance and metadata
    calculation_time_ms: float = Field(..., description="Total calculation time")
    performance_stats: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Performance statistics"
    )
    
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


class MotionFilterRequest(BaseModel):
    """Request for motion-based filtering of existing ACG data."""
    
    motion_filters: List[MotionStatusFilter] = Field(
        ...,
        description="Motion status filters to apply"
    )
    
    color_scheme: str = Field(
        default="default",
        description="Color scheme for styling"
    )
    
    include_legend: bool = Field(
        default=True,
        description="Include legend data in response"
    )


class MotionFilterResponse(BaseModel):
    """Response for motion-based filtering operations."""
    
    success: bool = Field(..., description="Operation success status")
    
    filtered_features: List[Dict[str, Any]] = Field(
        ...,
        description="Filtered GeoJSON features"
    )
    
    styling_metadata: Dict[str, Any] = Field(
        ...,
        description="Motion-based styling metadata"
    )
    
    legend_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Legend data if requested"
    )
    
    filter_stats: Dict[str, Any] = Field(
        ...,
        description="Statistics about filtering operation"
    )


class ACGPerformanceResponse(BaseModel):
    """Response for ACG performance statistics."""
    
    success: bool = Field(..., description="Request success status")
    
    performance_stats: Dict[str, Any] = Field(
        ...,
        description="Detailed performance statistics"
    )
    
    retrograde_integration_stats: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Retrograde integration performance statistics"
    )
    
    aspect_lines_stats: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Aspect-to-angle lines performance statistics"
    )
    
    recommendations: List[str] = Field(
        default=[],
        description="Performance optimization recommendations"
    )


class ACGCacheRequest(BaseModel):
    """Request for ACG cache operations."""
    
    operation: Literal["clear", "stats", "clear_by_type"] = Field(
        ...,
        description="Cache operation to perform"
    )
    
    cache_type: Optional[str] = Field(
        default=None,
        description="Specific cache type for targeted operations"
    )


class ACGCacheResponse(BaseModel):
    """Response for ACG cache operations."""
    
    success: bool = Field(..., description="Operation success status")
    
    operation: str = Field(..., description="Operation performed")
    
    cache_stats: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Cache statistics"
    )
    
    message: str = Field(..., description="Operation result message")


# Configuration models
class ACGVisualizationConfig(BaseModel):
    """Configuration for ACG visualization enhancements."""
    
    motion_visualization: bool = Field(
        default=True,
        description="Enable motion-based visualization"
    )
    
    color_schemes: Dict[str, Dict[str, str]] = Field(
        default={
            "default": {"direct": "#3366cc", "retrograde": "#cc3333", "stationary": "#ffaa00"},
            "pastel": {"direct": "#6699ff", "retrograde": "#ff6666", "stationary": "#ffcc66"}
        },
        description="Available color schemes"
    )
    
    animation_support: bool = Field(
        default=True,
        description="Enable animation metadata generation"
    )
    
    line_styling: Dict[str, Any] = Field(
        default={
            "default_opacity": 0.8,
            "default_line_width": 2.0,
            "glow_effects": True,
            "animation_hints": True
        },
        description="Line styling configuration"
    )


# Export all models
__all__ = [
    "AspectLineType",
    "AngleType", 
    "MotionStatusFilter",
    "AspectLinesConfig",
    "EnhancedACGLinesRequest",
    "AspectLineRequest",
    "AspectLineFeatureResponse",
    "EnhancedACGLinesResponse",
    "MotionFilterRequest",
    "MotionFilterResponse",
    "ACGPerformanceResponse",
    "ACGCacheRequest",
    "ACGCacheResponse",
    "ACGVisualizationConfig"
]