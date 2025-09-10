"""
Astrological Sect Calculator - Day/Night Chart Determination

Professional implementation of sect determination for Arabic parts calculations.
Supports multiple validation methods with confidence scoring and edge case handling.

Traditional Methods:
- House position method (Sun in houses 7-12 = day, 1-6 = night)  
- Horizon calculation method (Sun above/below mathematical horizon)
- Ascendant degrees method (0-180° = day, 180-360° = night)

Edge Cases:
- Polar region births (midnight sun/polar night)
- Twilight births (Sun very close to horizon)
- Missing data fallbacks
"""

import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from .arabic_parts_models import SectDetermination, ChartSect
from ..tools.ephemeris import PlanetPosition, HouseSystem
from extracted.systems.utils.const import normalize_longitude


class SectCalculationMethod:
    """Constants for sect determination methods."""
    HOUSE_POSITION = "house_position"
    HORIZON_CALCULATION = "horizon_calculation"  
    ASCENDANT_DEGREES = "ascendant_degrees"
    COMPOSITE = "composite"


@dataclass
class SectAnalysisData:
    """Input data for sect analysis."""
    sun_longitude: float
    sun_latitude: float = 0.0
    ascendant_longitude: float = 0.0
    midheaven_longitude: float = 0.0
    
    # House system data
    house_cusps: Optional[List[float]] = None
    sun_house: Optional[int] = None
    
    # Geographic data for horizon calculations
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None
    birth_datetime: Optional[datetime] = None
    
    # Optional: raw calculation data
    julian_day: Optional[float] = None
    local_sidereal_time: Optional[float] = None


class SectCalculator:
    """
    Professional astrological sect calculator with multiple validation methods.
    
    Implements traditional and modern approaches to sect determination with
    confidence scoring and comprehensive edge case handling.
    """
    
    def __init__(self):
        """Initialize sect calculator."""
        # Confidence thresholds for different scenarios
        self.high_confidence_threshold = 0.95
        self.medium_confidence_threshold = 0.80
        self.polar_latitude_threshold = 66.5  # Arctic/Antarctic circles
        self.twilight_threshold_degrees = 6.0  # Civil twilight
    
    def determine_sect(
        self, 
        analysis_data: SectAnalysisData,
        primary_method: str = SectCalculationMethod.HOUSE_POSITION,
        validate_with_alternatives: bool = True
    ) -> SectDetermination:
        """
        Determine chart sect using specified method with optional validation.
        
        Args:
            analysis_data: Complete data for sect analysis
            primary_method: Primary calculation method to use
            validate_with_alternatives: Cross-validate with other methods
            
        Returns:
            SectDetermination with confidence scoring and metadata
        """
        # Primary calculation
        primary_result = self._calculate_by_method(analysis_data, primary_method)
        
        # Initialize result
        sect_determination = SectDetermination(
            is_day_chart=primary_result["is_day"],
            primary_method=primary_method,
            confidence=primary_result["confidence"],
            sun_house=analysis_data.sun_house,
            ascendant_degrees=analysis_data.ascendant_longitude
        )
        
        # Add supporting data based on primary method
        if primary_method == SectCalculationMethod.HOUSE_POSITION:
            sun_house = primary_result.get("sun_house")
            sect_determination.sun_house = sun_house
            # Derive sun_above_horizon from house position
            if sun_house is not None:
                sect_determination.sun_above_horizon = sun_house >= 7 and sun_house <= 12
        elif primary_method == SectCalculationMethod.HORIZON_CALCULATION:
            sect_determination.sun_above_horizon = primary_result.get("above_horizon")
        
        # Cross-validate with alternative methods if requested
        if validate_with_alternatives:
            alternative_results = {}
            
            method_names = {
                SectCalculationMethod.HOUSE_POSITION: "house_position_method",
                SectCalculationMethod.HORIZON_CALCULATION: "horizon_calculation_method", 
                SectCalculationMethod.ASCENDANT_DEGREES: "ascendant_degrees_method"
            }
            
            for method in [SectCalculationMethod.HOUSE_POSITION, 
                          SectCalculationMethod.HORIZON_CALCULATION,
                          SectCalculationMethod.ASCENDANT_DEGREES]:
                if method != primary_method:
                    try:
                        alt_result = self._calculate_by_method(analysis_data, method)
                        method_name = method_names.get(method, str(method))
                        alternative_results[method_name] = alt_result["is_day"]
                    except Exception:
                        # Alternative method failed - not critical
                        pass
            
            sect_determination.alternative_methods = alternative_results
            
            # Adjust confidence based on agreement between methods
            sect_determination.confidence = self._calculate_consensus_confidence(
                primary_result, alternative_results
            )
        
        # Check for special conditions
        sect_determination.is_polar_birth = self._is_polar_birth(analysis_data)
        sect_determination.is_twilight_birth = self._is_twilight_birth(analysis_data)
        
        return sect_determination
    
    def _calculate_by_method(
        self, 
        analysis_data: SectAnalysisData, 
        method: str
    ) -> Dict[str, Any]:
        """
        Calculate sect using specific method.
        
        Args:
            analysis_data: Input data for calculation
            method: Calculation method to use
            
        Returns:
            Dictionary with is_day, confidence, and method-specific data
        """
        if method == SectCalculationMethod.HOUSE_POSITION:
            return self._calculate_by_house_position(analysis_data)
        elif method == SectCalculationMethod.HORIZON_CALCULATION:
            return self._calculate_by_horizon(analysis_data)
        elif method == SectCalculationMethod.ASCENDANT_DEGREES:
            return self._calculate_by_ascendant_degrees(analysis_data)
        else:
            raise ValueError(f"Unknown sect calculation method: {method}")
    
    def _calculate_by_house_position(self, analysis_data: SectAnalysisData) -> Dict[str, Any]:
        """
        Calculate sect using traditional house position method.
        
        Sun in houses 7-12 = day chart
        Sun in houses 1-6 = night chart
        
        This is the most traditional and reliable method when house data is available.
        """
        if analysis_data.sun_house is None:
            # Try to calculate house from cusps if available
            if analysis_data.house_cusps and len(analysis_data.house_cusps) >= 12:
                sun_house = self._calculate_sun_house_from_cusps(
                    analysis_data.sun_longitude, 
                    analysis_data.house_cusps
                )
            else:
                raise ValueError("No house position data available for sect calculation")
        else:
            sun_house = analysis_data.sun_house
        
        # Traditional house-based determination
        is_day_chart = sun_house >= 7  # Houses 7-12 = day, 1-6 = night
        
        # High confidence for house-based method when house data is reliable
        confidence = 0.95 if sun_house in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] else 0.80
        
        return {
            "is_day": is_day_chart,
            "confidence": confidence,
            "sun_house": sun_house,
            "method_data": {
                "house_position": sun_house,
                "day_houses": list(range(7, 13)),
                "night_houses": list(range(1, 7))
            }
        }
    
    def _calculate_by_horizon(self, analysis_data: SectAnalysisData) -> Dict[str, Any]:
        """
        Calculate sect using mathematical horizon method.
        
        Sun above mathematical horizon = day chart
        Sun below mathematical horizon = night chart
        
        Requires geographic coordinates and precise time.
        """
        if not all([analysis_data.birth_latitude, analysis_data.birth_longitude, 
                   analysis_data.birth_datetime]):
            raise ValueError("Geographic coordinates and time required for horizon calculation")
        
        # Calculate Sun's altitude above horizon
        sun_altitude = self._calculate_solar_altitude(
            analysis_data.sun_longitude,
            analysis_data.sun_latitude,
            analysis_data.birth_latitude,
            analysis_data.birth_longitude,
            analysis_data.birth_datetime
        )
        
        is_day_chart = sun_altitude > 0.0
        
        # Calculate confidence based on how far Sun is from horizon
        altitude_abs = abs(sun_altitude)
        if altitude_abs > 18.0:  # Well above/below horizon
            confidence = 0.98
        elif altitude_abs > 6.0:   # Clearly above/below (civil twilight)
            confidence = 0.90
        elif altitude_abs > 1.0:   # Somewhat above/below
            confidence = 0.75
        else:  # Very close to horizon
            confidence = 0.60
        
        return {
            "is_day": is_day_chart,
            "confidence": confidence,
            "above_horizon": is_day_chart,
            "method_data": {
                "solar_altitude": sun_altitude,
                "altitude_abs": altitude_abs,
                "horizon_threshold": 0.0
            }
        }
    
    def _calculate_by_ascendant_degrees(self, analysis_data: SectAnalysisData) -> Dict[str, Any]:
        """
        Calculate sect using Ascendant degrees method.
        
        Ascendant 0-180° = day chart (Sun in upper hemisphere)  
        Ascendant 180-360° = night chart (Sun in lower hemisphere)
        
        Less reliable than house position method, used as fallback.
        """
        ascendant = normalize_longitude(analysis_data.ascendant_longitude)
        
        is_day_chart = ascendant <= 180.0
        
        # Lower confidence for this method as it's less precise
        # Higher confidence when ascendant is well away from 0/180 boundaries
        distance_from_boundaries = min(
            abs(ascendant - 0.0),
            abs(ascendant - 180.0),
            abs(ascendant - 360.0) if ascendant > 300 else 180.0
        )
        
        if distance_from_boundaries > 45.0:
            confidence = 0.75
        elif distance_from_boundaries > 15.0:
            confidence = 0.65
        else:
            confidence = 0.50  # Low confidence near boundaries
        
        return {
            "is_day": is_day_chart,
            "confidence": confidence,
            "method_data": {
                "ascendant_degrees": ascendant,
                "distance_from_boundary": distance_from_boundaries,
                "boundary_threshold": 180.0
            }
        }
    
    def _calculate_sun_house_from_cusps(self, sun_longitude: float, house_cusps: List[float]) -> int:
        """
        Calculate which house the Sun is in based on house cusps.
        
        Args:
            sun_longitude: Sun's ecliptic longitude
            house_cusps: List of 12 house cusp longitudes
            
        Returns:
            House number (1-12)
        """
        sun_long = normalize_longitude(sun_longitude)
        
        # Handle house cusps that may wrap around 360°
        for i in range(12):
            current_cusp = normalize_longitude(house_cusps[i])
            next_cusp = normalize_longitude(house_cusps[(i + 1) % 12])
            
            # Check if Sun is in this house
            if next_cusp > current_cusp:
                # Normal case: cusp doesn't cross 0°
                if current_cusp <= sun_long < next_cusp:
                    return i + 1
            else:
                # Cusp crosses 0° boundary
                if sun_long >= current_cusp or sun_long < next_cusp:
                    return i + 1
        
        # Fallback - should not happen with valid data
        return 1
    
    def _calculate_solar_altitude(
        self, 
        sun_longitude: float, 
        sun_latitude: float,
        birth_lat: float, 
        birth_lon: float, 
        birth_time: datetime
    ) -> float:
        """
        Calculate Sun's altitude above the mathematical horizon.
        
        This is a simplified calculation for sect determination.
        For precise altitude, would need full ephemeris calculation.
        
        Args:
            sun_longitude: Sun's ecliptic longitude
            sun_latitude: Sun's ecliptic latitude  
            birth_lat: Birth latitude in degrees
            birth_lon: Birth longitude in degrees
            birth_time: Birth datetime
            
        Returns:
            Solar altitude in degrees (positive = above horizon)
        """
        # Convert to radians
        sun_lat_rad = math.radians(sun_latitude)
        birth_lat_rad = math.radians(birth_lat)
        
        # Approximate declination from ecliptic latitude and longitude
        # This is simplified - full calculation would use obliquity of ecliptic
        obliquity = math.radians(23.44)  # Mean obliquity
        sun_lon_rad = math.radians(sun_longitude)
        
        declination = math.asin(
            math.sin(obliquity) * math.sin(sun_lon_rad) + 
            math.cos(obliquity) * math.sin(sun_lat_rad)
        )
        
        # Calculate hour angle (simplified - assumes local solar time ≈ birth time)
        # For precise calculation would need local sidereal time
        hour_angle_approx = 0.0  # Simplified assumption
        
        # Calculate altitude using spherical trigonometry
        altitude_rad = math.asin(
            math.sin(birth_lat_rad) * math.sin(declination) +
            math.cos(birth_lat_rad) * math.cos(declination) * math.cos(hour_angle_approx)
        )
        
        return math.degrees(altitude_rad)
    
    def _calculate_consensus_confidence(
        self, 
        primary_result: Dict[str, Any], 
        alternative_results: Dict[str, bool]
    ) -> float:
        """
        Calculate confidence based on agreement between calculation methods.
        
        Args:
            primary_result: Result from primary method
            alternative_results: Results from alternative methods
            
        Returns:
            Adjusted confidence score (0.0-1.0)
        """
        if not alternative_results:
            return primary_result["confidence"]
        
        primary_is_day = primary_result["is_day"]
        base_confidence = primary_result["confidence"]
        
        # Count agreements and disagreements
        agreements = sum(1 for is_day in alternative_results.values() if is_day == primary_is_day)
        total_alternatives = len(alternative_results)
        
        agreement_ratio = agreements / total_alternatives if total_alternatives > 0 else 1.0
        
        # Adjust confidence based on consensus
        if agreement_ratio >= 1.0:  # All methods agree
            return min(base_confidence + 0.05, 0.99)  # Slight boost
        elif agreement_ratio >= 0.67:  # Majority agree
            return base_confidence
        elif agreement_ratio >= 0.33:  # Mixed results
            return max(base_confidence - 0.15, 0.50)
        else:  # Most methods disagree
            return max(base_confidence - 0.30, 0.30)
    
    def _is_polar_birth(self, analysis_data: SectAnalysisData) -> bool:
        """
        Check if birth occurred in polar regions where traditional sect rules may not apply.
        
        Args:
            analysis_data: Birth data to analyze
            
        Returns:
            True if birth is in polar region (beyond Arctic/Antarctic circles)
        """
        if analysis_data.birth_latitude is None:
            return False
        
        return abs(analysis_data.birth_latitude) > self.polar_latitude_threshold
    
    def _is_twilight_birth(self, analysis_data: SectAnalysisData) -> bool:
        """
        Check if birth occurred during twilight (Sun very close to horizon).
        
        Args:
            analysis_data: Birth data to analyze
            
        Returns:
            True if birth occurred during twilight period
        """
        if not all([analysis_data.birth_latitude, analysis_data.birth_longitude, 
                   analysis_data.birth_datetime]):
            return False
        
        try:
            sun_altitude = self._calculate_solar_altitude(
                analysis_data.sun_longitude,
                analysis_data.sun_latitude,
                analysis_data.birth_latitude,
                analysis_data.birth_longitude,
                analysis_data.birth_datetime
            )
            
            # Check if Sun is within twilight range
            return abs(sun_altitude) <= self.twilight_threshold_degrees
            
        except Exception:
            return False
    
    def create_analysis_data_from_chart(
        self,
        sun_position: PlanetPosition,
        houses: HouseSystem,
        birth_latitude: Optional[float] = None,
        birth_longitude: Optional[float] = None,
        birth_datetime: Optional[datetime] = None
    ) -> SectAnalysisData:
        """
        Create SectAnalysisData from standard chart calculation results.
        
        Args:
            sun_position: Sun's calculated position
            houses: House system calculation results
            birth_latitude: Geographic latitude of birth
            birth_longitude: Geographic longitude of birth
            birth_datetime: Birth date/time
            
        Returns:
            SectAnalysisData ready for sect calculation
        """
        # Calculate Sun's house position
        sun_house = None
        if houses.house_cusps and len(houses.house_cusps) >= 12:
            sun_house = self._calculate_sun_house_from_cusps(
                sun_position.longitude, 
                houses.house_cusps
            )
        
        return SectAnalysisData(
            sun_longitude=sun_position.longitude,
            sun_latitude=sun_position.latitude,
            ascendant_longitude=houses.ascendant,
            midheaven_longitude=houses.midheaven,
            house_cusps=houses.house_cusps,
            sun_house=sun_house,
            birth_latitude=birth_latitude,
            birth_longitude=birth_longitude,
            birth_datetime=birth_datetime
        )
    
    def get_sect_explanation(self, sect_determination: SectDetermination) -> str:
        """
        Get human-readable explanation of sect determination.
        
        Args:
            sect_determination: Sect calculation result
            
        Returns:
            Detailed explanation string
        """
        sect_type = "day" if sect_determination.is_day_chart else "night"
        confidence_pct = sect_determination.confidence * 100
        
        explanation = f"This is a {sect_type} chart (confidence: {confidence_pct:.1f}%). "
        
        if sect_determination.primary_method == SectCalculationMethod.HOUSE_POSITION:
            if sect_determination.sun_house:
                explanation += f"Sun is in house {sect_determination.sun_house}. "
                if sect_determination.sun_house >= 7:
                    explanation += "Houses 7-12 indicate a day chart."
                else:
                    explanation += "Houses 1-6 indicate a night chart."
        
        elif sect_determination.primary_method == SectCalculationMethod.HORIZON_CALCULATION:
            if sect_determination.sun_above_horizon is not None:
                if sect_determination.sun_above_horizon:
                    explanation += "Sun is above the mathematical horizon."
                else:
                    explanation += "Sun is below the mathematical horizon."
        
        elif sect_determination.primary_method == SectCalculationMethod.ASCENDANT_DEGREES:
            if sect_determination.ascendant_degrees is not None:
                asc_deg = sect_determination.ascendant_degrees
                explanation += f"Ascendant at {asc_deg:.1f}°. "
                if asc_deg <= 180:
                    explanation += "0-180° indicates a day chart."
                else:
                    explanation += "180-360° indicates a night chart."
        
        # Add special conditions
        if sect_determination.is_polar_birth:
            explanation += " Note: Polar birth - traditional sect rules may not fully apply."
        
        if sect_determination.is_twilight_birth:
            explanation += " Note: Twilight birth - Sun is very close to horizon."
        
        # Add alternative method validation if available
        if sect_determination.alternative_methods:
            agreements = sum(1 for is_day in sect_determination.alternative_methods.values() 
                           if is_day == sect_determination.is_day_chart)
            total = len(sect_determination.alternative_methods)
            
            explanation += f" Alternative methods: {agreements}/{total} agree."
        
        return explanation


# Convenience functions for common operations
def determine_chart_sect(
    sun_position: PlanetPosition,
    houses: HouseSystem,
    birth_latitude: Optional[float] = None,
    birth_longitude: Optional[float] = None,
    birth_datetime: Optional[datetime] = None,
    method: str = SectCalculationMethod.HOUSE_POSITION
) -> SectDetermination:
    """
    Convenience function to determine chart sect from standard chart data.
    
    Args:
        sun_position: Sun's calculated position
        houses: House system results
        birth_latitude: Geographic latitude (optional)
        birth_longitude: Geographic longitude (optional)  
        birth_datetime: Birth datetime (optional)
        method: Calculation method to use
        
    Returns:
        SectDetermination result
    """
    calculator = SectCalculator()
    
    analysis_data = calculator.create_analysis_data_from_chart(
        sun_position=sun_position,
        houses=houses,
        birth_latitude=birth_latitude,
        birth_longitude=birth_longitude,
        birth_datetime=birth_datetime
    )
    
    return calculator.determine_sect(analysis_data, method)


def is_day_chart_simple(sun_house: int) -> bool:
    """
    Simple day/night determination from Sun's house position.
    
    Args:
        sun_house: House number where Sun is located (1-12)
        
    Returns:
        True for day chart, False for night chart
    """
    return sun_house >= 7 if 1 <= sun_house <= 12 else True