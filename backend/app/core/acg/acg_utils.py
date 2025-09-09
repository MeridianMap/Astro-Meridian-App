"""
ACG Utilities - Mathematical and utility functions for ACG calculations

Implements the mathematical foundations from the ACG Engine overview,
including sidereal time calculations, coordinate transformations,
and geometric operations for astrocartography lines.

Based on the mathematical specifications in ACG_FEATURE_MASTER_CONTEXT.md
and the ACG Engine overview document.
"""

import numpy as np
import math
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime
import swisseph as swe
import logging

logger = logging.getLogger(__name__)

# Constants
DEG_TO_RAD = np.pi / 180.0
RAD_TO_DEG = 180.0 / np.pi


def wrap_deg(x: np.ndarray) -> np.ndarray:
    """
    Wrap angle(s) to [0, 360) degrees.
    
    Args:
        x: Angle(s) in degrees
        
    Returns:
        Wrapped angle(s) in [0, 360) range
    """
    x = np.asarray(x)
    y = np.mod(x, 360.0)
    y[y < 0] += 360.0
    return y


def wrap_pm180(x: np.ndarray) -> np.ndarray:
    """
    Wrap angle(s) to (-180, 180] degrees.
    
    Args:
        x: Angle(s) in degrees
        
    Returns:
        Wrapped angle(s) in (-180, 180] range
    """
    x = np.asarray(x)
    y = (x + 180.0) % 360.0 - 180.0
    # Ensure +180 not returned as -180
    y[y <= -180.0] += 360.0
    return y


def normalize_geojson_coordinates(coordinates):
    """
    Normalize coordinates for GeoJSON compliance.
    Ensures all longitudes are within [-180, 180] range.
    
    Args:
        coordinates: GeoJSON coordinate structure (nested lists)
        
    Returns:
        Normalized coordinates with proper longitude wrapping
    """
    if isinstance(coordinates, (list, tuple)):
        if len(coordinates) == 2 and all(isinstance(x, (int, float)) for x in coordinates):
            # This is a [longitude, latitude] pair
            lon, lat = coordinates
            normalized_lon = wrap_pm180(np.array([lon]))[0]
            return [float(normalized_lon), float(lat)]
        else:
            # This is a nested structure, recurse
            return [normalize_geojson_coordinates(coord) for coord in coordinates]
    else:
        return coordinates


def gmst_deg_from_jd_ut1(jd: float) -> float:
    """
    Calculate Greenwich Mean Sidereal Time from Julian Day (UT1).
    
    Uses IAU 2006/2000A precision formula from ACG Engine overview.
    
    Args:
        jd: Julian Day in UT1 (UTC approximation acceptable for mapping)
        
    Returns:
        GMST in degrees [0, 360)
    """
    T = (jd - 2451545.0) / 36525.0
    gmst = (280.46061837
            + 360.98564736629 * (jd - 2451545.0)
            + 0.000387933 * T * T
            - (T**3) / 38710000.0)
    return wrap_deg(np.array([gmst]))[0]


def lst_deg(gmst_deg: float, lon_deg: float) -> float:
    """
    Calculate Local Sidereal Time from GMST and longitude.
    
    Args:
        gmst_deg: Greenwich Mean Sidereal Time in degrees
        lon_deg: East longitude in degrees
        
    Returns:
        LST in degrees [0, 360)
    """
    return wrap_deg(np.array([gmst_deg + lon_deg]))[0]


def hour_angle(lst_deg_val: float, ra_deg: float) -> float:
    """
    Calculate hour angle from LST and right ascension.
    
    Args:
        lst_deg_val: Local Sidereal Time in degrees
        ra_deg: Right ascension in degrees
        
    Returns:
        Hour angle in degrees (-180, 180]
    """
    return wrap_pm180(np.array([lst_deg_val - ra_deg]))[0]


def mc_ic_longitudes(alpha_deg: float, gmst_deg: float) -> Tuple[float, float]:
    """
    Calculate MC and IC meridian longitudes.
    
    MC: Body on local meridian (H = 0)
    IC: Body on anti-meridian (H = 180°)
    
    Args:
        alpha_deg: Right ascension in degrees
        gmst_deg: Greenwich Mean Sidereal Time in degrees
        
    Returns:
        Tuple of (MC longitude, IC longitude) in degrees
    """
    lam_mc = wrap_deg(np.array([alpha_deg - gmst_deg]))[0]
    lam_ic = wrap_deg(np.array([alpha_deg + 180.0 - gmst_deg]))[0]
    return lam_mc, lam_ic


def build_ns_meridian(lon_deg: float, n_samples: int = 721) -> np.ndarray:
    """
    Build a north-south meridian line for MC/IC lines.
    
    Args:
        lon_deg: Meridian longitude in degrees
        n_samples: Number of latitude samples
        
    Returns:
        Nx2 array of [longitude, latitude] coordinates
    """
    lats = np.linspace(-89.9, 89.9, n_samples)
    # Convert longitude to [-180, 180) for GeoJSON compatibility
    lon_normalized = ((lon_deg + 540) % 360) - 180
    lons = np.full_like(lats, lon_normalized)
    return np.column_stack([lons, lats])


def ac_dc_line(
    alpha_deg: float,
    delta_deg: float, 
    gmst_deg: float,
    kind: str = 'AC',
    n_samples: int = 1441
) -> np.ndarray:
    """
    Calculate AC (Ascendant) or DC (Descendant) line coordinates.
    
    Uses the horizon crossing formula from ACG Engine overview:
    φ = atan2(-cos δ cos H, sin δ)
    
    Args:
        alpha_deg: Right ascension in degrees
        delta_deg: Declination in degrees
        gmst_deg: Greenwich Mean Sidereal Time in degrees
        kind: 'AC' or 'DC'
        n_samples: Number of longitude samples
        
    Returns:
        Nx2 array of [longitude, latitude] coordinates
    """
    lons = np.linspace(-180.0, 180.0, n_samples)
    lsts = lst_deg(gmst_deg, lons)  # Vectorized LST calculation
    H = wrap_pm180(lsts - alpha_deg)
    
    # Filter by horizon crossing type
    if kind == 'AC':
        mask = (H < 0)  # Body east of meridian (rising)
    else:  # DC
        mask = (H > 0)  # Body west of meridian (setting)
    
    # Calculate latitude using horizon crossing formula
    # For altitude = 0: sin(φ) * sin(δ) + cos(φ) * cos(δ) * cos(H) = 0
    # Solving: tan(φ) = -cos(δ) * cos(H) / sin(δ)
    cd = np.cos(delta_deg * DEG_TO_RAD)
    sd = np.sin(delta_deg * DEG_TO_RAD)
    cH = np.cos(H * DEG_TO_RAD)
    
    # Use atan instead of atan2 for the correct horizon crossing formula
    # Handle case where denominator is very small (near celestial pole)
    sd_safe = np.where(np.abs(sd) < 1e-10, np.sign(sd) * 1e-10, sd)
    tan_phi = (-cd * cH) / sd_safe
    phis = np.arctan(tan_phi) * RAD_TO_DEG
    
    # Apply mask and validity checks
    keep = mask & np.isfinite(phis) & (np.abs(phis) <= 90.0)
    
    # If no points pass the mask, try with a more lenient approach
    if not np.any(keep):
        logger.debug(f"Primary mask failed for {kind}, delta={delta_deg:.2f}°. Trying backup approach.")
        # For edge cases, try removing the H mask constraint
        keep = np.isfinite(phis) & (np.abs(phis) <= 90.0)
        
        # If still no valid points, return empty array
        if not np.any(keep):
            # Let's debug what's happening with detailed diagnostics
            finite_count = np.sum(np.isfinite(phis))
            valid_lat_count = np.sum(np.abs(phis) <= 90.0)
            mask_count = np.sum(mask)
            
            # Sample some calculated latitudes for debugging
            sample_phis = phis[np.isfinite(phis)][:5] if finite_count > 0 else []
            min_phi = np.min(phis[np.isfinite(phis)]) if finite_count > 0 else float('nan')
            max_phi = np.max(phis[np.isfinite(phis)]) if finite_count > 0 else float('nan')
            
            logger.warning(f"No valid {kind} line points for delta={delta_deg:.2f}°. finite={finite_count}, valid_lat={valid_lat_count}, mask={mask_count}")
            logger.warning(f"Calculated latitude range: [{min_phi:.1f}°, {max_phi:.1f}°], samples={sample_phis}")
            
            # Since latitudes are outside ±90°, there's likely a formula error
            # For now, return empty to avoid invalid coordinates
            return np.array([]).reshape(0, 2)
    
    lons_keep = lons[keep]
    phis_keep = phis[keep]
    
    return np.column_stack([lons_keep, phis_keep])


def ascendant_longitude(phi_deg: float, lst_deg_val: float, eps_deg: float) -> float:
    """
    Calculate ecliptic longitude of local Ascendant.
    
    Uses the formula: Λ_ASC = atan2(sin Θ cos ε + tan φ sin ε, cos Θ)
    where Θ = LST in radians.
    
    Args:
        phi_deg: Latitude in degrees
        lst_deg_val: Local Sidereal Time in degrees
        eps_deg: True obliquity in degrees
        
    Returns:
        Ascendant longitude in degrees [0, 360)
    """
    theta = lst_deg_val * DEG_TO_RAD
    eps = eps_deg * DEG_TO_RAD
    tphi = np.tan(phi_deg * DEG_TO_RAD)
    
    num = np.sin(theta) * np.cos(eps) + tphi * np.sin(eps)
    den = np.cos(theta)
    
    lam_asc = np.arctan2(num, den) * RAD_TO_DEG
    return wrap_deg(np.array([lam_asc]))[0]


def ac_aspect_lines(
    lambda_body_deg: float,
    gmst_deg: float,
    eps_deg: float,
    aspect_deg: float,
    n_lon: int = 361,
    n_lat: int = 181
) -> List[np.ndarray]:
    """
    Calculate AC aspect lines using contour extraction.
    
    Finds curves where wrap(λ_body - Λ_ASC(φ, λ)) = aspect_deg.
    
    Args:
        lambda_body_deg: Body's ecliptic longitude in degrees
        gmst_deg: Greenwich Mean Sidereal Time in degrees
        eps_deg: True obliquity in degrees
        aspect_deg: Target aspect angle in degrees (60, 90, 120, etc.)
        n_lon: Number of longitude grid points
        n_lat: Number of latitude grid points
        
    Returns:
        List of coordinate arrays for line segments
    """
    lons = np.linspace(-180.0, 180.0, n_lon)
    lats = np.linspace(-89.5, 89.5, n_lat)
    
    LON, LAT = np.meshgrid(lons, lats)
    
    # Calculate LST for each grid point
    LST = np.zeros_like(LON)
    for i in range(len(lats)):
        for j in range(len(lons)):
            LST[i, j] = lst_deg(gmst_deg, LON[i, j])
    
    # Calculate Ascendant longitude for each grid point
    Lam_asc = np.zeros_like(LON)
    for i in range(len(lats)):
        for j in range(len(lons)):
            try:
                Lam_asc[i, j] = ascendant_longitude(LAT[i, j], LST[i, j], eps_deg)
            except:
                Lam_asc[i, j] = np.nan
    
    # Calculate aspect difference
    Delta = wrap_deg(lambda_body_deg - Lam_asc)
    
    # Find where Delta ≈ aspect_deg
    target = wrap_pm180(Delta - aspect_deg)
    
    # Extract approximate contour (simplified approach)
    tol = 1.0  # degrees tolerance for grid-based extraction
    mask = np.abs(target) <= tol
    
    if not np.any(mask):
        return []
    
    # Get points near the contour
    points = np.column_stack([LON[mask], LAT[mask]])
    
    # Segment points (simplified - could use proper contour extraction)
    if len(points) == 0:
        return []
    
    return [points]  # Return as single segment for now


def h_rise(phi_deg: float, delta_deg: float) -> float:
    """
    Calculate rise hour angle for given latitude and declination.
    
    Args:
        phi_deg: Latitude in degrees
        delta_deg: Declination in degrees
        
    Returns:
        Rise hour angle in degrees
    """
    tphi = np.tan(phi_deg * DEG_TO_RAD)
    td = np.tan(delta_deg * DEG_TO_RAD)
    x = np.clip(-tphi * td, -1.0, 1.0)
    return -np.arccos(x) * RAD_TO_DEG


def h_set(phi_deg: float, delta_deg: float) -> float:
    """
    Calculate set hour angle for given latitude and declination.
    
    Args:
        phi_deg: Latitude in degrees
        delta_deg: Declination in degrees
        
    Returns:
        Set hour angle in degrees
    """
    tphi = np.tan(phi_deg * DEG_TO_RAD)
    td = np.tan(delta_deg * DEG_TO_RAD)
    x = np.clip(-tphi * td, -1.0, 1.0)
    return np.arccos(x) * RAD_TO_DEG


def h_event(event: str, phi_deg: float, delta_deg: float) -> float:
    """
    Calculate hour angle for specific astronomical event.
    
    Args:
        event: Event type ('RISE', 'SET', 'CULM', 'ANTI')
        phi_deg: Latitude in degrees
        delta_deg: Declination in degrees
        
    Returns:
        Hour angle in degrees
        
    Raises:
        ValueError: For unknown event type
    """
    if event == 'RISE':
        return h_rise(phi_deg, delta_deg)
    elif event == 'SET':
        return h_set(phi_deg, delta_deg)
    elif event == 'CULM':
        return 0.0
    elif event == 'ANTI':
        return 180.0
    else:
        raise ValueError(f"Unknown event type: {event}")


def find_paran_latitudes(
    alpha1: float, delta1: float,
    alpha2: float, delta2: float,
    event1: str, event2: str,
    lat_min: float = -89.0,
    lat_max: float = 89.0,
    lat_step: float = 0.1,
    tol: float = 1e-3
) -> List[Tuple[float, float]]:
    """
    Find latitudes where two bodies are in paran (simultaneous events).
    
    Solves: wrap(LST1 - LST2) = 0 where LSTi = αi + H_eventi(δi, φ)
    
    Args:
        alpha1, alpha2: Right ascensions in degrees
        delta1, delta2: Declinations in degrees
        event1, event2: Event types for each body
        lat_min, lat_max: Latitude search range
        lat_step: Search step size
        tol: Root-finding tolerance
        
    Returns:
        List of (latitude, LST) tuples for paran solutions
    """
    phis = np.arange(lat_min, lat_max + lat_step, lat_step)
    vals = []
    
    for phi in phis:
        try:
            H1 = h_event(event1, phi, delta1)
            H2 = h_event(event2, phi, delta2)
            F = wrap_pm180(np.array([(alpha1 + H1) - (alpha2 + H2)]))[0]
            vals.append(F)
        except:
            vals.append(np.nan)
    
    vals = np.array(vals)
    roots = []
    
    # Find sign changes indicating roots
    for i in range(len(phis) - 1):
        if np.isfinite(vals[i]) and np.isfinite(vals[i+1]):
            if vals[i] == 0 or vals[i+1] == 0 or (vals[i] * vals[i+1] < 0):
                # Bisection refinement
                a, b = phis[i], phis[i+1]
                fa, fb = vals[i], vals[i+1]
                
                for _ in range(40):  # Max iterations
                    m = 0.5 * (a + b)
                    try:
                        fm = wrap_pm180(np.array([
                            (alpha1 + h_event(event1, m, delta1)) -
                            (alpha2 + h_event(event2, m, delta2))
                        ]))[0]
                    except:
                        break
                    
                    if np.sign(fm) == np.sign(fa):
                        a, fa = m, fm
                    else:
                        b, fb = m, fm
                    
                    if abs(b - a) < tol:
                        break
                
                phi_star = 0.5 * (a + b)
                try:
                    LST = wrap_deg(np.array([
                        alpha1 + h_event(event1, phi_star, delta1)
                    ]))[0]
                    roots.append((phi_star, LST))
                except:
                    continue
    
    return roots


def paran_longitude(lst_deg_val: float, gmst_deg: float) -> float:
    """
    Convert paran LST to longitude.
    
    Args:
        lst_deg_val: Local Sidereal Time in degrees
        gmst_deg: Greenwich Mean Sidereal Time in degrees
        
    Returns:
        Longitude in degrees [-180, 180]
    """
    lon = wrap_deg(np.array([lst_deg_val - gmst_deg]))[0]
    # Convert to [-180, 180] for GeoJSON
    if lon > 180:
        lon -= 360
    return lon


def ecl_to_eq(lambda_deg: float, beta_deg: float, eps_deg: float) -> Tuple[float, float]:
    """
    Convert ecliptic coordinates to equatorial coordinates.
    
    Args:
        lambda_deg: Ecliptic longitude in degrees
        beta_deg: Ecliptic latitude in degrees
        eps_deg: True obliquity in degrees
        
    Returns:
        Tuple of (right ascension, declination) in degrees
    """
    lam = lambda_deg * DEG_TO_RAD
    bet = beta_deg * DEG_TO_RAD
    eps = eps_deg * DEG_TO_RAD
    
    sin_dec = np.sin(bet) * np.cos(eps) + np.cos(bet) * np.sin(eps) * np.sin(lam)
    dec = np.arcsin(sin_dec)
    
    y = np.sin(lam) * np.cos(eps) - np.tan(bet) * np.sin(eps)
    x = np.cos(lam)
    ra = np.arctan2(y, x)
    
    return wrap_deg(np.array([ra * RAD_TO_DEG]))[0], dec * RAD_TO_DEG


def segment_line_at_discontinuities(
    coords: np.ndarray,
    max_lon_jump: float = 90.0,
    max_lat_jump: float = 10.0
) -> List[np.ndarray]:
    """
    Segment a line at large discontinuities for better GeoJSON rendering.
    
    Args:
        coords: Nx2 array of [longitude, latitude] coordinates
        max_lon_jump: Maximum longitude jump before segmenting
        max_lat_jump: Maximum latitude jump before segmenting
        
    Returns:
        List of coordinate arrays for line segments
    """
    if len(coords) < 2:
        return [coords] if len(coords) > 0 else []
    
    segments = []
    current_segment = [coords[0]]
    
    for i in range(1, len(coords)):
        prev_coord = coords[i-1]
        curr_coord = coords[i]
        
        lon_diff = abs(curr_coord[0] - prev_coord[0])
        lat_diff = abs(curr_coord[1] - prev_coord[1])
        
        # Handle longitude wrap-around
        if lon_diff > 180:
            lon_diff = 360 - lon_diff
        
        if lon_diff > max_lon_jump or lat_diff > max_lat_jump:
            # Start new segment
            if len(current_segment) > 1:
                segments.append(np.array(current_segment))
            current_segment = [curr_coord]
        else:
            current_segment.append(curr_coord)
    
    # Add final segment
    if len(current_segment) > 1:
        segments.append(np.array(current_segment))
    
    return segments


def get_swiss_ephemeris_version() -> str:
    """
    Get Swiss Ephemeris version string.
    
    Returns:
        Version string
    """
    try:
        return swe.version
    except:
        return "unknown"


def validate_coordinates(longitude: float, latitude: float) -> bool:
    """
    Validate geographic coordinates.
    
    Args:
        longitude: Longitude in degrees
        latitude: Latitude in degrees
        
    Returns:
        True if valid, False otherwise
    """
    return (-180.0 <= longitude <= 180.0) and (-90.0 <= latitude <= 90.0)