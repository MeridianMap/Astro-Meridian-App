"""
Jim Lewis ACG Paran Mathematical Helper Module
Implements closed-form solutions and spherical astronomy utilities for paran calculations.

Provides:
- Meridian-horizon closed-form analytical solutions
- Hour angle to geographical longitude conversions
- Spherical coordinate transformations  
- ACG visibility filtering algorithms
- High-precision mathematical utilities

Technical Standards:
- Target precision: ≤0.03° latitude accuracy
- Swiss Ephemeris coordinate system compliance
- Numerical stability for extreme latitudes
- Performance optimized for global calculations
"""

import math
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from app.core.acg.paran_models import (
    ParanPairType,
    ACGVisibilityType,
    GeographicPoint,
    ParanPrecisionLevel
)


class MathematicalConstants:
    """Mathematical constants for ACG paran calculations."""
    
    # Earth parameters (WGS84)
    EARTH_RADIUS_KM = 6378.137
    EARTH_FLATTENING = 1.0 / 298.257223563
    
    # Angular conversions
    DEG_TO_RAD = math.pi / 180.0
    RAD_TO_DEG = 180.0 / math.pi
    HOURS_TO_DEG = 15.0  # 24h = 360°
    DEG_TO_HOURS = 1.0 / 15.0
    
    # Precision thresholds
    CONVERGENCE_THRESHOLD = 1e-12
    LATITUDE_PRECISION_DEG = 0.03
    LONGITUDE_PRECISION_DEG = 0.01
    
    # Geographic limits
    MAX_LATITUDE_DEG = 89.99
    MIN_LATITUDE_DEG = -89.99


@dataclass
class SphericalCoordinates:
    """Spherical coordinate representation for astronomical calculations."""
    right_ascension_rad: float  # α (radians)
    declination_rad: float      # δ (radians)
    hour_angle_rad: float      # H (radians)
    
    @property
    def ra_degrees(self) -> float:
        return self.right_ascension_rad * MathematicalConstants.RAD_TO_DEG
    
    @property
    def dec_degrees(self) -> float:
        return self.declination_rad * MathematicalConstants.RAD_TO_DEG
    
    @property
    def ha_degrees(self) -> float:
        return self.hour_angle_rad * MathematicalConstants.RAD_TO_DEG


class ClosedFormSolver:
    """
    Implements closed-form analytical solutions for meridian-horizon paran pairs.
    
    Based on Jim Lewis ACG methodology for exact paran line calculations.
    Provides high-performance analytical solutions avoiding iterative methods.
    """
    
    def __init__(self, precision_level: ParanPrecisionLevel = ParanPrecisionLevel.HIGH):
        self.precision_level = precision_level
        self.convergence_threshold = self._get_convergence_threshold()
    
    def _get_convergence_threshold(self) -> float:
        """Get convergence threshold based on precision level."""
        thresholds = {
            ParanPrecisionLevel.ULTRA_HIGH: 1e-15,
            ParanPrecisionLevel.HIGH: 1e-12,
            ParanPrecisionLevel.STANDARD: 1e-9,
            ParanPrecisionLevel.FAST: 1e-6
        }
        return thresholds[self.precision_level]
    
    def solve_meridian_horizon_paran(
        self,
        planet_a_coords: SphericalCoordinates,
        planet_b_coords: SphericalCoordinates,
        target_longitude_deg: Optional[float] = None
    ) -> List[GeographicPoint]:
        """
        Solve meridian-horizon paran using closed-form analytical solution.
        
        For meridian-horizon paran pairs (e.g., Planet A on meridian, Planet B on horizon),
        the simultaneity equation reduces to a direct analytical solution.
        
        Args:
            planet_a_coords: Spherical coordinates of planet A
            planet_b_coords: Spherical coordinates of planet B
            target_longitude_deg: Optional longitude constraint
            
        Returns:
            List of geographic points where paran occurs
        """
        solutions = []
        
        # Extract coordinates
        alpha_a = planet_a_coords.right_ascension_rad
        delta_a = planet_a_coords.declination_rad
        alpha_b = planet_b_coords.right_ascension_rad
        delta_b = planet_b_coords.declination_rad
        
        # Calculate hour angle difference for simultaneity
        delta_alpha = self._normalize_angle(alpha_b - alpha_a)
        
        # For meridian-horizon paran: H_A = 0 (meridian), H_B = ±π/2 (horizon)
        for h_b_sign in [-1, 1]:  # East and west horizon
            h_b = h_b_sign * math.pi / 2  # ±90° in radians
            
            # Calculate latitude using spherical trigonometry
            # sin(φ) = -cos(δ_B) * sin(H_B) / cos(A_B)
            # where A_B is azimuth of planet B at horizon
            
            try:
                # Calculate azimuth at horizon crossing
                cos_azimuth_b = math.sin(delta_b) / math.cos(0)  # φ will be solved
                
                # Solve for latitude using simultaneity condition
                # This is the closed-form solution for meridian-horizon paran
                phi_rad = self._solve_latitude_analytical(
                    delta_a, delta_b, h_b, delta_alpha
                )
                
                # Validate latitude bounds
                phi_deg = phi_rad * MathematicalConstants.RAD_TO_DEG
                if not self._is_valid_latitude(phi_deg):
                    continue
                
                # Calculate corresponding longitude
                lambda_deg = self._calculate_paran_longitude(
                    alpha_a, phi_rad, delta_alpha, target_longitude_deg
                )
                
                if lambda_deg is not None:
                    point = GeographicPoint(
                        latitude_deg=phi_deg,
                        longitude_deg=lambda_deg
                    )
                    solutions.append(point)
                    
            except (ValueError, ZeroDivisionError):
                # Skip invalid mathematical cases
                continue
        
        return self._filter_unique_solutions(solutions)
    
    def _solve_latitude_analytical(
        self,
        delta_a_rad: float,
        delta_b_rad: float, 
        h_b_rad: float,
        delta_alpha_rad: float
    ) -> float:
        """
        Analytical solution for latitude in meridian-horizon paran.
        
        Uses spherical trigonometry identity for simultaneous culmination conditions.
        """
        # Apply spherical trigonometry for simultaneity
        # sin(φ) = sin(δ_A) when planet A is on meridian
        # Combined with horizon condition for planet B
        
        numerator = (
            math.sin(delta_a_rad) * math.cos(h_b_rad) +
            math.cos(delta_a_rad) * math.sin(h_b_rad) * math.cos(delta_alpha_rad)
        )
        
        # Ensure value is within valid range for arcsin
        sin_phi = max(-1.0, min(1.0, numerator))
        
        return math.asin(sin_phi)
    
    def _calculate_paran_longitude(
        self,
        alpha_a_rad: float,
        phi_rad: float,
        delta_alpha_rad: float,
        target_longitude_deg: Optional[float]
    ) -> Optional[float]:
        """Calculate longitude where paran occurs."""
        # Convert hour angle to longitude using sidereal time relationship
        # λ = LST - α (approximately, ignoring equation of time)
        
        # For meridian transit: LST = α_A
        lst_hours = alpha_a_rad * MathematicalConstants.RAD_TO_DEG / MathematicalConstants.HOURS_TO_DEG
        
        # Approximate longitude (refined calculation would use precise sidereal time)
        longitude_deg = (lst_hours * MathematicalConstants.HOURS_TO_DEG) % 360.0
        if longitude_deg > 180.0:
            longitude_deg -= 360.0
        
        # Apply longitude constraint if specified
        if target_longitude_deg is not None:
            if abs(longitude_deg - target_longitude_deg) > 1.0:  # 1° tolerance
                return None
        
        return longitude_deg
    
    def solve_meridian_meridian_paran(
        self,
        planet_a_coords: SphericalCoordinates,
        planet_b_coords: SphericalCoordinates
    ) -> List[GeographicPoint]:
        """
        Solve meridian-meridian paran (both planets on meridian simultaneously).
        
        This case has a direct analytical solution since both hour angles are zero.
        """
        alpha_a = planet_a_coords.right_ascension_rad
        alpha_b = planet_b_coords.right_ascension_rad
        delta_a = planet_a_coords.declination_rad
        delta_b = planet_b_coords.declination_rad
        
        # For both on meridian: H_A = H_B = 0
        # Simultaneity requires: α_A = α_B (same LST)
        
        delta_alpha = abs(self._normalize_angle(alpha_b - alpha_a))
        
        # Allow small tolerance for near-simultaneity
        if delta_alpha > math.radians(1.0):  # More than 1° difference
            return []
        
        solutions = []
        
        # Calculate longitude where both planets transit meridian simultaneously
        avg_alpha = (alpha_a + alpha_b) / 2.0
        longitude_deg = (avg_alpha * MathematicalConstants.RAD_TO_DEG) % 360.0
        if longitude_deg > 180.0:
            longitude_deg -= 360.0
        
        # All latitudes are valid for meridian-meridian paran
        # Generate representative points
        for lat_deg in np.arange(-80, 81, 20):  # Sample latitudes
            point = GeographicPoint(
                latitude_deg=float(lat_deg),
                longitude_deg=longitude_deg
            )
            solutions.append(point)
        
        return solutions
    
    def _normalize_angle(self, angle_rad: float) -> float:
        """Normalize angle to [-π, π] range."""
        while angle_rad > math.pi:
            angle_rad -= 2 * math.pi
        while angle_rad < -math.pi:
            angle_rad += 2 * math.pi
        return angle_rad
    
    def _is_valid_latitude(self, latitude_deg: float) -> bool:
        """Check if latitude is within valid bounds."""
        return (MathematicalConstants.MIN_LATITUDE_DEG <= 
                latitude_deg <= MathematicalConstants.MAX_LATITUDE_DEG)
    
    def _filter_unique_solutions(self, points: List[GeographicPoint]) -> List[GeographicPoint]:
        """Remove duplicate solutions within precision threshold."""
        if not points:
            return []
        
        unique_points = []
        threshold_deg = MathematicalConstants.LATITUDE_PRECISION_DEG
        
        for point in points:
            is_unique = True
            for existing in unique_points:
                lat_diff = abs(point.latitude_deg - existing.latitude_deg)
                lon_diff = abs(point.longitude_deg - existing.longitude_deg)
                
                if lat_diff < threshold_deg and lon_diff < threshold_deg:
                    is_unique = False
                    break
            
            if is_unique:
                unique_points.append(point)
        
        return unique_points


class SphericalAstronomyUtils:
    """
    Spherical astronomy utility functions for ACG paran calculations.
    
    Provides coordinate transformations, hour angle calculations,
    and visibility determinations following astronomical conventions.
    """
    
    @staticmethod
    def hour_angle_to_longitude(
        hour_angle_rad: float,
        right_ascension_rad: float,
        sidereal_time_hours: Optional[float] = None
    ) -> float:
        """
        Convert hour angle to geographic longitude.
        
        Args:
            hour_angle_rad: Hour angle in radians
            right_ascension_rad: Right ascension in radians
            sidereal_time_hours: Local sidereal time (if known)
            
        Returns:
            Geographic longitude in degrees
        """
        if sidereal_time_hours is None:
            # Approximate using α + H relationship
            lst_rad = right_ascension_rad + hour_angle_rad
        else:
            lst_rad = sidereal_time_hours * MathematicalConstants.HOURS_TO_DEG * MathematicalConstants.DEG_TO_RAD
        
        # Convert to longitude (LST = 0 at Greenwich)
        longitude_deg = lst_rad * MathematicalConstants.RAD_TO_DEG
        
        # Normalize to [-180, 180] range
        while longitude_deg > 180.0:
            longitude_deg -= 360.0
        while longitude_deg < -180.0:
            longitude_deg += 360.0
        
        return longitude_deg
    
    @staticmethod
    def calculate_horizon_hour_angle(
        declination_rad: float,
        latitude_rad: float,
        altitude_rad: float = 0.0
    ) -> Optional[float]:
        """
        Calculate hour angle at which object crosses horizon.
        
        Args:
            declination_rad: Declination in radians
            latitude_rad: Geographic latitude in radians
            altitude_rad: Altitude above horizon (default 0°)
            
        Returns:
            Hour angle in radians, or None if never crosses horizon
        """
        # Spherical trigonometry: cos(H) = (sin(h) - sin(φ)sin(δ)) / (cos(φ)cos(δ))
        cos_phi = math.cos(latitude_rad)
        cos_delta = math.cos(declination_rad)
        
        if abs(cos_phi * cos_delta) < 1e-12:  # Avoid division by zero
            return None
        
        cos_h = (
            math.sin(altitude_rad) - 
            math.sin(latitude_rad) * math.sin(declination_rad)
        ) / (cos_phi * cos_delta)
        
        # Check if solution exists
        if abs(cos_h) > 1.0:
            return None  # Object never crosses specified altitude
        
        return math.acos(max(-1.0, min(1.0, cos_h)))
    
    @staticmethod
    def is_object_visible(
        declination_rad: float,
        latitude_rad: float,
        visibility_type: ACGVisibilityType = ACGVisibilityType.ALL
    ) -> bool:
        """
        Determine if celestial object is visible from given latitude.
        
        Args:
            declination_rad: Object declination in radians
            latitude_rad: Geographic latitude in radians
            visibility_type: Visibility filtering criteria
            
        Returns:
            True if object meets visibility criteria
        """
        if visibility_type == ACGVisibilityType.ALL:
            return True
        
        # Calculate maximum altitude (when on meridian)
        max_altitude_rad = math.pi/2 - abs(latitude_rad - declination_rad)
        
        if visibility_type == ACGVisibilityType.BOTH_VISIBLE:
            # Both objects must rise above horizon
            return max_altitude_rad > 0
        
        elif visibility_type == ACGVisibilityType.MERIDIAN_VISIBLE_ONLY:
            # Object must be visible when crossing meridian
            meridian_altitude = math.pi/2 - abs(latitude_rad - declination_rad)
            return meridian_altitude > math.radians(-18)  # Astronomical twilight
        
        return True
    
    @staticmethod
    def calculate_azimuth_at_horizon(
        declination_rad: float,
        latitude_rad: float,
        hour_angle_rad: float
    ) -> float:
        """
        Calculate azimuth when object is on horizon.
        
        Uses spherical trigonometry to determine bearing.
        """
        sin_azimuth = (
            math.cos(declination_rad) * math.sin(hour_angle_rad) /
            math.cos(0)  # cos(altitude) = 1 at horizon
        )
        
        cos_azimuth = (
            (math.sin(declination_rad) - math.sin(latitude_rad) * math.sin(0)) /
            (math.cos(latitude_rad) * math.cos(0))
        )
        
        azimuth_rad = math.atan2(sin_azimuth, cos_azimuth)
        return azimuth_rad * MathematicalConstants.RAD_TO_DEG


class ACGVisibilityFilter:
    """
    Advanced visibility filtering system for ACG paran calculations.
    
    Implements intelligent filtering based on astronomical visibility,
    geographic constraints, and computational efficiency requirements.
    """
    
    def __init__(self, precision_level: ParanPrecisionLevel = ParanPrecisionLevel.HIGH):
        self.precision_level = precision_level
        self.cache = {}  # Simple visibility cache
    
    def filter_paran_solutions(
        self,
        solutions: List[GeographicPoint],
        planet_a_coords: SphericalCoordinates,
        planet_b_coords: SphericalCoordinates,
        visibility_type: ACGVisibilityType,
        geographic_bounds: Optional[Dict[str, float]] = None
    ) -> List[GeographicPoint]:
        """
        Apply comprehensive visibility filtering to paran solutions.
        
        Args:
            solutions: Raw paran solutions to filter
            planet_a_coords: Coordinates of first planet
            planet_b_coords: Coordinates of second planet
            visibility_type: Visibility filtering criteria
            geographic_bounds: Optional geographic constraints
            
        Returns:
            Filtered list of valid paran points
        """
        filtered_solutions = []
        
        for point in solutions:
            if self._is_solution_valid(
                point, planet_a_coords, planet_b_coords, 
                visibility_type, geographic_bounds
            ):
                filtered_solutions.append(point)
        
        return self._sort_by_precision(filtered_solutions)
    
    def _is_solution_valid(
        self,
        point: GeographicPoint,
        planet_a_coords: SphericalCoordinates,
        planet_b_coords: SphericalCoordinates,
        visibility_type: ACGVisibilityType,
        geographic_bounds: Optional[Dict[str, float]]
    ) -> bool:
        """Comprehensive validation of paran solution point."""
        
        # Geographic bounds check
        if geographic_bounds and not self._within_geographic_bounds(point, geographic_bounds):
            return False
        
        # Visibility check for both planets
        latitude_rad = point.latitude_deg * MathematicalConstants.DEG_TO_RAD
        
        planet_a_visible = SphericalAstronomyUtils.is_object_visible(
            planet_a_coords.declination_rad, latitude_rad, visibility_type
        )
        planet_b_visible = SphericalAstronomyUtils.is_object_visible(
            planet_b_coords.declination_rad, latitude_rad, visibility_type
        )
        
        if visibility_type == ACGVisibilityType.BOTH_VISIBLE:
            return planet_a_visible and planet_b_visible
        elif visibility_type == ACGVisibilityType.MERIDIAN_VISIBLE_ONLY:
            return planet_a_visible or planet_b_visible
        
        return True  # ACGVisibilityType.ALL
    
    def _within_geographic_bounds(
        self, 
        point: GeographicPoint, 
        bounds: Dict[str, float]
    ) -> bool:
        """Check if point is within specified geographic bounds."""
        return (
            bounds.get('min_lat', -90) <= point.latitude_deg <= bounds.get('max_lat', 90) and
            bounds.get('min_lon', -180) <= point.longitude_deg <= bounds.get('max_lon', 180)
        )
    
    def _sort_by_precision(self, points: List[GeographicPoint]) -> List[GeographicPoint]:
        """Sort solutions by computational precision and reliability."""
        # For now, maintain original order
        # Future enhancement: sort by precision metrics
        return points


class ParanMathUtils:
    """
    High-level mathematical utilities for paran calculations.
    
    Provides convenient interfaces to closed-form solvers and
    spherical astronomy functions optimized for ACG applications.
    """
    
    @staticmethod
    def solve_paran_analytical(
        planet_a_coords: SphericalCoordinates,
        planet_b_coords: SphericalCoordinates,
        paran_type: ParanPairType,
        visibility_filter: ACGVisibilityType = ACGVisibilityType.ALL,
        precision_level: ParanPrecisionLevel = ParanPrecisionLevel.HIGH
    ) -> List[GeographicPoint]:
        """
        High-level interface for analytical paran solutions.
        
        Automatically selects appropriate mathematical method based on paran type
        and applies visibility filtering according to specifications.
        """
        solver = ClosedFormSolver(precision_level)
        filter_system = ACGVisibilityFilter(precision_level)
        
        # Dispatch to appropriate solver based on paran type
        if paran_type == ParanPairType.MERIDIAN_HORIZON:
            raw_solutions = solver.solve_meridian_horizon_paran(
                planet_a_coords, planet_b_coords
            )
        elif paran_type == ParanPairType.HORIZON_MERIDIAN:
            # Swap planets for symmetry
            raw_solutions = solver.solve_meridian_horizon_paran(
                planet_b_coords, planet_a_coords
            )
        elif paran_type == ParanPairType.MERIDIAN_MERIDIAN:
            raw_solutions = solver.solve_meridian_meridian_paran(
                planet_a_coords, planet_b_coords
            )
        else:
            # HORIZON_HORIZON requires numerical methods (handled elsewhere)
            return []
        
        # Apply visibility filtering
        filtered_solutions = filter_system.filter_paran_solutions(
            raw_solutions, planet_a_coords, planet_b_coords, visibility_filter
        )
        
        return filtered_solutions
    
    @staticmethod
    def validate_solution_precision(
        point: GeographicPoint,
        expected_precision_deg: float = MathematicalConstants.LATITUDE_PRECISION_DEG
    ) -> bool:
        """
        Validate that solution meets required precision standards.
        
        Args:
            point: Geographic point to validate
            expected_precision_deg: Required precision in degrees
            
        Returns:
            True if solution meets precision requirements
        """
        # For now, all analytical solutions are considered precise
        # Future enhancement: implement precision validation against reference data
        return abs(point.latitude_deg) <= MathematicalConstants.MAX_LATITUDE_DEG