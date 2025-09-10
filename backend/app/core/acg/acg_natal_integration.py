"""
ACG Natal Chart Integration (PRP 7)

Provides robust integration between the ACG engine and natal chart data.
Ensures all relevant natal chart attributes are accessible and correctly
incorporated into ACG calculations and metadata.

This module handles:
- Validation of natal chart data for ACG calculations
- Conversion between existing natal models and ACG types
- Enrichment of ACG metadata with natal context
- Integration with existing chart calculation pipeline
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import logging

from .acg_types import (
    ACGBodyData, ACGCoordinates, ACGNatalInfo, ACGNatalData,
    ACGRequest, ACGBody, ACGBodyType, ACGMetadata
)
from extracted.systems.ephemeris_utils.charts.natal import NatalChart, ChartData
from extracted.systems.ephemeris_utils.charts.subject import Subject, SubjectData
from extracted.systems.ephemeris_utils.classes.serialize import PlanetPosition
from extracted.systems.ephemeris_utils.const import PLANET_NAMES, SwePlanets
from extracted.systems.ephemeris_utils.tools.ephemeris import get_planet

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class ACGNatalIntegrator:
    """
    Integrates natal chart data with ACG calculations.
    
    Provides methods to convert between existing natal chart structures
    and ACG-specific data models, ensuring complete data flow and validation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_natal_data(self, natal_data: Optional[ACGNatalData]) -> bool:
        """
        Validate natal chart data for ACG calculations.
        
        Args:
            natal_data: Natal chart data to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValueError: If validation fails with specific error
        """
        if natal_data is None:
            return True  # Natal data is optional
        
        try:
            # Validate coordinate ranges
            if natal_data.birthplace_lat is not None:
                if not (-90.0 <= natal_data.birthplace_lat <= 90.0):
                    raise ValueError(f"Invalid birth latitude: {natal_data.birthplace_lat}")
            
            if natal_data.birthplace_lon is not None:
                if not (-180.0 <= natal_data.birthplace_lon <= 180.0):
                    raise ValueError(f"Invalid birth longitude: {natal_data.birthplace_lon}")
            
            # Validate house system
            valid_systems = ['placidus', 'koch', 'porphyry', 'regiomontanus', 
                           'campanus', 'equal', 'whole_sign']
            if natal_data.houses_system and natal_data.houses_system.lower() not in valid_systems:
                self.logger.warning(f"Unknown house system: {natal_data.houses_system}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Natal data validation failed: {e}")
            raise ValueError(f"Invalid natal data: {e}")
    
    def create_subject_from_acg_request(self, request: ACGRequest) -> Optional[Subject]:
        """
        Create a Subject instance from ACG request data.
        
        Args:
            request: ACG calculation request
            
        Returns:
            Subject instance if natal data is complete, None otherwise
        """
        if not request.natal:
            return None
        
        natal = request.natal
        
        # Check if we have minimum required data
        if (natal.birthplace_lat is None or 
            natal.birthplace_lon is None):
            self.logger.info("Insufficient natal data to create Subject")
            return None
        
        try:
            # Parse epoch for birth datetime
            birth_dt = datetime.fromisoformat(request.epoch.replace('Z', '+00:00'))
            
            # Format coordinates for Subject constructor
            lat_str = f"{abs(natal.birthplace_lat)}{'N' if natal.birthplace_lat >= 0 else 'S'}"
            lon_str = f"{abs(natal.birthplace_lon)}{'E' if natal.birthplace_lon >= 0 else 'W'}"
            
            # Create subject
            subject = Subject(
                name="ACG Subject",
                datetime=birth_dt.strftime("%Y-%m-%d %H:%M:%S"),
                latitude=lat_str,
                longitude=lon_str,
                altitude=natal.birthplace_alt_m or 0.0
            )
            
            return subject
            
        except Exception as e:
            self.logger.error(f"Failed to create Subject from ACG request: {e}")
            return None
    
    def extract_natal_info_from_chart(
        self, 
        chart_data: ChartData, 
        body_id: int
    ) -> Optional[ACGNatalInfo]:
        """
        Extract natal information for a specific body from chart data.
        
        Args:
            chart_data: Complete natal chart data
            body_id: Swiss Ephemeris body ID
            
        Returns:
            ACGNatalInfo with natal context or None if not found
        """
        try:
            # Get planet position
            planet_pos = chart_data.get_object_position(body_id)
            if not planet_pos:
                return None
            
            # Get aspects for this body
            aspects_data = []
            for aspect in chart_data.get_aspects_for_object(body_id):
                aspects_data.append({
                    'aspect_name': aspect.aspect_name,
                    'other_body': aspect.object2_name if aspect.object1_id == body_id else aspect.object1_name,
                    'orb': aspect.orb,
                    'applying': aspect.applying
                })
            
            # Determine dignity (simplified - could be enhanced)
            dignity = self._calculate_essential_dignity(planet_pos, chart_data)
            
            # Extract house information
            house_info = getattr(planet_pos, 'house_position', None)
            house_number = house_info.get('number') if house_info else None
            
            return ACGNatalInfo(
                dignity=dignity,
                house=house_number,
                retrograde=getattr(planet_pos, 'longitude_speed', 0) < 0,
                sign=getattr(planet_pos, 'sign_name', None),
                element=getattr(planet_pos, 'element', None),
                modality=getattr(planet_pos, 'modality', None),
                aspects=aspects_data if aspects_data else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract natal info for body {body_id}: {e}")
            return None
    
    def _calculate_essential_dignity(
        self, 
        planet_pos: PlanetPosition, 
        chart_data: ChartData
    ) -> Optional[str]:
        """
        Calculate essential dignity for a planet (simplified implementation).
        
        Args:
            planet_pos: Planet position data
            chart_data: Complete chart data
            
        Returns:
            Dignity string or None
        """
        # This is a simplified dignity calculation
        # A full implementation would check rulership, exaltation, etc.
        
        sign_name = getattr(planet_pos, 'sign_name', None)
        if not sign_name:
            return None
        
        # Basic rulership check (could be expanded)
        dignity_map = {
            'Sun': {'Leo': 'ruler', 'Aries': 'exaltation'},
            'Moon': {'Cancer': 'ruler', 'Taurus': 'exaltation'},
            'Mercury': {'Gemini': 'ruler', 'Virgo': 'ruler'},
            'Venus': {'Taurus': 'ruler', 'Libra': 'ruler', 'Pisces': 'exaltation'},
            'Mars': {'Aries': 'ruler', 'Scorpio': 'ruler', 'Capricorn': 'exaltation'},
            'Jupiter': {'Sagittarius': 'ruler', 'Pisces': 'ruler', 'Cancer': 'exaltation'},
            'Saturn': {'Capricorn': 'ruler', 'Aquarius': 'ruler', 'Libra': 'exaltation'}
        }
        
        planet_name = getattr(planet_pos, 'name', '')
        if planet_name in dignity_map:
            dignities = dignity_map[planet_name]
            return dignities.get(sign_name)
        
        return None
    
    def enrich_acg_bodies_with_natal_data(
        self, 
        bodies: List[ACGBodyData],
        chart_data: Optional[ChartData]
    ) -> List[ACGBodyData]:
        """
        Enrich ACG body data with natal chart information.
        
        Args:
            bodies: List of ACG body data to enrich
            chart_data: Natal chart data for context
            
        Returns:
            List of enriched ACG body data
        """
        if not chart_data:
            return bodies
        
        enriched_bodies = []
        
        for body_data in bodies:
            try:
                # Try to find matching body in chart
                body_id = self._get_body_id_from_name(body_data.body.id)
                if body_id is not None:
                    natal_info = self.extract_natal_info_from_chart(chart_data, body_id)
                    if natal_info:
                        # Create new body data with natal info
                        enriched_body = ACGBodyData(
                            body=body_data.body,
                            coordinates=body_data.coordinates,
                            natal_info=natal_info,
                            calculation_time_ms=body_data.calculation_time_ms
                        )
                        enriched_bodies.append(enriched_body)
                        continue
                
                # If no natal info found, use original
                enriched_bodies.append(body_data)
                
            except Exception as e:
                self.logger.warning(f"Failed to enrich body {body_data.body.id}: {e}")
                enriched_bodies.append(body_data)
        
        return enriched_bodies
    
    def _get_body_id_from_name(self, body_name: str) -> Optional[int]:
        """
        Get Swiss Ephemeris body ID from name.
        
        Args:
            body_name: Body name (e.g., 'Sun', 'Moon')
            
        Returns:
            Swiss Ephemeris ID or None if not found
        """
        # Reverse lookup in PLANET_NAMES
        name_to_id = {v: k for k, v in PLANET_NAMES.items()}
        return name_to_id.get(body_name)
    
    def create_natal_chart_for_acg(
        self, 
        request: ACGRequest
    ) -> Optional[ChartData]:
        """
        Create a complete natal chart for ACG calculations.
        
        Args:
            request: ACG calculation request
            
        Returns:
            Complete natal chart data or None if not possible
        """
        try:
            # Create subject from request
            subject = self.create_subject_from_acg_request(request)
            if not subject:
                return None
            
            # Configure natal chart calculation
            house_system = "P"  # Default to Placidus
            if request.natal and request.natal.houses_system:
                system_map = {
                    'placidus': 'P',
                    'koch': 'K', 
                    'porphyry': 'O',
                    'regiomontanus': 'R',
                    'campanus': 'C',
                    'equal': 'E',
                    'whole_sign': 'W'
                }
                house_system = system_map.get(
                    request.natal.houses_system.lower(), 
                    'P'
                )
            
            # Create and calculate natal chart
            natal_chart = NatalChart(
                subject=subject,
                house_system=house_system,
                include_asteroids=True,
                include_nodes=True,
                include_lilith=True,
                parallel_processing=True
            )
            
            chart_data = natal_chart.calculate()
            
            self.logger.info(f"Created natal chart for ACG with {len(chart_data.planets)} bodies")
            return chart_data
            
        except Exception as e:
            self.logger.error(f"Failed to create natal chart for ACG: {e}")
            return None
    
    def convert_to_acg_coordinates(self, planet_pos: PlanetPosition) -> ACGCoordinates:
        """
        Convert PlanetPosition to ACGCoordinates.
        
        Args:
            planet_pos: Planet position from natal chart
            
        Returns:
            ACGCoordinates instance
        """
        return ACGCoordinates(
            ra=getattr(planet_pos, 'right_ascension', 0.0),
            dec=getattr(planet_pos, 'declination', 0.0),
            lambda_=planet_pos.longitude,
            beta=planet_pos.latitude,
            distance=planet_pos.distance,
            speed=getattr(planet_pos, 'longitude_speed', None)
        )
    
    def validate_acg_request_natal_compatibility(
        self, 
        request: ACGRequest
    ) -> Dict[str, Any]:
        """
        Validate that ACG request is compatible with natal chart integration.
        
        Args:
            request: ACG calculation request
            
        Returns:
            Validation result with status and details
        """
        result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'natal_available': False,
            'chart_creatable': False
        }
        
        try:
            # Check natal data presence
            if request.natal:
                result['natal_available'] = True
                
                # Validate natal data
                if self.validate_natal_data(request.natal):
                    result['chart_creatable'] = (
                        request.natal.birthplace_lat is not None and
                        request.natal.birthplace_lon is not None
                    )
                    
                    if not result['chart_creatable']:
                        result['warnings'].append(
                            "Incomplete natal data - chart context unavailable"
                        )
                else:
                    result['errors'].append("Invalid natal data provided")
                    result['valid'] = False
            else:
                result['warnings'].append(
                    "No natal data provided - ACG lines will lack astrological context"
                )
            
            # Check epoch format
            try:
                datetime.fromisoformat(request.epoch.replace('Z', '+00:00'))
            except ValueError:
                result['errors'].append("Invalid epoch format")
                result['valid'] = False
            
        except Exception as e:
            result['errors'].append(f"Validation error: {e}")
            result['valid'] = False
        
        return result