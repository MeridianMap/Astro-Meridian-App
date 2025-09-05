"""
Arabic Parts Data Models - Professional Astrological Data Structures

Comprehensive data models for Arabic parts calculations including:
- Individual Arabic part results with metadata
- Batch calculation requests and responses
- Sect determination and formula tracking
- Integration with ephemeris calculation pipeline

Follows established patterns from serialize.py and aspects.py
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json

from .arabic_parts_formulas import LotFormula


class ChartSect(Enum):
    """Chart sect determination (day or night)."""
    DAY = "day"
    NIGHT = "night"
    UNKNOWN = "unknown"


class CalculationMethod(Enum):
    """Method used for lot calculation."""
    TRADITIONAL = "traditional"
    MODERN = "modern"
    CUSTOM = "custom"


@dataclass(frozen=True)
class ArabicPart:
    """
    Represents a calculated Arabic part with complete metadata.
    
    Immutable data structure for thread safety and caching.
    """
    name: str  # Internal name (e.g., "fortune", "spirit")
    display_name: str  # Human-readable name (e.g., "Lot of Fortune")
    longitude: float  # Ecliptic longitude in degrees (0-360)
    latitude: float = 0.0  # Ecliptic latitude (usually 0 for lots)
    
    # Zodiacal position information
    sign_name: Optional[str] = None  # "Aries", "Taurus", etc.
    sign_degree: Optional[float] = None  # Degree within sign (0-30)
    sign_minute: Optional[float] = None  # Minute within degree
    
    # House position information
    house_number: Optional[int] = None  # House position (1-12)
    house_degree: Optional[float] = None  # Degrees from house cusp
    
    # Calculation metadata
    formula_used: str = ""  # Actual formula applied
    is_day_chart: Optional[bool] = None  # Sect determination
    sect_method: str = "house_position"  # Method used for sect determination
    
    # Quality and reliability indicators
    calculation_method: CalculationMethod = CalculationMethod.TRADITIONAL
    confidence_score: float = 1.0  # 0.0-1.0 calculation reliability
    
    # Additional metadata
    traditional_source: Optional[str] = None  # Historical source reference
    description: Optional[str] = None  # Astrological meaning
    keywords: List[str] = field(default_factory=list)  # Associated keywords
    
    # Calculation context
    calculation_time: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    dependencies: List[str] = field(default_factory=list)  # Other lots this depends on
    
    @property
    def sign_position_string(self) -> str:
        """Get formatted sign position (e.g., "15°Aries32")."""
        if self.sign_name and self.sign_degree is not None:
            degrees = int(self.sign_degree)
            minutes = int((self.sign_degree - degrees) * 60) if self.sign_minute is None else int(self.sign_minute)
            return f"{degrees:02d}°{self.sign_name}{minutes:02d}'"
        return f"{self.longitude:.2f}°"
    
    @property
    def house_position_string(self) -> str:
        """Get formatted house position (e.g., "House 5, +12.3°")."""
        if self.house_number and self.house_degree is not None:
            return f"House {self.house_number}, {self.house_degree:+.1f}°"
        return f"House {self.house_number}" if self.house_number else "Unknown house"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation for JSON serialization."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "sign_name": self.sign_name,
            "sign_degree": self.sign_degree,
            "sign_minute": self.sign_minute,
            "sign_position": self.sign_position_string,
            "house_number": self.house_number,
            "house_degree": self.house_degree,
            "house_position": self.house_position_string,
            "formula_used": self.formula_used,
            "is_day_chart": self.is_day_chart,
            "sect_method": self.sect_method,
            "calculation_method": self.calculation_method.value,
            "confidence_score": self.confidence_score,
            "traditional_source": self.traditional_source,
            "description": self.description,
            "keywords": self.keywords,
            "calculation_time": self.calculation_time.isoformat() if self.calculation_time else None,
            "dependencies": self.dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArabicPart':
        """Create instance from dictionary representation."""
        # Handle enum conversion
        calc_method = CalculationMethod(data.get("calculation_method", "traditional"))
        
        # Handle datetime conversion
        calc_time = None
        if data.get("calculation_time"):
            calc_time = datetime.fromisoformat(data["calculation_time"].replace('Z', '+00:00'))
        
        return cls(
            name=data["name"],
            display_name=data["display_name"],
            longitude=data["longitude"],
            latitude=data.get("latitude", 0.0),
            sign_name=data.get("sign_name"),
            sign_degree=data.get("sign_degree"),
            sign_minute=data.get("sign_minute"),
            house_number=data.get("house_number"),
            house_degree=data.get("house_degree"),
            formula_used=data.get("formula_used", ""),
            is_day_chart=data.get("is_day_chart"),
            sect_method=data.get("sect_method", "house_position"),
            calculation_method=calc_method,
            confidence_score=data.get("confidence_score", 1.0),
            traditional_source=data.get("traditional_source"),
            description=data.get("description"),
            keywords=data.get("keywords", []),
            calculation_time=calc_time,
            dependencies=data.get("dependencies", [])
        )


@dataclass
class SectDetermination:
    """
    Represents chart sect analysis with multiple validation methods.
    """
    is_day_chart: bool
    primary_method: str  # "house_position", "horizon_calculation", "ascendant_degrees"
    confidence: float  # 0.0-1.0 confidence in determination
    
    # Supporting data for validation
    sun_house: Optional[int] = None
    sun_above_horizon: Optional[bool] = None
    ascendant_degrees: Optional[float] = None
    
    # Alternative method results for cross-validation
    alternative_methods: Dict[str, bool] = field(default_factory=dict)
    
    # Special cases
    is_polar_birth: bool = False  # Birth in polar regions
    is_twilight_birth: bool = False  # Sun very close to horizon
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "is_day_chart": self.is_day_chart,
            "primary_method": self.primary_method,
            "confidence": self.confidence,
            "sun_house": self.sun_house,
            "sun_above_horizon": self.sun_above_horizon,
            "ascendant_degrees": self.ascendant_degrees,
            "alternative_methods": self.alternative_methods,
            "is_polar_birth": self.is_polar_birth,
            "is_twilight_birth": self.is_twilight_birth
        }


@dataclass
class ArabicPartsRequest:
    """
    Request configuration for Arabic parts calculation.
    """
    # Lot selection
    requested_parts: List[str] = field(default_factory=lambda: ["fortune", "spirit"])
    include_all_traditional: bool = False  # Calculate all 16 core lots
    include_optional_lots: bool = False  # Include optional lots
    
    # Custom formulas
    custom_formulas: Optional[Dict[str, Dict[str, str]]] = None  # name -> {day_formula, night_formula}
    
    # Calculation options
    house_system: str = "P"  # For house positions
    calculation_method: CalculationMethod = CalculationMethod.TRADITIONAL
    sect_determination_method: str = "house_position"  # or "horizon_calculation"
    
    # Output options
    include_metadata: bool = True
    include_dependencies: bool = True
    metadata_level: str = "standard"  # "minimal", "standard", "comprehensive"
    
    def get_all_requested_lots(self) -> List[str]:
        """Get complete list of lots to calculate based on request parameters."""
        from .arabic_parts_formulas import formula_registry
        
        lots = set(self.requested_parts)
        
        if self.include_all_traditional:
            lots.update(formula_registry.get_core_lots())
        
        if self.include_optional_lots:
            lots.update(formula_registry.get_optional_lots())
        
        if self.custom_formulas:
            lots.update(self.custom_formulas.keys())
        
        return sorted(list(lots))
    
    def validate(self) -> List[str]:
        """
        Validate request parameters.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        from .arabic_parts_formulas import formula_registry
        
        # Validate requested lots
        available_lots = formula_registry.list_available_lots()
        for lot_name in self.requested_parts:
            if lot_name not in available_lots and (not self.custom_formulas or lot_name not in self.custom_formulas):
                errors.append(f"Unknown Arabic part: {lot_name}")
        
        # Validate custom formulas if provided
        if self.custom_formulas:
            for lot_name, formulas in self.custom_formulas.items():
                if "day_formula" not in formulas:
                    errors.append(f"Missing day_formula for custom lot: {lot_name}")
                if "night_formula" not in formulas:
                    errors.append(f"Missing night_formula for custom lot: {lot_name}")
                
                # Parse formulas to check validity
                if "day_formula" in formulas:
                    parsed = formula_registry.parse_formula(formulas["day_formula"])
                    if not parsed.is_valid:
                        errors.append(f"Invalid day formula for {lot_name}: {parsed.error_message}")
                
                if "night_formula" in formulas:
                    parsed = formula_registry.parse_formula(formulas["night_formula"])
                    if not parsed.is_valid:
                        errors.append(f"Invalid night formula for {lot_name}: {parsed.error_message}")
        
        # Validate metadata level
        valid_levels = ["minimal", "standard", "comprehensive"]
        if self.metadata_level not in valid_levels:
            errors.append(f"Invalid metadata_level. Must be one of: {valid_levels}")
        
        return errors


@dataclass
class ArabicPartsResult:
    """
    Complete result of Arabic parts calculation with metadata.
    """
    # Core results (required fields first)
    calculated_parts: List[ArabicPart]
    sect_determination: SectDetermination
    
    # Summary statistics
    total_parts_calculated: int
    successful_calculations: int
    failed_calculations: int
    
    # Performance metrics
    calculation_time_ms: float
    
    # Calculation context
    formulas_used: Dict[str, str]  # lot_name -> formula_string
    calculation_method: CalculationMethod
    house_system_used: str
    
    # Optional fields with defaults
    cache_hit_rate: Optional[float] = None
    calculation_errors: List[Dict[str, str]] = field(default_factory=list)  # lot_name -> error_message
    warnings: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of lot calculations."""
        if self.total_parts_calculated == 0:
            return 0.0
        return self.successful_calculations / self.total_parts_calculated
    
    def get_part_by_name(self, name: str) -> Optional[ArabicPart]:
        """Get specific Arabic part by name."""
        for part in self.calculated_parts:
            if part.name == name:
                return part
        return None
    
    def get_parts_by_category(self, category: str) -> List[ArabicPart]:
        """Get all parts of a specific category (core/optional).""" 
        from .arabic_parts_formulas import formula_registry
        
        category_lots = formula_registry.list_available_lots(category)
        return [part for part in self.calculated_parts if part.name in category_lots]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation for API responses."""
        return {
            "calculated_parts": [part.to_dict() for part in self.calculated_parts],
            "sect_determination": self.sect_determination.to_dict(),
            "total_parts_calculated": self.total_parts_calculated,
            "successful_calculations": self.successful_calculations,
            "failed_calculations": self.failed_calculations,
            "success_rate": self.success_rate,
            "calculation_time_ms": self.calculation_time_ms,
            "cache_hit_rate": self.cache_hit_rate,
            "formulas_used": self.formulas_used,
            "calculation_method": self.calculation_method.value,
            "house_system_used": self.house_system_used,
            "calculation_errors": self.calculation_errors,
            "warnings": self.warnings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArabicPartsResult':
        """Create instance from dictionary representation."""
        parts = [ArabicPart.from_dict(part_data) for part_data in data["calculated_parts"]]
        sect = SectDetermination(**data["sect_determination"])
        calc_method = CalculationMethod(data.get("calculation_method", "traditional"))
        
        return cls(
            calculated_parts=parts,
            sect_determination=sect,
            total_parts_calculated=data["total_parts_calculated"],
            successful_calculations=data["successful_calculations"],
            failed_calculations=data["failed_calculations"],
            calculation_time_ms=data["calculation_time_ms"],
            cache_hit_rate=data.get("cache_hit_rate"),
            formulas_used=data["formulas_used"],
            calculation_method=calc_method,
            house_system_used=data["house_system_used"],
            calculation_errors=data.get("calculation_errors", []),
            warnings=data.get("warnings", [])
        )


@dataclass
class BatchArabicPartsRequest:
    """
    Request for calculating Arabic parts across multiple charts.
    """
    charts: List[Dict[str, Any]]  # Chart data for each calculation
    common_request: ArabicPartsRequest  # Common settings for all charts
    
    # Batch-specific options
    parallel_processing: bool = True
    max_workers: Optional[int] = None
    fail_fast: bool = False  # Stop on first error vs continue with others
    
    def validate(self) -> List[str]:
        """Validate batch request."""
        errors = []
        
        if not self.charts:
            errors.append("No charts provided for batch calculation")
        
        if len(self.charts) > 100:  # Reasonable limit
            errors.append("Batch size too large (max 100 charts)")
        
        # Validate common request
        errors.extend(self.common_request.validate())
        
        return errors


@dataclass
class BatchArabicPartsResult:
    """
    Result of batch Arabic parts calculation.
    """
    results: List[Union[ArabicPartsResult, Dict[str, str]]]  # Results or error info
    total_charts: int
    successful_charts: int
    failed_charts: int
    
    # Batch performance metrics
    total_processing_time_ms: float
    average_chart_time_ms: float
    parallel_efficiency: Optional[float] = None  # Actual vs theoretical speedup
    
    # Aggregate statistics
    total_parts_calculated: int = 0
    most_common_errors: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def batch_success_rate(self) -> float:
        """Calculate success rate for the entire batch."""
        if self.total_charts == 0:
            return 0.0
        return self.successful_charts / self.total_charts
    
    def get_aggregate_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics across all successful calculations."""
        successful_results = [r for r in self.results if isinstance(r, ArabicPartsResult)]
        
        if not successful_results:
            return {}
        
        total_parts = sum(r.total_parts_calculated for r in successful_results)
        total_successful = sum(r.successful_calculations for r in successful_results)
        avg_calc_time = sum(r.calculation_time_ms for r in successful_results) / len(successful_results)
        
        # Collect all calculated lot names
        all_lots = set()
        for result in successful_results:
            all_lots.update(part.name for part in result.calculated_parts)
        
        return {
            "total_parts_across_all_charts": total_parts,
            "total_successful_parts": total_successful,
            "average_calculation_time_ms": avg_calc_time,
            "unique_lots_calculated": sorted(list(all_lots)),
            "average_success_rate": total_successful / total_parts if total_parts > 0 else 0.0
        }


# Utility functions for common operations
def create_standard_request() -> ArabicPartsRequest:
    """Create a standard Arabic parts request with core lots."""
    return ArabicPartsRequest(
        requested_parts=["fortune", "spirit", "basis"],
        include_metadata=True,
        metadata_level="standard"
    )


def create_comprehensive_request() -> ArabicPartsRequest:
    """Create comprehensive request with all traditional lots."""
    return ArabicPartsRequest(
        include_all_traditional=True,
        include_optional_lots=True,
        include_metadata=True,
        metadata_level="comprehensive"
    )


def validate_custom_lot_definition(name: str, day_formula: str, night_formula: str) -> List[str]:
    """
    Validate a custom lot definition.
    
    Returns:
        List of validation errors (empty if valid)
    """
    from .arabic_parts_formulas import formula_registry
    
    errors = []
    
    # Validate name
    if not name or not name.isidentifier():
        errors.append("Lot name must be a valid identifier")
    
    # Validate formulas
    day_parsed = formula_registry.parse_formula(day_formula)
    if not day_parsed.is_valid:
        errors.append(f"Invalid day formula: {day_parsed.error_message}")
    
    night_parsed = formula_registry.parse_formula(night_formula)
    if not night_parsed.is_valid:
        errors.append(f"Invalid night formula: {night_parsed.error_message}")
    
    return errors