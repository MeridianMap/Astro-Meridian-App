"""
Meridian Ephemeris Engine - Natal Chart Construction

Provides comprehensive natal chart computation by aggregating all celestial objects,
houses, angles, and astrological points into a unified chart structure.

Maintains compatibility with Immanuel reference implementation while providing
enhanced features and performance optimizations through caching and parallel processing.

Features:
- Complete celestial object calculations (planets, asteroids, nodes, etc.)
- House system calculations with multiple systems support
- Angular points (Ascendant, Midheaven, etc.)
- Aspect calculations between all objects
- Extensible structure for additional astrological points
- Thread-safe computation with caching
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .subject import Subject, SubjectData
from ..tools.ephemeris import get_planet, get_houses, get_angles, ChartAngles
from ..tools.ephemeris import PlanetPosition, HouseSystem
from ..tools.position import (
    angular_separation, get_closest_aspect_angle, get_position_summary,
    is_in_same_sign, is_in_same_element, is_in_same_modality
)
from ..const import (
    SwePlanets, MODERN_PLANETS, MAJOR_ASTEROIDS, LUNAR_NODES,
    LILITH_POINTS, HouseSystems, PLANET_NAMES, get_planet_name
)
from ..settings import settings


@dataclass(frozen=True)
class AspectData:
    """Aspect relationship between two celestial objects."""
    object1_id: int
    object2_id: int
    object1_name: str
    object2_name: str
    aspect_name: str
    angle: float
    orb: float
    separation: float
    applying: Optional[bool] = None


@dataclass(frozen=True) 
class ChartData:
    """Complete natal chart data structure."""
    subject: SubjectData
    planets: Dict[int, PlanetPosition]
    houses: HouseSystem
    angles: ChartAngles
    aspects: List[AspectData]
    calculation_time: datetime
    chart_type: str = "natal"
    
    def get_object_position(self, object_id: int) -> Optional[PlanetPosition]:
        """Get position of celestial object by ID."""
        return self.planets.get(object_id)
    
    def get_objects_in_sign(self, sign_number: int) -> List[PlanetPosition]:
        """Get all objects in specified zodiac sign."""
        return [planet for planet in self.planets.values() 
                if planet.sign_number == sign_number]
    
    def get_objects_in_house(self, house_number: int) -> List[PlanetPosition]:
        """Get all objects in specified house."""
        return [planet for planet in self.planets.values()
                if planet.house_position and planet.house_position.get('number') == house_number]
    
    def get_aspects_for_object(self, object_id: int) -> List[AspectData]:
        """Get all aspects involving specified object."""
        return [aspect for aspect in self.aspects
                if aspect.object1_id == object_id or aspect.object2_id == object_id]


class NatalChart:
    """
    Natal chart computation engine.
    
    Aggregates all celestial objects, houses, angles, and aspects into a unified
    chart structure. Provides high-performance calculations through caching and
    optional parallel processing.
    
    Examples:
        >>> subject = Subject("John Doe", "1990-06-15 14:30", "40N45", "73W59")
        >>> chart = NatalChart(subject)
        >>> chart_data = chart.calculate()
        >>> sun_position = chart_data.get_object_position(SwePlanets.SUN)
        >>> print(f"Sun at {sun_position.longitude:.2f}° {sun_position.sign_name}")
    """
    
    def __init__(
        self,
        subject: Union[Subject, SubjectData],
        house_system: str = HouseSystems.PLACIDUS,
        include_asteroids: bool = True,
        include_nodes: bool = True,
        include_lilith: bool = True,
        aspect_orbs: Optional[Dict[str, float]] = None,
        parallel_processing: bool = True,
        **kwargs
    ):
        """
        Initialize natal chart calculator.
        
        Args:
            subject: Subject data or Subject instance
            house_system: House system code (default: Placidus)
            include_asteroids: Include major asteroids (default: True)
            include_nodes: Include lunar nodes (default: True)  
            include_lilith: Include Lilith points (default: True)
            aspect_orbs: Custom aspect orb settings
            parallel_processing: Use parallel processing for calculations (default: True)
            **kwargs: Additional parameters for extensibility
        """
        # Handle subject input
        if isinstance(subject, Subject):
            self.subject_data = subject.get_data()
        elif isinstance(subject, SubjectData):
            self.subject_data = subject
        else:
            raise TypeError(f"Expected Subject or SubjectData, got {type(subject)}")
        
        self.house_system = house_system
        self.include_asteroids = include_asteroids
        self.include_nodes = include_nodes
        self.include_lilith = include_lilith
        self.parallel_processing = parallel_processing
        
        # Aspect orb configuration
        self.aspect_orbs = aspect_orbs or self._default_aspect_orbs()
        
        # Thread safety
        self._calculation_lock = threading.RLock()
        self._cached_result: Optional[ChartData] = None
        
        # Settings
        self._settings = settings
    
    def _default_aspect_orbs(self) -> Dict[str, float]:
        """Default aspect orb settings."""
        return {
            'Conjunction': 8.0,
            'Opposition': 8.0,
            'Trine': 8.0,
            'Square': 7.0,
            'Sextile': 6.0,
            'Quincunx': 3.0,
            'Semisextile': 3.0,
            'Semisquare': 3.0,
            'Sesquisquare': 3.0
        }
    
    def _get_calculation_objects(self) -> List[int]:
        """Get list of celestial objects to calculate."""
        objects = MODERN_PLANETS.copy()
        
        if self.include_asteroids:
            objects.extend(MAJOR_ASTEROIDS)
        
        if self.include_nodes:
            objects.extend(LUNAR_NODES)
        
        if self.include_lilith:
            objects.extend(LILITH_POINTS)
        
        return objects
    
    def _calculate_single_object(self, object_id: int) -> Optional[PlanetPosition]:
        """Calculate position for a single celestial object."""
        try:
            position = get_planet(
                object_id,
                self.subject_data.julian_day,
                latitude=self.subject_data.latitude,
                longitude=self.subject_data.longitude,
                altitude=self.subject_data.altitude
            )
            
            # Add position summary information
            position_summary = get_position_summary(
                position.longitude,
                None  # Houses will be added later
            )
            
            # Enhance position with astrological information
            if hasattr(position, '__dict__'):
                position.sign_number = position_summary['sign']['number']
                position.sign_name = position_summary['sign']['name']
                position.sign_symbol = position_summary['sign']['symbol']
                position.sign_longitude = position_summary['sign_longitude']
                position.decan = position_summary['decan']
                position.element = position_summary['element']
                position.modality = position_summary['modality']
            
            return position
            
        except Exception as e:
            # Log error but don't fail entire calculation
            print(f"Warning: Failed to calculate {PLANET_NAMES.get(object_id, f'object {object_id}')}: {e}")
            return None
    
    def _calculate_objects_parallel(self, objects: List[int]) -> Dict[int, PlanetPosition]:
        """Calculate object positions using parallel processing."""
        results = {}
        
        if not self.parallel_processing or len(objects) < 4:
            # Use sequential processing for small lists or when disabled
            for obj_id in objects:
                position = self._calculate_single_object(obj_id)
                if position:
                    results[obj_id] = position
            return results
        
        # Parallel processing
        with ThreadPoolExecutor(max_workers=min(len(objects), 8)) as executor:
            future_to_object = {
                executor.submit(self._calculate_single_object, obj_id): obj_id 
                for obj_id in objects
            }
            
            for future in as_completed(future_to_object):
                obj_id = future_to_object[future]
                try:
                    position = future.result()
                    if position:
                        results[obj_id] = position
                except Exception as e:
                    print(f"Error calculating object {obj_id}: {e}")
        
        return results
    
    def _calculate_houses_and_angles(self) -> tuple[HouseSystem, ChartAngles]:
        """Calculate houses and angles."""
        try:
            houses = get_houses(
                self.subject_data.julian_day,
                self.subject_data.latitude,
                self.subject_data.longitude,
                house_system=self.house_system
            )

            # Normalize for chart exposure: charts should present exactly 12 cusps
            # Low-level get_houses may return 13 (index 0 unused). Always trim to 12 here.
            if hasattr(houses, 'house_cusps') and len(houses.house_cusps) == 13:
                cusps = houses.house_cusps
                houses = HouseSystem(
                    house_cusps=cusps[1:],
                    ascmc=houses.ascmc,
                    system_code=houses.system_code,
                    calculation_time=houses.calculation_time,
                    latitude=houses.latitude,
                    longitude=houses.longitude
                )
            
            angles_dict = get_angles(
                self.subject_data.julian_day,
                self.subject_data.latitude,
                self.subject_data.longitude
            )
            
            # Convert angles dict to ChartAngles object
            angles = ChartAngles(
                ascendant=angles_dict.get('ASC', 0.0),
                midheaven=angles_dict.get('MC', 0.0), 
                descendant=angles_dict.get('DESC', 0.0),
                imum_coeli=angles_dict.get('IC', 0.0),
                calculation_time=datetime.now()
            )
            
            return houses, angles
            
        except Exception as e:
            raise RuntimeError(f"Failed to calculate houses and angles: {e}") from e
    
    def _add_house_positions(self, planets: Dict[int, PlanetPosition], houses: HouseSystem) -> None:
        """Add house position information to planet positions."""
        import swisseph as swe
        
        for planet in planets.values():
            house_pos = None
            
            # Find which house contains this planet using house cusps
            for i in range(12):
                house_start = houses.house_cusps[i]
                house_end = houses.house_cusps[(i + 1) % 12] if i < 11 else houses.house_cusps[0]
                
                # Use Swiss Ephemeris angular difference for accuracy
                diff_start = swe.difdeg2n(planet.longitude, house_start)
                diff_end = swe.difdeg2n(house_end, house_start)
                
                if 0 <= diff_start < diff_end:
                    house_pos = {
                        'number': i + 1,
                        'longitude': house_start,
                        'size': diff_end,
                        'position_in_house': diff_start
                    }
                    break
            
            # Add house position to planet (need to make it mutable temporarily)
            if hasattr(planet, '__dict__'):
                planet.house_position = house_pos
    
    def _calculate_aspects(self, planets: Dict[int, PlanetPosition]) -> List[AspectData]:
        """Calculate aspects between all celestial objects."""
        aspects = []
        object_ids = list(planets.keys())
        
        for i, obj1_id in enumerate(object_ids):
            for obj2_id in object_ids[i+1:]:
                planet1 = planets[obj1_id]
                planet2 = planets[obj2_id]
                
                aspect_info = get_closest_aspect_angle(planet1.longitude, planet2.longitude)
                
                # Check if aspect is within orb
                aspect_name = aspect_info['aspect']
                orb = aspect_info['orb']
                allowed_orb = self.aspect_orbs.get(aspect_name, 0.0)
                
                if orb <= allowed_orb:
                    aspects.append(AspectData(
                        object1_id=obj1_id,
                        object2_id=obj2_id,
                        object1_name=get_planet_name(obj1_id),
                        object2_name=get_planet_name(obj2_id),
                        aspect_name=aspect_name,
                        angle=aspect_info['angle'],
                        orb=orb,
                        separation=aspect_info['separation'],
                        applying=aspect_info.get('applying')
                    ))
        
        return aspects
    
    def calculate(self, force_recalculate: bool = False) -> ChartData:
        """
        Calculate complete natal chart.
        
        Args:
            force_recalculate: Force recalculation even if cached result exists
            
        Returns:
            ChartData: Complete chart data structure
            
        Raises:
            RuntimeError: If calculation fails
        """
        with self._calculation_lock:
            # Return cached result if available
            if self._cached_result is not None and not force_recalculate:
                return self._cached_result
            
            try:
                calculation_start = datetime.now()
                
                # Get objects to calculate
                objects = self._get_calculation_objects()
                
                # Calculate object positions
                planets = self._calculate_objects_parallel(objects)
                
                if not planets:
                    raise RuntimeError("Failed to calculate any celestial object positions")
                
                # Calculate houses and angles
                houses, angles = self._calculate_houses_and_angles()
                
                # Add house positions to planets
                self._add_house_positions(planets, houses)
                
                # Calculate aspects
                aspects = self._calculate_aspects(planets)
                
                # Create chart data
                self._cached_result = ChartData(
                    subject=self.subject_data,
                    planets=planets,
                    houses=houses,
                    angles=angles,
                    aspects=aspects,
                    calculation_time=calculation_start,
                    chart_type="natal"
                )
                
                return self._cached_result
                
            except Exception as e:
                raise RuntimeError(f"Natal chart calculation failed: {e}") from e
    
    def get_quick_data(self) -> Dict[str, Any]:
        """
        Get essential chart data without full calculation.
        
        Returns basic planetary positions and angles for quick previews.
        """
        essential_objects = [SwePlanets.SUN, SwePlanets.MOON, SwePlanets.MERCURY,
                           SwePlanets.VENUS, SwePlanets.MARS, SwePlanets.JUPITER,
                           SwePlanets.SATURN]
        
        planets = {}
        for obj_id in essential_objects:
            position = self._calculate_single_object(obj_id)
            if position:
                planets[obj_id] = {
                    'longitude': position.longitude,
                    'sign_name': getattr(position, 'sign_name', 'Unknown'),
                    'sign_longitude': getattr(position, 'sign_longitude', 0)
                }
        
        try:
            houses, angles = self._calculate_houses_and_angles()
            angles_data = {
                'ascendant': angles.ascendant,
                'midheaven': angles.midheaven
            }
        except Exception:
            angles_data = {}
        
        return {
            'subject': self.subject_data.name,
            'datetime': self.subject_data.datetime.isoformat(),
            'planets': planets,
            'angles': angles_data
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert chart data to dictionary format.
        
        Returns:
            Dictionary representation suitable for JSON serialization
        """
        chart_data = self.calculate()
        
        return {
            'subject': {
                'name': chart_data.subject.name,
                'datetime': chart_data.subject.datetime.isoformat(),
                'julian_day': chart_data.subject.julian_day,
                'latitude': chart_data.subject.latitude,
                'longitude': chart_data.subject.longitude,
                'altitude': chart_data.subject.altitude
            },
            'planets': {
                str(obj_id): {
                    'name': PLANET_NAMES.get(obj_id, f'Object {obj_id}'),
                    'longitude': planet.longitude,
                    'latitude': planet.latitude,
                    'distance': planet.distance,
                    'sign_name': getattr(planet, 'sign_name', None),
                    'sign_longitude': getattr(planet, 'sign_longitude', None),
                    'house_position': getattr(planet, 'house_position', None)
                }
                for obj_id, planet in chart_data.planets.items()
            },
            'houses': {
                'system': chart_data.houses.system_code,
                'cusps': chart_data.houses.house_cusps,
                'ascmc': chart_data.houses.ascmc
            },
            'angles': {
                'ascendant': chart_data.angles.ascendant,
                'descendant': chart_data.angles.descendant,
                'midheaven': chart_data.angles.midheaven,
                'imum_coeli': chart_data.angles.imum_coeli
            },
            'aspects': [
                {
                    'object1': aspect.object1_name,
                    'object2': aspect.object2_name,
                    'aspect': aspect.aspect_name,
                    'orb': aspect.orb,
                    'applying': aspect.applying
                }
                for aspect in chart_data.aspects
            ],
            'calculation_time': chart_data.calculation_time.isoformat(),
            'chart_type': chart_data.chart_type
        }
    
    def __repr__(self) -> str:
        """String representation of NatalChart."""
        return (f"NatalChart(subject='{self.subject_data.name}', "
               f"system='{self.house_system}', "
               f"objects={len(self._get_calculation_objects())})")