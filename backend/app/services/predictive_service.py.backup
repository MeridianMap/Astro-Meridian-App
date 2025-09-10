"""
Predictive Astrology Service

High-level service layer for eclipse and transit predictions with NASA-validated accuracy.
Orchestrates the predictive calculation engines and provides unified interface for API endpoints.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..core.ephemeris.tools.eclipse_calculator import EclipseCalculator, EclipseCalculationError
from ..core.ephemeris.tools.transit_calculator import TransitCalculator, TransitCalculationError
from ..core.ephemeris.tools.predictive_search import EclipseSearchAlgorithms, TransitSearchAlgorithms
from ..core.ephemeris.tools.predictive_optimization import predictive_optimizer, PredictiveOptimizer
from ..core.ephemeris.tools.predictive_models import (
    SolarEclipse, LunarEclipse, Transit, SignIngress, EclipseVisibility, 
    GeographicLocation, PlanetaryStation
)
from ..api.models.predictive_schemas import LocationInput
from ..core.monitoring.metrics import get_metrics, timed_calculation
import swisseph as swe

logger = logging.getLogger(__name__)

class PredictiveServiceError(Exception):
    """Base exception for predictive service errors"""
    pass

class InvalidInputError(PredictiveServiceError):
    """Raised when input validation fails"""
    pass

class PredictiveService:
    """
    Main service class for predictive astrology calculations.
    
    Provides unified interface for eclipse predictions, transit calculations,
    and sign ingresses with performance optimization and error handling.
    """
    
    def __init__(self):
        """Initialize predictive service with calculation engines."""
        self.eclipse_calculator = EclipseCalculator()
        self.transit_calculator = TransitCalculator()
        self.eclipse_search = EclipseSearchAlgorithms()
        self.transit_search = TransitSearchAlgorithms()
        
        # Performance optimization system
        self.optimizer = predictive_optimizer
        
        # Thread pool for parallel calculations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Planet ID mapping
        self.PLANET_IDS = {
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
        
        logger.info("PredictiveService initialized successfully with performance optimizations")
    
    # Eclipse Methods
    
    @timed_calculation("service_solar_eclipse_search")
    async def find_next_solar_eclipse(
        self,
        start_date: datetime,
        eclipse_type: Optional[str] = None,
        location: Optional[LocationInput] = None
    ) -> Optional[SolarEclipse]:
        """
        Find the next solar eclipse from the given date.
        
        Args:
            start_date: Starting date for eclipse search
            eclipse_type: Optional eclipse type filter
            location: Optional location for visibility filtering
            
        Returns:
            SolarEclipse object or None if not found
            
        Raises:
            PredictiveServiceError: If calculation fails
        """
        try:
            # Convert location input if provided
            geo_location = None
            if location:
                geo_location = await self._convert_location_input(location)
            
            # Run eclipse search in executor to avoid blocking
            loop = asyncio.get_event_loop()
            eclipse = await loop.run_in_executor(
                self.executor,
                self.eclipse_calculator.find_next_solar_eclipse,
                start_date,
                eclipse_type,
                geo_location
            )
            
            if eclipse and location:
                # Add visibility information if location provided
                visibility = await self._calculate_eclipse_visibility(eclipse, geo_location)
                eclipse.metadata["visibility"] = visibility.dict()
            
            return eclipse
            
        except EclipseCalculationError as e:
            logger.error(f"Solar eclipse calculation failed: {e}")
            raise PredictiveServiceError(f"Solar eclipse search failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in solar eclipse search: {e}")
            raise PredictiveServiceError(f"Solar eclipse service error: {e}")
    
    @timed_calculation("service_lunar_eclipse_search")
    async def find_next_lunar_eclipse(
        self,
        start_date: datetime,
        eclipse_type: Optional[str] = None
    ) -> Optional[LunarEclipse]:
        """
        Find the next lunar eclipse from the given date.
        
        Args:
            start_date: Starting date for eclipse search
            eclipse_type: Optional eclipse type filter
            
        Returns:
            LunarEclipse object or None if not found
        """
        try:
            loop = asyncio.get_event_loop()
            eclipse = await loop.run_in_executor(
                self.executor,
                self.eclipse_calculator.find_next_lunar_eclipse,
                start_date,
                eclipse_type
            )
            
            return eclipse
            
        except EclipseCalculationError as e:
            logger.error(f"Lunar eclipse calculation failed: {e}")
            raise PredictiveServiceError(f"Lunar eclipse search failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in lunar eclipse search: {e}")
            raise PredictiveServiceError(f"Lunar eclipse service error: {e}")
    
    @timed_calculation("service_eclipse_range_search")
    async def search_eclipses_in_range(
        self,
        start_date: datetime,
        end_date: datetime,
        eclipse_types: Optional[List[str]] = None,
        location: Optional[LocationInput] = None
    ) -> Dict[str, List[Union[SolarEclipse, LunarEclipse]]]:
        """
        Search for eclipses within a date range.
        
        Args:
            start_date: Start of search range
            end_date: End of search range
            eclipse_types: Optional list of eclipse types to include
            location: Optional location for visibility filtering
            
        Returns:
            Dictionary with "solar" and "lunar" eclipse lists
        """
        try:
            # Convert location if provided
            geo_location = None
            if location:
                geo_location = await self._convert_location_input(location)
            
            # Run range search in executor
            loop = asyncio.get_event_loop()
            eclipses = await loop.run_in_executor(
                self.executor,
                self.eclipse_calculator.find_eclipses_in_range,
                start_date,
                end_date,
                eclipse_types,
                geo_location
            )
            
            return eclipses
            
        except Exception as e:
            logger.error(f"Eclipse range search failed: {e}")
            raise PredictiveServiceError(f"Eclipse range search failed: {e}")
    
    @timed_calculation("service_eclipse_visibility")
    async def calculate_eclipse_visibility(
        self,
        eclipse_time: datetime,
        eclipse_type: str,
        location: LocationInput
    ) -> EclipseVisibility:
        """
        Calculate eclipse visibility for a specific location.
        
        Args:
            eclipse_time: Eclipse maximum time
            eclipse_type: Eclipse type ('solar' or 'lunar')
            location: Observer location
            
        Returns:
            EclipseVisibility object
        """
        try:
            geo_location = await self._convert_location_input(location)
            
            # Create a mock eclipse object for visibility calculation
            if eclipse_type.lower() == 'solar':
                eclipse = SolarEclipse(
                    eclipse_type="total",  # Simplified for visibility calc
                    maximum_eclipse_time=eclipse_time,
                    eclipse_magnitude=1.0,
                    eclipse_obscuration=100.0
                )
            else:
                eclipse = LunarEclipse(
                    eclipse_type="total",
                    maximum_eclipse_time=eclipse_time,
                    eclipse_magnitude=1.0,
                    penumbral_magnitude=1.2
                )
            
            loop = asyncio.get_event_loop()
            visibility = await loop.run_in_executor(
                self.executor,
                self.eclipse_calculator.get_eclipse_visibility,
                eclipse,
                geo_location
            )
            
            return visibility
            
        except Exception as e:
            logger.error(f"Eclipse visibility calculation failed: {e}")
            raise PredictiveServiceError(f"Eclipse visibility calculation failed: {e}")
    
    # Transit Methods
    
    @timed_calculation("service_planet_transit")
    async def find_planet_transit(
        self,
        planet_name: str,
        target_degree: float,
        start_date: datetime,
        max_crossings: int = 1
    ) -> List[Transit]:
        """
        Find when a planet transits to a specific degree.
        
        Args:
            planet_name: Name of the planet
            target_degree: Target longitude in degrees
            start_date: Starting date for search
            max_crossings: Maximum crossings to find
            
        Returns:
            List of Transit objects
        """
        try:
            # Convert planet name to ID
            planet_id = self.PLANET_IDS.get(planet_name)
            if planet_id is None:
                raise InvalidInputError(f"Invalid planet name: {planet_name}")
            
            loop = asyncio.get_event_loop()
            transits = await loop.run_in_executor(
                self.executor,
                self.transit_calculator.find_next_transit,
                planet_id,
                target_degree,
                start_date,
                max_crossings
            )
            
            return transits
            
        except TransitCalculationError as e:
            logger.error(f"Planet transit calculation failed: {e}")
            raise PredictiveServiceError(f"Planet transit search failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in planet transit search: {e}")
            raise PredictiveServiceError(f"Planet transit service error: {e}")
    
    @timed_calculation("service_sign_ingresses")
    async def find_sign_ingresses(
        self,
        planet_names: Optional[List[str]] = None,
        start_date: datetime = None,
        end_date: Optional[datetime] = None,
        target_sign: Optional[str] = None
    ) -> Dict[str, List[SignIngress]]:
        """
        Find planetary sign ingresses.
        
        Args:
            planet_names: List of planet names (None for all)
            start_date: Search start date
            end_date: Search end date
            target_sign: Specific sign to search for
            
        Returns:
            Dictionary mapping planet names to ingress lists
        """
        try:
            if start_date is None:
                start_date = datetime.now()
            
            if end_date is None:
                end_date = start_date.replace(year=start_date.year + 1)
            
            # Convert planet names to IDs
            if planet_names is None:
                planet_ids = list(self.PLANET_IDS.values())
                planet_names = list(self.PLANET_IDS.keys())
            else:
                planet_ids = []
                for name in planet_names:
                    planet_id = self.PLANET_IDS.get(name)
                    if planet_id is None:
                        raise InvalidInputError(f"Invalid planet name: {name}")
                    planet_ids.append(planet_id)
            
            loop = asyncio.get_event_loop()
            
            # Use batch processing for multiple planets
            all_ingresses = await loop.run_in_executor(
                self.executor,
                self.transit_calculator.find_all_ingresses_in_range,
                start_date,
                end_date,
                planet_ids
            )
            
            return all_ingresses
            
        except Exception as e:
            logger.error(f"Sign ingress calculation failed: {e}")
            raise PredictiveServiceError(f"Sign ingress search failed: {e}")
    
    @timed_calculation("service_transit_search")
    async def search_transits(
        self,
        start_date: datetime,
        end_date: datetime,
        planet_names: Optional[List[str]] = None,
        target_degrees: Optional[List[float]] = None,
        search_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        General transit search with flexible criteria.
        
        Args:
            start_date: Search start date
            end_date: Search end date
            planet_names: Planets to include
            target_degrees: Specific degrees to search for
            search_criteria: Additional search parameters
            
        Returns:
            Dictionary with search results
        """
        try:
            results = {
                "transits": [],
                "ingresses": [],
                "stations": []
            }
            
            # Default to all planets if none specified
            if planet_names is None:
                planet_names = list(self.PLANET_IDS.keys())
            
            # Default to cardinal points if no degrees specified
            if target_degrees is None:
                target_degrees = [0.0, 90.0, 180.0, 270.0]  # Aries, Cancer, Libra, Capricorn points
            
            # Search for transits to specific degrees
            if target_degrees:
                transit_results = []
                for planet_name in planet_names:
                    for degree in target_degrees:
                        transits = await self.find_planet_transit(
                            planet_name, degree, start_date, 1
                        )
                        # Filter transits within date range
                        for transit in transits:
                            if start_date <= transit.exact_time <= end_date:
                                transit_results.append(transit)
                
                results["transits"] = sorted(transit_results, key=lambda t: t.exact_time)
            
            # Search for sign ingresses
            ingresses = await self.find_sign_ingresses(
                planet_names, start_date, end_date
            )
            
            # Flatten ingress results
            all_ingresses = []
            for planet_ingresses in ingresses.values():
                all_ingresses.extend(planet_ingresses)
            
            results["ingresses"] = sorted(all_ingresses, key=lambda i: i.ingress_time)
            
            # Add search metadata
            results["metadata"] = {
                "search_range_days": (end_date - start_date).days,
                "planets_searched": planet_names,
                "degrees_searched": target_degrees,
                "total_results": len(results["transits"]) + len(results["ingresses"])
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Transit search failed: {e}")
            raise PredictiveServiceError(f"Transit search failed: {e}")
    
    # Enhanced Ephemeris Integration Methods
    
    async def get_upcoming_eclipses(
        self,
        start_date: datetime,
        count: int = 5
    ) -> List[Union[SolarEclipse, LunarEclipse]]:
        """
        Get upcoming eclipses for enhanced ephemeris response.
        
        Args:
            start_date: Starting date
            count: Number of eclipses to return
            
        Returns:
            List of upcoming eclipses
        """
        try:
            eclipses = []
            current_date = start_date
            
            while len(eclipses) < count:
                # Search for solar eclipse
                solar = await self.find_next_solar_eclipse(current_date)
                
                # Search for lunar eclipse  
                lunar = await self.find_next_lunar_eclipse(current_date)
                
                # Add the earlier eclipse
                next_eclipse = None
                if solar and lunar:
                    next_eclipse = solar if solar.maximum_eclipse_time <= lunar.maximum_eclipse_time else lunar
                elif solar:
                    next_eclipse = solar
                elif lunar:
                    next_eclipse = lunar
                else:
                    break  # No more eclipses found
                
                eclipses.append(next_eclipse)
                current_date = next_eclipse.maximum_eclipse_time + timedelta(days=1)
            
            return eclipses
            
        except Exception as e:
            logger.error(f"Failed to get upcoming eclipses: {e}")
            return []
    
    async def find_planetary_transits_to_points(
        self,
        chart_points: Dict[str, float],
        start_date: datetime,
        end_date: datetime,
        orb_degrees: float = 1.0
    ) -> Dict[str, List[Transit]]:
        """
        Find transits to natal chart points.
        
        Args:
            chart_points: Dictionary of chart points (planet/angle names to degrees)
            start_date: Search start date
            end_date: Search end date  
            orb_degrees: Orb for transit detection
            
        Returns:
            Dictionary mapping chart points to transiting planets
        """
        try:
            transit_results = {}
            
            for point_name, point_degree in chart_points.items():
                transit_results[point_name] = []
                
                # Search for transits from all planets to this point
                for planet_name in self.PLANET_IDS.keys():
                    transits = await self.find_planet_transit(
                        planet_name, point_degree, start_date, 3  # Allow multiple crossings
                    )
                    
                    # Filter by date range and add to results
                    for transit in transits:
                        if start_date <= transit.exact_time <= end_date:
                            transit_results[point_name].append(transit)
            
            return transit_results
            
        except Exception as e:
            logger.error(f"Failed to find transits to chart points: {e}")
            return {}
    
    async def calculate_solar_return_timing(
        self,
        birth_date: datetime,
        return_year: int
    ) -> Optional[datetime]:
        """
        Calculate exact solar return timing.
        
        Args:
            birth_date: Original birth date
            return_year: Year for solar return
            
        Returns:
            Exact solar return datetime
        """
        try:
            # Get birth sun degree
            birth_jd = swe.julday(
                birth_date.year, birth_date.month, birth_date.day,
                birth_date.hour + birth_date.minute/60.0 + birth_date.second/3600.0
            )
            
            birth_sun_pos, _ = swe.calc_ut(birth_jd, swe.SUN, swe.FLG_SWIEPH)
            birth_sun_degree = birth_sun_pos[0]
            
            # Find when Sun returns to this degree in the return year
            search_start = datetime(return_year, birth_date.month, birth_date.day) - timedelta(days=2)
            
            transits = await self.find_planet_transit(
                "Sun", birth_sun_degree, search_start, 1
            )
            
            return transits[0].exact_time if transits else None
            
        except Exception as e:
            logger.error(f"Solar return calculation failed: {e}")
            return None
    
    async def calculate_lunar_return_timing(
        self,
        birth_date: datetime,
        return_date: datetime
    ) -> Optional[datetime]:
        """
        Calculate lunar return timing nearest to specified date.
        
        Args:
            birth_date: Original birth date
            return_date: Approximate return date
            
        Returns:
            Exact lunar return datetime
        """
        try:
            # Get birth moon degree
            birth_jd = swe.julday(
                birth_date.year, birth_date.month, birth_date.day,
                birth_date.hour + birth_date.minute/60.0 + birth_date.second/3600.0
            )
            
            birth_moon_pos, _ = swe.calc_ut(birth_jd, swe.MOON, swe.FLG_SWIEPH)
            birth_moon_degree = birth_moon_pos[0]
            
            # Search within ±15 days of return date
            search_start = return_date - timedelta(days=15)
            
            transits = await self.find_planet_transit(
                "Moon", birth_moon_degree, search_start, 1
            )
            
            return transits[0].exact_time if transits else None
            
        except Exception as e:
            logger.error(f"Lunar return calculation failed: {e}")
            return None
    
    # Utility Methods
    
    async def _convert_location_input(self, location: LocationInput) -> GeographicLocation:
        """Convert LocationInput to GeographicLocation."""
        try:
            # Convert coordinate inputs to decimal degrees
            latitude = await self._convert_coordinate_input(location.latitude)
            longitude = await self._convert_coordinate_input(location.longitude)
            
            return GeographicLocation(
                latitude=latitude,
                longitude=longitude,
                elevation=location.elevation or 0.0,
                timezone=location.timezone.name if location.timezone and hasattr(location.timezone, 'name') else "UTC"
            )
            
        except Exception as e:
            logger.error(f"Location conversion failed: {e}")
            raise InvalidInputError(f"Invalid location format: {e}")
    
    async def _convert_coordinate_input(self, coord_input) -> float:
        """Convert coordinate input to decimal degrees."""
        if coord_input.decimal is not None:
            return float(coord_input.decimal)
        
        if coord_input.dms is not None:
            # Parse DMS string (simplified - would need full DMS parser)
            return self._parse_dms_string(coord_input.dms)
        
        if coord_input.components is not None:
            # Convert components to decimal
            degrees = coord_input.components.get('degrees', 0)
            minutes = coord_input.components.get('minutes', 0)
            seconds = coord_input.components.get('seconds', 0)
            direction = coord_input.components.get('direction', '').upper()
            
            decimal = abs(degrees) + abs(minutes)/60.0 + abs(seconds)/3600.0
            
            if direction in ['S', 'W']:
                decimal = -decimal
            
            return decimal
        
        raise InvalidInputError("No valid coordinate format provided")
    
    def _parse_dms_string(self, dms: str) -> float:
        """Parse DMS string to decimal degrees (simplified implementation)."""
        # This is a simplified parser - production would need more robust parsing
        import re
        
        # Extract numbers and direction
        numbers = re.findall(r'\d+\.?\d*', dms)
        direction = re.findall(r'[NSEW]', dms.upper())
        
        if not numbers:
            raise ValueError("No numeric values found in DMS string")
        
        degrees = float(numbers[0]) if len(numbers) > 0 else 0
        minutes = float(numbers[1]) if len(numbers) > 1 else 0
        seconds = float(numbers[2]) if len(numbers) > 2 else 0
        
        decimal = degrees + minutes/60.0 + seconds/3600.0
        
        if direction and direction[0] in ['S', 'W']:
            decimal = -decimal
        
        return decimal
    
    async def _calculate_eclipse_visibility(
        self, 
        eclipse: Union[SolarEclipse, LunarEclipse], 
        location: GeographicLocation
    ) -> EclipseVisibility:
        """Calculate eclipse visibility for location."""
        try:
            loop = asyncio.get_event_loop()
            visibility = await loop.run_in_executor(
                self.executor,
                self.eclipse_calculator.get_eclipse_visibility,
                eclipse,
                location
            )
            return visibility
            
        except Exception as e:
            logger.warning(f"Eclipse visibility calculation failed: {e}")
            # Return default visibility object
            return EclipseVisibility(
                is_visible=False,
                eclipse_type_at_location="unknown",
                maximum_eclipse_time=eclipse.maximum_eclipse_time,
                eclipse_magnitude_at_location=0.0,
                contact_times={},
                metadata={"error": str(e)}
            )
    
    # Performance Optimized Methods
    
    @timed_calculation("service_optimized_eclipse_search")
    async def search_eclipses_optimized(
        self,
        start_date: datetime,
        end_date: datetime,
        eclipse_types: Optional[List[str]] = None
    ) -> Dict[str, List[Union[SolarEclipse, LunarEclipse]]]:
        """
        Performance-optimized eclipse search using vectorization and caching.
        
        Args:
            start_date: Search start date
            end_date: Search end date
            eclipse_types: Optional eclipse type filter
            
        Returns:
            Dictionary with optimized eclipse results
        """
        try:
            # Use optimizer for high-performance search
            optimized_results = self.optimizer.optimize_eclipse_search(
                start_date, end_date, eclipse_types
            )
            
            # Convert to proper eclipse objects
            solar_eclipses = []
            lunar_eclipses = []
            
            for result in optimized_results:
                if result.get('type') == 'solar':
                    # Convert to SolarEclipse object (simplified)
                    eclipse_time = self._jd_to_datetime(result['julian_day'])
                    solar_eclipse = SolarEclipse(
                        eclipse_type="total",  # Simplified
                        maximum_eclipse_time=eclipse_time,
                        eclipse_magnitude=1.0,
                        eclipse_obscuration=100.0,
                        metadata={'optimized_calculation': True}
                    )
                    solar_eclipses.append(solar_eclipse)
                
                elif result.get('type') == 'lunar':
                    # Convert to LunarEclipse object (simplified)
                    eclipse_time = self._jd_to_datetime(result['julian_day'])
                    lunar_eclipse = LunarEclipse(
                        eclipse_type="total",  # Simplified
                        maximum_eclipse_time=eclipse_time,
                        eclipse_magnitude=1.0,
                        penumbral_magnitude=1.2,
                        metadata={'optimized_calculation': True}
                    )
                    lunar_eclipses.append(lunar_eclipse)
            
            logger.info(f"Optimized eclipse search found {len(solar_eclipses)} solar, {len(lunar_eclipses)} lunar eclipses")
            
            return {
                'solar': solar_eclipses,
                'lunar': lunar_eclipses
            }
            
        except Exception as e:
            logger.error(f"Optimized eclipse search failed: {e}")
            # Fallback to regular method
            return await self.search_eclipses_in_range(start_date, end_date, eclipse_types)
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """
        Get performance optimization status and metrics.
        
        Returns:
            Dictionary with optimization status
        """
        try:
            return self.optimizer.get_optimization_report()
        except Exception as e:
            logger.error(f"Failed to get optimization status: {e}")
            return {
                'performance_metrics': {'error': str(e)},
                'optimization_status': {
                    'vectorization_enabled': False,
                    'intelligent_caching_enabled': False,
                    'parallel_processing_enabled': False
                },
                'recommendations': ['Optimization system unavailable'],
                'system_info': {'optimization_level': 'disabled'}
            }
    
    def _jd_to_datetime(self, jd: float) -> datetime:
        """Convert Julian Day to datetime."""
        import swisseph as swe
        year, month, day, hour = swe.revjul(jd)
        
        hour_int = int(hour)
        minute_float = (hour - hour_int) * 60
        minute_int = int(minute_float)
        second_float = (minute_float - minute_int) * 60
        second_int = int(second_float)
        microsecond = int((second_float - second_int) * 1000000)
        
        return datetime(year, month, day, hour_int, minute_int, second_int, microsecond)


# Global service instance
predictive_service = PredictiveService()