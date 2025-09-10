"""
ACG Core Calculations Engine (PRP 1)

Implements the complete astrocartography calculation engine supporting all
line types (MC, IC, AC, DC, aspects, parans) and all celestial bodies
(planets, asteroids, hermetic lots, fixed stars, lunar nodes, Black Moon Lilith).

Based on specifications in ACG_FEATURE_MASTER_CONTEXT.md and mathematical
foundations from the ACG Engine overview document.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import numpy as np
import swisseph as swe
import logging

from .acg_types import (
    ACGRequest, ACGResult, ACGBody, ACGBodyType, ACGLineType, ACGOptions,
    ACGBodyData, ACGLineData, ACGCoordinates, ACGLineInfo, ACGMetadata,
    ACGNatalInfo
)
from .acg_utils import (
    gmst_deg_from_jd_ut1, mc_ic_longitudes, build_ns_meridian,
    ac_dc_line, ac_aspect_lines, find_paran_latitudes, paran_longitude,
    ecl_to_eq, segment_line_at_discontinuities, get_swiss_ephemeris_version,
    wrap_deg, wrap_pm180, normalize_geojson_coordinates
)
from .acg_natal_integration import ACGNatalIntegrator
from .acg_cache import get_acg_cache_manager

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class ACGCalculationEngine:
    """
    Core ACG calculation engine.
    
    Provides comprehensive astrocartography calculations for all supported
    line types and celestial bodies with high performance and accuracy.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.natal_integrator = ACGNatalIntegrator()
        self.cache_manager = get_acg_cache_manager()
        
        # Body registry for supported celestial objects
        self.body_registry = self._initialize_body_registry()
        
        # Default calculation options
        self.default_options = ACGOptions()
        
        # Swiss Ephemeris initialization
        self._init_swiss_ephemeris()
    
    def _init_swiss_ephemeris(self):
        """Initialize Swiss Ephemeris with appropriate settings."""
        try:
            # Set ephemeris path if needed
            # swe.set_ephe_path('/path/to/ephemeris/files')
            
            # Test Swiss Ephemeris availability
            jd_test = 2451545.0  # J2000.0
            result = swe.calc_ut(jd_test, swe.SUN)
            self.logger.info(f"Swiss Ephemeris initialized, version: {get_swiss_ephemeris_version()}")
            
        except Exception as e:
            self.logger.error(f"Swiss Ephemeris initialization failed: {e}")
            raise RuntimeError(f"Cannot initialize Swiss Ephemeris: {e}")
    
    def _initialize_body_registry(self) -> List[Dict[str, Any]]:
        """
        Initialize registry of supported celestial bodies.
        
        Returns:
            List of body definitions with SE constants and metadata
        """
        return [
            # Luminaries and Planets
            {"id": "Sun", "type": ACGBodyType.PLANET, "se_id": swe.SUN, "number": 0},
            {"id": "Moon", "type": ACGBodyType.PLANET, "se_id": swe.MOON, "number": 1},
            {"id": "Mercury", "type": ACGBodyType.PLANET, "se_id": swe.MERCURY, "number": 2},
            {"id": "Venus", "type": ACGBodyType.PLANET, "se_id": swe.VENUS, "number": 3},
            {"id": "Mars", "type": ACGBodyType.PLANET, "se_id": swe.MARS, "number": 4},
            {"id": "Jupiter", "type": ACGBodyType.PLANET, "se_id": swe.JUPITER, "number": 5},
            {"id": "Saturn", "type": ACGBodyType.PLANET, "se_id": swe.SATURN, "number": 6},
            {"id": "Uranus", "type": ACGBodyType.PLANET, "se_id": swe.URANUS, "number": 7},
            {"id": "Neptune", "type": ACGBodyType.PLANET, "se_id": swe.NEPTUNE, "number": 8},
            {"id": "Pluto", "type": ACGBodyType.DWARF, "se_id": swe.PLUTO, "number": 9},
            
            # Lunar Nodes
            {"id": "TrueNode", "type": ACGBodyType.NODE, "se_id": swe.TRUE_NODE, "number": 11},
            {"id": "MeanNode", "type": ACGBodyType.NODE, "se_id": swe.MEAN_NODE, "number": 10},
            
            # Black Moon Lilith (150-mile radius, render AC/DC/IC/MC + aspect lines)
            {"id": "LilithMean", "type": ACGBodyType.POINT, "se_id": swe.MEAN_APOG, "number": 12,
             "influence_radius_miles": 150.0, "render_orb_only": False},
            {"id": "LilithOsc", "type": ACGBodyType.POINT, "se_id": swe.OSCU_APOG, "number": 13,
             "influence_radius_miles": 150.0, "render_orb_only": False},
            
            # Major Asteroids (150-mile radius, render AC/DC/IC/MC + aspect lines)
            # NOTE: Asteroids require additional Swiss Ephemeris data files (seas_*.se1)
            # Uncomment when asteroid ephemeris files are available:
            # {"id": "Chiron", "type": ACGBodyType.ASTEROID, "se_id": swe.CHIRON, "number": 15,
            #  "influence_radius_miles": 150.0, "render_orb_only": False},
            # {"id": "Ceres", "type": ACGBodyType.ASTEROID, "se_id": swe.CERES, "number": 17,
            #  "influence_radius_miles": 150.0, "render_orb_only": False},
            # {"id": "Pallas", "type": ACGBodyType.ASTEROID, "se_id": swe.PALLAS, "number": 18,
            #  "influence_radius_miles": 150.0, "render_orb_only": False},
            # {"id": "Juno", "type": ACGBodyType.ASTEROID, "se_id": swe.JUNO, "number": 19,
            #  "influence_radius_miles": 150.0, "render_orb_only": False},
            # {"id": "Vesta", "type": ACGBodyType.ASTEROID, "se_id": swe.VESTA, "number": 20,
            #  "influence_radius_miles": 150.0, "render_orb_only": False},
            
            # Extended Asteroids (completing your 7-asteroid set)
            # NOTE: Requires Swiss Ephemeris asteroid files
            # {"id": "Eros", "type": ACGBodyType.ASTEROID, "se_id": 433, "number": 433,
            #  "influence_radius_miles": 150.0, "render_orb_only": False},
            
            # Dwarf Planets (using asteroid numbers for objects without SE constants)
            # NOTE: Eris requires additional ephemeris files
            # {"id": "Eris", "type": ACGBodyType.DWARF, "se_id": 136199, "number": 136199},
            
            # Foundation 24 Fixed Stars (100-mile radius, orbs only)
            # NOTE: Fixed stars require sefstars.txt file from Swiss Ephemeris
            # Download from: https://www.astro.com/swisseph/swephinfo_e.htm
            # Uncomment when star catalog file is available:
            
            # {"id": "Regulus", "type": ACGBodyType.FIXED_STAR, "se_name": "Regulus",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Aldebaran", "type": ACGBodyType.FIXED_STAR, "se_name": "Aldebaran", 
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Antares", "type": ACGBodyType.FIXED_STAR, "se_name": "Antares",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Fomalhaut", "type": ACGBodyType.FIXED_STAR, "se_name": "Fomalhaut",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Spica", "type": ACGBodyType.FIXED_STAR, "se_name": "Spica",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Arcturus", "type": ACGBodyType.FIXED_STAR, "se_name": "Arcturus",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Sirius", "type": ACGBodyType.FIXED_STAR, "se_name": "Sirius",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Canopus", "type": ACGBodyType.FIXED_STAR, "se_name": "Canopus",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Vega", "type": ACGBodyType.FIXED_STAR, "se_name": "Vega",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Capella", "type": ACGBodyType.FIXED_STAR, "se_name": "Capella",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Betelgeuse", "type": ACGBodyType.FIXED_STAR, "se_name": "Betelgeuse",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Rigel", "type": ACGBodyType.FIXED_STAR, "se_name": "Rigel",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Altair", "type": ACGBodyType.FIXED_STAR, "se_name": "Altair",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Algol", "type": ACGBodyType.FIXED_STAR, "se_name": "Algol",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Procyon", "type": ACGBodyType.FIXED_STAR, "se_name": "Procyon",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Bellatrix", "type": ACGBodyType.FIXED_STAR, "se_name": "Bellatrix",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Deneb", "type": ACGBodyType.FIXED_STAR, "se_name": "Deneb",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Alcyone", "type": ACGBodyType.FIXED_STAR, "se_name": "Alcyone",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Achernar", "type": ACGBodyType.FIXED_STAR, "se_name": "Achernar",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Acrux", "type": ACGBodyType.FIXED_STAR, "se_name": "Acrux",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Alphecca", "type": ACGBodyType.FIXED_STAR, "se_name": "Alphecca",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Rasalhague", "type": ACGBodyType.FIXED_STAR, "se_name": "Rasalhague",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Denebola", "type": ACGBodyType.FIXED_STAR, "se_name": "Denebola",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
            # {"id": "Markab", "type": ACGBodyType.FIXED_STAR, "se_name": "Markab",
            #  "influence_radius_miles": 100.0, "render_orb_only": True},
             
            # Extended 77 Fixed Stars (80-mile radius, orbs only) - Sample of additional stars
            # {"id": "Alpheratz", "type": ACGBodyType.FIXED_STAR, "se_name": "Alpheratz",
            #  "influence_radius_miles": 80.0, "render_orb_only": True},
            # {"id": "Scheat", "type": ACGBodyType.FIXED_STAR, "se_name": "Scheat",
            #  "influence_radius_miles": 80.0, "render_orb_only": True},
            # {"id": "Pollux", "type": ACGBodyType.FIXED_STAR, "se_name": "Pollux",
            #  "influence_radius_miles": 80.0, "render_orb_only": True},
            # {"id": "Castor", "type": ACGBodyType.FIXED_STAR, "se_name": "Castor",
            #  "influence_radius_miles": 80.0, "render_orb_only": True},
            # {"id": "Hamal", "type": ACGBodyType.FIXED_STAR, "se_name": "Hamal",
            #  "influence_radius_miles": 80.0, "render_orb_only": True},
        ]
    
    def get_supported_bodies(self) -> List[ACGBody]:
        """
        Get list of all supported celestial bodies.
        
        Returns:
            List of ACGBody instances for all supported bodies
        """
        bodies = []
        for body_def in self.body_registry:
            bodies.append(ACGBody(
                id=body_def["id"],
                type=body_def["type"],
                number=body_def.get("number")
            ))
        return bodies
    
    def get_default_bodies(self) -> List[ACGBody]:
        """
        Get default set of bodies for ACG calculations.
        
        Returns:
            List of commonly used celestial bodies
        """
        default_ids = [
            "Sun", "Moon", "Mercury", "Venus", "Mars", 
            "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
        ]
        return [body for body in self.get_supported_bodies() if body.id in default_ids]
    
    def calculate_body_position(
        self, 
        body: ACGBody, 
        jd_ut1: float, 
        flags: int = swe.FLG_SWIEPH | swe.FLG_SPEED
    ) -> Optional[ACGCoordinates]:
        """
        Calculate position of a celestial body.
        
        Args:
            body: Body to calculate
            jd_ut1: Julian Day (UT1)
            flags: Swiss Ephemeris calculation flags
            
        Returns:
            ACGCoordinates or None if calculation fails
        """
        try:
            # Find body definition
            body_def = next((b for b in self.body_registry if b["id"] == body.id), None)
            if not body_def:
                self.logger.error(f"Unknown body: {body.id}")
                return None
            
            if body.type == ACGBodyType.FIXED_STAR:
                # Fixed star calculation
                star_name = body_def["se_name"]
                result = swe.fixstar2_ut(star_name, jd_ut1, flags)
                if result[1] != "":  # Error occurred
                    self.logger.error(f"Fixed star calculation failed for {star_name}: {result[1]}")
                    return None
                coords = result[0]
            else:
                # Planet/asteroid calculation
                se_id = body_def["se_id"]
                result = swe.calc_ut(jd_ut1, se_id, flags)
                if len(result) < 2:
                    self.logger.error(f"Body calculation failed for {body.id}")
                    return None
                coords = result[0]
            
            # Extract coordinates
            longitude = coords[0]  # Ecliptic longitude
            latitude = coords[1]   # Ecliptic latitude
            distance = coords[2]   # Distance
            speed = coords[3] if len(coords) > 3 else None
            
            # Convert ecliptic to equatorial coordinates
            obliquity = swe.calc_ut(jd_ut1, swe.ECL_NUT)[0][0]  # True obliquity
            ra, dec = self._ecl_to_eq(longitude, latitude, obliquity)
            
            return ACGCoordinates(
                ra=ra,
                dec=dec,
                lambda_=longitude,
                beta=latitude,
                distance=distance,
                speed=speed
            )
            
        except Exception as e:
            self.logger.error(f"Failed to calculate position for {body.id}: {e}")
            return None
    
    def _ecl_to_eq(self, lambda_deg: float, beta_deg: float, eps_deg: float) -> Tuple[float, float]:
        """Convert ecliptic to equatorial coordinates."""
        from .acg_utils import ecl_to_eq
        return ecl_to_eq(lambda_deg, beta_deg, eps_deg)
    
    def calculate_mc_ic_lines(
        self,
        body_data: ACGBodyData,
        gmst_deg: float,
        metadata_base: Dict[str, Any]
    ) -> List[ACGLineData]:
        """
        Calculate MC and IC lines for a body.
        
        Args:
            body_data: Body position data
            gmst_deg: Greenwich Mean Sidereal Time
            metadata_base: Base metadata for lines
            
        Returns:
            List of ACGLineData for MC and IC lines
        """
        lines = []
        
        try:
            # Calculate MC and IC longitudes
            lam_mc, lam_ic = mc_ic_longitudes(body_data.coordinates.ra, gmst_deg)
            
            # Build meridian coordinates
            mc_coords = build_ns_meridian(lam_mc)
            ic_coords = build_ns_meridian(lam_ic)
            
            # Create MC line
            mc_metadata = ACGMetadata(
                **{k: v for k, v in metadata_base.items() if k != 'id'},
                id=f"ACG_{body_data.body.id}_MC",
                line=ACGLineInfo(
                    angle="MC",
                    line_type="MC",
                    method="apparent, true obliquity, meridian crossing"
                )
            )
            
            mc_line = ACGLineData(
                line_type=ACGLineType.MC,
                geometry={
                    "type": "LineString",
                    "coordinates": mc_coords.tolist()
                },
                body_data=body_data,
                metadata=mc_metadata
            )
            lines.append(mc_line)
            
            # Create IC line
            ic_metadata = ACGMetadata(
                **{k: v for k, v in metadata_base.items() if k != 'id'},
                id=f"ACG_{body_data.body.id}_IC",
                line=ACGLineInfo(
                    angle="IC",
                    line_type="IC", 
                    method="apparent, true obliquity, anti-meridian crossing"
                )
            )
            
            ic_line = ACGLineData(
                line_type=ACGLineType.IC,
                geometry={
                    "type": "LineString", 
                    "coordinates": ic_coords.tolist()
                },
                body_data=body_data,
                metadata=ic_metadata
            )
            lines.append(ic_line)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate MC/IC lines for {body_data.body.id}: {e}")
        
        return lines
    
    def calculate_ac_dc_lines(
        self,
        body_data: ACGBodyData,
        gmst_deg: float,
        metadata_base: Dict[str, Any]
    ) -> List[ACGLineData]:
        """
        Calculate AC and DC lines for a body.
        
        Args:
            body_data: Body position data
            gmst_deg: Greenwich Mean Sidereal Time
            metadata_base: Base metadata for lines
            
        Returns:
            List of ACGLineData for AC and DC lines
        """
        lines = []
        
        try:
            # Calculate AC line
            ac_coords = ac_dc_line(
                body_data.coordinates.ra,
                body_data.coordinates.dec,
                gmst_deg,
                kind='AC'
            )
            
            if len(ac_coords) > 0:
                # Segment the line at discontinuities
                ac_segments = segment_line_at_discontinuities(ac_coords)
                
                if ac_segments:
                    ac_metadata = ACGMetadata(
                        **{k: v for k, v in metadata_base.items() if k != 'id'},
                        id=f"ACG_{body_data.body.id}_AC",
                        line=ACGLineInfo(
                            angle="AC",
                            line_type="AC",
                            method="apparent, horizon crossing, ascending"
                        )
                    )
                    
                    raw_coordinates = [seg.tolist() for seg in ac_segments] if len(ac_segments) > 1 else ac_segments[0].tolist()
                    geometry = {
                        "type": "MultiLineString" if len(ac_segments) > 1 else "LineString",
                        "coordinates": normalize_geojson_coordinates(raw_coordinates)
                    }
                    
                    ac_line = ACGLineData(
                        line_type=ACGLineType.AC,
                        geometry=geometry,
                        body_data=body_data,
                        metadata=ac_metadata
                    )
                    lines.append(ac_line)
                else:
                    self.logger.warning(f"AC line segments empty for {body_data.body.id}")
            else:
                self.logger.warning(f"AC coordinates empty for {body_data.body.id} (RA={body_data.coordinates.ra:.2f}°, Dec={body_data.coordinates.dec:.2f}°)")
            
            # Calculate DC line
            dc_coords = ac_dc_line(
                body_data.coordinates.ra,
                body_data.coordinates.dec,
                gmst_deg,
                kind='DC'
            )
            
            if len(dc_coords) > 0:
                # Segment the line at discontinuities
                dc_segments = segment_line_at_discontinuities(dc_coords)
                
                if dc_segments:
                    dc_metadata = ACGMetadata(
                        **{k: v for k, v in metadata_base.items() if k != 'id'},
                        id=f"ACG_{body_data.body.id}_DC",
                        line=ACGLineInfo(
                            angle="DC",
                            line_type="DC",
                            method="apparent, horizon crossing, descending"
                        )
                    )
                    
                    raw_coordinates = [seg.tolist() for seg in dc_segments] if len(dc_segments) > 1 else dc_segments[0].tolist()
                    geometry = {
                        "type": "MultiLineString" if len(dc_segments) > 1 else "LineString",
                        "coordinates": normalize_geojson_coordinates(raw_coordinates)
                    }
                    
                    dc_line = ACGLineData(
                        line_type=ACGLineType.DC,
                        geometry=geometry,
                        body_data=body_data,
                        metadata=dc_metadata
                    )
                    lines.append(dc_line)
                else:
                    self.logger.warning(f"DC line segments empty for {body_data.body.id}")
            else:
                self.logger.warning(f"DC coordinates empty for {body_data.body.id} (RA={body_data.coordinates.ra:.2f}°, Dec={body_data.coordinates.dec:.2f}°)")
            
        except Exception as e:
            self.logger.error(f"Failed to calculate AC/DC lines for {body_data.body.id}: {e}")
        
        return lines
    
    def calculate_mc_aspect_lines(
        self,
        body_data: ACGBodyData,
        gmst_deg: float,
        aspects: List[int],
        metadata_base: Dict[str, Any]
    ) -> List[ACGLineData]:
        """
        Calculate MC aspect lines for a body.
        
        Args:
            body_data: Body position data
            gmst_deg: Greenwich Mean Sidereal Time
            aspects: List of aspect angles (60, 90, 120, etc.)
            metadata_base: Base metadata for lines
            
        Returns:
            List of ACGLineData for MC aspect lines
        """
        lines = []
        
        aspect_names = {60: "sextile", 90: "square", 120: "trine", 
                       240: "trine", 270: "square", 300: "sextile"}
        
        for aspect_deg in aspects:
            try:
                # MC aspect is simply a meridian at α + aspect_angle
                lam_aspect = wrap_deg(np.array([body_data.coordinates.ra + aspect_deg - gmst_deg]))[0]
                aspect_coords = build_ns_meridian(lam_aspect)
                
                aspect_metadata = ACGMetadata(
                    **{k: v for k, v in metadata_base.items() if k != 'id'},
                    id=f"ACG_{body_data.body.id}_MC_ASPECT_{aspect_deg}",
                    line=ACGLineInfo(
                        angle=aspect_deg,
                        aspect=aspect_names.get(aspect_deg, f"{aspect_deg}°"),
                        line_type="MC_ASPECT",
                        method=f"apparent, meridian {aspect_deg}° from MC"
                    )
                )
                
                aspect_line = ACGLineData(
                    line_type=ACGLineType.MC_ASPECT,
                    geometry={
                        "type": "LineString",
                        "coordinates": aspect_coords.tolist()
                    },
                    body_data=body_data,
                    metadata=aspect_metadata
                )
                lines.append(aspect_line)
                
            except Exception as e:
                self.logger.error(f"Failed to calculate MC aspect {aspect_deg}° for {body_data.body.id}: {e}")
        
        return lines
    
    def calculate_ac_aspect_lines(
        self,
        body_data: ACGBodyData,
        gmst_deg: float,
        obliquity_deg: float,
        aspects: List[int],
        metadata_base: Dict[str, Any]
    ) -> List[ACGLineData]:
        """
        Calculate AC aspect lines for a body.
        
        Args:
            body_data: Body position data
            gmst_deg: Greenwich Mean Sidereal Time
            obliquity_deg: True obliquity
            aspects: List of aspect angles
            metadata_base: Base metadata for lines
            
        Returns:
            List of ACGLineData for AC aspect lines
        """
        lines = []
        
        aspect_names = {60: "sextile", 90: "square", 120: "trine",
                       240: "trine", 270: "square", 300: "sextile"}
        
        for aspect_deg in aspects:
            try:
                # Calculate AC aspect line using contour extraction
                aspect_segments = ac_aspect_lines(
                    body_data.coordinates.lambda_,
                    gmst_deg,
                    obliquity_deg,
                    aspect_deg
                )
                
                if aspect_segments:
                    aspect_metadata = ACGMetadata(
                        **{k: v for k, v in metadata_base.items() if k != 'id'},
                        id=f"ACG_{body_data.body.id}_AC_ASPECT_{aspect_deg}",
                        line=ACGLineInfo(
                            angle=aspect_deg,
                            aspect=aspect_names.get(aspect_deg, f"{aspect_deg}°"),
                            line_type="AC_ASPECT",
                            method=f"apparent, ascendant {aspect_deg}° aspect contour"
                        )
                    )
                    
                    raw_coordinates = [seg.tolist() for seg in aspect_segments] if len(aspect_segments) > 1 else aspect_segments[0].tolist()
                    geometry = {
                        "type": "MultiLineString" if len(aspect_segments) > 1 else "LineString",
                        "coordinates": normalize_geojson_coordinates(raw_coordinates)
                    }
                    
                    aspect_line = ACGLineData(
                        line_type=ACGLineType.AC_ASPECT,
                        geometry=geometry,
                        body_data=body_data,
                        metadata=aspect_metadata
                    )
                    lines.append(aspect_line)
                
            except Exception as e:
                self.logger.error(f"Failed to calculate AC aspect {aspect_deg}° for {body_data.body.id}: {e}")
        
        return lines
    
    def calculate_paran_lines(
        self,
        body_data_list: List[ACGBodyData],
        gmst_deg: float,
        metadata_base: Dict[str, Any]
    ) -> List[ACGLineData]:
        """
        Calculate paran lines between body pairs.
        
        Args:
            body_data_list: List of body position data
            gmst_deg: Greenwich Mean Sidereal Time
            metadata_base: Base metadata template
            
        Returns:
            List of ACGLineData for paran lines
        """
        lines = []
        events = ['RISE', 'SET', 'CULM', 'ANTI']
        
        # Generate body pairs
        for i in range(len(body_data_list)):
            for j in range(i + 1, len(body_data_list)):
                body1 = body_data_list[i]
                body2 = body_data_list[j]
                
                # Calculate parans for selected event combinations
                event_pairs = [
                    ('RISE', 'CULM'), ('SET', 'CULM'),
                    ('RISE', 'SET'), ('CULM', 'ANTI')
                ]
                
                for event1, event2 in event_pairs:
                    try:
                        paran_solutions = find_paran_latitudes(
                            body1.coordinates.ra, body1.coordinates.dec,
                            body2.coordinates.ra, body2.coordinates.dec,
                            event1, event2
                        )
                        
                        if paran_solutions:
                            # Create paran line segments
                            for phi_star, lst_star in paran_solutions:
                                lon_star = paran_longitude(lst_star, gmst_deg)
                                
                                # Create a latitude band around the paran latitude
                                lat_band = 2.0  # degrees
                                paran_coords = np.array([
                                    [lon_star - 180, phi_star - lat_band/2],
                                    [lon_star + 180, phi_star - lat_band/2],
                                    [lon_star + 180, phi_star + lat_band/2],
                                    [lon_star - 180, phi_star + lat_band/2],
                                    [lon_star - 180, phi_star - lat_band/2]
                                ])
                                
                                paran_metadata = ACGMetadata(
                                    id=f"PARAN_{body1.body.id}_{body2.body.id}_{event1}_{event2}_BAND",
                                    type="paran",
                                    **{k: v for k, v in metadata_base.items() if k not in ['id', 'type']},
                                    line=ACGLineInfo(
                                        angle=f"{event1}-{event2}",
                                        line_type="PARAN",
                                        method=f"paran: {body1.body.id} {event1} with {body2.body.id} {event2}"
                                    ),
                                    # Add individual body coordinates to prevent reuse
                                    paran_coords={
                                        body1.body.id: {
                                            "ra": body1.coordinates.ra,
                                            "dec": body1.coordinates.dec,
                                            "ecliptic_lon": body1.coordinates.lambda_
                                        },
                                        body2.body.id: {
                                            "ra": body2.coordinates.ra,
                                            "dec": body2.coordinates.dec,
                                            "ecliptic_lon": body2.coordinates.lambda_
                                        }
                                    }
                                )
                                
                                paran_line = ACGLineData(
                                    line_type=ACGLineType.PARAN,
                                    geometry={
                                        "type": "Polygon",
                                        "coordinates": normalize_geojson_coordinates([paran_coords.tolist()])
                                    },
                                    body_data=body1,  # Primary body
                                    metadata=paran_metadata
                                )
                                lines.append(paran_line)
                    
                    except Exception as e:
                        self.logger.error(f"Failed to calculate paran {event1}-{event2} for {body1.body.id}-{body2.body.id}: {e}")
        
        return lines
    
    def calculate_acg_lines(self, request: ACGRequest) -> ACGResult:
        """
        Main ACG calculation method with caching support.
        
        Args:
            request: ACG calculation request
            
        Returns:
            ACGResult with GeoJSON FeatureCollection
            
        Raises:
            ValueError: If request validation fails
            RuntimeError: If calculation fails
        """
        calc_start_time = time.time()
        
        try:
            # Check cache first
            cached_result = self.cache_manager.get_cached_result(request)
            if cached_result:
                calc_duration = time.time() - calc_start_time
                self.cache_manager.stats['calculation_time_saved'] += calc_duration
                self.logger.info(f"ACG calculation served from cache in {calc_duration * 1000:.2f}ms")
                return cached_result
            # Validate request
            validation_result = self.natal_integrator.validate_acg_request_natal_compatibility(request)
            if not validation_result['valid']:
                raise ValueError(f"Request validation failed: {validation_result['errors']}")
            
            # Parse epoch and calculate Julian Day
            epoch_dt = datetime.fromisoformat(request.epoch.replace('Z', '+00:00'))
            jd_ut1 = request.jd if request.jd else swe.julday(
                epoch_dt.year, epoch_dt.month, epoch_dt.day,
                epoch_dt.hour + epoch_dt.minute/60.0 + epoch_dt.second/3600.0
            )
            
            # Calculate GMST and obliquity
            gmst_deg = gmst_deg_from_jd_ut1(jd_ut1)
            obliquity_deg = swe.calc_ut(jd_ut1, swe.ECL_NUT)[0][0]
            
            # Determine bodies to calculate
            bodies = request.bodies if request.bodies else self.get_default_bodies()
            
            # Get calculation options
            options = request.options if request.options else self.default_options
            
            # Calculate body positions
            body_data_list = []
            for body in bodies:
                body_calc_start = time.time()
                coordinates = self.calculate_body_position(body, jd_ut1)
                body_calc_time = (time.time() - body_calc_start) * 1000
                
                if coordinates:
                    body_data = ACGBodyData(
                        body=body,
                        coordinates=coordinates,
                        calculation_time_ms=body_calc_time
                    )
                    body_data_list.append(body_data)
            
            # Create natal chart if possible for context enrichment
            chart_data = None
            if validation_result['chart_creatable']:
                chart_data = self.natal_integrator.create_natal_chart_for_acg(request)
                if chart_data:
                    body_data_list = self.natal_integrator.enrich_acg_bodies_with_natal_data(
                        body_data_list, chart_data
                    )
            
            # Generate all lines
            all_lines = []
            
            for body_data in body_data_list:
                # Get body definition for rendering metadata
                body_def = next((b for b in self.body_registry if b["id"] == body_data.body.id), {})
                
                # Base metadata for this body
                metadata_base = {
                    'id': body_data.body.id,
                    'type': 'body',
                    'kind': body_data.body.type,
                    'number': body_data.body.number,
                    'epoch': request.epoch,
                    'jd': jd_ut1,
                    'gmst': gmst_deg,
                    'obliquity': obliquity_deg,
                    'coords': body_data.coordinates,
                    'natal': body_data.natal_info,
                    'flags': options.flags,
                    'se_version': get_swiss_ephemeris_version(),
                    'source': 'Meridian-ACG',
                    'calculation_time_ms': body_data.calculation_time_ms,
                    # Add rendering metadata from body definition
                    'influence_radius_miles': body_def.get('influence_radius_miles', 0.0),
                    'render_orb_only': body_def.get('render_orb_only', False)
                }
                
                # Skip line calculations if body is orb-only (e.g., fixed stars)
                if not body_def.get('render_orb_only', False):
                    # Determine which line types to calculate
                    line_types = options.line_types if options.line_types else [
                        ACGLineType.MC, ACGLineType.IC, ACGLineType.AC, ACGLineType.DC
                    ]
                    
                    # Calculate MC/IC lines
                    if ACGLineType.MC in line_types or ACGLineType.IC in line_types:
                        mc_ic_lines = self.calculate_mc_ic_lines(body_data, gmst_deg, metadata_base)
                        all_lines.extend(mc_ic_lines)
                    
                    # Calculate AC/DC lines
                    if ACGLineType.AC in line_types or ACGLineType.DC in line_types:
                        ac_dc_lines = self.calculate_ac_dc_lines(body_data, gmst_deg, metadata_base)
                        all_lines.extend(ac_dc_lines)
                
                    # Calculate MC aspect lines (only for bodies that render lines)
                    if options.aspects:
                        aspect_degrees = [60, 90, 120, 240, 270, 300]  # Default aspects
                        mc_aspect_lines = self.calculate_mc_aspect_lines(
                            body_data, gmst_deg, aspect_degrees, metadata_base
                        )
                        all_lines.extend(mc_aspect_lines)
                    
                        # Calculate AC aspect lines
                        ac_aspect_lines = self.calculate_ac_aspect_lines(
                            body_data, gmst_deg, obliquity_deg, aspect_degrees, metadata_base
                        )
                        all_lines.extend(ac_aspect_lines)
            
            # Calculate parans if requested
            if options.include_parans and len(body_data_list) > 1:
                paran_lines = self.calculate_paran_lines(body_data_list, gmst_deg, metadata_base)
                all_lines.extend(paran_lines)
            
            # Convert to GeoJSON features
            features = []
            for line_data in all_lines:
                feature = {
                    "type": "Feature",
                    "geometry": line_data.geometry,
                    "properties": self._metadata_to_properties(line_data.metadata)
                }
                features.append(feature)
            
            calc_total_time = (time.time() - calc_start_time) * 1000
            self.logger.info(f"ACG calculation completed in {calc_total_time:.2f}ms, {len(features)} features generated")
            
            # Create result
            result = ACGResult(
                type="FeatureCollection",
                features=features
            )
            
            # Cache the result
            self.cache_manager.set_cached_result(request, result)
            
            return result
            
        except Exception as e:
            # Allow validation errors to propagate for proper 422 handling at API layer
            if isinstance(e, ValueError):
                raise
            self.logger.error(f"ACG calculation failed: {e}")
            raise RuntimeError(f"ACG calculation failed: {e}")
    
    def _metadata_to_properties(self, metadata: ACGMetadata) -> Dict[str, Any]:
        """
        Convert ACGMetadata to GeoJSON properties dict.
        
        Args:
            metadata: ACG metadata object
            
        Returns:
            Dictionary suitable for GeoJSON properties
        """
        props = {
            'id': metadata.id,
            'type': metadata.type,
            'kind': metadata.kind.value,
            'epoch': metadata.epoch,
            'jd': metadata.jd,
            'gmst': metadata.gmst,
            'obliquity': metadata.obliquity,
            'coords': {
                'ra': metadata.coords.ra,
                'dec': metadata.coords.dec,
                'lambda': metadata.coords.lambda_,
                'beta': metadata.coords.beta,
                'distance': metadata.coords.distance,
                'speed': metadata.coords.speed
            },
            'line': {
                'angle': metadata.line.angle,
                'aspect': metadata.line.aspect,
                'line_type': metadata.line.line_type,
                'method': metadata.line.method,
                'segment_id': metadata.line.segment_id,
                'orb': metadata.line.orb
            },
            'source': metadata.source,
            'calculation_time_ms': metadata.calculation_time_ms
        }
        
        # Add optional fields
        if metadata.number is not None:
            props['number'] = metadata.number
        
        if metadata.natal:
            props['natal'] = {
                'dignity': metadata.natal.dignity,
                'house': metadata.natal.house,
                'retrograde': metadata.natal.retrograde,
                'sign': metadata.natal.sign,
                'element': metadata.natal.element,
                'modality': metadata.natal.modality,
                'aspects': metadata.natal.aspects
            }
        
        if metadata.flags is not None:
            props['flags'] = metadata.flags
        
        if metadata.se_version:
            props['se_version'] = metadata.se_version
        
        if metadata.color:
            props['color'] = metadata.color
        
        if metadata.style:
            props['style'] = metadata.style
        
        if metadata.z_index is not None:
            props['z_index'] = metadata.z_index
        
        if metadata.hit_radius is not None:
            props['hit_radius'] = metadata.hit_radius
        
        # Add rendering metadata for asteroids and fixed stars
        if metadata.influence_radius_miles > 0.0:
            props['influence_radius_miles'] = metadata.influence_radius_miles
        
        if metadata.render_orb_only:
            props['render_orb_only'] = metadata.render_orb_only
        
        if metadata.custom:
            props['custom'] = metadata.custom
        
        return props