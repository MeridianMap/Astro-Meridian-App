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
from ..core.ephemeris.const import PLANET_NAMES, get_sign_from_longitude, get_sign_name
from ..core.ephemeris.tools.ephemeris import validate_ephemeris_files, analyze_retrograde_motion
from ..core.ephemeris.tools.aspects import AspectCalculator
from ..core.ephemeris.tools.orb_systems import OrbSystemManager
from ..core.ephemeris.tools.arabic_parts import ArabicPartsCalculator
from ..core.ephemeris.tools.arabic_parts_models import ArabicPartsRequest
from ..core.ephemeris.tools.fixed_stars import FixedStarCalculator


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
    
    # House system code to name mapping
    _HOUSE_SYSTEM_NAMES = {
        'P': 'placidus',
        'K': 'koch', 
        'O': 'porphyrius',
        'R': 'regiomontanus',
        'C': 'campanus',
        'A': 'equal',
        'V': 'vehlow',
        'W': 'whole_sign',
        'T': 'topocentric',
        'M': 'morinus',
        'H': 'horizontal',
        'B': 'alcabitus',
        'G': 'gauquelin_sectors'
    }
    
    def __init__(self):
        """Initialize ephemeris service."""
        self.start_time = time.time()
        self._ephemeris_validation_cache: Optional[Dict[str, bool]] = None
        self._last_validation_check: Optional[float] = None
        self._validation_cache_ttl = 300  # 5 minutes
        
        # Set up Swiss Ephemeris library path for fixed stars FIRST
        self._setup_swiss_ephemeris_path()
        
        # Force reload of fixed stars module to pick up new path
        import sys
        if 'app.core.ephemeris.tools.fixed_stars' in sys.modules:
            del sys.modules['app.core.ephemeris.tools.fixed_stars']
        
        # Initialize predictive service integration
        self._predictive_available = True
        try:
            from .predictive_service import predictive_service
            self._predictive_service = predictive_service
        except ImportError:
            self._predictive_available = False
            self._predictive_service = None
        
        # Initialize fixed star calculator AFTER path setup
        from ..core.ephemeris.tools.fixed_stars import FixedStarCalculator
        self.fixed_star_calculator = FixedStarCalculator()
    
    def _get_sign_name(self, longitude: float) -> str:
        """Get zodiac sign name from longitude."""
        sign_number = get_sign_from_longitude(longitude)
        return get_sign_name(sign_number)
    
    def _get_sign_position(self, longitude: float) -> float:
        """Get position within zodiac sign from longitude."""
        return longitude % 30.0
    
    def _normalize_house_system_code(self, system_code: str) -> str:
        """
        Normalize house system code to canonical name.
        
        Args:
            system_code: House system code (e.g., 'P', 'K', etc.)
            
        Returns:
            Canonical house system name (e.g., 'placidus', 'koch', etc.)
        """
        if system_code in self._HOUSE_SYSTEM_NAMES:
            return self._HOUSE_SYSTEM_NAMES[system_code]
        else:
            # If already a canonical name, return as-is
            # Otherwise, default to placidus
            canonical_names = set(self._HOUSE_SYSTEM_NAMES.values())
            return system_code if system_code in canonical_names else 'placidus'
    
    def _setup_swiss_ephemeris_path(self):
        """Set up Swiss Ephemeris library path for enhanced fixed star calculations."""
        import os
        import swisseph as swe
        
        # Find project root by looking for specific folders
        current_dir = os.path.dirname(__file__)
        project_root = current_dir
        
        # Go up directories until we find the Swiss Eph Library Files folder
        max_levels = 10
        for _ in range(max_levels):
            potential_swe_path = os.path.join(project_root, "Swiss Eph Library Files")
            if os.path.exists(potential_swe_path):
                swe_lib_path = potential_swe_path
                break
            parent = os.path.dirname(project_root)
            if parent == project_root:  # Reached filesystem root
                break
            project_root = parent
        else:
            # Fallback - try absolute path based on known project location
            swe_lib_path = "C:/Users/jacks/OneDrive/Desktop/MERIDIAN/Meridian DEV/ASTRO MERIDIAN APP V1.0/Swiss Eph Library Files"
        
        if os.path.exists(swe_lib_path):
            # Set environment variable
            os.environ['SE_EPHE_PATH'] = swe_lib_path
            
            # Also try to set path using any available Swiss Ephemeris method
            try:
                # Some versions might have swe.set_ephemeris_path()
                if hasattr(swe, 'set_ephemeris_path'):
                    swe.set_ephemeris_path(swe_lib_path)
            except:
                pass  # Not critical if this method doesn't exist
                
            # Verify star catalog exists
            star_catalog = os.path.join(swe_lib_path, "sefstars.txt")
            if os.path.exists(star_catalog):
                print(f"Swiss Ephemeris library path configured: {swe_lib_path}")
                print(f"Star catalog found: {os.path.getsize(star_catalog):,} bytes")
            else:
                print(f"Warning: Swiss Ephemeris path set but no star catalog found at {star_catalog}")
        else:
            print(f"Swiss Ephemeris library folder not found at: {swe_lib_path}")
    
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
            predictive_features_available=self._predictive_available,
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
    
    def _get_timezone_offset(self, subject) -> Optional[float]:
        """
        Calculate UTC offset for timezone-aware datetime handling.
        
        Args:
            subject: Subject instance with timezone information
            
        Returns:
            UTC offset in hours, or None if cannot be determined
        """
        try:
            import pytz
            
            if hasattr(subject, 'timezone_name') and subject.timezone_name:
                # Get timezone from name
                tz = pytz.timezone(subject.timezone_name)
                
                # Use the subject's datetime to get the correct offset (handles DST)
                if hasattr(subject, 'datetime') and subject.datetime:
                    dt_naive = subject.datetime.replace(tzinfo=None)
                    dt_localized = tz.localize(dt_naive)
                    offset_seconds = dt_localized.utcoffset().total_seconds()
                    return offset_seconds / 3600  # Convert to hours
                    
            elif hasattr(subject, 'utc_offset') and subject.utc_offset is not None:
                return float(subject.utc_offset)
                
        except Exception:
            # If timezone calculation fails, return existing value
            if hasattr(subject, 'utc_offset'):
                return subject.utc_offset
            
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
    
    def _format_planet_response(self, planet_id: int, planet_data: Any, retrograde_analysis: Optional[Dict] = None, dignities_data: Optional[Dict] = None) -> PlanetResponse:
        """
        Format planet data for API response.
        
        Args:
            planet_id: Planet ID
            planet_data: Planet position data
            retrograde_analysis: Optional retrograde analysis data
            dignities_data: Optional dignities analysis data
            
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
        
        # Get planet name for lookups
        planet_name = PLANET_NAMES.get(planet_id, f"Object {planet_id}")
        
        # Extract retrograde information from planet speed
        is_retrograde = False
        motion_type = 'direct'
        longitude_speed = round(getattr(planet_data, 'longitude_speed', 0), 6) if getattr(planet_data, 'longitude_speed', None) is not None else None
        
        # Determine retrograde status directly from longitude speed (< 0 = retrograde)
        if longitude_speed is not None and longitude_speed < 0:
            is_retrograde = True
            motion_type = 'retrograde'
            
        # Override with retrograde analysis data if available (for more complex cases)
        if retrograde_analysis:
            retrograde_bodies = retrograde_analysis.get('retrograde_bodies', [])
            for body_data in retrograde_bodies:
                if isinstance(body_data, dict) and body_data.get('name', '').lower() == planet_name.lower():
                    is_retrograde = True
                    motion_type = 'retrograde'
                    break
        
        # Extract dignity information from analysis data or planet data
        dignity_info = None
        if dignities_data:
            planet_dignities = dignities_data.get('planet_dignities', {})
            planet_key = planet_name.lower().replace(' ', '_')
            if planet_key in planet_dignities:
                dignities = planet_dignities[planet_key]
                from ..api.models.schemas import EssentialDignityInfo
                dignity_info = EssentialDignityInfo(**dignities)
        
        if dignity_info is None:
            # Try to extract from planet data directly
            dignities = getattr(planet_data, 'essential_dignities', None)
            if dignities:
                from ..api.models.schemas import EssentialDignityInfo
                dignity_info = EssentialDignityInfo(**dignities)
        
        # Normalize precision for consistency (6 decimal places for angles)
        longitude = round(planet_data.longitude, 6) if planet_data.longitude is not None else None
        latitude = round(planet_data.latitude, 6) if planet_data.latitude is not None else None
        sign_longitude = round(getattr(planet_data, 'sign_longitude', 0), 6) if getattr(planet_data, 'sign_longitude', None) is not None else None
        
        # Debug: Print values being set
        if planet_name == 'Mercury':
            print(f"DEBUG _format_planet_response - Creating Mercury PlanetResponse:")
            print(f"  is_retrograde: {is_retrograde} (type: {type(is_retrograde)})")
            print(f"  motion_type: {motion_type} (type: {type(motion_type)})")
            print(f"  longitude_speed: {longitude_speed}")
        
        planet_response = PlanetResponse(
            name=planet_name,
            longitude=longitude,
            latitude=latitude,
            distance=planet_data.distance,  # Keep distance as-is (already in AU)
            longitude_speed=longitude_speed,
            is_retrograde=is_retrograde,
            motion_type=motion_type,
            sign_name=getattr(planet_data, 'sign_name', None),
            sign_longitude=sign_longitude,
            house_number=house_number,
            element=element,
            modality=modality,
            essential_dignities=dignity_info
        )
        
        # Debug: Verify object after creation
        if planet_name == 'Mercury':
            print(f"DEBUG _format_planet_response - Created Mercury PlanetResponse:")
            print(f"  is_retrograde: {planet_response.is_retrograde}")
            print(f"  motion_type: {planet_response.motion_type}")
        
        return planet_response
    
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
        # Calculate proper UTC offset if needed
        utc_offset = chart_data.subject.utc_offset
        if utc_offset is None:
            utc_offset = self._get_timezone_offset(chart_data.subject)
        
        subject_response = SubjectResponse(
            name=chart_data.subject.name,
            datetime=chart_data.subject.datetime.isoformat(),
            julian_day=round(chart_data.subject.julian_day, 6),
            latitude=round(chart_data.subject.latitude, 6),
            longitude=round(chart_data.subject.longitude, 6),
            altitude=chart_data.subject.altitude,
            timezone_name=chart_data.subject.timezone_name,
            utc_offset=round(utc_offset, 1) if utc_offset is not None else None
        )
        
        # Format planets
        planets_response = {}
        for planet_id, planet_data in chart_data.planets.items():
            planet_name = PLANET_NAMES.get(planet_id, f"Object {planet_id}")
            planets_response[planet_name] = self._format_planet_response(planet_id, planet_data, None, None)
        
        # Format houses
        # Normalize house cusps to 12 for API response (tests expect 12)
        cusps = chart_data.houses.house_cusps
        if isinstance(cusps, list) and len(cusps) == 13 and cusps[0] == 0:
            cusps = cusps[1:]
        houses_response = HousesResponse(
            system=self._normalize_house_system_code(chart_data.houses.system_code),
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
        
        # Prepare summary metadata
        features_included = ["planets", "houses", "angles", "aspects"]
        # Note: request object not available in this context, using static features
        features_included.extend(["aspect_analysis", "essential_dignities"])
        
        summary_metadata = {
            "data_version": "1.0",
            "api_version": "1.0.0", 
            "epoch": calculation_time.isoformat(),
            "swiss_ephemeris_version": getattr(chart_data, 'se_version', 'unknown'),
            "source": "Meridian Ephemeris Engine",
            "calculation_method": "Swiss Ephemeris + Meridian Enhancements",
            "total_planets": len(planets_response),
            "total_aspects": len(aspects_response),
            "house_system": houses_response.system
        }
        
        return NatalChartResponse(
            success=True,
            subject=subject_response,
            planets=planets_response,
            houses=houses_response,
            angles=angles_response,
            aspects=aspects_response,
            calculation_time=calculation_time.isoformat(),
            chart_type=chart_data.chart_type,
            summary=summary_metadata,
            features_included=features_included
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
                house_system=self._normalize_house_system_code(getattr(config, 'house_system', 'P')),
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
    
    def calculate_natal_chart_enhanced(
        self, 
        request: NatalChartRequest,
        include_aspects: bool = True,
        aspect_orb_preset: str = "traditional",
        custom_orb_config: Optional[Dict] = None,
        include_arabic_parts: bool = False,
        arabic_parts_selection: List[str] = None,
        include_all_traditional_parts: bool = False,
        custom_arabic_formulas: Optional[Dict[str, Dict[str, str]]] = None,
        include_south_nodes: bool = True,
        include_retrograde_analysis: bool = True,
        include_dignities: bool = False,
        include_fixed_stars: bool = False,
        fixed_star_magnitude_limit: float = 2.0
    ) -> Dict[str, Any]:
        """
        Calculate natal chart with enhanced features including aspects, Arabic parts, fixed stars, and analysis.
        
        Args:
            request: Natal chart request data
            include_aspects: Include aspect calculations
            aspect_orb_preset: Orb system preset ("traditional", "modern", "tight")
            custom_orb_config: Custom orb configuration (overrides preset)
            include_arabic_parts: Include Arabic parts calculations
            arabic_parts_selection: List of specific Arabic parts to calculate
            include_all_traditional_parts: Calculate all 16 traditional lots
            custom_arabic_formulas: Custom lot formulas (name -> {day_formula, night_formula})
            include_south_nodes: Include calculated South Node positions
            include_retrograde_analysis: Include retrograde motion analysis
            include_dignities: Include essential dignities calculations
            include_fixed_stars: Include fixed star positions and aspects
            fixed_star_magnitude_limit: Maximum magnitude for automatic star selection
            
        Returns:
            Enhanced natal chart response with additional features
            
        Raises:
            InputValidationError: If input validation fails
            CalculationError: If chart calculation fails
        """
        try:
            calculation_start = time.time()
            
            # Get standard natal chart
            standard_response = self.calculate_natal_chart(request)
            
            # Extract chart data for enhancement
            chart_dict = standard_response.model_dump() if hasattr(standard_response, 'model_dump') else standard_response
            
            # Add South Nodes if requested
            if include_south_nodes and 'planets' in chart_dict:
                from ..core.ephemeris.tools.ephemeris import get_point
                from ..core.ephemeris.tools.ephemeris import julian_day_from_datetime
                
                # Get Julian Day from the chart data
                julian_day = chart_dict.get('julian_day')
                if not julian_day:
                    # Calculate from datetime if not present
                    subject_data = chart_dict.get('subject', {})
                    if 'datetime' in subject_data:
                        julian_day = julian_day_from_datetime(
                            datetime.fromisoformat(subject_data['datetime'].replace('Z', '+00:00'))
                        )
                
                if julian_day:
                    # Add Mean South Node
                    planet_names = [getattr(planet, 'name', str(planet)) for planet in chart_dict['planets']]
                    if 'Mean Node' in planet_names:
                        try:
                            south_node_mean = get_point('south_node', julian_day)
                            chart_dict['planets'].append(self._format_planet_data(south_node_mean, 'south_node_mean'))
                        except Exception as e:
                            # Log but don't fail the entire calculation
                            pass
                    
                    # Add True South Node
                    if 'True Node' in planet_names:
                        try:
                            south_node_true = get_point('true_south_node', julian_day)
                            chart_dict['planets'].append(self._format_planet_data(south_node_true, 'south_node_true'))
                        except Exception as e:
                            # Log but don't fail the entire calculation
                            pass
            
            # Add retrograde analysis if requested
            if include_retrograde_analysis and 'planets' in chart_dict:
                from ..core.ephemeris.tools.ephemeris import analyze_retrograde_motion
                
                planet_positions = {}
                for planet in chart_dict['planets']:
                    planet_name = getattr(planet, 'name', str(planet))
                    if hasattr(planet, 'longitude_speed'):
                        planet_positions[planet_name.lower().replace(' ', '_')] = planet
                
                if planet_positions:  # Only analyze if we have planets with speed data
                    chart_dict['retrograde_analysis'] = analyze_retrograde_motion(
                        planet_positions, 
                        chart_dict.get('julian_day')
                    )
            
            # Add aspect calculations if requested
            if include_aspects and 'planets' in chart_dict:
                try:
                    # Generate cache key for aspect calculations
                    aspect_cache_key = self._generate_aspect_cache_key(
                        chart_dict['planets'], aspect_orb_preset, custom_orb_config
                    )
                    
                    # Try to get cached aspects first
                    cached_aspects = self._get_cached_aspects(aspect_cache_key)
                    
                    if cached_aspects:
                        # Use cached results
                        chart_dict['aspects'] = cached_aspects['aspects']
                        chart_dict['aspect_matrix'] = cached_aspects['aspect_matrix']
                    else:
                        # Calculate aspects and cache results
                        orb_manager = OrbSystemManager()
                        
                        # Get orb configuration - use custom if provided, otherwise use preset
                        if custom_orb_config:
                            orb_config = orb_manager.create_custom_orb_config(custom_orb_config)
                        else:
                            orb_config = orb_manager.get_orb_preset(aspect_orb_preset)
                        
                        # Initialize aspect calculator
                        aspect_calculator = AspectCalculator(orb_config)
                        
                        # Convert planets data to PlanetPosition objects for aspect calculation
                        planet_positions = self._convert_planets_to_positions(chart_dict['planets'])
                        
                        if planet_positions:
                            # Calculate aspect matrix
                            aspect_matrix = aspect_calculator.calculate_aspect_matrix(planet_positions)
                            
                            # Format aspects for response
                            formatted_aspects = self._format_aspects_for_response(aspect_matrix.aspects)
                            aspect_matrix_data = {
                                'total_aspects': aspect_matrix.total_aspects,
                                'major_aspects': aspect_matrix.major_aspects,
                                'minor_aspects': aspect_matrix.minor_aspects,
                                'orb_config_used': aspect_matrix.orb_config_used,
                                'calculation_time_ms': aspect_matrix.calculation_time_ms
                            }
                            
                            # Cache the results (24 hour TTL)
                            self._cache_aspects(aspect_cache_key, {
                                'aspects': formatted_aspects,
                                'aspect_matrix': aspect_matrix_data
                            }, ttl=86400)
                            
                            # Update chart data
                            chart_dict['aspects'] = formatted_aspects
                            chart_dict['aspect_matrix'] = aspect_matrix_data
                        
                except Exception as e:
                    # Log but don't fail the entire calculation
                    import logging
                    logging.warning(f"Aspect calculation failed: {e}")
                    # Keep original aspects from standard chart
            
            # Add Arabic parts calculations if requested
            if include_arabic_parts:
                try:
                    # Create Arabic parts request
                    parts_request = ArabicPartsRequest(
                        requested_parts=arabic_parts_selection or ["fortune", "spirit"],
                        include_all_traditional=include_all_traditional_parts,
                        custom_formulas=custom_arabic_formulas,
                        include_metadata=True,
                        metadata_level="standard"
                    )
                    
                    # Initialize Arabic parts calculator
                    arabic_calculator = ArabicPartsCalculator()
                    
                    # Convert chart data to proper format for calculation
                    chart_data = self._convert_dict_to_chart_data(chart_dict)
                    
                    # Calculate Arabic parts
                    arabic_result = arabic_calculator.calculate_arabic_parts(
                        chart_data, parts_request
                    )
                    
                    # Format results for response - structure expected by route handler
                    parts_by_name = {}
                    for part in arabic_result.calculated_parts:
                        part_dict = part.to_dict()
                        parts_by_name[part.name] = part_dict
                    
                    chart_dict['arabic_parts'] = {
                        'arabic_parts': parts_by_name,
                        'sect_determination': arabic_result.sect_determination.to_dict(),
                        'formulas_used': arabic_result.formulas_used,
                        'calculation_time_ms': arabic_result.calculation_time_ms,
                        'total_parts_calculated': arabic_result.total_parts_calculated
                    }
                    
                except Exception as e:
                    # Log but don't fail the entire calculation
                    import logging
                    logging.warning(f"Arabic parts calculation failed: {e}")
                    # Add empty results to maintain response structure
                    chart_dict['arabic_parts'] = []
                    chart_dict['arabic_parts_metadata'] = {
                        'calculation_error': str(e)
                    }
            
            # Add essential dignities calculation if requested
            if include_dignities:
                try:
                    from ..core.ephemeris.tools.dignities import EssentialDignitiesCalculator
                    
                    # Initialize dignities calculator - using traditional rulers (no modern planets)
                    dignities_calculator = EssentialDignitiesCalculator(use_modern_rulers=False)
                    
                    # Convert chart planets data to proper format for dignities calculation
                    planets_data_for_dignities = {}
                    if isinstance(chart_dict.get('planets'), dict):
                        # API format: planets as dict by name
                        for planet_name, planet_data in chart_dict['planets'].items():
                            # Find planet ID from name
                            from ..core.ephemeris.const import PLANET_NAMES
                            planet_id = None
                            for pid, name in PLANET_NAMES.items():
                                if name == planet_name:
                                    planet_id = pid
                                    break
                            
                            if planet_id is not None:
                                planets_data_for_dignities[planet_id] = planet_data
                    
                    # Determine if day chart (for triplicity calculation)
                    # Day chart = Sun above horizon (houses 7-12)
                    is_day_chart = True  # Default
                    sun_data = chart_dict['planets'].get('Sun')
                    if sun_data and 'angles' in chart_dict:
                        try:
                            # Get Sun longitude and Ascendant
                            sun_longitude = getattr(sun_data, 'longitude', sun_data.get('longitude', 0))
                            angles = chart_dict['angles']
                            ascendant = getattr(angles, 'ascendant', angles.get('ascendant', 0))
                            
                            # Calculate if Sun is above horizon (traditional method)
                            # Day chart = Sun in houses 7-12 (above horizon)
                            # Night chart = Sun in houses 1-6 (below horizon)
                            
                            # Method 1: Check which side of ASC-DESC axis Sun is on
                            # Descendant is 180° from Ascendant
                            descendant = (ascendant + 180) % 360
                            
                            # Sun is above horizon if it's between DESC and ASC (going clockwise)
                            # This corresponds to houses 7, 8, 9, 10, 11, 12
                            if descendant > ascendant:
                                # Normal case: DESC > ASC (e.g., DESC=270°, ASC=90°)
                                is_day_chart = descendant <= sun_longitude or sun_longitude <= ascendant
                            else:
                                # Wrapped case: DESC < ASC (e.g., DESC=30°, ASC=210°)  
                                is_day_chart = descendant <= sun_longitude <= ascendant
                        except Exception:
                            # If calculation fails, use time of day as fallback
                            birth_time = getattr(chart_data.subject, 'datetime', None)
                            if birth_time:
                                hour = birth_time.hour
                                is_day_chart = 6 <= hour <= 18  # Rough day/night by clock time
                    
                    # Calculate dignities for all planets
                    dignity_results = dignities_calculator.calculate_batch_dignities(
                        planets_data_for_dignities, is_day_chart
                    )
                    
                    # Add dignity info to each planet in chart_dict
                    for planet_name, planet_data in chart_dict['planets'].items():
                        # Find corresponding dignity result
                        planet_id = None
                        from ..core.ephemeris.const import PLANET_NAMES
                        for pid, name in PLANET_NAMES.items():
                            if name == planet_name:
                                planet_id = pid
                                break
                        
                        if planet_id in dignity_results:
                            dignity_info = dignity_results[planet_id]
                            
                            # Only include dignities if there's meaningful information
                            # (skip if all scores are zero - typical for non-planetary bodies)
                            if (dignity_info.total_score != 0 or 
                                dignity_info.dignities_held or 
                                dignity_info.debilities_held):
                                
                                # Add dignity info to planet data
                                if hasattr(planet_data, '__dict__'):
                                    planet_data.essential_dignities = {
                                        'total_score': dignity_info.total_score,
                                        'rulership_score': dignity_info.rulership_score,
                                        'exaltation_score': dignity_info.exaltation_score,
                                        'triplicity_score': dignity_info.triplicity_score,
                                        'term_score': dignity_info.term_score,
                                        'face_score': dignity_info.face_score,
                                        'dignities_held': dignity_info.dignities_held,
                                        'debilities_held': dignity_info.debilities_held
                                    }
                                elif isinstance(planet_data, dict):
                                    planet_data['essential_dignities'] = {
                                        'total_score': dignity_info.total_score,
                                        'rulership_score': dignity_info.rulership_score,
                                        'exaltation_score': dignity_info.exaltation_score,
                                        'triplicity_score': dignity_info.triplicity_score,
                                        'term_score': dignity_info.term_score,
                                        'face_score': dignity_info.face_score,
                                        'dignities_held': dignity_info.dignities_held,
                                        'debilities_held': dignity_info.debilities_held
                                    }
                    
                except Exception as e:
                    # Log but don't fail the entire calculation
                    import logging
                    logging.warning(f"Essential dignities calculation failed: {e}")
            
            # Add fixed stars if requested
            if include_fixed_stars:
                try:
                    fixed_stars_result = self.calculate_fixed_stars(
                        request, 
                        star_names=None,  # Use available stars
                        include_aspects=True,
                        magnitude_limit=fixed_star_magnitude_limit
                    )
                    
                    chart_dict['fixed_stars'] = fixed_stars_result
                    
                except Exception as e:
                    # Log but don't fail the entire calculation
                    import logging
                    logging.warning(f"Fixed stars calculation failed: {e}")
                    chart_dict['fixed_stars'] = {
                        'stars': {},
                        'count': 0,
                        'selected_stars_count': 0,
                        'calculation_error': str(e)
                    }
            
            # Update calculation time
            calculation_time = time.time() - calculation_start
            chart_dict['calculation_time'] = calculation_time
            
            # Integrate enhanced features back into planet responses
            if 'planets' in chart_dict:
                retrograde_analysis = chart_dict.get('retrograde_analysis')
                dignities_data = chart_dict.get('dignities')
                
                # Update each planet with enhanced data
                for planet_name, planet_data in chart_dict['planets'].items():
                    # Add retrograde information
                    is_retrograde = False
                    motion_type = 'direct'
                    longitude_speed = planet_data.get('longitude_speed', 0)
                    
                    # Determine from speed first
                    if longitude_speed is not None and longitude_speed < 0:
                        is_retrograde = True
                        motion_type = 'retrograde'
                    
                    # Override with retrograde analysis if available
                    if retrograde_analysis:
                        retrograde_bodies = retrograde_analysis.get('retrograde_bodies', [])
                        for body_data in retrograde_bodies:
                            if isinstance(body_data, dict) and body_data.get('name', '').lower() == planet_name.lower():
                                is_retrograde = True
                                motion_type = 'retrograde'
                                break
                    
                    # Update planet data with retrograde info
                    planet_data['is_retrograde'] = is_retrograde
                    planet_data['motion_type'] = motion_type
                    
                    # Add dignities information
                    if dignities_data and 'planet_dignities' in dignities_data:
                        planet_key = planet_name.lower().replace(' ', '_')
                        if planet_key in dignities_data['planet_dignities']:
                            planet_dignities = dignities_data['planet_dignities'][planet_key]
                            planet_data['essential_dignities'] = planet_dignities
                        # Skip empty dignities - no longer providing default empty structure
            
            return chart_dict
            
        except InputValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Enhanced chart calculation failed: {str(e)}") from e
    
    def _convert_planets_to_positions(self, planets_data: Dict[str, Any]) -> List[Any]:
        """
        Convert planets data to PlanetPosition objects for aspect calculation.
        
        Args:
            planets_data: Dictionary of planet data from chart response
            
        Returns:
            List of PlanetPosition objects
        """
        from ..core.ephemeris.tools.ephemeris import PlanetPosition
        from ..core.ephemeris.const import PLANET_NAMES
        
        positions = []
        
        # Get reverse planet name mapping
        name_to_id = {v: k for k, v in PLANET_NAMES.items()}
        
        for planet_name, planet_data in planets_data.items():
            # Get planet ID from name
            planet_id = name_to_id.get(planet_name, 0)
            
            # Extract data from planet response
            if hasattr(planet_data, 'longitude'):
                longitude = planet_data.longitude
                latitude = planet_data.latitude
                distance = planet_data.distance
                longitude_speed = getattr(planet_data, 'longitude_speed', 0.0)
            else:
                # Handle dictionary format
                longitude = planet_data.get('longitude', 0.0)
                latitude = planet_data.get('latitude', 0.0) 
                distance = planet_data.get('distance', 1.0)
                longitude_speed = planet_data.get('longitude_speed', 0.0)
            
            # Create PlanetPosition object
            position = PlanetPosition(
                longitude=longitude,
                latitude=latitude,
                distance=distance,
                longitude_speed=longitude_speed,
                planet_id=planet_id
            )
            
            positions.append(position)
        
        return positions
    
    def _format_aspects_for_response(self, aspects: List[Any]) -> List[Dict[str, Any]]:
        """
        Format aspect objects for API response.
        
        Args:
            aspects: List of Aspect objects
            
        Returns:
            List of formatted aspect dictionaries
        """
        formatted_aspects = []
        
        for aspect in aspects:
            formatted_aspect = {
                'object1': aspect.planet1.title().replace('_', ' '),
                'object2': aspect.planet2.title().replace('_', ' '),
                'aspect': aspect.aspect_type.title().replace('_', ' '),
                'angle': round(aspect.angle, 2),
                'orb': round(aspect.orb_percentage / 100 * aspect.orb_used, 2),
                'applying': bool(aspect.is_applying),  # Ensure Python bool, not numpy.bool_
                'strength': round(aspect.strength, 3),
                'exact_angle': aspect.exact_angle,
                'orb_percentage': round(aspect.orb_percentage, 1)
            }
            formatted_aspects.append(formatted_aspect)
        
        return formatted_aspects
    
    def _generate_aspect_cache_key(self, planets_data: Dict[str, Any], orb_preset: str, custom_orb_config: Optional[Dict]) -> str:
        """
        Generate cache key for aspect calculations.
        
        Args:
            planets_data: Planet position data
            orb_preset: Orb preset name
            custom_orb_config: Custom orb configuration
            
        Returns:
            Cache key string
        """
        import hashlib
        import json
        
        # Create deterministic key from planet positions and orb config
        key_data = {
            'planets': {
                name: {
                    'longitude': round(getattr(planet, 'longitude', planet.get('longitude', 0)), 3),
                    'longitude_speed': round(getattr(planet, 'longitude_speed', planet.get('longitude_speed', 0)), 6)
                }
                for name, planet in planets_data.items()
            },
            'orb_preset': orb_preset,
            'custom_orb_config': custom_orb_config
        }
        
        key_json = json.dumps(key_data, sort_keys=True)
        return f"aspects:{hashlib.md5(key_json.encode()).hexdigest()}"
    
    def _get_cached_aspects(self, cache_key: str) -> Optional[Dict]:
        """
        Get cached aspect calculation results.
        
        Args:
            cache_key: Cache key for aspect data
            
        Returns:
            Cached aspect data or None if not found
        """
        try:
            # Try memory cache first (if available)
            if hasattr(self, '_aspect_cache'):
                cached_data = self._aspect_cache.get(cache_key)
                if cached_data:
                    return cached_data
            
            # Note: Redis cache integration would go here in production
            # For now, we'll use a simple in-memory cache
            return None
            
        except Exception:
            # Cache errors should not break the calculation
            return None
    
    def _convert_dict_to_chart_data(self, chart_dict: Dict[str, Any]):
        """
        Convert chart dictionary format to ChartData object for Arabic parts calculation.
        
        Args:
            chart_dict: Chart data in dictionary format
            
        Returns:
            ChartData object suitable for Arabic parts calculation
        """
        from ..core.ephemeris.tools.ephemeris import ChartData, PlanetPosition, HouseSystem
        
        # Extract planet positions
        planets = {}
        planet_name_to_id = {
            'Sun': 0, 'Moon': 1, 'Mercury': 2, 'Venus': 3, 'Mars': 4,
            'Jupiter': 5, 'Saturn': 6, 'Uranus': 7, 'Neptune': 8, 'Pluto': 9,
            'North Node (Mean)': 10, 'North Node (True)': 11,
            'Lilith (Mean)': 12, 'Lilith (True)': 13, 'Earth': 14,
            'Chiron': 15, 'Pholus': 16, 'Ceres': 17, 'Pallas': 18, 'Juno': 19, 'Vesta': 20
        }
        
        planets_data = chart_dict.get('planets', {})
        for planet_name, planet_data in planets_data.items():
            if planet_name in planet_name_to_id:
                planet_id = planet_name_to_id[planet_name]
                
                # Extract planet data (handle both object and dict formats)
                if hasattr(planet_data, 'longitude'):
                    longitude = planet_data.longitude
                    latitude = planet_data.latitude
                    distance = planet_data.distance
                    longitude_speed = getattr(planet_data, 'longitude_speed', 0.0)
                else:
                    longitude = planet_data.get('longitude', 0.0)
                    latitude = planet_data.get('latitude', 0.0)
                    distance = planet_data.get('distance', 1.0)
                    longitude_speed = planet_data.get('longitude_speed', 0.0)
                
                planets[planet_id] = PlanetPosition(
                    longitude=longitude,
                    latitude=latitude,
                    distance=distance,
                    longitude_speed=longitude_speed,
                    planet_id=planet_id
                )
        
        # Extract house system data
        houses_data = chart_dict.get('houses', {})
        angles_data = chart_dict.get('angles', {})
        
        # Handle both object and dict formats
        if hasattr(houses_data, 'cusps'):
            house_cusps = houses_data.cusps
            system_code = houses_data.system
        else:
            house_cusps = houses_data.get('cusps', [])
            system_code = houses_data.get('system', 'P')
        
        if hasattr(angles_data, 'ascendant'):
            ascendant = angles_data.ascendant
            midheaven = angles_data.midheaven
            descendant = angles_data.descendant
            imum_coeli = angles_data.imum_coeli
        else:
            ascendant = angles_data.get('ascendant', 0.0)
            midheaven = angles_data.get('midheaven', 90.0)
            descendant = angles_data.get('descendant', 180.0)
            imum_coeli = angles_data.get('imum_coeli', 270.0)
        
        # Create ASCMC array (Ascendant, MC, ARMC, Vertex, etc.)
        ascmc = [ascendant, midheaven, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        house_system = HouseSystem(
            house_cusps=house_cusps,
            ascmc=ascmc,
            system_code=self._normalize_house_system_code(system_code),
            calculation_time=chart_dict.get('calculation_time', datetime.now()),
            latitude=0.0,  # Default values - not critical for Arabic parts
            longitude=0.0
        )
        
        # Create chart data object
        chart_data = ChartData(
            planets=planets,
            houses=house_system,
            calculation_time=chart_dict.get('calculation_time', datetime.now()),
            julian_day=chart_dict.get('julian_day', 2451545.0),  # Default J2000
            settings={}
        )
        
        return chart_data
    
    def _cache_aspects(self, cache_key: str, aspect_data: Dict, ttl: int = 86400) -> None:
        """
        Cache aspect calculation results.
        
        Args:
            cache_key: Cache key for aspect data
            aspect_data: Aspect calculation results to cache
            ttl: Time to live in seconds (default 24 hours)
        """
        try:
            # Initialize simple memory cache if not exists
            if not hasattr(self, '_aspect_cache'):
                self._aspect_cache = {}
                self._aspect_cache_timestamps = {}
            
            import time
            current_time = time.time()
            
            # Clean expired entries periodically
            expired_keys = [
                key for key, timestamp in self._aspect_cache_timestamps.items()
                if current_time - timestamp > ttl
            ]
            for key in expired_keys:
                self._aspect_cache.pop(key, None)
                self._aspect_cache_timestamps.pop(key, None)
            
            # Cache the new data
            self._aspect_cache[cache_key] = aspect_data
            self._aspect_cache_timestamps[cache_key] = current_time
            
            # Note: Redis cache integration would go here in production
            
        except Exception:
            # Cache errors should not break the calculation
            pass
    
    def _format_planet_data(self, planet_data: Dict[str, Any], internal_name: str) -> Any:
        """
        Format planet data for response.
        
        Args:
            planet_data: Raw planet calculation data
            internal_name: Internal name for the planet
            
        Returns:
            Formatted planet response object
        """
        # This would need to match your existing PlanetResponse format
        # For now, return a basic structure
        return type('Planet', (), {
            'name': planet_data.get('name', internal_name),
            'longitude': planet_data.get('longitude', 0.0),
            'latitude': planet_data.get('latitude', 0.0),
            'distance': planet_data.get('distance', 0.0),
            'longitude_speed': planet_data.get('speed', 0.0),
            'is_retrograde': planet_data.get('is_retrograde', False),
            'motion_type': planet_data.get('motion_type', 'unknown')
        })
    
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
    
    # Predictive Astrology Integration Methods
    
    async def get_upcoming_eclipses_for_chart(
        self,
        subject: Subject,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming eclipses relevant to a natal chart.
        
        Args:
            subject: Chart subject with birth information
            count: Number of eclipses to return
            
        Returns:
            List of eclipse information with relevance to natal chart
        """
        if not self._predictive_available:
            return []
        
        try:
            eclipses = await self._predictive_service.get_upcoming_eclipses(
                datetime.now(), count
            )
            
            # Add relevance information to natal chart
            eclipse_data = []
            for eclipse in eclipses:
                eclipse_info = {
                    'type': 'solar' if hasattr(eclipse, 'eclipse_type') and eclipse.eclipse_type else 'lunar',
                    'date': eclipse.maximum_eclipse_time.isoformat(),
                    'eclipse_degree': getattr(eclipse, 'eclipse_longitude', 0.0),
                    'relevance_score': self._calculate_eclipse_relevance(eclipse, subject)
                }
                eclipse_data.append(eclipse_info)
            
            return eclipse_data
            
        except Exception as e:
            # Log error but don't fail the main chart calculation
            print(f"Failed to get upcoming eclipses: {e}")
            return []
    
    async def get_upcoming_transits_to_chart(
        self,
        subject: Subject,
        months_ahead: int = 12
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get upcoming transits to natal chart points.
        
        Args:
            subject: Chart subject with birth information
            months_ahead: Months to search ahead
            
        Returns:
            Dictionary mapping chart points to upcoming transits
        """
        if not self._predictive_available:
            return {}
        
        try:
            # Calculate natal chart to get positions
            natal_chart = NatalChart(subject)
            chart_data = natal_chart.calculate()
            
            # Extract chart points (planets, angles)
            chart_points = {}
            for planet in chart_data.planets:
                chart_points[planet.name] = planet.longitude
            
            # Add angles
            chart_points['Ascendant'] = chart_data.angles.ascendant
            chart_points['Midheaven'] = chart_data.angles.midheaven
            
            # Search for transits
            end_date = datetime.now().replace(month=datetime.now().month + months_ahead)
            transits = await self._predictive_service.find_planetary_transits_to_points(
                chart_points, datetime.now(), end_date, orb_degrees=2.0
            )
            
            # Format transit data
            formatted_transits = {}
            for point, point_transits in transits.items():
                formatted_transits[point] = []
                for transit in point_transits[:5]:  # Limit to 5 transits per point
                    formatted_transits[point].append({
                        'transiting_planet': transit.planet_name,
                        'transit_time': transit.exact_time.isoformat(),
                        'is_retrograde': transit.is_retrograde,
                        'orb': abs(transit.target_longitude - chart_points[point])
                    })
            
            return formatted_transits
            
        except Exception as e:
            print(f"Failed to get upcoming transits: {e}")
            return {}
    
    def _calculate_eclipse_relevance(self, eclipse, subject: Subject) -> float:
        """
        Calculate how relevant an eclipse is to a natal chart.
        
        Args:
            eclipse: Eclipse object
            subject: Natal chart subject
            
        Returns:
            Relevance score (0-1)
        """
        try:
            # This is a simplified relevance calculation
            # Real implementation would check eclipse degree against natal positions
            
            # Base relevance
            relevance = 0.3
            
            # Check if eclipse is near birthday (solar return relevance)
            birth_month = subject.birth_date.month
            eclipse_month = eclipse.maximum_eclipse_time.month
            
            if abs(birth_month - eclipse_month) <= 1:
                relevance += 0.3
            
            # Check if eclipse is in birth location (simplified)
            # Real implementation would check eclipse visibility at birth location
            relevance += 0.2
            
            return min(relevance, 1.0)
            
        except Exception:
            return 0.1  # Default low relevance
    
    async def calculate_solar_return_timing(
        self,
        subject: Subject,
        return_year: int
    ) -> Optional[datetime]:
        """
        Calculate exact solar return timing for a subject.
        
        Args:
            subject: Natal chart subject
            return_year: Year for solar return
            
        Returns:
            Exact solar return datetime or None if calculation fails
        """
        if not self._predictive_available:
            return None
        
        try:
            return await self._predictive_service.calculate_solar_return_timing(
                subject.birth_date, return_year
            )
        except Exception as e:
            print(f"Solar return calculation failed: {e}")
            return None
    
    async def calculate_lunar_return_timing(
        self,
        subject: Subject,
        return_date: datetime
    ) -> Optional[datetime]:
        """
        Calculate lunar return timing for a subject.
        
        Args:
            subject: Natal chart subject
            return_date: Approximate return date
            
        Returns:
            Exact lunar return datetime or None if calculation fails
        """
        if not self._predictive_available:
            return None
        
        try:
            return await self._predictive_service.calculate_lunar_return_timing(
                subject.birth_date, return_date
            )
        except Exception as e:
            print(f"Lunar return calculation failed: {e}")
            return None
    
    def is_predictive_available(self) -> bool:
        """Check if predictive features are available."""
        return self._predictive_available
    
    def get_predictive_capabilities(self) -> Dict[str, bool]:
        """Get available predictive capabilities."""
        if not self._predictive_available:
            return {
                'eclipse_calculations': False,
                'transit_calculations': False,
                'solar_returns': False,
                'lunar_returns': False
            }
        
        return {
            'eclipse_calculations': True,
            'transit_calculations': True,
            'solar_returns': True,
            'lunar_returns': True,
            'nasa_validated': True,
            'sign_ingresses': True
        }
    
    def calculate_fixed_stars(
        self,
        request: NatalChartRequest,
        star_names: Optional[List[str]] = None,
        include_aspects: bool = True,
        magnitude_limit: float = 2.0
    ) -> Dict[str, Any]:
        """
        Calculate fixed star positions and aspects for a natal chart.
        
        Args:
            request: Natal chart request
            star_names: Specific stars to calculate (None for available stars)
            include_aspects: Whether to include star-planet aspects
            magnitude_limit: Maximum magnitude for automatic star selection
            
        Returns:
            Dictionary with fixed star calculations
        """
        try:
            # Parse inputs
            subject = self._create_subject_from_request(request.subject)
            
            # Calculate Julian day - Subject already has julian_day calculated
            jd = subject._data.julian_day
            
            # Get available stars
            if star_names is None:
                available_stars = self.fixed_star_calculator.get_available_stars()
                bright_stars = self.fixed_star_calculator.find_stars_by_magnitude(magnitude_limit)
                star_names = [star for star in available_stars if star in bright_stars]
            
            # Calculate star positions
            star_positions = self.fixed_star_calculator.calculate_multiple_stars(
                star_names, jd
            )
            
            # Format star positions
            formatted_stars = {}
            for star_name, star_data in star_positions.items():
                if star_data:
                    formatted_stars[star_name] = {
                        'name': star_data['name'],
                        'longitude': round(star_data['longitude'], 6),
                        'latitude': round(star_data['latitude'], 6),
                        'magnitude': star_data['magnitude'],
                        'spectral_class': star_data['spectral_class'],
                        'constellation': star_data['constellation'],
                        'traditional_name': star_data['traditional_name'],
                        'sign_name': self._get_sign_name(star_data['longitude']),
                        'sign_position': self._get_sign_position(star_data['longitude']),
                        'distance_light_years': star_data.get('distance', 0) / 63241.077  # AU to light years
                    }
            
            result = {
                'stars': formatted_stars,
                'count': len(formatted_stars),
                'selected_stars_count': len([s for s in formatted_stars.keys() 
                                          if s in self.fixed_star_calculator.get_foundation_24_stars()])
            }
            
            # Calculate aspects if requested
            if include_aspects and formatted_stars:
                # Get planet positions for aspects
                chart = self.calculate_natal_chart_enhanced(
                    request, 
                    include_aspects=False,
                    include_dignities=False,
                    include_arabic_parts=False
                )
                
                # Extract planets data from response
                if hasattr(chart, 'model_dump'):
                    # Pydantic v2 compatibility
                    chart_dict = chart.model_dump()
                elif hasattr(chart, 'dict'):
                    # Pydantic v1 compatibility
                    chart_dict = chart.model_dump()
                else:
                    # Already a dictionary
                    chart_dict = chart
                    
                planet_positions = chart_dict.get('planets', {})
                
                # Calculate star-planet aspects
                star_aspects = self.fixed_star_calculator.calculate_star_aspects(
                    star_positions, planet_positions, orb_degrees=1.0
                )
                
                # Format aspects
                formatted_aspects = []
                for aspect in star_aspects:
                    formatted_aspects.append({
                        'star': aspect['star'],
                        'planet': aspect['planet'],
                        'aspect': aspect['aspect'],
                        'orb': round(aspect['orb'], 3),
                        'exact': aspect['exact'],
                        'star_longitude': round(aspect['star_longitude'], 6),
                        'planet_longitude': round(aspect['planet_longitude'], 6)
                    })
                
                result['aspects'] = formatted_aspects
                result['aspect_count'] = len(formatted_aspects)
            
            return result
            
        except Exception as e:
            raise CalculationError(f"Fixed star calculation failed: {str(e)}")
    
    def get_fixed_star_availability(self) -> Dict[str, Any]:
        """
        Get information about fixed star availability.
        
        Returns:
            Dictionary with star availability information
        """
        return self.fixed_star_calculator.validate_star_availability()
    
    def get_foundation_24_stars(self) -> List[str]:
        """
        Get the Foundation 24 fixed stars available for calculation.
        
        Returns:
            List of available Foundation 24 star names
        """
        return self.fixed_star_calculator.get_foundation_24_stars()


# Global service instance
ephemeris_service = EphemerisService()