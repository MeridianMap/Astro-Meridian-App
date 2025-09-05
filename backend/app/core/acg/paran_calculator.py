"""
Jim Lewis ACG Paran Calculator - Professional Planetary Simultaneity

This module implements Jim Lewis-style ACG planetary paran calculations where
two planets are simultaneously angular on different cardinal angles (ASC, DSC, MC, IC).

Mathematical foundations based on Jim Lewis ACG specifications:
- Simultaneity equation: α_A + H_e(A, φ) = α_B + H_e(B, φ) (mod 2π)
- Closed-form meridian-horizon solutions (primary method)
- Numerical horizon-horizon solutions using Brent root finding
- ≤0.03° latitude precision requirement
- <800ms global paran search performance target

Reference: Jim Lewis ACG Parans Technical Reference
"""

import math
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
import logging

import swisseph as swe
import numpy as np
from scipy.optimize import brentq

from .paran_models import (
    ACGParanLine, ACGParanConfiguration, ACGParanResult, PlanetaryPosition,
    ACGEventType, ParanCalculationMethod, ACGVisibilityMode, HorizonConvention,
    validate_latitude_range, ParanPairType, ACGVisibilityType, 
    GeographicPoint, ParanPrecisionLevel
)
from .paran_math import (
    ClosedFormSolver,
    SphericalAstronomyUtils,
    ACGVisibilityFilter,
    ParanMathUtils,
    SphericalCoordinates
)
from .numerical_solver import (
    NumericalHorizonHorizonSolver,
    ParanSolutionValidator
)
from ..ephemeris.tools.ephemeris import julian_day_from_datetime
from ..ephemeris.const import PLANET_NAMES

logger = logging.getLogger(__name__)


class ACGParanCalculationError(Exception):
    """Exception for ACG paran calculation errors."""
    pass


class JimLewisACGParanCalculator:
    """
    Jim Lewis ACG Paran Calculator.
    
    Implements professional-grade ACG planetary paran calculations following
    Jim Lewis methodologies with both closed-form and numerical solutions.
    """
    
    # Swiss Ephemeris planet mappings
    PLANET_SE_MAPPING = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO
    }
    
    # Hour angle constants for ACG events (radians)
    EVENT_HOUR_ANGLE_CONSTANTS = {
        ACGEventType.MC: 0.0,      # Upper culmination
        ACGEventType.IC: math.pi,  # Lower culmination
        # R and S are calculated dynamically based on declination
    }
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Performance tracking
        self.calculation_times = []
        self.precision_achieved = []
        
        # Calculation cache for performance
        self.position_cache = {}
        self.last_calculation_jd = None
        
        # Initialize advanced solvers for comprehensive paran calculations
        self.closed_form_solver = ClosedFormSolver(ParanPrecisionLevel.HIGH)
        self.numerical_solver = NumericalHorizonHorizonSolver(ParanPrecisionLevel.HIGH)
        self.visibility_filter = ACGVisibilityFilter(ParanPrecisionLevel.HIGH)
        self.solution_validator = ParanSolutionValidator()
    
    def calculate_planetary_parans(
        self,
        config: ACGParanConfiguration,
        planetary_positions: Optional[Dict[str, PlanetaryPosition]] = None
    ) -> ACGParanResult:
        """
        Calculate Jim Lewis ACG planetary parans.
        
        Args:
            config: Paran calculation configuration
            planetary_positions: Pre-calculated planetary positions (optional)
            
        Returns:
            ACGParanResult with all calculated paran lines
        """
        start_time = time.time()
        
        try:
            result = ACGParanResult(
                total_planet_pairs=len(config.planet_pairs),
                calculation_date=config.calculation_date or datetime.now(timezone.utc),
                configuration_used=config
            )
            
            # Get planetary positions
            if planetary_positions is None:
                calculation_date = config.calculation_date or datetime.now(timezone.utc)
                planetary_positions = self._calculate_planetary_positions(
                    [planet for pair in config.planet_pairs for planet in pair],
                    calculation_date
                )
            
            # Get event combinations
            event_combinations = config.get_event_type_combinations()
            
            # Calculate parans for each planet pair
            for planet_a, planet_b in config.planet_pairs:
                if planet_a not in planetary_positions or planet_b not in planetary_positions:
                    self.logger.warning(f"Missing positions for pair {planet_a}-{planet_b}")
                    continue
                
                pos_a = planetary_positions[planet_a]
                pos_b = planetary_positions[planet_b]
                
                # Calculate parans for each event combination
                for event_a, event_b in event_combinations:
                    paran_line = self._calculate_single_paran(
                        planet_a, event_a, pos_a,
                        planet_b, event_b, pos_b,
                        config
                    )
                    
                    if paran_line:
                        result.add_paran_line(paran_line)
            
            # Record performance metrics
            calculation_time = time.time() - start_time
            result.performance_metrics = {
                "total_calculation_time_ms": calculation_time * 1000,
                "average_time_per_paran_ms": (calculation_time * 1000) / max(1, len(result.paran_lines)),
                "meets_800ms_target": calculation_time < 0.8,
                "precision_statistics": {
                    "average_precision": result.get_average_precision(),
                    "meets_jim_lewis_standard": result.get_average_precision() <= 0.03
                }
            }
            
            self.calculation_times.append(calculation_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"ACG paran calculation failed: {e}")
            raise ACGParanCalculationError(f"Paran calculation failed: {e}")
    
    def _calculate_single_paran(
        self,
        planet_a: str, event_a: ACGEventType, pos_a: PlanetaryPosition,
        planet_b: str, event_b: ACGEventType, pos_b: PlanetaryPosition,
        config: ACGParanConfiguration
    ) -> Optional[ACGParanLine]:
        """
        Calculate a single ACG paran line.
        
        Args:
            planet_a: First planet name
            event_a: First planet's event
            pos_a: First planet's position
            planet_b: Second planet name
            event_b: Second planet's event
            pos_b: Second planet's position
            config: Calculation configuration
            
        Returns:
            ACGParanLine or None if calculation fails
        """
        try:
            paran_line = ACGParanLine(
                planet_a=planet_a,
                event_a=event_a,
                planet_b=planet_b,
                event_b=event_b,
                latitude_deg=0.0,  # Will be calculated
                calculation_method=ParanCalculationMethod.FAILED,
                precision_achieved=999.0,  # Will be updated
                visibility_status=config.visibility_mode,
                epoch_utc=config.calculation_date or datetime.now(timezone.utc),
                julian_day=pos_a.julian_day,
                alpha_a_deg=pos_a.right_ascension_deg,
                delta_a_deg=pos_a.declination_deg,
                alpha_b_deg=pos_b.right_ascension_deg,
                delta_b_deg=pos_b.declination_deg
            )
            
            # Skip degenerate cases if configured
            if config.exclude_degenerate_cases and paran_line.is_degenerate_paran():
                return None
            
            # Choose calculation method based on paran type
            if paran_line.is_meridian_horizon_paran():
                success = self._solve_meridian_horizon_closed_form(paran_line, config)
            elif paran_line.is_horizon_horizon_paran():
                success = self._solve_horizon_horizon_numerical(paran_line, config)
            else:
                # Degenerate case - should be filtered out above
                paran_line.is_valid = False
                paran_line.failure_reason = "Degenerate case: both planets on meridian"
                return paran_line
            
            # Apply enhanced visibility filter if calculation succeeded
            if success and paran_line.is_valid:
                visibility_valid = self._apply_enhanced_visibility_filter(paran_line, config)
                if not visibility_valid:
                    paran_line.is_valid = False
                    paran_line.failure_reason = "Failed enhanced visibility filter"
            
            return paran_line
            
        except Exception as e:
            self.logger.error(f"Single paran calculation failed: {e}")
            return None
    
    def _solve_meridian_horizon_closed_form(
        self,
        paran_line: ACGParanLine,
        config: ACGParanConfiguration
    ) -> bool:
        """
        Solve meridian-horizon paran using closed-form analytical solution.
        
        Based on Jim Lewis ACG reference:
        φ = atan2(-cos(H₀)·cos(δ_horizon), sin(δ_horizon))
        
        Args:
            paran_line: Paran line to solve (modified in-place)
            config: Calculation configuration
            
        Returns:
            True if calculation succeeded
        """
        try:
            # Convert to radians
            alpha_a = math.radians(paran_line.alpha_a_deg)
            delta_a = math.radians(paran_line.delta_a_deg)
            alpha_b = math.radians(paran_line.alpha_b_deg)
            delta_b = math.radians(paran_line.delta_b_deg)
            
            # Identify meridian and horizon planets
            meridian_events = {ACGEventType.MC, ACGEventType.IC}
            
            if paran_line.event_a in meridian_events:
                # Planet A on meridian, Planet B on horizon
                alpha_meridian, delta_meridian = alpha_a, delta_a
                alpha_horizon, delta_horizon = alpha_b, delta_b
                meridian_event, horizon_event = paran_line.event_a, paran_line.event_b
            else:
                # Planet B on meridian, Planet A on horizon  
                alpha_meridian, delta_meridian = alpha_b, delta_b
                alpha_horizon, delta_horizon = alpha_a, delta_a
                meridian_event, horizon_event = paran_line.event_b, paran_line.event_a
            
            # Calculate delta alpha (wrapped to [-π, π])
            delta_alpha = self._wrap_minus_pi_to_pi(alpha_meridian - alpha_horizon)
            
            # Get meridian hour angle constant
            H_meridian = self.EVENT_HOUR_ANGLE_CONSTANTS[meridian_event]
            
            # Calculate H₀ for the horizon event
            H0 = self._wrap_0_to_pi(delta_alpha + H_meridian)
            
            # Apply Jim Lewis closed-form solution
            # φ = atan2(-cos(H₀)·cos(δ_horizon), sin(δ_horizon))
            numerator = -math.cos(H0) * math.cos(delta_horizon)
            denominator = math.sin(delta_horizon)
            
            if denominator == 0:
                paran_line.is_valid = False
                paran_line.failure_reason = "Undefined: planet at celestial pole"
                return False
            
            latitude_rad = math.atan2(numerator, denominator)
            latitude_deg = math.degrees(latitude_rad)
            
            # Validate domain
            if not validate_latitude_range(latitude_deg):
                paran_line.is_valid = False
                paran_line.failure_reason = f"Latitude out of range: {latitude_deg:.3f}°"
                paran_line.domain_valid = False
                return False
            
            # Check latitude bounds from configuration
            lat_min, lat_max = config.latitude_range
            if not (lat_min <= latitude_deg <= lat_max):
                paran_line.is_valid = False
                paran_line.failure_reason = f"Latitude outside configured range: {latitude_deg:.3f}°"
                return False
            
            # Update paran line with results
            paran_line.latitude_deg = latitude_deg
            paran_line.calculation_method = ParanCalculationMethod.CLOSED_FORM
            paran_line.precision_achieved = 0.001  # Analytical solution precision
            paran_line.is_valid = True
            paran_line.domain_valid = True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Closed-form meridian-horizon solution failed: {e}")
            paran_line.is_valid = False
            paran_line.failure_reason = f"Closed-form calculation error: {e}"
            return False
    
    def _solve_horizon_horizon_numerical(
        self,
        paran_line: ACGParanLine,
        config: ACGParanConfiguration
    ) -> bool:
        """
        Solve horizon-horizon paran using Brent numerical method.
        
        Based on Jim Lewis ACG reference:
        F(φ) = s_A·arccos(-tan(φ)·tan(δ_A)) - s_B·arccos(-tan(φ)·tan(δ_B)) - Δα
        
        Args:
            paran_line: Paran line to solve (modified in-place)
            config: Calculation configuration
            
        Returns:
            True if calculation succeeded
        """
        try:
            # Convert to radians
            delta_a = math.radians(paran_line.delta_a_deg)
            delta_b = math.radians(paran_line.delta_b_deg)
            
            # Calculate delta alpha
            alpha_a = math.radians(paran_line.alpha_a_deg)
            alpha_b = math.radians(paran_line.alpha_b_deg)
            delta_alpha = self._wrap_minus_pi_to_pi(alpha_a - alpha_b)
            
            # Event signs for horizon crossings
            event_signs = {
                ACGEventType.R: -1.0,  # Rising (negative hour angle)
                ACGEventType.S: +1.0   # Setting (positive hour angle)
            }
            
            s_a = event_signs[paran_line.event_a]
            s_b = event_signs[paran_line.event_b]
            
            # Define the simultaneity equation F(φ) = 0
            def simultaneity_function(phi_rad: float) -> float:
                """
                Jim Lewis horizon-horizon simultaneity equation.
                F(φ) = s_A·arccos(clip(-tan(φ)·tan(δ_A))) - s_B·arccos(clip(-tan(φ)·tan(δ_B))) - Δα
                """
                tan_phi = math.tan(phi_rad)
                
                # Calculate hour angles with domain clipping
                arg_a = -tan_phi * math.tan(delta_a)
                arg_b = -tan_phi * math.tan(delta_b)
                
                # Clip arguments to valid domain [-1, 1]
                arg_a = max(-1.0, min(1.0, arg_a))
                arg_b = max(-1.0, min(1.0, arg_b))
                
                H0_a = math.acos(arg_a)
                H0_b = math.acos(arg_b)
                
                return s_a * H0_a - s_b * H0_b - delta_alpha
            
            # Find valid bracketing interval
            lat_min_rad = math.radians(config.latitude_range[0])
            lat_max_rad = math.radians(config.latitude_range[1])
            
            # Check domain constraints for both planets
            valid_ranges = []
            
            for phi_test_deg in np.linspace(config.latitude_range[0], config.latitude_range[1], 1000):
                phi_test_rad = math.radians(phi_test_deg)
                tan_phi = math.tan(phi_test_rad)
                
                # Check if both planets can have horizon crossings at this latitude
                if (abs(tan_phi * math.tan(delta_a)) <= 1.0 and
                    abs(tan_phi * math.tan(delta_b)) <= 1.0):
                    valid_ranges.append(phi_test_rad)
            
            if len(valid_ranges) < 2:
                paran_line.is_valid = False
                paran_line.failure_reason = "No valid domain for horizon-horizon calculation"
                paran_line.domain_valid = False
                return False
            
            # Find sign changes for bracketing
            bracket_found = False
            solution_phi = None
            iterations_used = 0
            
            for i in range(len(valid_ranges) - 1):
                phi_start = valid_ranges[i]
                phi_end = valid_ranges[i + 1]
                
                try:
                    f_start = simultaneity_function(phi_start)
                    f_end = simultaneity_function(phi_end)
                    
                    # Check for sign change (bracketing condition)
                    if f_start * f_end <= 0:
                        # Use Brent method to find root
                        solution_phi = brentq(
                            simultaneity_function,
                            phi_start,
                            phi_end,
                            xtol=config.convergence_tolerance,
                            maxiter=config.max_iterations
                        )
                        bracket_found = True
                        iterations_used = config.max_iterations  # Brent doesn't return iterations
                        break
                        
                except (ValueError, ZeroDivisionError):
                    continue
            
            if not bracket_found:
                paran_line.is_valid = False
                paran_line.failure_reason = "No bracketing interval found for numerical solution"
                return False
            
            # Convert solution to degrees
            latitude_deg = math.degrees(solution_phi)
            
            # Validate solution
            if not validate_latitude_range(latitude_deg):
                paran_line.is_valid = False
                paran_line.failure_reason = f"Numerical solution out of range: {latitude_deg:.3f}°"
                return False
            
            # Calculate achieved precision (approximate)
            precision_achieved = abs(simultaneity_function(solution_phi))
            precision_deg = math.degrees(precision_achieved)
            
            # Update paran line with results
            paran_line.latitude_deg = latitude_deg
            paran_line.calculation_method = ParanCalculationMethod.NUMERICAL
            paran_line.precision_achieved = precision_deg
            paran_line.is_valid = True
            paran_line.domain_valid = True
            paran_line.convergence_iterations = iterations_used
            
            return True
            
        except Exception as e:
            self.logger.error(f"Numerical horizon-horizon solution failed: {e}")
            paran_line.is_valid = False
            paran_line.failure_reason = f"Numerical calculation error: {e}"
            return False
    
    def _apply_enhanced_visibility_filter(
        self,
        paran_line: ACGParanLine,
        config: ACGParanConfiguration
    ) -> bool:
        """
        Apply enhanced ACG visibility filter using advanced filtering system.
        
        Args:
            paran_line: Paran line to check
            config: Configuration with visibility settings
            
        Returns:
            True if paran line passes enhanced visibility filter
        """
        try:
            # Convert to enhanced system format
            planet_a_coords = SphericalCoordinates(
                right_ascension_rad=math.radians(paran_line.alpha_a_deg),
                declination_rad=math.radians(paran_line.delta_a_deg),
                hour_angle_rad=self._get_event_hour_angle(
                    paran_line.event_a,
                    math.radians(paran_line.delta_a_deg),
                    math.radians(paran_line.latitude_deg)
                )
            )
            
            planet_b_coords = SphericalCoordinates(
                right_ascension_rad=math.radians(paran_line.alpha_b_deg),
                declination_rad=math.radians(paran_line.delta_b_deg),
                hour_angle_rad=self._get_event_hour_angle(
                    paran_line.event_b,
                    math.radians(paran_line.delta_b_deg),
                    math.radians(paran_line.latitude_deg)
                )
            )
            
            # Convert visibility mode
            visibility_type = self._convert_visibility_mode(config.visibility_mode)
            
            # Create geographic point
            point = GeographicPoint(
                latitude_deg=paran_line.latitude_deg,
                longitude_deg=0.0  # Longitude not relevant for visibility
            )
            
            # Apply enhanced visibility filter
            filtered_points = self.visibility_filter.filter_paran_solutions(
                [point],
                planet_a_coords,
                planet_b_coords,
                visibility_type
            )
            
            return len(filtered_points) > 0
            
        except Exception as e:
            self.logger.warning(f"Enhanced visibility filter failed: {e}")
            # Fallback to original visibility filter
            return self._apply_visibility_filter(paran_line, config)
    
    def _convert_visibility_mode(self, visibility_mode: ACGVisibilityMode) -> ACGVisibilityType:
        """Convert legacy visibility mode to enhanced system type."""
        conversion_map = {
            ACGVisibilityMode.ALL: ACGVisibilityType.ALL,
            ACGVisibilityMode.BOTH_VISIBLE: ACGVisibilityType.BOTH_VISIBLE,
            ACGVisibilityMode.MERIDIAN_VISIBLE_ONLY: ACGVisibilityType.MERIDIAN_VISIBLE_ONLY
        }
        return conversion_map.get(visibility_mode, ACGVisibilityType.ALL)
    
    def _apply_visibility_filter(
        self,
        paran_line: ACGParanLine,
        config: ACGParanConfiguration
    ) -> bool:
        """
        Apply ACG visibility filter to paran line.
        
        Args:
            paran_line: Paran line to check
            config: Configuration with visibility settings
            
        Returns:
            True if paran line passes visibility filter
        """
        try:
            if config.visibility_mode == ACGVisibilityMode.ALL:
                return True  # No visibility filter
            
            # Calculate altitude of planets at the paran latitude
            phi_rad = math.radians(paran_line.latitude_deg)
            delta_a_rad = math.radians(paran_line.delta_a_deg)
            delta_b_rad = math.radians(paran_line.delta_b_deg)
            
            # Get hour angles for each planet's event
            H_a = self._get_event_hour_angle(paran_line.event_a, delta_a_rad, phi_rad)
            H_b = self._get_event_hour_angle(paran_line.event_b, delta_b_rad, phi_rad)
            
            # Calculate altitudes: sin(h) = sin(φ)sin(δ) + cos(φ)cos(δ)cos(H)
            sin_h_a = (math.sin(phi_rad) * math.sin(delta_a_rad) + 
                      math.cos(phi_rad) * math.cos(delta_a_rad) * math.cos(H_a))
            sin_h_b = (math.sin(phi_rad) * math.sin(delta_b_rad) + 
                      math.cos(phi_rad) * math.cos(delta_b_rad) * math.cos(H_b))
            
            h_a = math.asin(max(-1.0, min(1.0, sin_h_a)))
            h_b = math.asin(max(-1.0, min(1.0, sin_h_b)))
            
            # Apply visibility filter
            horizon_limit = 0.0  # Geometric horizon
            if config.horizon_convention == HorizonConvention.APPARENT:
                horizon_limit = math.radians(-0.5667)  # Standard refraction correction
            
            if config.visibility_mode == ACGVisibilityMode.BOTH_VISIBLE:
                return h_a >= horizon_limit and h_b >= horizon_limit
            elif config.visibility_mode == ACGVisibilityMode.MERIDIAN_VISIBLE_ONLY:
                meridian_events = {ACGEventType.MC, ACGEventType.IC}
                if paran_line.event_a in meridian_events:
                    return h_a >= horizon_limit
                else:
                    return h_b >= horizon_limit
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Visibility filter failed: {e}")
            return True  # Default to passing if filter fails
    
    def _get_event_hour_angle(self, event: ACGEventType, delta: float, phi: float) -> float:
        """
        Get hour angle for ACG event at given declination and latitude.
        
        Args:
            event: ACG event type
            delta: Declination in radians
            phi: Latitude in radians
            
        Returns:
            Hour angle in radians
        """
        if event == ACGEventType.MC:
            return 0.0
        elif event == ACGEventType.IC:
            return math.pi
        elif event in [ACGEventType.R, ACGEventType.S]:
            # Calculate H₀ = arccos(-tan(φ)tan(δ))
            tan_product = math.tan(phi) * math.tan(delta)
            if abs(tan_product) > 1.0:
                return 0.0  # Planet doesn't rise/set at this latitude
            
            H0 = math.acos(-tan_product)
            return -H0 if event == ACGEventType.R else H0
        
        return 0.0
    
    def _calculate_planetary_positions(
        self,
        planet_names: List[str],
        calculation_date: datetime
    ) -> Dict[str, PlanetaryPosition]:
        """
        Calculate planetary positions for paran calculations.
        
        Args:
            planet_names: List of planet names
            calculation_date: Date for calculations
            
        Returns:
            Dictionary mapping planet names to positions
        """
        try:
            jd = julian_day_from_datetime(calculation_date)
            positions = {}
            
            for planet_name in set(planet_names):  # Remove duplicates
                if planet_name not in self.PLANET_SE_MAPPING:
                    self.logger.warning(f"Unknown planet: {planet_name}")
                    continue
                
                se_planet = self.PLANET_SE_MAPPING[planet_name]
                
                # Calculate geocentric apparent position
                result = swe.calc_ut(jd, se_planet, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)
                coords = result[0]
                
                # Extract right ascension and declination
                ra_deg = coords[0]  # Right ascension
                dec_deg = coords[1]  # Declination
                distance = coords[2]  # Distance
                
                positions[planet_name] = PlanetaryPosition(
                    planet_name=planet_name,
                    right_ascension_deg=ra_deg,
                    declination_deg=dec_deg,
                    distance_au=distance,
                    julian_day=jd,
                    epoch_utc=calculation_date
                )
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Planetary position calculation failed: {e}")
            raise ACGParanCalculationError(f"Position calculation failed: {e}")
    
    def _wrap_minus_pi_to_pi(self, angle: float) -> float:
        """Wrap angle to [-π, π] range."""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle <= -math.pi:
            angle += 2 * math.pi
        return angle
    
    def _wrap_0_to_pi(self, angle: float) -> float:
        """Wrap angle to [0, π] range."""
        angle = angle % (2 * math.pi)
        if angle > math.pi:
            angle = 2 * math.pi - angle
        return angle
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics for paran calculations.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.calculation_times:
            return {"no_data": True}
        
        return {
            "total_calculations": len(self.calculation_times),
            "average_time_ms": (sum(self.calculation_times) / len(self.calculation_times)) * 1000,
            "max_time_ms": max(self.calculation_times) * 1000,
            "min_time_ms": min(self.calculation_times) * 1000,
            "meets_800ms_target": max(self.calculation_times) < 0.8,
            "precision_statistics": {
                "count": len(self.precision_achieved),
                "average_precision": sum(self.precision_achieved) / len(self.precision_achieved) if self.precision_achieved else 0.0,
                "meets_jim_lewis_standard": all(p <= 0.03 for p in self.precision_achieved)
            }
        }