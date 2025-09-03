"""
Meridian Ephemeris API - Service Layer

Provides high-level service functions for the ephemeris API endpoints.
Handles input validation, data transformation, and chart calculation orchestration.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from dataclasses import asdict

from ..api.models.schemas import (
    NatalChartRequest, NatalChartResponse, SubjectResponse, PlanetResponse,
    HousesResponse, AnglesResponse, AspectResponse, ErrorResponse, HealthResponse,
    CoordinateInput, DateTimeInput, TimezoneInput, SubjectRequest
)
from ..core.ephemeris.charts.subject import Subject
from ..core.ephemeris.charts.natal import NatalChart
from ..core.ephemeris.const import PLANET_NAMES
from ..core.ephemeris.tools.ephemeris import validate_ephemeris_files


class EphemerisServiceError(Exception):
    """Base exception for ephemeris service errors."""
    pass


class InputValidationError(EphemerisServiceError):
    """Raised when input validation fails."""
    pass


class CalculationError(EphemerisServiceError):
    """Raised when chart calculation fails."""
    pass


class EphemerisService:
    """
    High-level ephemeris service for API operations.
    
    Provides abstraction layer between API routes and core ephemeris engine,
    handling input normalization, validation, and response formatting.
    """
    
    def __init__(self):
        """Initialize ephemeris service."""
        self.start_time = time.time()
        self._ephemeris_validation_cache: Optional[Dict[str, bool]] = None
        self._last_validation_check: Optional[float] = None
        self._validation_cache_ttl = 300  # 5 minutes
    
    def get_health_status(self) -> HealthResponse:
        """
        Get service health status.
        
        Returns:
            HealthResponse: Service health information
        """
        # Check ephemeris file availability (cached)
        current_time = time.time()
        if (self._ephemeris_validation_cache is None or 
            self._last_validation_check is None or
            current_time - self._last_validation_check > self._validation_cache_ttl):
            
            self._ephemeris_validation_cache = validate_ephemeris_files()
            self._last_validation_check = current_time
        
        ephemeris_available = all(self._ephemeris_validation_cache.values())
        
        return HealthResponse(
            status="healthy" if ephemeris_available else "degraded",
            version="1.0.0",
            ephemeris_available=ephemeris_available,
            uptime=current_time - self.start_time
        )
    
    def _normalize_coordinate_input(self, coord_input: CoordinateInput, coord_type: str) -> float:
        """
        Normalize coordinate input to decimal degrees.
        
        Args:
            coord_input: Coordinate input model
            coord_type: 'latitude' or 'longitude' for validation
            
        Returns:
            Normalized coordinate in decimal degrees
            
        Raises:
            InputValidationError: If coordinate cannot be normalized
        """
        try:
            if coord_input.decimal is not None:
                return float(coord_input.decimal)
            elif coord_input.dms is not None:
                return coord_input.dms  # Will be handled by Subject class
            elif coord_input.components is not None:
                # Convert components to decimal
                degrees = float(coord_input.components.get('degrees', 0))
                minutes = float(coord_input.components.get('minutes', 0))
                seconds = float(coord_input.components.get('seconds', 0))
                direction = coord_input.components.get('direction', '')
                
                decimal = degrees + minutes/60 + seconds/3600
                
                # Apply direction
                if isinstance(direction, str):
                    direction = direction.upper()
                    if direction in ['S', 'W']:
                        decimal = -decimal
                
                return decimal
            else:
                raise InputValidationError(f"No coordinate data provided for {coord_type}")
                
        except (ValueError, TypeError, KeyError) as e:
            raise InputValidationError(f"Invalid {coord_type} coordinate: {str(e)}") from e
    
    def _normalize_datetime_input(self, dt_input: DateTimeInput) -> Union[str, float, datetime]:
        """
        Normalize datetime input.
        
        Args:
            dt_input: Datetime input model
            
        Returns:
            Normalized datetime value for Subject class
            
        Raises:
            InputValidationError: If datetime cannot be normalized
        """
        try:
            if dt_input.iso_string is not None:
                return dt_input.iso_string
            elif dt_input.julian_day is not None:
                return float(dt_input.julian_day)
            elif dt_input.components is not None:
                comp = dt_input.components
                return datetime(
                    year=comp['year'],
                    month=comp['month'],
                    day=comp['day'],
                    hour=comp.get('hour', 0),
                    minute=comp.get('minute', 0),
                    second=comp.get('second', 0)
                )
            else:
                raise InputValidationError("No datetime data provided")
                
        except (ValueError, TypeError, KeyError) as e:
            raise InputValidationError(f"Invalid datetime: {str(e)}") from e
    
    def _normalize_timezone_input(self, tz_input: Optional[TimezoneInput]) -> Optional[Union[str, float]]:
        """
        Normalize timezone input.
        
        Args:
            tz_input: Timezone input model
            
        Returns:
            Normalized timezone value for Subject class
        """
        if tz_input is None:
            return None
            
        if tz_input.name is not None:
            return tz_input.name
        elif tz_input.utc_offset is not None:
            return float(tz_input.utc_offset)
        elif tz_input.auto_detect:
            return None  # Let Subject class handle auto-detection
        
        return None
    
    def _create_subject_from_request(self, subject_req: SubjectRequest) -> Subject:
        """
        Create Subject instance from API request.
        
        Args:
            subject_req: Subject request model
            
        Returns:
            Subject instance
            
        Raises:
            InputValidationError: If subject creation fails
        """
        try:
            # Normalize inputs
            latitude = self._normalize_coordinate_input(subject_req.latitude, 'latitude')
            longitude = self._normalize_coordinate_input(subject_req.longitude, 'longitude')
            dt = self._normalize_datetime_input(subject_req.datetime)
            timezone = self._normalize_timezone_input(subject_req.timezone)
            
            # Create subject
            subject = Subject(
                name=subject_req.name,
                datetime=dt,
                latitude=latitude,
                longitude=longitude,
                altitude=subject_req.altitude or 0.0,
                timezone=timezone
            )
            
            if not subject.is_valid():
                errors = subject.get_validation_errors()
                raise InputValidationError(f"Subject validation failed: {', '.join(errors)}")
            
            return subject
            
        except Exception as e:
            if isinstance(e, InputValidationError):
                raise
            raise InputValidationError(f"Failed to create subject: {str(e)}") from e
    
    def _format_planet_response(self, planet_id: int, planet_data: Any) -> PlanetResponse:
        """
        Format planet data for API response.
        
        Args:
            planet_id: Planet ID
            planet_data: Planet position data
            
        Returns:
            Formatted planet response
        """
        # Extract element and modality as strings
        element = getattr(planet_data, 'element', None)
        if isinstance(element, dict):
            element = element.get('name', None)
        
        modality = getattr(planet_data, 'modality', None)
        if isinstance(modality, dict):
            modality = modality.get('name', None)
        
        house_position = getattr(planet_data, 'house_position', None)
        house_number = house_position.get('number') if isinstance(house_position, dict) else None
        
        return PlanetResponse(
            name=PLANET_NAMES.get(planet_id, f"Object {planet_id}"),
            longitude=planet_data.longitude,
            latitude=planet_data.latitude,
            distance=planet_data.distance,
            longitude_speed=getattr(planet_data, 'longitude_speed', None),
            sign_name=getattr(planet_data, 'sign_name', None),
            sign_longitude=getattr(planet_data, 'sign_longitude', None),
            house_number=house_number,
            element=element,
            modality=modality
        )
    
    def _format_chart_response(self, chart_data: Any, calculation_time: datetime) -> NatalChartResponse:
        """
        Format chart data for API response.
        
        Args:
            chart_data: Chart calculation results
            calculation_time: When calculation was performed
            
        Returns:
            Formatted natal chart response
        """
        # Format subject data
        subject_response = SubjectResponse(
            name=chart_data.subject.name,
            datetime=chart_data.subject.datetime.isoformat(),
            julian_day=chart_data.subject.julian_day,
            latitude=chart_data.subject.latitude,
            longitude=chart_data.subject.longitude,
            altitude=chart_data.subject.altitude,
            timezone_name=chart_data.subject.timezone_name,
            utc_offset=chart_data.subject.utc_offset
        )
        
        # Format planets
        planets_response = {}
        for planet_id, planet_data in chart_data.planets.items():
            planet_name = PLANET_NAMES.get(planet_id, f"Object {planet_id}")
            planets_response[planet_name] = self._format_planet_response(planet_id, planet_data)
        
        # Format houses
        # Normalize house cusps to 12 for API response (tests expect 12)
        cusps = chart_data.houses.house_cusps
        if isinstance(cusps, list) and len(cusps) == 13 and cusps[0] == 0:
            cusps = cusps[1:]
        houses_response = HousesResponse(
            system=chart_data.houses.system_code,
            cusps=cusps
        )
        
        # Format angles
        angles_response = AnglesResponse(
            ascendant=chart_data.angles.ascendant,
            midheaven=chart_data.angles.midheaven,
            descendant=chart_data.angles.descendant,
            imum_coeli=chart_data.angles.imum_coeli
        )
        
        # Format aspects
        aspects_response = []
        for aspect in chart_data.aspects:
            aspects_response.append(AspectResponse(
                object1=aspect.object1_name,
                object2=aspect.object2_name,
                aspect=aspect.aspect_name,
                angle=aspect.angle,
                orb=aspect.orb,
                applying=aspect.applying
            ))
        
        return NatalChartResponse(
            success=True,
            subject=subject_response,
            planets=planets_response,
            houses=houses_response,
            angles=angles_response,
            aspects=aspects_response,
            calculation_time=calculation_time.isoformat(),
            chart_type=chart_data.chart_type
        )
    
    def calculate_natal_chart(self, request: NatalChartRequest) -> NatalChartResponse:
        """
        Calculate natal chart from API request.
        
        Args:
            request: Natal chart request
            
        Returns:
            Complete natal chart response
            
        Raises:
            InputValidationError: If input validation fails
            CalculationError: If chart calculation fails
        """
        calculation_start = datetime.now()
        
        try:
            # Create subject from request
            subject = self._create_subject_from_request(request.subject)
            
            # Create natal chart with configuration
            config = request.configuration or {}
            chart = NatalChart(
                subject=subject,
                house_system=getattr(config, 'house_system', 'P'),
                include_asteroids=getattr(config, 'include_asteroids', True),
                include_nodes=getattr(config, 'include_nodes', True),
                include_lilith=getattr(config, 'include_lilith', True),
                aspect_orbs=getattr(config, 'aspect_orbs', None),
                parallel_processing=getattr(config, 'parallel_processing', True)
            )
            
            # Calculate chart
            chart_data = chart.calculate()
            
            # Format and return response
            return self._format_chart_response(chart_data, calculation_start)
            
        except InputValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Chart calculation failed: {str(e)}") from e
    
    def create_error_response(self, error: Exception) -> ErrorResponse:
        """
        Create standardized error response.
        
        Args:
            error: Exception that occurred
            
        Returns:
            Formatted error response
        """
        if isinstance(error, InputValidationError):
            return ErrorResponse(
                error="validation_error",
                message=str(error),
                details={"type": "input_validation"}
            )
        elif isinstance(error, CalculationError):
            return ErrorResponse(
                error="calculation_error", 
                message=str(error),
                details={"type": "ephemeris_calculation"}
            )
        else:
            return ErrorResponse(
                error="internal_error",
                message="An unexpected error occurred",
                details={"type": "unknown", "original_message": str(error)}
            )


# Global service instance
ephemeris_service = EphemerisService()