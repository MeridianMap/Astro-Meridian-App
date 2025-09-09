"""
Meridian Ephemeris Engine - Subject Data Model

Provides robust subject input normalization and validation for chart construction.
Handles birth data including date, time, location coordinates, and timezone information
with full compatibility to Immanuel reference implementation.

Features:
- Comprehensive input validation and normalization
- Timezone-aware datetime handling with DST support
- Coordinate validation and normalization
- Flexible input format support (strings, objects, coordinates)
- Thread-safe data handling
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union, Dict, Any
from zoneinfo import ZoneInfo

from ..tools.date import to_datetime, to_julian_day, get_timezone_info, lookup_timezone_by_coordinates
from ..tools.convert import to_decimal, normalize_latitude, normalize_longitude


@dataclass(frozen=True)
class SubjectData:
    """
    Immutable subject birth data with validated and normalized values.
    
    All inputs are normalized to standard formats:
    - datetime: timezone-aware datetime object in UTC or local timezone
    - julian_day: precise Julian Day Number for calculations
    - latitude/longitude: decimal degrees with proper bounds
    - timezone: ZoneInfo object or UTC offset
    """
    name: str
    datetime: datetime
    julian_day: float
    latitude: float
    longitude: float
    altitude: float = 0.0
    timezone_name: Optional[str] = None
    utc_offset: Optional[float] = None
    
    def __post_init__(self):
        """Validate data integrity after initialization."""
        # Validate coordinate bounds
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Latitude {self.latitude} must be between -90 and 90 degrees")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Longitude {self.longitude} must be between -180 and 180 degrees")
        
        # Validate datetime consistency
        if self.datetime.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")
        
        # Validate Julian Day consistency (within reasonable bounds)
        if not (1000000 <= self.julian_day <= 5000000):
            raise ValueError(f"Julian Day {self.julian_day} is outside reasonable astronomical range")


class Subject:
    """
    Subject data handler with input normalization and validation.
    
    Accepts flexible input formats and normalizes to standard SubjectData format.
    Handles timezone resolution via coordinates when timezone is not explicitly provided.
    
    Examples:
        >>> subject = Subject(
        ...     name="John Doe",
        ...     datetime="1990-06-15 14:30:00",
        ...     latitude="40°45'N", 
        ...     longitude="73°59'W"
        ... )
        >>> chart_data = subject.get_data()
        >>> print(chart_data.julian_day)
        2448067.1041666665
    """
    
    def __init__(
        self,
        name: str,
        datetime: Union[str, datetime, float],
        latitude: Union[str, float],
        longitude: Union[str, float],
        altitude: float = 0.0,
        timezone: Optional[Union[str, float, ZoneInfo]] = None,
        **kwargs
    ):
        """
        Initialize Subject with flexible input formats.
        
        Args:
            name: Subject name or identifier
            datetime: Birth datetime (string, datetime object, or Julian Day)
            latitude: Latitude (string with direction or decimal degrees)
            longitude: Longitude (string with direction or decimal degrees) 
            altitude: Altitude in meters (default: 0.0)
            timezone: Timezone (name, UTC offset, or ZoneInfo object)
            **kwargs: Additional parameters for future extensibility
        
        Raises:
            ValueError: If inputs cannot be parsed or validated
            TypeError: If inputs are of unsupported types
        """
        self._raw_inputs = {
            'name': name,
            'datetime': datetime, 
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'timezone': timezone,
            **kwargs
        }
        self._data: Optional[SubjectData] = None
        self._validation_errors: list = []
        
        # Perform validation and normalization
        self._validate_and_normalize()
    
    def _validate_and_normalize(self) -> None:
        """Validate inputs and create normalized SubjectData."""
        try:
            # Validate and normalize name
            name = self._normalize_name(self._raw_inputs['name'])
            
            # Validate and normalize coordinates
            latitude = self._normalize_coordinate(self._raw_inputs['latitude'], 'latitude')
            longitude = self._normalize_coordinate(self._raw_inputs['longitude'], 'longitude')
            altitude = float(self._raw_inputs['altitude'])
            
            # Normalize timezone info
            timezone_info = self._normalize_timezone(self._raw_inputs['timezone'], latitude, longitude)
            
            # Normalize datetime
            dt = self._normalize_datetime(self._raw_inputs['datetime'], timezone_info)
            
            # Calculate Julian Day
            julian_day = to_julian_day(dt)
            if julian_day is None:
                raise ValueError("Failed to calculate Julian Day from datetime")
            
            # Extract timezone information
            timezone_name = None
            utc_offset = None
            
            if isinstance(timezone_info, ZoneInfo):
                timezone_name = str(timezone_info)
                # For ZoneInfo, also calculate the UTC offset for this specific datetime
                try:
                    dt_with_tz = dt.replace(tzinfo=timezone_info)
                    utc_offset = dt_with_tz.utcoffset().total_seconds() / 3600.0
                except Exception:
                    # Fallback: try to localize the datetime
                    try:
                        import pytz
                        if hasattr(pytz.timezone(str(timezone_info)), 'localize'):
                            dt_localized = pytz.timezone(str(timezone_info)).localize(dt.replace(tzinfo=None))
                            utc_offset = dt_localized.utcoffset().total_seconds() / 3600.0
                    except Exception:
                        pass
            elif timezone_info is not None and hasattr(timezone_info, 'utcoffset'):
                # Handle datetime.timezone objects
                utc_offset = timezone_info.utcoffset(dt).total_seconds() / 3600.0
            
            # Create immutable data object
            self._data = SubjectData(
                name=name,
                datetime=dt,
                julian_day=julian_day,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                timezone_name=timezone_name,
                utc_offset=utc_offset
            )
            
        except Exception as e:
            self._validation_errors.append(str(e))
            raise ValueError(f"Subject validation failed: {str(e)}") from e
    
    def _normalize_name(self, name: Any) -> str:
        """Normalize subject name."""
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, got {type(name)}")
        
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty")
        
        return name
    
    def _normalize_coordinate(self, coord: Union[str, float], coord_type: str) -> float:
        """Normalize coordinate to decimal degrees."""
        try:
            decimal = to_decimal(coord)
            if decimal is None:
                raise ValueError(f"Cannot parse {coord_type}: {coord}")
            
            if coord_type == 'latitude':
                return normalize_latitude(decimal)
            else:
                # For longitude, convert to -180 to 180 range
                normalized = normalize_longitude(decimal)  # This gives 0-360
                return normalized if normalized <= 180 else normalized - 360
                
        except Exception as e:
            raise ValueError(f"Invalid {coord_type} '{coord}': {str(e)}") from e
    
    def _normalize_timezone(self, tz: Any, lat: float, lon: float) -> Optional[Any]:
        """Normalize timezone information."""
        if tz is None:
            # Try to determine timezone from coordinates
            tz_name = lookup_timezone_by_coordinates(lat, lon)
            if tz_name:
                return ZoneInfo(tz_name)
            return None
        
        if isinstance(tz, str):
            try:
                return ZoneInfo(tz)
            except Exception:
                raise ValueError(f"Invalid timezone name: {tz}")
        
        if isinstance(tz, (int, float)):
            from datetime import timezone, timedelta
            return timezone(timedelta(hours=float(tz)))
        
        if isinstance(tz, ZoneInfo):
            return tz
        
        raise TypeError(f"Unsupported timezone type: {type(tz)}")
    
    def _normalize_datetime(self, dt: Any, tz_info: Any) -> datetime:
        """Normalize datetime with timezone information."""
        if isinstance(dt, float):
            # Assume Julian Day
            result = to_datetime(dt)
            if result is None:
                raise ValueError(f"Cannot convert Julian Day {dt} to datetime")
            return result
        
        # Handle string or datetime inputs with timezone
        if tz_info:
            if isinstance(tz_info, ZoneInfo):
                result = to_datetime(dt, timezone_name=str(tz_info))
            else:
                offset_hours = tz_info.utcoffset(datetime.now()).total_seconds() / 3600.0
                result = to_datetime(dt, utc_offset=offset_hours)
        else:
            result = to_datetime(dt)
        
        if result is None:
            raise ValueError(f"Cannot parse datetime: {dt}")
        
        return result
    
    def get_data(self) -> SubjectData:
        """
        Get validated and normalized subject data.
        
        Returns:
            SubjectData: Immutable subject data object
            
        Raises:
            ValueError: If validation failed during initialization
        """
        if self._data is None:
            raise ValueError("Subject data is not available due to validation errors")
        return self._data
    
    def is_valid(self) -> bool:
        """Check if subject data is valid."""
        return self._data is not None and not self._validation_errors
    
    def get_validation_errors(self) -> list:
        """Get list of validation errors."""
        return self._validation_errors.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert subject data to dictionary format.
        
        Returns:
            Dictionary representation suitable for JSON serialization
        """
        if not self.is_valid():
            return {'valid': False, 'errors': self._validation_errors}
        
        data = self._data
        return {
            'valid': True,
            'name': data.name,
            'datetime': data.datetime.isoformat(),
            'julian_day': data.julian_day,
            'latitude': data.latitude,
            'longitude': data.longitude,
            'altitude': data.altitude,
            'timezone_name': data.timezone_name,
            'utc_offset': data.utc_offset
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subject':
        """
        Create Subject from dictionary data.
        
        Args:
            data: Dictionary containing subject data
            
        Returns:
            Subject instance
        """
        return cls(
            name=data['name'],
            datetime=data['datetime'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            altitude=data.get('altitude', 0.0),
            timezone=data.get('timezone_name') or data.get('utc_offset')
        )
    
    def __repr__(self) -> str:
        """String representation of Subject."""
        if self.is_valid():
            data = self._data
            return (f"Subject(name='{data.name}', "
                   f"datetime='{data.datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}', "
                   f"lat={data.latitude:.4f}, lon={data.longitude:.4f})")
        else:
            return f"Subject(invalid, errors={len(self._validation_errors)})"