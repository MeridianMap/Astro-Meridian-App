"""
Meridian Ephemeris Engine - Constants Module

Defines indices, mappings, and constants for astronomical calculations
using Swiss Ephemeris as the authoritative backend.
"""

import swisseph as swe
from typing import Dict, List, Tuple


# Swiss Ephemeris Planet Constants (as defined in swisseph)
class SwePlanets:
    """Swiss Ephemeris planet indices."""
    SUN = swe.SUN
    MOON = swe.MOON
    MERCURY = swe.MERCURY
    VENUS = swe.VENUS
    MARS = swe.MARS
    JUPITER = swe.JUPITER
    SATURN = swe.SATURN
    URANUS = swe.URANUS
    NEPTUNE = swe.NEPTUNE
    PLUTO = swe.PLUTO
    MEAN_NODE = swe.MEAN_NODE
    TRUE_NODE = swe.TRUE_NODE
    MEAN_APOG = swe.MEAN_APOG  # Mean Lilith
    OSCULATING_APOG = swe.OSCU_APOG  # True Lilith
    EARTH = swe.EARTH
    CHIRON = swe.CHIRON


# Swiss Ephemeris Asteroids
class SweAsteroids:
    """Swiss Ephemeris asteroid indices."""
    CHIRON = swe.CHIRON
    PHOLUS = swe.PHOLUS
    CERES = swe.CERES
    PALLAS = swe.PALLAS
    JUNO = swe.JUNO
    VESTA = swe.VESTA


# Swiss Ephemeris Flags
class SweFlags:
    """Swiss Ephemeris calculation flags."""
    SWIEPH = swe.FLG_SWIEPH
    JPLEPH = swe.FLG_JPLEPH
    MOSEPH = swe.FLG_MOSEPH
    HELCTR = swe.FLG_HELCTR
    TRUEPOS = swe.FLG_TRUEPOS
    J2000 = swe.FLG_J2000
    NONUT = swe.FLG_NONUT
    SPEED = swe.FLG_SPEED
    NOGDEFL = swe.FLG_NOGDEFL
    NOABERR = swe.FLG_NOABERR
    EQUATORIAL = swe.FLG_EQUATORIAL
    XYZ = swe.FLG_XYZ
    RADIANS = swe.FLG_RADIANS
    BARYCTR = swe.FLG_BARYCTR
    TOPOCTR = swe.FLG_TOPOCTR
    SIDEREAL = swe.FLG_SIDEREAL


# House Systems
class HouseSystems:
    """Swiss Ephemeris house system codes."""
    PLACIDUS = 'P'
    KOCH = 'K'
    PORPHYRIUS = 'O'
    REGIOMONTANUS = 'R'
    CAMPANUS = 'C'
    EQUAL = 'E'
    WHOLE_SIGN = 'W'
    ALCABITUS = 'B'
    MORINUS = 'M'
    KRUSINSKI = 'U'
    GALACTIC_EQUATOR = 'G'
    AZIMUTHAL = 'H'
    POLICH_PAGE = 'T'
    CARTER_EQUAL = 'D'
    VEHLOW_EQUAL = 'V'
    MERIDIAN = 'X'
    AXIAL_ROTATION = 'N'
    HORIZONTAL = 'I'


# Ayanamsa (Sidereal Mode) Constants
class Ayanamsa:
    """Swiss Ephemeris ayanamsa constants."""
    FAGAN_BRADLEY = swe.SIDM_FAGAN_BRADLEY
    LAHIRI = swe.SIDM_LAHIRI
    DE_LUCE = swe.SIDM_DELUCE
    RAMAN = swe.SIDM_RAMAN
    USHASHASHI = swe.SIDM_USHASHASHI
    KRISHNAMURTI = swe.SIDM_KRISHNAMURTI
    DJWHAL_KHUL = swe.SIDM_DJWHAL_KHUL
    YUKTESHWAR = swe.SIDM_YUKTESHWAR
    JN_BHASIN = swe.SIDM_JN_BHASIN
    BABYL_KUGLER1 = swe.SIDM_BABYL_KUGLER1
    BABYL_KUGLER2 = swe.SIDM_BABYL_KUGLER2
    BABYL_KUGLER3 = swe.SIDM_BABYL_KUGLER3
    BABYL_HUBER = swe.SIDM_BABYL_HUBER
    BABYL_ETPSC = swe.SIDM_BABYL_ETPSC
    ALDEBARAN_15TAU = swe.SIDM_ALDEBARAN_15TAU
    HIPPARCHOS = swe.SIDM_HIPPARCHOS
    SASSANIAN = swe.SIDM_SASSANIAN
    J2000 = swe.SIDM_J2000
    J1900 = swe.SIDM_J1900
    B1950 = swe.SIDM_B1950


# Zodiac Signs
class Signs:
    """Zodiac signs with degrees."""
    ARIES = 0
    TAURUS = 30
    GEMINI = 60
    CANCER = 90
    LEO = 120
    VIRGO = 150
    LIBRA = 180
    SCORPIO = 210
    SAGITTARIUS = 240
    CAPRICORN = 270
    AQUARIUS = 300
    PISCES = 330


# Aspect Constants
class Aspects:
    """Major astrological aspects in degrees."""
    CONJUNCTION = 0
    OPPOSITION = 180
    SQUARE = 90
    TRINE = 120
    SEXTILE = 60
    QUINCUNX = 150
    SEMISEXTILE = 30
    SEMISQUARE = 45
    SESQUISQUARE = 135
    QUINTILE = 72
    BIQUINTILE = 144
    SEPTILE = 51.43
    BISEPTILE = 102.86
    TRISEPTILE = 154.29
    OCTILE = 45  # Same as semisquare
    TRIOCTILE = 135  # Same as sesquisquare


# Planet Names and Properties
PLANET_NAMES: Dict[int, str] = {
    SwePlanets.SUN: 'Sun',
    SwePlanets.MOON: 'Moon',
    SwePlanets.MERCURY: 'Mercury',
    SwePlanets.VENUS: 'Venus',
    SwePlanets.MARS: 'Mars',
    SwePlanets.JUPITER: 'Jupiter',
    SwePlanets.SATURN: 'Saturn',
    SwePlanets.URANUS: 'Uranus',
    SwePlanets.NEPTUNE: 'Neptune',
    SwePlanets.PLUTO: 'Pluto',
    SwePlanets.MEAN_NODE: 'North Node (Mean)',
    SwePlanets.TRUE_NODE: 'North Node (True)',
    SwePlanets.MEAN_APOG: 'Lilith (Mean)',
    SwePlanets.OSCULATING_APOG: 'Lilith (True)',
    SwePlanets.EARTH: 'Earth',
    SwePlanets.CHIRON: 'Chiron',
    16: 'Pholus',                                   # (5145) Pholus - centaur
    17: 'Ceres',                                    # (1) Ceres - dwarf planet
    18: 'Pallas',                                   # (2) Pallas - asteroid
    19: 'Juno',                                     # (3) Juno - asteroid
    20: 'Vesta',                                    # (4) Vesta - asteroid
}

PLANET_SYMBOLS: Dict[int, str] = {
    SwePlanets.SUN: '☉',
    SwePlanets.MOON: '☽',
    SwePlanets.MERCURY: '☿',
    SwePlanets.VENUS: '♀',
    SwePlanets.MARS: '♂',
    SwePlanets.JUPITER: '♃',
    SwePlanets.SATURN: '♄',
    SwePlanets.URANUS: '⛢',
    SwePlanets.NEPTUNE: '♆',
    SwePlanets.PLUTO: '♇',
    SwePlanets.MEAN_NODE: '☊',
    SwePlanets.TRUE_NODE: '☊',
    SwePlanets.MEAN_APOG: '⚸',
    SwePlanets.OSCULATING_APOG: '⚸',
    SwePlanets.EARTH: '🜨',
    SwePlanets.CHIRON: '⚷',
    16: '⚷',  # Pholus (centaur symbol)
    17: '⚳',  # Ceres (official symbol)
    18: '⚴',  # Pallas (official symbol)
    19: '⚵',  # Juno (official symbol)
    20: '⚶',  # Vesta (official symbol)
}

SIGN_NAMES: Dict[int, str] = {
    1: 'Aries', 2: 'Taurus', 3: 'Gemini', 4: 'Cancer',
    5: 'Leo', 6: 'Virgo', 7: 'Libra', 8: 'Scorpio',
    9: 'Sagittarius', 10: 'Capricorn', 11: 'Aquarius', 12: 'Pisces'
}

SIGN_SYMBOLS: Dict[int, str] = {
    1: '♈', 2: '♉', 3: '♊', 4: '♋',
    5: '♌', 6: '♍', 7: '♎', 8: '♏',
    9: '♐', 10: '♑', 11: '♒', 12: '♓'
}

HOUSE_SYSTEM_NAMES: Dict[str, str] = {
    'P': 'Placidus',
    'K': 'Koch',
    'O': 'Porphyrius',
    'R': 'Regiomontanus',
    'C': 'Campanus',
    'E': 'Equal',
    'W': 'Whole Sign',
    'B': 'Alcabitus',
    'M': 'Morinus',
    'U': 'Krusinski',
    'G': 'Galactic Equator',
    'H': 'Azimuthal',
    'T': 'Polich-Page',
    'D': 'Carter Equal',
    'V': 'Vehlow Equal',
    'X': 'Meridian',
    'N': 'Axial Rotation',
    'I': 'Horizontal'
}

# Standard calculation sets
TRADITIONAL_PLANETS: List[int] = [
    SwePlanets.SUN, SwePlanets.MOON, SwePlanets.MERCURY,
    SwePlanets.VENUS, SwePlanets.MARS, SwePlanets.JUPITER, SwePlanets.SATURN
]

MODERN_PLANETS: List[int] = TRADITIONAL_PLANETS + [
    SwePlanets.URANUS, SwePlanets.NEPTUNE, SwePlanets.PLUTO
]

MAJOR_ASTEROIDS: List[int] = [
    SwePlanets.CHIRON, SweAsteroids.CERES, SweAsteroids.PALLAS,
    SweAsteroids.JUNO, SweAsteroids.VESTA
]

LUNAR_NODES: List[int] = [
    SwePlanets.MEAN_NODE, SwePlanets.TRUE_NODE
]

LILITH_POINTS: List[int] = [
    SwePlanets.MEAN_APOG, SwePlanets.OSCULATING_APOG
]

# Default calculation flags
DEFAULT_FLAGS = SweFlags.SWIEPH | SweFlags.SPEED

# Swiss Ephemeris constants for reference
SWE_VERSION = swe.version
SWE_DEFAULT_EPHE_PATH = swe.default_ephe_path if hasattr(swe, 'default_ephe_path') else None

# Coordinate conversion constants
DEGREES_PER_RADIAN = 180.0 / 3.141592653589793
RADIANS_PER_DEGREE = 3.141592653589793 / 180.0
HOURS_PER_DAY = 24.0
MINUTES_PER_HOUR = 60.0
SECONDS_PER_MINUTE = 60.0
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
SECONDS_PER_DAY = SECONDS_PER_HOUR * HOURS_PER_DAY

# Julian Date constants
J2000_0 = 2451545.0  # Julian Date for J2000.0 epoch
J1900_0 = 2415020.0  # Julian Date for J1900.0 epoch

# Utility functions
def get_planet_name(planet_id: int) -> str:
    """Get the name of a planet by its Swiss Ephemeris ID."""
    return PLANET_NAMES.get(planet_id, f"Planet {planet_id}")

def get_planet_symbol(planet_id: int) -> str:
    """Get the symbol of a planet by its Swiss Ephemeris ID."""
    return PLANET_SYMBOLS.get(planet_id, "?")

def get_sign_from_longitude(longitude: float) -> int:
    """Get the zodiac sign number (1-12) from a longitude in degrees."""
    # Normalize longitude to 0-360 range
    normalized_longitude = longitude % 360.0
    return int(normalized_longitude // 30) + 1

def get_sign_name(sign_number: int) -> str:
    """Get the name of a zodiac sign by its number (1-12)."""
    return SIGN_NAMES.get(sign_number, f"Sign {sign_number}")

def get_sign_symbol(sign_number: int) -> str:
    """Get the symbol of a zodiac sign by its number (1-12)."""
    return SIGN_SYMBOLS.get(sign_number, "?")

def degrees_in_sign(longitude: float) -> float:
    """Get the degrees within a sign (0-29.999...) from a longitude."""
    return longitude % 30.0

def normalize_longitude(longitude: float) -> float:
    """Normalize longitude to 0-360 degrees."""
    return longitude % 360.0

def longitude_to_dms(longitude: float) -> Tuple[int, int, float]:
    """Convert longitude to degrees, minutes, seconds."""
    degrees = int(longitude)
    minutes_float = (longitude - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    return degrees, minutes, seconds