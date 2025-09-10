"""
Jim Lewis ACG Paran Data Models

Professional data structures for Jim Lewis-style ACG planetary paran calculations.
Implements the complete ACG paran data model with support for both closed-form
meridian-horizon solutions and numerical horizon-horizon solutions.

Based on Jim Lewis ACG specifications with ≤0.03° latitude precision requirements.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class ACGEventType(Enum):
    """ACG angular events for paran calculations."""
    MC = "MC"  # Upper culmination (meridian crossing)
    IC = "IC"  # Lower culmination (anti-meridian crossing)  
    R = "R"    # Rising (eastern horizon crossing)
    S = "S"    # Setting (western horizon crossing)


class ParanCalculationMethod(Enum):
    """Calculation methods for paran solutions."""
    CLOSED_FORM = "closed_form"        # Analytical meridian-horizon solution
    NUMERICAL = "numerical"            # Brent method horizon-horizon solution
    FAILED = "failed"                  # Calculation failed


class ACGVisibilityMode(Enum):
    """ACG standard visibility filter modes."""
    ALL = "all"                        # No visibility filter (geometric only)
    BOTH_VISIBLE = "both_visible"      # Both planets above horizon
    MERIDIAN_VISIBLE_ONLY = "meridian_visible_only"  # Only meridian planet visible


class HorizonConvention(Enum):
    """Horizon conventions for paran calculations."""
    GEOMETRIC = "geometric"            # True geometric horizon (h = 0°)
    APPARENT = "apparent"              # Apparent horizon with refraction (h = -0.5667°)


@dataclass
class ACGParanLine:
    """
    Single ACG planetary paran line.
    
    Represents a constant-latitude line where two planets are simultaneously
    angular according to Jim Lewis ACG paran calculations.
    """
    
    # Planet and event configuration
    planet_a: str                      # First planet name
    event_a: ACGEventType              # First planet's angular event
    planet_b: str                      # Second planet name
    event_b: ACGEventType              # Second planet's angular event
    
    # Calculation results
    latitude_deg: float                # Constant latitude where simultaneity occurs
    calculation_method: ParanCalculationMethod  # Method used for calculation
    precision_achieved: float          # Actual precision achieved (degrees)
    
    # Visibility and status
    visibility_status: ACGVisibilityMode       # Visibility filter applied
    is_valid: bool = True              # Whether calculation succeeded
    failure_reason: Optional[str] = None       # Reason if calculation failed
    
    # Astronomical context
    epoch_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    julian_day: Optional[float] = None
    
    # Identification and metadata
    line_id: str = field(default="")   # Unique identifier
    
    # Mathematical details
    alpha_a_deg: Optional[float] = None        # RA of planet A
    delta_a_deg: Optional[float] = None        # Dec of planet A
    alpha_b_deg: Optional[float] = None        # RA of planet B
    delta_b_deg: Optional[float] = None        # Dec of planet B
    
    # Domain validation
    domain_valid: bool = True          # Whether solution is in valid domain
    convergence_iterations: Optional[int] = None  # Iterations for numerical method
    
    def __post_init__(self):
        """Generate line ID if not provided."""
        if not self.line_id:
            self.line_id = f"paran_{self.planet_a}_{self.event_a.value}_{self.planet_b}_{self.event_b.value}_{self.epoch_utc.strftime('%Y%m%d')}"
    
    def get_paran_description(self) -> str:
        """Get human-readable paran description."""
        return f"{self.planet_a} {self.event_a.value} with {self.planet_b} {self.event_b.value}"
    
    def is_meridian_horizon_paran(self) -> bool:
        """Check if this is a meridian-horizon paran (closed-form solvable)."""
        meridian_events = {ACGEventType.MC, ACGEventType.IC}
        horizon_events = {ACGEventType.R, ACGEventType.S}
        
        return ((self.event_a in meridian_events and self.event_b in horizon_events) or
                (self.event_a in horizon_events and self.event_b in meridian_events))
    
    def is_horizon_horizon_paran(self) -> bool:
        """Check if this is a horizon-horizon paran (numerical solution required)."""
        horizon_events = {ACGEventType.R, ACGEventType.S}
        return self.event_a in horizon_events and self.event_b in horizon_events
    
    def is_degenerate_paran(self) -> bool:
        """Check if this is a degenerate paran case (both on meridian)."""
        meridian_events = {ACGEventType.MC, ACGEventType.IC}
        return self.event_a in meridian_events and self.event_b in meridian_events
    
    def get_event_hour_angle_constant(self, event: ACGEventType) -> float:
        """
        Get hour angle constant for ACG event type.
        
        Args:
            event: ACG event type
            
        Returns:
            Hour angle constant in radians
        """
        import math
        
        constants = {
            ACGEventType.MC: 0.0,      # Upper culmination
            ACGEventType.IC: math.pi,  # Lower culmination
            # R and S require H₀ calculation based on declination
        }
        
        return constants.get(event, 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "line_id": self.line_id,
            "planets": {
                "planet_a": self.planet_a,
                "event_a": self.event_a.value,
                "planet_b": self.planet_b,
                "event_b": self.event_b.value,
                "description": self.get_paran_description()
            },
            "calculation": {
                "latitude_deg": self.latitude_deg,
                "method": self.calculation_method.value,
                "precision_achieved": self.precision_achieved,
                "is_valid": self.is_valid,
                "failure_reason": self.failure_reason,
                "convergence_iterations": self.convergence_iterations
            },
            "astronomical_data": {
                "epoch_utc": self.epoch_utc.isoformat(),
                "julian_day": self.julian_day,
                "alpha_a_deg": self.alpha_a_deg,
                "delta_a_deg": self.delta_a_deg,
                "alpha_b_deg": self.alpha_b_deg,
                "delta_b_deg": self.delta_b_deg
            },
            "validation": {
                "domain_valid": self.domain_valid,
                "visibility_status": self.visibility_status.value,
                "paran_type": {
                    "is_meridian_horizon": self.is_meridian_horizon_paran(),
                    "is_horizon_horizon": self.is_horizon_horizon_paran(),
                    "is_degenerate": self.is_degenerate_paran()
                }
            }
        }


@dataclass
class ACGParanConfiguration:
    """
    Configuration for ACG paran calculations.
    
    Defines which planet pairs, event combinations, and calculation
    parameters to use for paran line generation.
    """
    
    # Planet selection
    planet_pairs: List[Tuple[str, str]] = field(default_factory=list)
    
    # Event combination settings
    event_combinations: List[str] = field(default_factory=lambda: ["meridian_horizon", "horizon_horizon"])
    include_both_directions: bool = True   # Calculate both A-B and B-A paran directions
    
    # Visibility and precision
    visibility_mode: ACGVisibilityMode = ACGVisibilityMode.ALL
    horizon_convention: HorizonConvention = HorizonConvention.GEOMETRIC
    precision_target: float = 0.03        # Target precision in degrees (Jim Lewis standard)
    
    # Time and calculation settings
    time_anchor: str = "12:00Z"           # Fixed daily epoch for deterministic results
    calculation_date: Optional[datetime] = None
    
    # Performance settings
    max_iterations: int = 100             # Maximum iterations for numerical solver
    convergence_tolerance: float = 1e-8   # Convergence tolerance in radians
    
    # Filtering options
    exclude_degenerate_cases: bool = True # Exclude trivial meridian-meridian parans
    latitude_range: Tuple[float, float] = (-89.5, 89.5)  # Valid latitude range
    
    def __post_init__(self):
        """Set default planet pairs if none provided."""
        if not self.planet_pairs:
            # Default Jim Lewis ACG planet pairs
            default_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
            self.planet_pairs = []
            
            # Generate all unique pairs
            for i in range(len(default_planets)):
                for j in range(i + 1, len(default_planets)):
                    self.planet_pairs.append((default_planets[i], default_planets[j]))
    
    def get_event_type_combinations(self) -> List[Tuple[ACGEventType, ACGEventType]]:
        """
        Get all event type combinations for paran calculation.
        
        Returns:
            List of event type pairs for paran calculation
        """
        combinations = []
        
        if "meridian_horizon" in self.event_combinations:
            meridian_events = [ACGEventType.MC, ACGEventType.IC]
            horizon_events = [ACGEventType.R, ACGEventType.S]
            
            # Meridian-Horizon combinations
            for meridian_event in meridian_events:
                for horizon_event in horizon_events:
                    combinations.append((meridian_event, horizon_event))
                    if self.include_both_directions:
                        combinations.append((horizon_event, meridian_event))
        
        if "horizon_horizon" in self.event_combinations:
            horizon_events = [ACGEventType.R, ACGEventType.S]
            
            # Horizon-Horizon combinations
            for i, event_a in enumerate(horizon_events):
                for j, event_b in enumerate(horizon_events):
                    if i != j:  # Different events
                        combinations.append((event_a, event_b))
        
        # Remove degenerate cases if requested
        if self.exclude_degenerate_cases:
            meridian_events = {ACGEventType.MC, ACGEventType.IC}
            combinations = [
                (ea, eb) for ea, eb in combinations
                if not (ea in meridian_events and eb in meridian_events)
            ]
        
        return combinations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "planet_pairs": self.planet_pairs,
            "event_combinations": self.event_combinations,
            "include_both_directions": self.include_both_directions,
            "visibility_mode": self.visibility_mode.value,
            "horizon_convention": self.horizon_convention.value,
            "precision_target": self.precision_target,
            "time_anchor": self.time_anchor,
            "calculation_date": self.calculation_date.isoformat() if self.calculation_date else None,
            "performance_settings": {
                "max_iterations": self.max_iterations,
                "convergence_tolerance": self.convergence_tolerance
            },
            "filtering": {
                "exclude_degenerate_cases": self.exclude_degenerate_cases,
                "latitude_range": self.latitude_range
            }
        }


@dataclass
class ACGParanResult:
    """
    Complete result of ACG paran calculations.
    
    Contains all calculated paran lines with metadata, performance
    statistics, and validation information.
    """
    
    # Core results
    paran_lines: List[ACGParanLine] = field(default_factory=list)
    
    # Calculation statistics
    total_planet_pairs: int = 0
    total_paran_lines_calculated: int = 0
    successful_calculations: int = 0
    failed_calculations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Method breakdown
    calculation_summary: Dict[str, int] = field(default_factory=lambda: {
        "closed_form": 0,
        "numerical": 0,
        "failed": 0,
        "degenerate_suppressed": 0
    })
    
    # Performance metrics
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    calculation_date: Optional[datetime] = None
    configuration_used: Optional[ACGParanConfiguration] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_paran_line(self, paran_line: ACGParanLine) -> None:
        """Add a paran line to the results."""
        self.paran_lines.append(paran_line)
        self.total_paran_lines_calculated += 1
        
        if paran_line.is_valid:
            self.successful_calculations += 1
            method_key = paran_line.calculation_method.value
            self.calculation_summary[method_key] += 1
        else:
            self.failed_calculations.append({
                "line_id": paran_line.line_id,
                "planets": f"{paran_line.planet_a}-{paran_line.planet_b}",
                "events": f"{paran_line.event_a.value}-{paran_line.event_b.value}",
                "failure_reason": paran_line.failure_reason
            })
            self.calculation_summary["failed"] += 1
    
    def get_success_rate(self) -> float:
        """Calculate success rate of paran calculations."""
        if self.total_paran_lines_calculated == 0:
            return 0.0
        return self.successful_calculations / self.total_paran_lines_calculated
    
    def get_paran_lines_by_method(self, method: ParanCalculationMethod) -> List[ACGParanLine]:
        """Get paran lines calculated with specific method."""
        return [line for line in self.paran_lines if line.calculation_method == method and line.is_valid]
    
    def get_paran_lines_by_planet_pair(self, planet_a: str, planet_b: str) -> List[ACGParanLine]:
        """Get all paran lines for a specific planet pair."""
        return [
            line for line in self.paran_lines 
            if ((line.planet_a == planet_a and line.planet_b == planet_b) or
                (line.planet_a == planet_b and line.planet_b == planet_a))
            and line.is_valid
        ]
    
    def get_average_precision(self) -> float:
        """Get average precision achieved across all valid calculations."""
        valid_lines = [line for line in self.paran_lines if line.is_valid]
        if not valid_lines:
            return 0.0
        return sum(line.precision_achieved for line in valid_lines) / len(valid_lines)
    
    def meets_jim_lewis_standards(self) -> bool:
        """Check if results meet Jim Lewis ACG standards."""
        avg_precision = self.get_average_precision()
        success_rate = self.get_success_rate()
        
        return (
            avg_precision <= 0.03 and     # ≤0.03° precision requirement
            success_rate >= 0.95 and       # High success rate
            len(self.paran_lines) > 0       # At least some results
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "results_summary": {
                "total_planet_pairs": self.total_planet_pairs,
                "total_paran_lines": self.total_paran_lines_calculated,
                "successful_calculations": self.successful_calculations,
                "success_rate": self.get_success_rate(),
                "average_precision": self.get_average_precision(),
                "meets_jim_lewis_standards": self.meets_jim_lewis_standards()
            },
            "calculation_breakdown": self.calculation_summary,
            "paran_lines": [line.to_dict() for line in self.paran_lines if line.is_valid],
            "failed_calculations": self.failed_calculations,
            "performance_metrics": self.performance_metrics,
            "metadata": {
                **self.metadata,
                "calculation_date": self.calculation_date.isoformat() if self.calculation_date else None,
                "configuration": self.configuration_used.to_dict() if self.configuration_used else None
            }
        }


@dataclass
class PlanetaryPosition:
    """Planetary position for paran calculations."""
    
    planet_name: str
    right_ascension_deg: float     # Geocentric apparent RA
    declination_deg: float         # Geocentric apparent declination
    distance_au: float = 1.0       # Distance in AU
    
    # Time context
    julian_day: float = 0.0
    epoch_utc: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "planet_name": self.planet_name,
            "coordinates": {
                "right_ascension_deg": self.right_ascension_deg,
                "declination_deg": self.declination_deg,
                "distance_au": self.distance_au
            },
            "time_context": {
                "julian_day": self.julian_day,
                "epoch_utc": self.epoch_utc.isoformat() if self.epoch_utc else None
            }
        }


# Utility functions for paran model validation
def validate_latitude_range(latitude_deg: float) -> bool:
    """Validate that latitude is within reasonable bounds."""
    return -90.0 <= latitude_deg <= 90.0


def validate_paran_configuration(config: ACGParanConfiguration) -> List[str]:
    """
    Validate paran configuration for common issues.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of validation warnings/errors
    """
    issues = []
    
    # Check planet pairs
    if not config.planet_pairs:
        issues.append("No planet pairs specified")
    
    # Check precision target
    if config.precision_target <= 0 or config.precision_target > 1.0:
        issues.append(f"Invalid precision target: {config.precision_target}")
    
    # Check latitude range
    lat_min, lat_max = config.latitude_range
    if lat_min >= lat_max or abs(lat_min) > 90 or abs(lat_max) > 90:
        issues.append(f"Invalid latitude range: {config.latitude_range}")
    
    # Check convergence settings
    if config.convergence_tolerance <= 0 or config.convergence_tolerance > 1e-3:
        issues.append(f"Invalid convergence tolerance: {config.convergence_tolerance}")
    
    if config.max_iterations < 10 or config.max_iterations > 1000:
        issues.append(f"Invalid max iterations: {config.max_iterations}")
    
    return issues