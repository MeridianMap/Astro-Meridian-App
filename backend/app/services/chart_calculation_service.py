"""
Chart Calculation Service

Focused service for chart calculation orchestration.
Replaces ephemeris_service.py lines 562-603 chart calculation logic.

This service coordinates all calculation components to produce comprehensive
chart data while maintaining clear separation of concerns.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

from ..core.ephemeris.adapters.swiss_ephemeris_adapter import swiss_adapter
from ..core.ephemeris.models.planet_data import PlanetData, create_planet_data_from_swiss_ephemeris
from ..core.ephemeris.const import MODERN_PLANETS, MAJOR_ASTEROIDS, LUNAR_NODES, LILITH_POINTS
from ..api.models.schemas import NatalChartRequest

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class ChartCalculationService:
    """
    Focused service for chart calculation orchestration.
    
    Single responsibility: coordinate all calculations to produce comprehensive chart data.
    Does NOT handle:
    - Input validation (handled by Pydantic models)
    - Response formatting (handled by separate formatters)  
    - Caching (handled by separate cache layer)
    - API concerns (handled by route handlers)
    """
    
    def __init__(self):
        """Initialize calculation service with adapter."""
        self.swiss_adapter = swiss_adapter
        
    def calculate_comprehensive_chart(self, request: NatalChartRequest, 
                                    include_asteroids: bool = True,
                                    include_nodes: bool = True,
                                    include_lilith: bool = True,
                                    include_fixed_stars: bool = False,
                                    fixed_star_magnitude_limit: float = 2.0) -> Dict[str, Any]:
        """
        Calculate complete chart with all features.
        
        Args:
            request: Validated natal chart request
            include_asteroids: Include major asteroids
            include_nodes: Include lunar nodes
            include_lilith: Include Lilith points
            include_fixed_stars: Include fixed stars
            fixed_star_magnitude_limit: Maximum magnitude for fixed stars
            
        Returns:
            Complete chart data dictionary
            
        Raises:
            RuntimeError: If critical calculations fail
        """
        calculation_start = datetime.now()
        
        try:
            # Convert request to calculation parameters
            jd = self._to_julian_day(request.subject.datetime.iso_string)
            lat = float(request.subject.latitude.decimal)
            lon = float(request.subject.longitude.decimal)
            
            # Calculate core components
            logger.info(f"Starting chart calculation for JD {jd}")
            
            planets = self._calculate_all_planets(jd, include_asteroids, include_nodes, include_lilith)
            houses = self._calculate_houses(jd, lat, lon, request.configuration.house_system)
            angles = self._extract_angles(houses)
            
            # Add house positions to planets
            self._assign_house_positions(planets, houses)
            
            # Build result
            result = {
                'planets': {p.name: p for p in planets},
                'houses': houses,
                'angles': angles,
                'calculation_metadata': {
                    'julian_day': jd,
                    'calculation_time': calculation_start,
                    'total_objects_calculated': len(planets),
                    'house_system': request.configuration.house_system
                }
            }
            
            # Add optional features
            if include_fixed_stars:
                result['fixed_stars'] = self._calculate_fixed_stars(jd, fixed_star_magnitude_limit)
            
            logger.info(f"Chart calculation completed: {len(planets)} objects")
            return result
            
        except Exception as e:
            logger.error(f"Chart calculation failed: {e}")
            raise RuntimeError(f"Chart calculation failed: {e}")
    
    def _calculate_all_planets(self, julian_day: float, include_asteroids: bool,
                             include_nodes: bool, include_lilith: bool) -> List[PlanetData]:
        """
        Calculate positions for all requested celestial objects.
        
        Args:
            julian_day: Julian Day for calculation
            include_asteroids: Include major asteroids
            include_nodes: Include lunar nodes
            include_lilith: Include Lilith points
            
        Returns:
            List of PlanetData objects
        """
        planets = []
        calculation_time = datetime.now()
        
        # Traditional planets (always included)
        for planet_id in MODERN_PLANETS:
            try:
                name = self.swiss_adapter.get_planet_name(planet_id)
                position_data, flags = self.swiss_adapter.calculate_position(planet_id, julian_day)
                
                planet = create_planet_data_from_swiss_ephemeris(
                    planet_id, name, position_data, calculation_time, flags
                )
                planets.append(planet)
                
            except Exception as e:
                logger.error(f"Failed to calculate planet {planet_id}: {e}")
                continue
        
        # Major asteroids (optional)
        if include_asteroids:
            for asteroid_id in MAJOR_ASTEROIDS:
                try:
                    name = self.swiss_adapter.get_planet_name(asteroid_id)
                    position_data, flags = self.swiss_adapter.calculate_position(asteroid_id, julian_day)
                    
                    planet = create_planet_data_from_swiss_ephemeris(
                        asteroid_id, name, position_data, calculation_time, flags
                    )
                    planets.append(planet)
                    
                except Exception as e:
                    logger.warning(f"Failed to calculate asteroid {asteroid_id}: {e}")
                    continue
        
        # Lunar nodes (optional)  
        if include_nodes:
            for node_id in LUNAR_NODES:
                try:
                    name = self.swiss_adapter.get_planet_name(node_id)
                    if 'True' in name:
                        name = name.replace('(', '').replace(')', '')  # Clean up naming
                    
                    position_data, flags = self.swiss_adapter.calculate_position(node_id, julian_day)
                    
                    planet = create_planet_data_from_swiss_ephemeris(
                        node_id, name, position_data, calculation_time, flags
                    )
                    planets.append(planet)
                    
                except Exception as e:
                    logger.warning(f"Failed to calculate node {node_id}: {e}")
                    continue
        
        # Lilith points (optional)
        if include_lilith:
            for lilith_id in LILITH_POINTS:
                try:
                    name = self.swiss_adapter.get_planet_name(lilith_id)
                    if 'mean' in name.lower():
                        name = "Lilith (Mean)"
                    elif 'osculating' in name.lower() or 'true' in name.lower():
                        name = "Lilith (True)"
                    
                    position_data, flags = self.swiss_adapter.calculate_position(lilith_id, julian_day)
                    
                    planet = create_planet_data_from_swiss_ephemeris(
                        lilith_id, name, position_data, calculation_time, flags
                    )
                    planets.append(planet)
                    
                except Exception as e:
                    logger.warning(f"Failed to calculate Lilith {lilith_id}: {e}")
                    continue
        
        return planets
    
    def _calculate_houses(self, julian_day: float, latitude: float, longitude: float,
                         house_system: str = 'P') -> Dict[str, Any]:
        """
        Calculate house cusps and related data.
        
        Args:
            julian_day: Julian Day for calculation
            latitude: Observer latitude
            longitude: Observer longitude  
            house_system: House system code
            
        Returns:
            Dictionary with house data
        """
        try:
            house_cusps, ascmc = self.swiss_adapter.calculate_houses(
                julian_day, latitude, longitude, house_system
            )
            
            # Convert to standard format
            houses_dict = {}
            for i, cusp in enumerate(house_cusps):
                houses_dict[f'house_{i+1}'] = cusp
            
            # Add angles from ASCMC array
            houses_dict.update({
                'ascendant': ascmc[0],
                'midheaven': ascmc[1], 
                'armc': ascmc[2],
                'vertex': ascmc[3],
                'descendant': (ascmc[0] + 180) % 360,
                'imum_coeli': (ascmc[1] + 180) % 360
            })
            
            return {
                'house_cusps': house_cusps,
                'system': house_system,
                'houses': houses_dict
            }
            
        except Exception as e:
            logger.error(f"House calculation failed: {e}")
            raise RuntimeError(f"House calculation failed: {e}")
    
    def _extract_angles(self, houses: Dict[str, Any]) -> Dict[str, float]:
        """Extract chart angles from house calculation."""
        return {
            'ASC': houses['houses']['ascendant'],
            'MC': houses['houses']['midheaven'],
            'DSC': houses['houses']['descendant'], 
            'IC': houses['houses']['imum_coeli'],
            'ARMC': houses['houses']['armc'],
            'Vertex': houses['houses']['vertex']
        }
    
    def _assign_house_positions(self, planets: List[PlanetData], houses: Dict[str, Any]) -> None:
        """
        Assign house positions to planets based on longitude.
        
        Modifies planets in-place by setting house_number attribute.
        """
        house_cusps = houses['house_cusps']
        
        for planet in planets:
            planet.house_number = self._find_house_for_longitude(planet.longitude, house_cusps)
    
    def _find_house_for_longitude(self, longitude: float, house_cusps: List[float]) -> int:
        """
        Find which house contains the given longitude.
        
        Args:
            longitude: Planet longitude (0-360)
            house_cusps: List of 12 house cusps
            
        Returns:
            House number (1-12)
        """
        # Normalize longitude
        while longitude < 0:
            longitude += 360
        while longitude >= 360:
            longitude -= 360
        
        # Check each house (cusps are already in 0-360 range)
        for i in range(12):
            cusp_start = house_cusps[i]
            cusp_end = house_cusps[(i + 1) % 12]
            
            # Handle wrap-around at 0/360 degrees
            if cusp_start <= cusp_end:
                if cusp_start <= longitude < cusp_end:
                    return i + 1
            else:  # Wrap around 0 degrees
                if longitude >= cusp_start or longitude < cusp_end:
                    return i + 1
        
        return 1  # Default to first house if calculation fails
    
    def _calculate_fixed_stars(self, julian_day: float, magnitude_limit: float) -> Dict[str, Any]:
        """
        Calculate fixed star positions (placeholder for future implementation).
        
        Args:
            julian_day: Julian Day for calculation
            magnitude_limit: Maximum magnitude to include
            
        Returns:
            Dictionary with fixed star data
        """
        # TODO: Implement fixed star calculations
        return {
            'stars': {},
            'magnitude_limit': magnitude_limit,
            'count': 0,
            'note': 'Fixed star calculation not yet implemented'
        }
    
    def _to_julian_day(self, iso_string: str) -> float:
        """
        Convert ISO datetime string to Julian Day.
        
        Args:
            iso_string: ISO format datetime string
            
        Returns:
            Julian Day as float
        """
        try:
            # Parse ISO string to datetime components
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            
            year = dt.year
            month = dt.month
            day = dt.day
            hour = dt.hour + dt.minute/60 + dt.second/3600 + dt.microsecond/3600000000
            
            return self.swiss_adapter.calculate_julian_day(year, month, day, hour)
            
        except Exception as e:
            logger.error(f"Julian day conversion failed for '{iso_string}': {e}")
            raise ValueError(f"Invalid datetime format: {iso_string}")


# Global service instance
chart_calculation_service = ChartCalculationService()