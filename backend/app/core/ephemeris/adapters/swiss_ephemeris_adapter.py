"""
Swiss Ephemeris Adapter

Single point of Swiss Ephemeris integration with proper lifecycle management.
Follows astro.com recommended patterns for initialization and cleanup.

Replaces 32 scattered Swiss Ephemeris calls across the codebase.
"""

import swisseph as swe
from typing import List, Tuple, Optional, Any
from threading import Lock
import logging
from ..settings import settings

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class SwissEphemerisAdapter:
    """
    Single point of Swiss Ephemeris integration with proper lifecycle management.
    Follows astro.com recommended patterns for initialization and cleanup.
    
    Features:
    - Singleton pattern for consistent configuration
    - Thread-safe initialization
    - Proper swe.set_ephe_path() and swe.close() lifecycle
    - Centralized error handling
    - Swiss Ephemeris best practices implementation
    """
    
    _instance = None
    _lock = Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, ephemeris_path: Optional[str] = None) -> None:
        """
        Initialize Swiss Ephemeris with proper path setting.
        
        Per astro.com documentation:
        "The first function that should be called before any other function 
        of the Swiss Ephemeris is swe_set_ephe_path()"
        
        Args:
            ephemeris_path: Path to ephemeris files, uses settings.ephemeris_path if None
        """
        if self._initialized:
            return
            
        try:
            path = ephemeris_path or settings.ephemeris_path
            swe.set_ephe_path(path)  # Must be called first per astro.com docs
            self._initialized = True
            logger.info(f"Swiss Ephemeris initialized with path: {path}")
        except Exception as e:
            logger.error(f"Failed to initialize Swiss Ephemeris: {e}")
            raise RuntimeError(f"Swiss Ephemeris initialization failed: {e}")
    
    def calculate_position(self, object_id: int, julian_day: float, 
                         flags: Optional[int] = None) -> Tuple[List[float], int]:
        """
        Calculate celestial object position using Swiss Ephemeris.
        
        Args:
            object_id: Swiss Ephemeris planet constant
            julian_day: Julian Day Number for calculation
            flags: Swiss Ephemeris calculation flags
            
        Returns:
            Tuple of (position_data, return_flags)
            position_data: [longitude, latitude, distance, long_speed, lat_speed, dist_speed]
            
        Raises:
            RuntimeError: If calculation fails or adapter not initialized
        """
        if not self._initialized:
            self.initialize()
        
        try:
            flags = flags or settings.swe_flags
            result, ret_flags = swe.calc_ut(julian_day, object_id, flags)
            
            if len(result) < 6:
                raise RuntimeError(f"Swiss Ephemeris calculation failed for object {object_id}")
            
            return result, ret_flags
            
        except Exception as e:
            logger.error(f"Swiss Ephemeris calculation failed for object {object_id}: {e}")
            raise RuntimeError(f"Position calculation failed: {e}")
    
    def calculate_houses(self, julian_day: float, latitude: float, 
                        longitude: float, system: str = 'P') -> Tuple[List[float], List[float]]:
        """
        Calculate house cusps using Swiss Ephemeris.
        
        Args:
            julian_day: Julian Day Number
            latitude: Observer latitude in degrees (positive=North)
            longitude: Observer longitude in degrees (positive=East per European convention)
            system: House system code (P=Placidus, K=Koch, etc.)
            
        Returns:
            Tuple of (house_cusps, ascmc)
            house_cusps: List of 12 house cusps
            ascmc: List of angles [ASC, MC, ARMC, Vertex, etc.]
        """
        if not self._initialized:
            self.initialize()
            
        try:
            # Validate house system
            valid_systems = ['P', 'K', 'O', 'R', 'C', 'E', 'W', 'B', 'M', 'U', 'G', 'H', 'T', 'D', 'V', 'X', 'N', 'I']
            if system not in valid_systems:
                logger.warning(f"Invalid house system '{system}', defaulting to Placidus")
                system = 'P'
            
            house_cusps, ascmc = swe.houses(julian_day, latitude, longitude, system.encode('utf-8'))
            return list(house_cusps), list(ascmc)
            
        except Exception as e:
            logger.error(f"House calculation failed: {e}")
            raise RuntimeError(f"House calculation failed: {e}")
    
    def calculate_julian_day(self, year: int, month: int, day: int, 
                           hour: float = 12.0, calendar_type: int = 1) -> float:
        """
        Calculate Julian Day Number from calendar date.
        
        Args:
            year: Calendar year
            month: Calendar month (1-12)
            day: Calendar day (1-31)
            hour: Hour as decimal (0.0-23.999...)
            calendar_type: 1=Gregorian, 0=Julian calendar
            
        Returns:
            Julian Day Number as float
        """
        try:
            return swe.julday(year, month, day, hour, calendar_type)
        except Exception as e:
            logger.error(f"Julian day calculation failed: {e}")
            raise RuntimeError(f"Julian day calculation failed: {e}")
    
    def get_planet_name(self, object_id: int) -> str:
        """
        Get standard planet name for Swiss Ephemeris object ID.
        
        Args:
            object_id: Swiss Ephemeris planet constant
            
        Returns:
            Planet name as string
        """
        try:
            return swe.get_planet_name(object_id)
        except Exception as e:
            logger.warning(f"Could not get name for object {object_id}: {e}")
            return f"Object_{object_id}"
    
    def normalize_longitude(self, longitude: float) -> float:
        """
        Normalize longitude to 0-360 degrees range.
        
        Args:
            longitude: Longitude in degrees
            
        Returns:
            Normalized longitude (0-360)
        """
        while longitude < 0:
            longitude += 360
        while longitude >= 360:
            longitude -= 360
        return longitude
    
    def cleanup(self) -> None:
        """
        Proper cleanup of Swiss Ephemeris resources.
        
        Per astro.com documentation:
        "swe.close() should be called at the end of your program"
        """
        if self._initialized:
            try:
                swe.close()
                self._initialized = False
                logger.info("Swiss Ephemeris cleanup completed")
            except Exception as e:
                logger.error(f"Swiss Ephemeris cleanup failed: {e}")
    
    def is_initialized(self) -> bool:
        """Check if adapter is initialized."""
        return self._initialized
    
    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()


# Global adapter instance following singleton pattern
swiss_adapter = SwissEphemerisAdapter()