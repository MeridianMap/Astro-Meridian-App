"""
Swiss Ephemeris wrapper for extracted systems - Auto-setup and safe calls
"""

import os
import sys
from pathlib import Path
import swisseph as swe

# Global Swiss Ephemeris state
_SWISS_EPH_INITIALIZED = False
_SWISS_EPH_PATH = None

def setup_swiss_ephemeris_for_extraction(base_path: str = None) -> str:
    """Setup Swiss Ephemeris with multiple fallback strategies"""
    global _SWISS_EPH_PATH
    
    if base_path is None:
        # Auto-detect project root
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "Swiss Eph Library Files").exists():
                base_path = str(parent)
                break
        else:
            base_path = str(Path.cwd())
    
    # Search paths in order of preference
    search_paths = [
        os.path.join(base_path, "Swiss Eph Library Files"),
        os.path.join(base_path, "..", "Swiss Eph Library Files"),
        os.path.join(base_path, "..", "..", "Swiss Eph Library Files"),
        os.path.join(base_path, "..", "..", "..", "Swiss Eph Library Files"),
        os.environ.get('SE_EPHE_PATH', ''),
        "/usr/share/swisseph",
        "C:/swisseph"
    ]
    
    for search_path in search_paths:
        if not search_path or not os.path.exists(search_path):
            continue
            
        # Verify critical files
        sefstars_path = os.path.join(search_path, "sefstars.txt")
        if os.path.exists(sefstars_path):
            try:
                swe.set_ephe_path(search_path)
                os.environ['SE_EPHE_PATH'] = search_path
                
                # Quick validation test
                test_result = swe.fixstar("Regulus", 2460000.5)
                if test_result and len(test_result) >= 2:
                    _SWISS_EPH_PATH = search_path
                    return search_path
                    
            except Exception:
                continue
    
    # If all paths fail
    raise RuntimeError(f"""
Swiss Ephemeris setup failed! 

Searched paths:
{chr(10).join(f'  - {path}' for path in search_paths if path)}

Required: 'Swiss Eph Library Files' directory containing:
  - sefstars.txt (fixed star catalog)
  - seas_18.se1 (asteroid ephemeris)
  - sepl_18.se1 (planet ephemeris)
  - semo_18.se1 (moon ephemeris)

Solutions:
1. Ensure Swiss Ephemeris files are in project root
2. Set SE_EPHE_PATH environment variable
3. Copy files to one of the search locations
""")

def ensure_swiss_ephemeris_setup():
    """Ensure Swiss Ephemeris is properly configured (call this before any calculations)"""
    global _SWISS_EPH_INITIALIZED, _SWISS_EPH_PATH
    
    if not _SWISS_EPH_INITIALIZED:
        _SWISS_EPH_PATH = setup_swiss_ephemeris_for_extraction()
        _SWISS_EPH_INITIALIZED = True
        
    return _SWISS_EPH_PATH

def safe_fixstar(star_name: str, julian_day: float):
    """Safe fixed star calculation with automatic Swiss Ephemeris setup"""
    ensure_swiss_ephemeris_setup()
    return swe.fixstar(star_name, julian_day)

def safe_fixstar_ut(star_name: str, julian_day_ut: float):
    """Safe fixed star calculation (UT variant) with automatic Swiss Ephemeris setup"""
    ensure_swiss_ephemeris_setup()
    return swe.fixstar_ut(star_name, julian_day_ut)

def safe_calc_ut(julian_day: float, body_id: int):
    """Safe planetary calculation with automatic Swiss Ephemeris setup"""
    ensure_swiss_ephemeris_setup()
    return swe.calc_ut(julian_day, body_id)

def safe_houses(julian_day: float, latitude: float, longitude: float, house_system: bytes = b'P'):
    """Safe house calculation with automatic Swiss Ephemeris setup
    
    Returns: (cusps, ascmc) where:
    - cusps[0] is unused, cusps[1-12] are house cusps 1-12
    - ascmc[0-3] are ASC, MC, ARMC, Vertex
    """
    ensure_swiss_ephemeris_setup()
    return swe.houses(julian_day, latitude, longitude, house_system)

# Auto-setup on module import (with error handling)
try:
    ensure_swiss_ephemeris_setup()
    print(f"✅ Swiss Ephemeris auto-configured: {_SWISS_EPH_PATH}")
except Exception as e:
    print(f"⚠️  Swiss Ephemeris auto-setup failed: {e}")
    print("   Manual setup may be required before calculations")
    _SWISS_EPH_INITIALIZED = False
