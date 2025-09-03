"""
Meridian Ephemeris Engine - Serialization Module

Provides efficient serialization and deserialization for ephemeris data
with support for JSON, binary formats, and custom astronomical data types.
"""

import json
import pickle
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import numpy as np


class EphemerisEncoder(json.JSONEncoder):
    """Custom JSON encoder for ephemeris data types."""
    
    def default(self, obj):
        """Convert non-serializable objects to serializable format."""
        if isinstance(obj, datetime):
            return {
                '__type__': 'datetime',
                'isoformat': obj.isoformat(),
                'timestamp': obj.timestamp()
            }
        elif isinstance(obj, np.ndarray):
            return {
                '__type__': 'numpy_array',
                'data': obj.tolist(),
                'dtype': str(obj.dtype),
                'shape': obj.shape
            }
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, complex):
            return {
                '__type__': 'complex',
                'real': obj.real,
                'imag': obj.imag
            }
        elif hasattr(obj, '__dict__'):
            # Handle custom objects with attributes
            return {
                '__type__': 'custom_object',
                '__class__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                'data': obj.__dict__
            }
        
        return super().default(obj)


class EphemerisDecoder:
    """Custom decoder for ephemeris data types."""
    
    @staticmethod
    def decode_hook(dct: Dict[str, Any]) -> Any:
        """Decode custom objects from dictionary representation."""
        if '__type__' not in dct:
            return dct
        
        obj_type = dct['__type__']
        
        if obj_type == 'datetime':
            return datetime.fromisoformat(dct['isoformat'])
        elif obj_type == 'numpy_array':
            return np.array(dct['data'], dtype=dct['dtype']).reshape(dct['shape'])
        elif obj_type == 'complex':
            return complex(dct['real'], dct['imag'])
        elif obj_type == 'custom_object':
            # Note: This requires the class to be importable
            # For security, we'll return the data dict instead
            return {
                'class': dct['__class__'],
                'module': dct['__module__'],
                'data': dct['data']
            }
        
        return dct


class EphemerisData:
    """Container for ephemeris calculation results."""
    
    def __init__(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize ephemeris data container.
        
        Args:
            data: Calculation results data
            metadata: Optional metadata (timestamp, settings, etc.)
        """
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'data': self.data,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> 'EphemerisData':
        """Create instance from dictionary."""
        return cls(
            data=dct['data'],
            metadata=dct.get('metadata', {})
        )
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), cls=EphemerisEncoder, indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EphemerisData':
        """Deserialize from JSON string."""
        dct = json.loads(json_str, object_hook=EphemerisDecoder.decode_hook)
        return cls.from_dict(dct)
    
    def to_binary(self) -> bytes:
        """Serialize to binary format using pickle."""
        return pickle.dumps(self.to_dict())
    
    @classmethod
    def from_binary(cls, binary_data: bytes) -> 'EphemerisData':
        """Deserialize from binary format."""
        dct = pickle.loads(binary_data)
        return cls.from_dict(dct)


class PlanetPosition:
    """Represents a planet's calculated position."""
    
    def __init__(
        self,
        longitude: float,
        latitude: float,
        distance: float,
        longitude_speed: float,
        planet_id: int = 0,
        latitude_speed: float = 0.0,
        distance_speed: float = 0.0,
        calculation_time: Optional[datetime] = None,
        flags: int = 0
    ):
        """Initialize planet position data.
        Note: parameters are kept flexible for test construction convenience.
        """
        self.planet_id = planet_id
        self.longitude = longitude
        self.latitude = latitude
        self.distance = distance
        self.longitude_speed = longitude_speed
        self.latitude_speed = latitude_speed
        self.distance_speed = distance_speed
        self.calculation_time = calculation_time or datetime.now(timezone.utc)
        self.flags = flags
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'planet_id': self.planet_id,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'distance': self.distance,
            'longitude_speed': self.longitude_speed,
            'latitude_speed': self.latitude_speed,
            'distance_speed': self.distance_speed,
            'calculation_time': self.calculation_time,
            'flags': self.flags
        }
    
    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> 'PlanetPosition':
        """Create instance from dictionary."""
        return cls(**dct)
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), cls=EphemerisEncoder, indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PlanetPosition':
        """Deserialize from JSON string."""
        dct = json.loads(json_str, object_hook=EphemerisDecoder.decode_hook)
        return cls.from_dict(dct)


class HouseSystem:
    """Represents a calculated house system."""
    
    def __init__(
        self,
        house_cusps: List[float],
        ascmc: List[float],
        system_code: str,
        calculation_time: datetime,
        latitude: float,
        longitude: float
    ):
        """Initialize house system data."""
        self.house_cusps = house_cusps  # 12 house cusps
        self.ascmc = ascmc  # [Asc, MC, ARMC, Vertex, Equatorial Asc, Co-Asc, Polar Asc, etc.]
        self.system_code = system_code
        self.calculation_time = calculation_time
        self.latitude = latitude
        self.longitude = longitude
    
    @property
    def ascendant(self) -> float:
        """Get the Ascendant (AC) angle."""
        return self.ascmc[0] if len(self.ascmc) > 0 else 0.0
    
    @property
    def midheaven(self) -> float:
        """Get the Midheaven (MC) angle."""
        return self.ascmc[1] if len(self.ascmc) > 1 else 0.0
    
    @property
    def descendant(self) -> float:
        """Get the Descendant (DC) angle."""
        return (self.ascendant + 180.0) % 360.0
    
    @property
    def imum_coeli(self) -> float:
        """Get the Imum Coeli (IC) angle."""
        return (self.midheaven + 180.0) % 360.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'house_cusps': self.house_cusps,
            'ascmc': self.ascmc,
            'system_code': self.system_code,
            'calculation_time': self.calculation_time,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
    
    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> 'HouseSystem':
        """Create instance from dictionary."""
        return cls(**dct)
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), cls=EphemerisEncoder, indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'HouseSystem':
        """Deserialize from JSON string."""
        dct = json.loads(json_str, object_hook=EphemerisDecoder.decode_hook)
        return cls.from_dict(dct)


class ChartData:
    """Complete chart calculation results."""
    
    def __init__(
        self,
        planets: Dict[int, PlanetPosition],
        houses: HouseSystem,
        calculation_time: datetime,
        julian_day: float,
        settings: Optional[Dict[str, Any]] = None
    ):
        """Initialize chart data."""
        self.planets = planets
        self.houses = houses
        self.calculation_time = calculation_time
        self.julian_day = julian_day
        self.settings = settings or {}
    
    def get_planet(self, planet_id: int) -> Optional[PlanetPosition]:
        """Get planet position by ID."""
        return self.planets.get(planet_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'planets': {pid: planet.to_dict() for pid, planet in self.planets.items()},
            'houses': self.houses.to_dict(),
            'calculation_time': self.calculation_time,
            'julian_day': self.julian_day,
            'settings': self.settings
        }
    
    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> 'ChartData':
        """Create instance from dictionary."""
        planets = {
            int(pid): PlanetPosition.from_dict(pdata)
            for pid, pdata in dct['planets'].items()
        }
        houses = HouseSystem.from_dict(dct['houses'])
        
        return cls(
            planets=planets,
            houses=houses,
            calculation_time=dct['calculation_time'],
            julian_day=dct['julian_day'],
            settings=dct.get('settings', {})
        )
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), cls=EphemerisEncoder, indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ChartData':
        """Deserialize from JSON string."""
        dct = json.loads(json_str, object_hook=EphemerisDecoder.decode_hook)
        return cls.from_dict(dct)
    
    def to_binary(self) -> bytes:
        """Serialize to binary format."""
        return pickle.dumps(self.to_dict())
    
    @classmethod
    def from_binary(cls, binary_data: bytes) -> 'ChartData':
        """Deserialize from binary format."""
        dct = pickle.loads(binary_data)
        return cls.from_dict(dct)


# Utility functions for common serialization tasks
def serialize_calculation_result(
    result: Any,
    format: str = 'json',
    include_metadata: bool = True
) -> Union[str, bytes]:
    """
    Serialize calculation result in specified format.
    
    Args:
        result: Result to serialize
        format: 'json' or 'binary'
        include_metadata: Whether to include metadata
    
    Returns:
        Serialized data
    """
    if include_metadata:
        data = EphemerisData(
            data=result,
            metadata={'format': format, 'version': '1.0'}
        )
    else:
        data = result
    
    if format == 'json':
        if hasattr(data, 'to_json'):
            return data.to_json()
        else:
            return json.dumps(data, cls=EphemerisEncoder)
    elif format == 'binary':
        if hasattr(data, 'to_binary'):
            return data.to_binary()
        else:
            return pickle.dumps(data)
    else:
        raise ValueError(f"Unsupported format: {format}")


def deserialize_calculation_result(
    data: Union[str, bytes],
    format: str = 'json'
) -> Any:
    """
    Deserialize calculation result from specified format.
    
    Args:
        data: Serialized data
        format: 'json' or 'binary'
    
    Returns:
        Deserialized result
    """
    if format == 'json':
        return json.loads(data, object_hook=EphemerisDecoder.decode_hook)
    elif format == 'binary':
        return pickle.loads(data)
    else:
        raise ValueError(f"Unsupported format: {format}")


def convert_numpy_to_json_safe(obj: Any) -> Any:
    """Convert numpy types to JSON-safe equivalents."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_to_json_safe(item) for item in obj]
    else:
        return obj