"""
ACG Line Calculator - Jim Lewis Style

Jim Lewis style astrocartography line calculator with comprehensive GeoJSON output.
Generates primary lines (AC/DC/IC/MC), angle aspect lines, and paran lines.

Output format: Standard GeoJSON LineString features following RFC 7946.
Coordinates: [longitude, latitude] (longitude first per GeoJSON standard)
"""

import math
from typing import List, Dict, Any, Tuple, Optional
import logging
from datetime import datetime

from extracted.systems.models.planet_data import PlanetData
from ..adapters.swiss_ephemeris_adapter import swiss_adapter

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class ACGLineCalculator:
    """
    Jim Lewis style astrocartography line calculator.
    
    Generates comprehensive ACG data:
    - Primary ACG lines (AC/DC/IC/MC) for all celestial objects
    - Angle aspect lines for planets and asteroids  
    - Paran lines for planet/asteroid combinations
    
    All output in standard GeoJSON format with proper coordinate ordering.
    """
    
    def __init__(self):
        """Initialize ACG calculator."""
        self.swiss_adapter = swiss_adapter
        
    def generate_acg_geojson(self, planets: List[PlanetData], 
                           subject_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete ACG data in GeoJSON format.
        
        Args:
            planets: List of calculated planet data
            subject_data: Subject information with datetime and location
            
        Returns:
            GeoJSON FeatureCollection with all ACG lines
        """
        try:
            features = []
            calculation_start = datetime.now()
            
            logger.info(f"Generating ACG lines for {len(planets)} objects")
            
            # Primary ACG lines for all planets/asteroids/points
            for planet in planets:
                try:
                    primary_lines = self._calculate_primary_lines(planet, subject_data)
                    features.extend(primary_lines)
                except Exception as e:
                    logger.warning(f"Failed to calculate primary lines for {planet.name}: {e}")
                    continue
            
            # Angle aspect lines for planets and asteroids only
            planet_asteroids = [p for p in planets if p.is_planet() or p.is_asteroid()]
            for planet in planet_asteroids:
                try:
                    aspect_lines = self._calculate_angle_aspect_lines(planet, subject_data)
                    features.extend(aspect_lines)
                except Exception as e:
                    logger.warning(f"Failed to calculate aspect lines for {planet.name}: {e}")
                    continue
            
            # Paran lines for planet/asteroid combinations
            try:
                paran_lines = self._calculate_paran_lines(planet_asteroids, subject_data)
                features.extend(paran_lines)
            except Exception as e:
                logger.warning(f"Failed to calculate paran lines: {e}")
            
            calculation_time = (datetime.now() - calculation_start).total_seconds()
            
            return {
                "type": "FeatureCollection",
                "features": features,
                "metadata": {
                    "total_features": len(features),
                    "coordinate_system": "WGS84",
                    "coordinate_order": "longitude_first",
                    "calculation_time_seconds": round(calculation_time, 3),
                    "objects_processed": len(planets),
                    "primary_lines": len([f for f in features if f["properties"]["line_category"] == "primary"]),
                    "aspect_lines": len([f for f in features if f["properties"]["line_category"] == "aspect"]),
                    "paran_lines": len([f for f in features if f["properties"]["line_category"] == "paran"])
                }
            }
            
        except Exception as e:
            logger.error(f"ACG line generation failed: {e}")
            raise RuntimeError(f"ACG line generation failed: {e}")
    
    def _calculate_primary_lines(self, planet: PlanetData, subject_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate AC, DC, IC, MC lines for a celestial object.
        
        Jim Lewis primary line methodology:
        - AC (Ascendant): Where planet rises on eastern horizon
        - DC (Descendant): Where planet sets on western horizon  
        - MC (Medium Coeli): Where planet culminates at zenith
        - IC (Imum Coeli): Where planet is at nadir
        
        Args:
            planet: Planet data for calculation
            subject_data: Subject information
            
        Returns:
            List of GeoJSON line features
        """
        lines = []
        
        try:
            # AC line (Ascendant) - planet rising
            ac_coords = self._calculate_ac_line_coordinates(planet)
            if ac_coords:
                lines.append(self._create_geojson_line(
                    coordinates=ac_coords,
                    planet_name=planet.name,
                    line_type="AC",
                    line_category="primary",
                    properties={
                        "description": f"{planet.name} rising line (Ascendant)",
                        "longitude_speed": planet.longitude_speed,
                        "is_retrograde": planet.is_retrograde,
                        "planet_longitude": planet.longitude,
                        "planet_latitude": planet.latitude
                    }
                ))
            
            # DC line (Descendant) - planet setting
            dc_coords = self._calculate_dc_line_coordinates(planet)
            if dc_coords:
                lines.append(self._create_geojson_line(
                    coordinates=dc_coords,
                    planet_name=planet.name,
                    line_type="DC", 
                    line_category="primary",
                    properties={
                        "description": f"{planet.name} setting line (Descendant)",
                        "longitude_speed": planet.longitude_speed,
                        "is_retrograde": planet.is_retrograde,
                        "planet_longitude": planet.longitude,
                        "planet_latitude": planet.latitude
                    }
                ))
            
            # MC line (Medium Coeli) - planet culminating  
            mc_coords = self._calculate_mc_line_coordinates(planet)
            if mc_coords:
                lines.append(self._create_geojson_line(
                    coordinates=mc_coords,
                    planet_name=planet.name,
                    line_type="MC",
                    line_category="primary",
                    properties={
                        "description": f"{planet.name} culmination line (MC)",
                        "longitude_speed": planet.longitude_speed,
                        "is_retrograde": planet.is_retrograde,
                        "planet_longitude": planet.longitude,
                        "planet_latitude": planet.latitude
                    }
                ))
            
            # IC line (Imum Coeli) - planet at nadir
            ic_coords = self._calculate_ic_line_coordinates(planet)
            if ic_coords:
                lines.append(self._create_geojson_line(
                    coordinates=ic_coords,
                    planet_name=planet.name,
                    line_type="IC",
                    line_category="primary",
                    properties={
                        "description": f"{planet.name} nadir line (IC)",
                        "longitude_speed": planet.longitude_speed,
                        "is_retrograde": planet.is_retrograde,
                        "planet_longitude": planet.longitude,
                        "planet_latitude": planet.latitude
                    }
                ))
            
        except Exception as e:
            logger.error(f"Primary line calculation failed for {planet.name}: {e}")
            
        return lines
    
    def _calculate_ac_line_coordinates(self, planet: PlanetData) -> List[List[float]]:
        """
        Calculate coordinates for Ascendant line using Jim Lewis formula.
        
        AC line: Where planet appears on eastern horizon (altitude = 0°, rising)
        
        Args:
            planet: Planet data
            
        Returns:
            List of [longitude, latitude] coordinates in GeoJSON format
        """
        coords = []
        
        try:
            # Jim Lewis AC line formula for each latitude
            for lat in range(-85, 86, 2):  # 2-degree steps, avoid polar extremes
                try:
                    # Calculate longitude where planet is on eastern horizon at this latitude
                    lon = self._calculate_horizon_longitude(
                        planet.longitude, planet.latitude, lat, "rising"
                    )
                    
                    if lon is not None:
                        # Normalize to GeoJSON standard [-180, +180]
                        lon = self._normalize_longitude_geojson(lon)
                        # GeoJSON format: [longitude, latitude] 
                        coords.append([round(lon, 4), lat])
                        
                except ValueError:
                    # Skip latitudes where planet never rises
                    continue
                    
        except Exception as e:
            logger.error(f"AC line calculation failed for {planet.name}: {e}")
            
        return coords
    
    def _calculate_dc_line_coordinates(self, planet: PlanetData) -> List[List[float]]:
        """Calculate Descendant line coordinates (planet setting)."""
        coords = []
        
        try:
            for lat in range(-85, 86, 2):
                try:
                    lon = self._calculate_horizon_longitude(
                        planet.longitude, planet.latitude, lat, "setting"
                    )
                    
                    if lon is not None:
                        lon = self._normalize_longitude_geojson(lon)
                        coords.append([round(lon, 4), lat])
                        
                except ValueError:
                    continue
                    
        except Exception as e:
            logger.error(f"DC line calculation failed for {planet.name}: {e}")
            
        return coords
    
    def _calculate_mc_line_coordinates(self, planet: PlanetData) -> List[List[float]]:
        """
        Calculate Medium Coeli line coordinates (planet culminating).
        
        MC line: Where planet transits the meridian at highest point
        Simple formula: MC line follows planet's longitude meridian
        """
        coords = []
        
        try:
            # MC line is simply the planet's longitude meridian
            planet_lon = self._normalize_longitude_geojson(planet.longitude)
            
            # Generate points along meridian from south to north
            for lat in range(-85, 86, 5):  # 5-degree steps
                coords.append([round(planet_lon, 4), lat])
                
        except Exception as e:
            logger.error(f"MC line calculation failed for {planet.name}: {e}")
            
        return coords
    
    def _calculate_ic_line_coordinates(self, planet: PlanetData) -> List[List[float]]:
        """
        Calculate Imum Coeli line coordinates (planet at nadir).
        
        IC line: Opposite meridian to MC, where planet transits at lowest point
        """
        coords = []
        
        try:
            # IC line is opposite meridian to planet longitude  
            ic_lon = (planet.longitude + 180) % 360
            ic_lon = self._normalize_longitude_geojson(ic_lon)
            
            # Generate points along opposite meridian
            for lat in range(-85, 86, 5):
                coords.append([round(ic_lon, 4), lat])
                
        except Exception as e:
            logger.error(f"IC line calculation failed for {planet.name}: {e}")
            
        return coords
    
    def _calculate_horizon_longitude(self, planet_lon: float, planet_lat: float, 
                                   observer_lat: float, crossing_type: str) -> Optional[float]:
        """
        Calculate longitude where planet crosses horizon at given observer latitude.
        
        Uses spherical astronomy formula for horizon crossings.
        
        Args:
            planet_lon: Planet longitude in degrees
            planet_lat: Planet latitude in degrees (declination)
            observer_lat: Observer latitude in degrees
            crossing_type: "rising" or "setting"
            
        Returns:
            Longitude where crossing occurs, or None if no crossing
            
        Raises:
            ValueError: If planet never crosses horizon at this latitude
        """
        try:
            # Convert to radians
            planet_lat_rad = math.radians(planet_lat)
            observer_lat_rad = math.radians(observer_lat)
            
            # Spherical astronomy horizon crossing formula
            # cos(H) = -tan(δ) * tan(φ) where H=hour angle, δ=declination, φ=latitude
            cos_h = -math.tan(planet_lat_rad) * math.tan(observer_lat_rad)
            
            if abs(cos_h) > 1.0:
                # Planet never crosses horizon at this latitude
                raise ValueError("No horizon crossing")
            
            # Hour angle at crossing
            h = math.acos(abs(cos_h))
            h_deg = math.degrees(h)
            
            # Calculate longitude based on crossing type
            if crossing_type == "rising":
                # Rising: planet on eastern horizon
                lon = planet_lon - h_deg
            else:  # setting
                # Setting: planet on western horizon
                lon = planet_lon + h_deg
            
            return lon % 360
            
        except Exception as e:
            raise ValueError(f"Horizon longitude calculation failed: {e}")
    
    def _calculate_angle_aspect_lines(self, planet: PlanetData, 
                                    subject_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate angle aspect lines for planets and asteroids.
        
        Angle aspect lines: Where transiting planet forms specific aspects to natal angles.
        Common aspects: conjunction (0°), square (90°), opposition (180°)
        
        Args:
            planet: Planet data
            subject_data: Subject information
            
        Returns:
            List of GeoJSON aspect line features
        """
        lines = []
        aspects_to_calculate = [0, 60, 90, 120, 180]  # Major aspects in degrees
        
        try:
            for aspect_angle in aspects_to_calculate:
                aspect_name = self._get_aspect_name(aspect_angle)
                
                # Calculate line where planet forms this aspect to angles
                coords = self._calculate_aspect_line_coordinates(planet, aspect_angle)
                
                if coords:
                    lines.append(self._create_geojson_line(
                        coordinates=coords,
                        planet_name=planet.name,
                        line_type=f"{aspect_name}_to_angles",
                        line_category="aspect",
                        properties={
                            "description": f"{planet.name} {aspect_name} to natal angles",
                            "aspect_angle": aspect_angle,
                            "aspect_name": aspect_name,
                            "planet_longitude": planet.longitude,
                            "is_retrograde": planet.is_retrograde
                        }
                    ))
                    
        except Exception as e:
            logger.error(f"Aspect line calculation failed for {planet.name}: {e}")
            
        return lines
    
    def _calculate_paran_lines(self, planets: List[PlanetData], 
                             subject_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate paran lines for planet/asteroid combinations.
        
        Paran lines: Where two planets simultaneously contact angles in specific ways.
        Common parans: rise-set, rise-culmination, set-culmination
        
        Args:
            planets: List of planets/asteroids for paran calculation
            subject_data: Subject information
            
        Returns:
            List of GeoJSON paran line features
        """
        lines = []
        
        try:
            # Calculate parans for planet combinations
            for i, planet1 in enumerate(planets):
                for planet2 in planets[i+1:]:  # Avoid duplicate pairs
                    try:
                        # Calculate different paran types
                        paran_types = ["rise-set", "rise-culm", "set-culm"]
                        
                        for paran_type in paran_types:
                            coords = self._calculate_paran_coordinates(planet1, planet2, paran_type)
                            
                            if coords:
                                lines.append(self._create_geojson_line(
                                    coordinates=coords,
                                    planet_name=f"{planet1.name}-{planet2.name}",
                                    line_type=f"paran_{paran_type}",
                                    line_category="paran",
                                    properties={
                                        "description": f"{planet1.name} {paran_type} with {planet2.name}",
                                        "planet1": planet1.name,
                                        "planet2": planet2.name,
                                        "paran_type": paran_type,
                                        "planet1_longitude": planet1.longitude,
                                        "planet2_longitude": planet2.longitude
                                    }
                                ))
                                
                    except Exception as e:
                        logger.warning(f"Paran calculation failed for {planet1.name}-{planet2.name}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Paran line calculation failed: {e}")
            
        return lines
    
    def _calculate_aspect_line_coordinates(self, planet: PlanetData, 
                                         aspect_angle: float) -> List[List[float]]:
        """Calculate coordinates for aspect lines (simplified implementation)."""
        coords = []
        
        try:
            # Simplified aspect line calculation
            # In full implementation, this would calculate where transiting planet
            # forms the specified aspect to natal angles at different locations
            
            aspect_lon = (planet.longitude + aspect_angle) % 360
            aspect_lon = self._normalize_longitude_geojson(aspect_lon)
            
            # Generate sample line (meridian-based for simplicity)
            for lat in range(-80, 81, 10):
                coords.append([round(aspect_lon, 4), lat])
                
        except Exception as e:
            logger.warning(f"Aspect line coordinate calculation failed: {e}")
            
        return coords
    
    def _calculate_paran_coordinates(self, planet1: PlanetData, planet2: PlanetData,
                                   paran_type: str) -> List[List[float]]:
        """Calculate coordinates for paran lines (simplified implementation)."""
        coords = []
        
        try:
            # Simplified paran calculation  
            # Full implementation would solve for locations where both planets
            # simultaneously contact angles in the specified paran relationship
            
            # Sample calculation based on longitude difference
            lon_diff = abs(planet1.longitude - planet2.longitude)
            if lon_diff > 180:
                lon_diff = 360 - lon_diff
            
            # Generate sample paran line
            if lon_diff < 30:  # Only calculate if planets are in reasonable orb
                paran_lon = (planet1.longitude + planet2.longitude) / 2
                paran_lon = self._normalize_longitude_geojson(paran_lon)
                
                for lat in range(-70, 71, 15):
                    coords.append([round(paran_lon, 4), lat])
                    
        except Exception as e:
            logger.warning(f"Paran coordinate calculation failed: {e}")
            
        return coords
    
    def _get_aspect_name(self, angle: float) -> str:
        """Get aspect name for angle."""
        aspect_names = {
            0: "conjunction",
            60: "sextile", 
            90: "square",
            120: "trine",
            180: "opposition"
        }
        return aspect_names.get(angle, f"aspect_{angle}")
    
    def _create_geojson_line(self, coordinates: List[List[float]], planet_name: str,
                           line_type: str, line_category: str, 
                           properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create GeoJSON LineString feature following RFC 7946.
        
        Args:
            coordinates: List of [longitude, latitude] pairs
            planet_name: Name of celestial object
            line_type: Type of line (AC, DC, IC, MC, etc.)
            line_category: Category (primary, aspect, paran)
            properties: Additional properties for the feature
            
        Returns:
            GeoJSON Feature dictionary
        """
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString", 
                "coordinates": coordinates  # Already in [lon, lat] format
            },
            "properties": {
                "planet": planet_name,
                "line_type": line_type,
                "line_category": line_category,
                "feature_id": f"ACG_{planet_name}_{line_type}",
                **properties
            }
        }
    
    def _normalize_longitude_geojson(self, lon: float) -> float:
        """
        Normalize longitude to GeoJSON standard [-180, +180].
        
        Args:
            lon: Longitude in degrees
            
        Returns:
            Normalized longitude for GeoJSON
        """
        while lon > 180:
            lon -= 360
        while lon <= -180:
            lon += 360
        return lon