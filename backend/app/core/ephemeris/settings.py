"""
Meridian Ephemeris Engine - Settings Module

Provides configuration management for the ephemeris engine with thread-safe 
singleton pattern and Swiss Ephemeris path management.
"""

import os
import threading
from typing import Any, Dict, List, Optional
import swisseph as swe


class EphemerisSettings:
    """Core settings for the Meridian Ephemeris Engine."""
    
    def __init__(self) -> None:
        """Initialize default settings."""
        self._lock = threading.RLock()
        
        # Ephemeris file paths
        self._ephemeris_path: str = self._get_default_ephemeris_path()
        
        # Calculation settings
        self.default_latitude: float = 0.0
        self.default_longitude: float = 0.0
        self.default_house_system: str = 'P'  # Placidus
        
        # Swiss Ephemeris flags
        self.swe_flags: int = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        # Precision settings
        self.angle_precision: int = 3  # decimal places
        self.time_precision: int = 6   # decimal places
        
        # Cache settings
        self.enable_cache: bool = True
        self.cache_size: int = 1000
        self.cache_ttl: int = 3600  # seconds
        
        # Coordinate systems
        self.coordinate_system: str = 'tropical'  # tropical or sidereal
        self.ayanamsa: int = swe.SIDM_FAGAN_BRADLEY
        
        # Default objects to calculate
        self.default_planets: List[int] = [
            swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
            swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO
        ]
        
        self.default_points: List[int] = [
            swe.MEAN_NODE, swe.TRUE_NODE, swe.CHIRON
        ]
        
        # House systems mapping
        self.house_systems: Dict[str, str] = {
            'placidus': 'P',
            'koch': 'K',
            'porphyrius': 'O',
            'regiomontanus': 'R',
            'campanus': 'C',
            'equal': 'E',
            'whole_sign': 'W',
            'alcabitus': 'B',
            'morinus': 'M',
            'krusinski': 'U',
            'galactic_equator': 'G',
            'azimuthal': 'H',
            'polich_page': 'T',
            'carter_equal': 'D'
        }
        
        # Initialize Swiss Ephemeris path
        self._set_swe_path()
    
    def _get_default_ephemeris_path(self) -> str:
        """Get the default ephemeris files path."""
        # Check relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__)))))
        ephemeris_path = os.path.join(project_root, 'ephemeris')
        
        if os.path.exists(ephemeris_path):
            return ephemeris_path
        
        # Fall back to current directory
        return os.path.join(os.getcwd(), 'ephemeris')
    
    def _set_swe_path(self) -> None:
        """Set the Swiss Ephemeris file path."""
        if os.path.exists(self._ephemeris_path):
            swe.set_ephe_path(self._ephemeris_path)
    
    @property
    def ephemeris_path(self) -> str:
        """Get the ephemeris file path."""
        with self._lock:
            return self._ephemeris_path
    
    @ephemeris_path.setter
    def ephemeris_path(self, path: str) -> None:
        """Set the ephemeris file path."""
        with self._lock:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Ephemeris path does not exist: {path}")
            
            self._ephemeris_path = path
            self._set_swe_path()
    
    def add_ephemeris_path(self, path: str) -> None:
        """Add an additional ephemeris file path."""
        with self._lock:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Ephemeris path does not exist: {path}")
            
            current_paths = self._ephemeris_path.split(os.pathsep)
            if path not in current_paths:
                self._ephemeris_path = f"{self._ephemeris_path}{os.pathsep}{path}"
                self._set_swe_path()
    
    def get_house_system_code(self, system: str) -> str:
        """Get Swiss Ephemeris house system code."""
        system_lower = system.lower()
        if system_lower in self.house_systems:
            return self.house_systems[system_lower]
        
        # Return as-is if it's already a single character (assume it's a valid code)
        if len(system) == 1:
            return system.upper()
        
        # Default to Placidus
        return 'P'
    
    def update(self, **kwargs) -> None:
        """Update multiple settings at once."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    raise AttributeError(f"Unknown setting: {key}")
    
    def reset(self) -> None:
        """Reset all settings to defaults."""
        with self._lock:
            self.__init__()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export settings as a dictionary."""
        with self._lock:
            return {
                'ephemeris_path': self._ephemeris_path,
                'default_latitude': self.default_latitude,
                'default_longitude': self.default_longitude,
                'default_house_system': self.default_house_system,
                'swe_flags': self.swe_flags,
                'angle_precision': self.angle_precision,
                'time_precision': self.time_precision,
                'enable_cache': self.enable_cache,
                'cache_size': self.cache_size,
                'cache_ttl': self.cache_ttl,
                'coordinate_system': self.coordinate_system,
                'ayanamsa': self.ayanamsa,
                'default_planets': self.default_planets.copy(),
                'default_points': self.default_points.copy(),
            }


class SettingsSingleton:
    """Thread-safe singleton for global settings access."""
    
    _instance: Optional[EphemerisSettings] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls) -> EphemerisSettings:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = EphemerisSettings()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.reset()
            else:
                cls._instance = EphemerisSettings()
    
    @classmethod
    def get_instance(cls) -> EphemerisSettings:
        """Get the singleton instance."""
        return cls()


# Global settings instance
settings = SettingsSingleton()