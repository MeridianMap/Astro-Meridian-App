"""
Minimal const utilities for extracted systems.
"""

from typing import Tuple

SIGN_NAMES = {
    1: 'Aries', 2: 'Taurus', 3: 'Gemini', 4: 'Cancer',
    5: 'Leo', 6: 'Virgo', 7: 'Libra', 8: 'Scorpio',
    9: 'Sagittarius', 10: 'Capricorn', 11: 'Aquarius', 12: 'Pisces'
}

def normalize_longitude(longitude: float) -> float:
    """Normalize longitude to 0-360 degrees."""
    return longitude % 360.0

def get_sign_from_longitude(longitude: float) -> int:
    """Get zodiac sign number (1-12) from ecliptic longitude."""
    return int((longitude % 360.0) // 30) + 1

def get_sign_name(sign_number: int) -> str:
    return SIGN_NAMES.get(sign_number, f"Sign {sign_number}")
