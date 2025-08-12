"""
Unit tests for the Meridian Ephemeris Engine constants module.
"""

import pytest
import swisseph as swe

from app.core.ephemeris.const import (
    SwePlanets, SweFlags, HouseSystems, Ayanamsa, Signs, Aspects,
    PLANET_NAMES, PLANET_SYMBOLS, SIGN_NAMES, SIGN_SYMBOLS,
    get_planet_name, get_planet_symbol, get_sign_from_longitude,
    get_sign_name, get_sign_symbol, degrees_in_sign, normalize_longitude,
    longitude_to_dms, DEFAULT_FLAGS
)


class TestSwePlanets:
    """Test Swiss Ephemeris planet constants."""
    
    def test_planet_constants_match_swe(self):
        """Test that planet constants match Swiss Ephemeris values."""
        assert SwePlanets.SUN == swe.SUN
        assert SwePlanets.MOON == swe.MOON
        assert SwePlanets.MERCURY == swe.MERCURY
        assert SwePlanets.VENUS == swe.VENUS
        assert SwePlanets.MARS == swe.MARS
        assert SwePlanets.JUPITER == swe.JUPITER
        assert SwePlanets.SATURN == swe.SATURN
        assert SwePlanets.URANUS == swe.URANUS
        assert SwePlanets.NEPTUNE == swe.NEPTUNE
        assert SwePlanets.PLUTO == swe.PLUTO
        assert SwePlanets.MEAN_NODE == swe.MEAN_NODE
        assert SwePlanets.TRUE_NODE == swe.TRUE_NODE
        assert SwePlanets.CHIRON == swe.CHIRON
    
    def test_planet_uniqueness(self):
        """Test that all planet constants are unique."""
        planets = [
            SwePlanets.SUN, SwePlanets.MOON, SwePlanets.MERCURY,
            SwePlanets.VENUS, SwePlanets.MARS, SwePlanets.JUPITER,
            SwePlanets.SATURN, SwePlanets.URANUS, SwePlanets.NEPTUNE,
            SwePlanets.PLUTO, SwePlanets.MEAN_NODE, SwePlanets.TRUE_NODE,
            SwePlanets.CHIRON
        ]
        assert len(planets) == len(set(planets))


class TestSweFlags:
    """Test Swiss Ephemeris flag constants."""
    
    def test_flag_constants_match_swe(self):
        """Test that flag constants match Swiss Ephemeris values."""
        assert SweFlags.SWIEPH == swe.FLG_SWIEPH
        assert SweFlags.SPEED == swe.FLG_SPEED
        assert SweFlags.TOPOCTR == swe.FLG_TOPOCTR
        assert SweFlags.SIDEREAL == swe.FLG_SIDEREAL
        assert SweFlags.RADIANS == swe.FLG_RADIANS
    
    def test_default_flags(self):
        """Test default calculation flags."""
        assert DEFAULT_FLAGS == (SweFlags.SWIEPH | SweFlags.SPEED)


class TestHouseSystems:
    """Test house system constants."""
    
    def test_house_system_codes(self):
        """Test house system single-character codes."""
        assert HouseSystems.PLACIDUS == 'P'
        assert HouseSystems.KOCH == 'K'
        assert HouseSystems.EQUAL == 'E'
        assert HouseSystems.WHOLE_SIGN == 'W'
        assert HouseSystems.CAMPANUS == 'C'
        assert HouseSystems.REGIOMONTANUS == 'R'
    
    def test_house_system_uniqueness(self):
        """Test that house system codes are unique."""
        codes = [
            HouseSystems.PLACIDUS, HouseSystems.KOCH, HouseSystems.EQUAL,
            HouseSystems.WHOLE_SIGN, HouseSystems.CAMPANUS, HouseSystems.REGIOMONTANUS,
            HouseSystems.PORPHYRIUS, HouseSystems.ALCABITUS, HouseSystems.MORINUS
        ]
        assert len(codes) == len(set(codes))


class TestAyanamsa:
    """Test ayanamsa constants."""
    
    def test_ayanamsa_constants_match_swe(self):
        """Test that ayanamsa constants match Swiss Ephemeris values."""
        assert Ayanamsa.FAGAN_BRADLEY == swe.SIDM_FAGAN_BRADLEY
        assert Ayanamsa.LAHIRI == swe.SIDM_LAHIRI
        assert Ayanamsa.KRISHNAMURTI == swe.SIDM_KRISHNAMURTI


class TestSigns:
    """Test zodiac sign constants."""
    
    def test_sign_degrees(self):
        """Test zodiac sign degree positions."""
        assert Signs.ARIES == 0
        assert Signs.TAURUS == 30
        assert Signs.GEMINI == 60
        assert Signs.CANCER == 90
        assert Signs.LEO == 120
        assert Signs.VIRGO == 150
        assert Signs.LIBRA == 180
        assert Signs.SCORPIO == 210
        assert Signs.SAGITTARIUS == 240
        assert Signs.CAPRICORN == 270
        assert Signs.AQUARIUS == 300
        assert Signs.PISCES == 330
    
    def test_sign_sequence(self):
        """Test that signs are in correct 30-degree sequence."""
        signs = [
            Signs.ARIES, Signs.TAURUS, Signs.GEMINI, Signs.CANCER,
            Signs.LEO, Signs.VIRGO, Signs.LIBRA, Signs.SCORPIO,
            Signs.SAGITTARIUS, Signs.CAPRICORN, Signs.AQUARIUS, Signs.PISCES
        ]
        
        for i, sign_degree in enumerate(signs):
            assert sign_degree == i * 30


class TestAspects:
    """Test aspect constants."""
    
    def test_major_aspects(self):
        """Test major aspect degrees."""
        assert Aspects.CONJUNCTION == 0
        assert Aspects.OPPOSITION == 180
        assert Aspects.SQUARE == 90
        assert Aspects.TRINE == 120
        assert Aspects.SEXTILE == 60
        assert Aspects.QUINCUNX == 150
    
    def test_minor_aspects(self):
        """Test minor aspect degrees."""
        assert Aspects.SEMISEXTILE == 30
        assert Aspects.SEMISQUARE == 45
        assert Aspects.SESQUISQUARE == 135
        assert Aspects.QUINTILE == 72
        assert Aspects.BIQUINTILE == 144


class TestPlanetNames:
    """Test planet name mappings."""
    
    def test_planet_names_coverage(self):
        """Test that all major planets have names."""
        major_planets = [
            SwePlanets.SUN, SwePlanets.MOON, SwePlanets.MERCURY,
            SwePlanets.VENUS, SwePlanets.MARS, SwePlanets.JUPITER,
            SwePlanets.SATURN, SwePlanets.URANUS, SwePlanets.NEPTUNE,
            SwePlanets.PLUTO
        ]
        
        for planet in major_planets:
            assert planet in PLANET_NAMES
            assert isinstance(PLANET_NAMES[planet], str)
            assert len(PLANET_NAMES[planet]) > 0
    
    def test_planet_symbols_coverage(self):
        """Test that all major planets have symbols."""
        major_planets = [
            SwePlanets.SUN, SwePlanets.MOON, SwePlanets.MERCURY,
            SwePlanets.VENUS, SwePlanets.MARS, SwePlanets.JUPITER,
            SwePlanets.SATURN, SwePlanets.URANUS, SwePlanets.NEPTUNE,
            SwePlanets.PLUTO
        ]
        
        for planet in major_planets:
            assert planet in PLANET_SYMBOLS
            assert isinstance(PLANET_SYMBOLS[planet], str)
            assert len(PLANET_SYMBOLS[planet]) > 0


class TestSignNames:
    """Test sign name mappings."""
    
    def test_sign_names_complete(self):
        """Test that all 12 signs have names."""
        for i in range(1, 13):
            assert i in SIGN_NAMES
            assert isinstance(SIGN_NAMES[i], str)
            assert len(SIGN_NAMES[i]) > 0
    
    def test_sign_symbols_complete(self):
        """Test that all 12 signs have symbols."""
        for i in range(1, 13):
            assert i in SIGN_SYMBOLS
            assert isinstance(SIGN_SYMBOLS[i], str)
            assert len(SIGN_SYMBOLS[i]) > 0


class TestUtilityFunctions:
    """Test utility functions for coordinate conversions."""
    
    def test_get_planet_name(self):
        """Test planet name retrieval."""
        assert get_planet_name(SwePlanets.SUN) == 'Sun'
        assert get_planet_name(SwePlanets.MOON) == 'Moon'
        assert get_planet_name(999) == 'Planet 999'  # Unknown planet
    
    def test_get_planet_symbol(self):
        """Test planet symbol retrieval."""
        assert get_planet_symbol(SwePlanets.SUN) == '☉'
        assert get_planet_symbol(SwePlanets.MARS) == '♂'
        assert get_planet_symbol(999) == '?'  # Unknown planet
    
    def test_get_sign_from_longitude(self):
        """Test sign calculation from longitude."""
        assert get_sign_from_longitude(0.0) == 1    # Aries
        assert get_sign_from_longitude(15.0) == 1   # Still Aries
        assert get_sign_from_longitude(30.0) == 2   # Taurus
        assert get_sign_from_longitude(45.0) == 2   # Still Taurus
        assert get_sign_from_longitude(90.0) == 4   # Cancer
        assert get_sign_from_longitude(180.0) == 7  # Libra
        assert get_sign_from_longitude(270.0) == 10 # Capricorn
        assert get_sign_from_longitude(359.9) == 12 # Pisces
    
    def test_get_sign_name(self):
        """Test sign name retrieval by number."""
        assert get_sign_name(1) == 'Aries'
        assert get_sign_name(4) == 'Cancer'
        assert get_sign_name(7) == 'Libra'
        assert get_sign_name(10) == 'Capricorn'
        assert get_sign_name(13) == 'Sign 13'  # Invalid sign
    
    def test_get_sign_symbol(self):
        """Test sign symbol retrieval by number."""
        assert get_sign_symbol(1) == '♈'  # Aries
        assert get_sign_symbol(5) == '♌'  # Leo
        assert get_sign_symbol(9) == '♐'  # Sagittarius
        assert get_sign_symbol(13) == '?'  # Invalid sign
    
    def test_degrees_in_sign(self):
        """Test degrees within sign calculation."""
        assert degrees_in_sign(0.0) == 0.0
        assert degrees_in_sign(15.5) == 15.5
        assert degrees_in_sign(30.0) == 0.0    # Start of new sign
        assert abs(degrees_in_sign(45.7) - 15.7) < 0.001   # 15.7 degrees in Taurus
        assert abs(degrees_in_sign(359.9) - 29.9) < 0.001  # Near end of Pisces
    
    def test_normalize_longitude(self):
        """Test longitude normalization to 0-360 range."""
        assert normalize_longitude(0.0) == 0.0
        assert normalize_longitude(180.0) == 180.0
        assert normalize_longitude(360.0) == 0.0
        assert normalize_longitude(450.0) == 90.0
        assert normalize_longitude(-90.0) == 270.0
        assert normalize_longitude(-180.0) == 180.0
    
    def test_longitude_to_dms(self):
        """Test longitude to degrees/minutes/seconds conversion."""
        # Test exact degrees
        deg, min, sec = longitude_to_dms(45.0)
        assert deg == 45
        assert min == 0
        assert sec == 0.0
        
        # Test with minutes
        deg, min, sec = longitude_to_dms(45.5)
        assert deg == 45
        assert min == 30
        assert sec == 0.0
        
        # Test with seconds
        deg, min, sec = longitude_to_dms(45.25833333)  # 45°15'30"
        assert deg == 45
        assert min == 15
        assert abs(sec - 30.0) < 0.1  # Allow small floating point error
    
    @pytest.mark.parametrize("longitude,expected_sign", [
        (0.0, 1), (29.9, 1),      # Aries
        (30.0, 2), (59.9, 2),     # Taurus
        (60.0, 3), (89.9, 3),     # Gemini
        (90.0, 4), (119.9, 4),    # Cancer
        (120.0, 5), (149.9, 5),   # Leo
        (150.0, 6), (179.9, 6),   # Virgo
        (180.0, 7), (209.9, 7),   # Libra
        (210.0, 8), (239.9, 8),   # Scorpio
        (240.0, 9), (269.9, 9),   # Sagittarius
        (270.0, 10), (299.9, 10), # Capricorn
        (300.0, 11), (329.9, 11), # Aquarius
        (330.0, 12), (359.9, 12)  # Pisces
    ])
    def test_longitude_sign_boundaries(self, longitude, expected_sign):
        """Test sign boundaries with various longitudes."""
        assert get_sign_from_longitude(longitude) == expected_sign