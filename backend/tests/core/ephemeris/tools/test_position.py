"""
Unit tests for the Meridian Ephemeris Engine position analysis utilities.
"""

import pytest
from unittest.mock import patch
from app.core.ephemeris.tools.position import (
    get_longitude, zodiac_sign, sign_longitude, opposite_sign, decan,
    element, modality, house_position, opposite_house_position,
    angular_separation, is_in_same_sign, is_in_same_element, 
    is_in_same_modality, get_position_summary, get_critical_degrees,
    is_at_critical_degree, is_at_sign_boundary, get_closest_aspect_angle,
    clear_house_cache, sign_name, sign_symbol, element_name, modality_name,
    format_position, Element, Modality, Decan, ELEMENT_NAMES, MODALITY_NAMES
)


class TestBasicPositionFunctions:
    """Test basic position extraction and calculation functions."""
    
    def test_get_longitude_from_dict(self):
        """Test longitude extraction from dictionary."""
        position_dict = {'lon': 120.5}
        assert get_longitude(position_dict) == 120.5
        
        position_dict = {'longitude': 135.75}
        assert get_longitude(position_dict) == 135.75
        
        # Missing longitude should default to 0
        empty_dict = {}
        assert get_longitude(empty_dict) == 0.0
    
    def test_get_longitude_from_float(self):
        """Test longitude extraction from float."""
        assert get_longitude(45.5) == 45.5
        assert get_longitude(180.0) == 180.0
        assert get_longitude(-90.0) == -90.0


class TestZodiacSignFunctions:
    """Test zodiac sign-related functions."""
    
    def test_zodiac_sign_calculation(self):
        """Test zodiac sign calculation for various longitudes."""
        assert zodiac_sign(0.0) == 1      # Aries
        assert zodiac_sign(15.0) == 1     # Still Aries
        assert zodiac_sign(30.0) == 2     # Taurus
        assert zodiac_sign(60.0) == 3     # Gemini
        assert zodiac_sign(90.0) == 4     # Cancer
        assert zodiac_sign(120.0) == 5    # Leo
        assert zodiac_sign(150.0) == 6    # Virgo
        assert zodiac_sign(180.0) == 7    # Libra
        assert zodiac_sign(210.0) == 8    # Scorpio
        assert zodiac_sign(240.0) == 9    # Sagittarius
        assert zodiac_sign(270.0) == 10   # Capricorn
        assert zodiac_sign(300.0) == 11   # Aquarius
        assert zodiac_sign(330.0) == 12   # Pisces
        assert zodiac_sign(359.9) == 12   # Still Pisces
    
    def test_zodiac_sign_with_dict_input(self):
        """Test zodiac sign with dictionary input."""
        position = {'lon': 45.0}
        assert zodiac_sign(position) == 2  # Taurus
    
    def test_sign_longitude_calculation(self):
        """Test longitude within sign calculation."""
        assert sign_longitude(0.0) == 0.0
        assert sign_longitude(15.0) == 15.0
        assert sign_longitude(30.0) == 0.0    # Start of Taurus
        assert sign_longitude(45.0) == 15.0   # 15° Taurus
        assert abs(sign_longitude(359.9) - 29.9) < 0.001  # 29.9° Pisces (within floating point tolerance)
    
    def test_opposite_sign_calculation(self):
        """Test opposite sign calculation."""
        assert opposite_sign(0.0) == 7     # Aries → Libra
        assert opposite_sign(30.0) == 8    # Taurus → Scorpio  
        assert opposite_sign(60.0) == 9    # Gemini → Sagittarius
        assert opposite_sign(90.0) == 10   # Cancer → Capricorn
        assert opposite_sign(120.0) == 11  # Leo → Aquarius
        assert opposite_sign(150.0) == 12  # Virgo → Pisces
        assert opposite_sign(180.0) == 1   # Libra → Aries
        assert opposite_sign(210.0) == 2   # Scorpio → Taurus
        assert opposite_sign(240.0) == 3   # Sagittarius → Gemini
        assert opposite_sign(270.0) == 4   # Capricorn → Cancer
        assert opposite_sign(300.0) == 5   # Aquarius → Leo
        assert opposite_sign(330.0) == 6   # Pisces → Virgo


class TestDecanFunctions:
    """Test decan calculation functions."""
    
    def test_decan_calculation(self):
        """Test decan calculation within signs."""
        # First decan (0-10°)
        assert decan(0.0) == 1
        assert decan(5.0) == 1
        assert decan(9.9) == 1
        
        # Second decan (10-20°)
        assert decan(10.0) == 2
        assert decan(15.0) == 2
        assert decan(19.9) == 2
        
        # Third decan (20-30°)
        assert decan(20.0) == 3
        assert decan(25.0) == 3
        assert decan(29.9) == 3
        
        # Test across sign boundaries
        assert decan(30.0) == 1   # Start of next sign, first decan
        assert decan(40.0) == 2   # Second decan of next sign
        assert decan(50.0) == 3   # Third decan of next sign
    
    def test_decan_with_dict_input(self):
        """Test decan with dictionary input."""
        position = {'lon': 45.0}  # 15° Taurus (second decan)
        assert decan(position) == 2


class TestElementAndModalityFunctions:
    """Test element and modality classification functions."""
    
    def test_element_calculation(self):
        """Test element classification."""
        # Fire signs (1, 5, 9) → element 1
        assert element(0.0) == Element.FIRE      # Aries
        assert element(120.0) == Element.FIRE    # Leo
        assert element(240.0) == Element.FIRE    # Sagittarius
        
        # Earth signs (2, 6, 10) → element 2
        assert element(30.0) == Element.EARTH    # Taurus
        assert element(150.0) == Element.EARTH   # Virgo
        assert element(270.0) == Element.EARTH   # Capricorn
        
        # Air signs (3, 7, 11) → element 3
        assert element(60.0) == Element.AIR      # Gemini
        assert element(180.0) == Element.AIR     # Libra
        assert element(300.0) == Element.AIR     # Aquarius
        
        # Water signs (4, 8, 12) → element 4
        assert element(90.0) == Element.WATER    # Cancer
        assert element(210.0) == Element.WATER   # Scorpio
        assert element(330.0) == Element.WATER   # Pisces
    
    def test_modality_calculation(self):
        """Test modality classification."""
        # Cardinal signs (1, 4, 7, 10) → modality 1
        assert modality(0.0) == Modality.CARDINAL    # Aries
        assert modality(90.0) == Modality.CARDINAL   # Cancer
        assert modality(180.0) == Modality.CARDINAL  # Libra
        assert modality(270.0) == Modality.CARDINAL  # Capricorn
        
        # Fixed signs (2, 5, 8, 11) → modality 2
        assert modality(30.0) == Modality.FIXED     # Taurus
        assert modality(120.0) == Modality.FIXED    # Leo
        assert modality(210.0) == Modality.FIXED    # Scorpio
        assert modality(300.0) == Modality.FIXED    # Aquarius
        
        # Mutable signs (3, 6, 9, 12) → modality 3
        assert modality(60.0) == Modality.MUTABLE   # Gemini
        assert modality(150.0) == Modality.MUTABLE  # Virgo
        assert modality(240.0) == Modality.MUTABLE  # Sagittarius
        assert modality(330.0) == Modality.MUTABLE  # Pisces


class TestHousePositions:
    """Test house position calculations."""
    
    def test_house_position_basic(self):
        """Test basic house position calculation."""
        # Mock house data
        houses = {
            'house1': {'number': 1, 'lon': 0.0, 'size': 30.0},
            'house2': {'number': 2, 'lon': 30.0, 'size': 30.0},
            'house3': {'number': 3, 'lon': 60.0, 'size': 30.0}
        }
        
        # Test position in first house
        with patch('swisseph.difdeg2n', side_effect=[15.0, 30.0]):
            result = house_position(15.0, houses)
            assert result['number'] == 1
        
        # Clear cache for clean test
        clear_house_cache()
    
    def test_house_position_caching(self):
        """Test that house positions are cached."""
        houses = {
            'house1': {'number': 1, 'lon': 0.0, 'size': 30.0}
        }
        
        with patch('swisseph.difdeg2n', side_effect=[15.0, 30.0]) as mock_swe:
            # First call should use Swiss Ephemeris
            result1 = house_position(15.0, houses)
            assert result1['number'] == 1
            
            # Second call should use cache
            result2 = house_position(15.0, houses)
            assert result2['number'] == 1
            
            # Should only have called Swiss Ephemeris once
            assert mock_swe.call_count == 2  # Called twice for the first calculation
        
        clear_house_cache()
    
    def test_opposite_house_position(self):
        """Test opposite house position calculation."""
        houses = {
            'house1': {'number': 1, 'lon': 0.0, 'size': 30.0},
            'house7': {'number': 7, 'lon': 180.0, 'size': 30.0}
        }
        
        with patch('swisseph.difdeg2n', side_effect=[15.0, 30.0]):
            # Position in house 1 should have opposite house 7
            result = opposite_house_position(15.0, houses)
            assert result['number'] == 7
        
        clear_house_cache()


class TestAngularMeasurements:
    """Test angular separation and relationship functions."""
    
    def test_angular_separation(self):
        """Test angular separation calculation."""
        with patch('swisseph.difdeg2n', return_value=45.0):
            separation = angular_separation(0.0, 45.0)
            assert separation == 45.0
        
        with patch('swisseph.difdeg2n', return_value=-90.0):
            separation = angular_separation(0.0, 270.0)
            assert separation == 90.0  # Should be absolute value
    
    def test_is_in_same_sign(self):
        """Test same sign detection."""
        assert is_in_same_sign(15.0, 25.0) is True    # Both in Aries
        assert is_in_same_sign(15.0, 45.0) is False   # Aries vs Taurus
        assert is_in_same_sign({'lon': 15.0}, 25.0) is True
    
    def test_is_in_same_element(self):
        """Test same element detection."""
        assert is_in_same_element(0.0, 120.0) is True   # Aries & Leo (Fire)
        assert is_in_same_element(0.0, 30.0) is False   # Aries & Taurus
        assert is_in_same_element(30.0, 270.0) is True  # Taurus & Capricorn (Earth)
    
    def test_is_in_same_modality(self):
        """Test same modality detection."""
        assert is_in_same_modality(0.0, 90.0) is True    # Aries & Cancer (Cardinal)
        assert is_in_same_modality(0.0, 30.0) is False   # Aries & Taurus
        assert is_in_same_modality(30.0, 120.0) is True  # Taurus & Leo (Fixed)


class TestPositionSummary:
    """Test comprehensive position summary function."""
    
    def test_get_position_summary_basic(self):
        """Test basic position summary without houses."""
        summary = get_position_summary(125.5)  # 5.5° Leo
        
        assert summary['longitude'] == 125.5
        assert summary['sign']['number'] == 5
        assert summary['sign']['name'] == 'Leo'
        assert summary['sign']['symbol'] == '♌'
        assert summary['sign_longitude'] == 5.5
        assert summary['decan'] == 1
        assert summary['element']['number'] == Element.FIRE
        assert summary['element']['name'] == 'Fire'
        assert summary['modality']['number'] == Modality.FIXED
        assert summary['modality']['name'] == 'Fixed'
    
    def test_get_position_summary_with_houses(self):
        """Test position summary with house data."""
        houses = {
            'house5': {'number': 5, 'lon': 120.0, 'size': 30.0}
        }
        
        with patch('swisseph.difdeg2n', side_effect=[5.5, 30.0]):
            summary = get_position_summary(125.5, houses)
            assert 'house' in summary
            assert summary['house']['number'] == 5


class TestCriticalDegreesAndBoundaries:
    """Test critical degree and boundary functions."""
    
    def test_get_critical_degrees(self):
        """Test critical degrees retrieval."""
        critical_degrees = get_critical_degrees()
        
        # Check that all signs have critical degrees
        for sign in range(1, 13):
            assert sign in critical_degrees
            assert isinstance(critical_degrees[sign], list)
            assert len(critical_degrees[sign]) > 0
    
    def test_is_at_critical_degree(self):
        """Test critical degree detection."""
        # Test some known critical degrees
        assert is_at_critical_degree(0.0, tolerance=1.0) is True    # 0° Aries
        assert is_at_critical_degree(13.0, tolerance=1.0) is True   # 13° Aries
        assert is_at_critical_degree(26.0, tolerance=1.0) is True   # 26° Aries
        
        # Test non-critical degrees
        assert is_at_critical_degree(7.0, tolerance=1.0) is False   # 7° Aries
        assert is_at_critical_degree(20.0, tolerance=1.0) is False  # 20° Aries
    
    def test_is_at_sign_boundary(self):
        """Test sign boundary detection."""
        assert is_at_sign_boundary(0.0, tolerance=1.0) is True    # 0° (start of sign)
        assert is_at_sign_boundary(29.0, tolerance=1.0) is True   # 29° (end of sign)
        assert is_at_sign_boundary(30.0, tolerance=1.0) is True   # 0° next sign
        assert is_at_sign_boundary(15.0, tolerance=1.0) is False  # Middle of sign


class TestAspectCalculations:
    """Test aspect-related calculations."""
    
    def test_get_closest_aspect_angle(self):
        """Test closest aspect calculation."""
        # Test exact conjunction
        with patch('app.core.ephemeris.tools.position.angular_separation', return_value=0.0):
            aspect = get_closest_aspect_angle(0.0, 0.0)
            assert aspect['aspect'] == 'Conjunction'
            assert aspect['angle'] == 0
            assert aspect['orb'] == 0.0
        
        # Test approximate square
        with patch('app.core.ephemeris.tools.position.angular_separation', return_value=92.0):
            aspect = get_closest_aspect_angle(0.0, 92.0)
            assert aspect['aspect'] == 'Square'
            assert aspect['angle'] == 90
            assert aspect['orb'] == 2.0
        
        # Test opposition
        with patch('app.core.ephemeris.tools.position.angular_separation', return_value=178.0):
            aspect = get_closest_aspect_angle(0.0, 178.0)
            assert aspect['aspect'] == 'Opposition'
            assert aspect['angle'] == 180
            assert aspect['orb'] == 2.0


class TestConvenienceFunctions:
    """Test convenience and formatting functions."""
    
    def test_sign_name(self):
        """Test sign name retrieval."""
        assert sign_name(0.0) == 'Aries'
        assert sign_name(30.0) == 'Taurus'
        assert sign_name(120.0) == 'Leo'
        assert sign_name({'lon': 180.0}) == 'Libra'
    
    def test_sign_symbol(self):
        """Test sign symbol retrieval."""
        assert sign_symbol(0.0) == '♈'    # Aries
        assert sign_symbol(120.0) == '♌'  # Leo
        assert sign_symbol({'lon': 180.0}) == '♎'  # Libra
    
    def test_element_name(self):
        """Test element name retrieval."""
        assert element_name(0.0) == 'Fire'     # Aries
        assert element_name(30.0) == 'Earth'   # Taurus
        assert element_name(60.0) == 'Air'     # Gemini
        assert element_name(90.0) == 'Water'   # Cancer
    
    def test_modality_name(self):
        """Test modality name retrieval."""
        assert modality_name(0.0) == 'Cardinal'  # Aries
        assert modality_name(30.0) == 'Fixed'    # Taurus
        assert modality_name(60.0) == 'Mutable'  # Gemini
    
    def test_format_position(self):
        """Test position formatting."""
        # 15.5° Leo
        formatted = format_position(125.5, include_seconds=True)
        assert 'Leo' in formatted
        assert '05°' in formatted
        assert '30\'' in formatted
        
        # Without seconds
        formatted = format_position(125.5, include_seconds=False)
        assert 'Leo' in formatted
        assert '05°' in formatted
        assert '30\'' in formatted
        assert '\"' not in formatted  # No seconds symbol


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_boundary_longitudes(self):
        """Test calculations at sign boundaries."""
        # Exactly at sign boundaries
        assert zodiac_sign(0.0) == 1
        assert zodiac_sign(30.0) == 2
        assert zodiac_sign(360.0) == 1  # Should wrap around
        
        # Sign longitude at boundaries
        assert sign_longitude(0.0) == 0.0
        assert sign_longitude(30.0) == 0.0
        assert sign_longitude(360.0) == 0.0
    
    def test_negative_longitudes(self):
        """Test handling of negative longitudes."""
        # Negative longitudes should still work
        # -30° = 330°, which is Pisces (sign 12)
        assert zodiac_sign(-30.0) == 12  # Should map to Pisces (330°)
        assert element(-30.0) == Element.WATER  # Pisces is Water
    
    def test_large_longitudes(self):
        """Test handling of very large longitudes."""
        # Should normalize properly
        large_longitude = 720.0 + 45.0  # Two full circles plus 45°
        assert zodiac_sign(large_longitude) == 2  # Should be Taurus
        assert abs(sign_longitude(large_longitude) - 15.0) < 0.001
    
    def test_house_position_no_match(self):
        """Test house position when no house matches."""
        houses = {
            'house1': {'number': 1, 'lon': 0.0, 'size': 15.0}  # Very small house
        }
        
        # Position far outside any house
        with patch('swisseph.difdeg2n', return_value=50.0):
            result = house_position(200.0, houses)
            assert result is None
        
        clear_house_cache()
    
    def test_invalid_house_data(self):
        """Test house position with invalid house data."""
        invalid_houses = {
            'house1': "not a dict",
            'house2': {'no_number': True}
        }
        
        result = house_position(15.0, invalid_houses)
        assert result is None
        
        clear_house_cache()


class TestConstantsAndMappings:
    """Test constants and mapping dictionaries."""
    
    def test_element_names_completeness(self):
        """Test that all element constants have names."""
        assert Element.FIRE in ELEMENT_NAMES
        assert Element.EARTH in ELEMENT_NAMES
        assert Element.AIR in ELEMENT_NAMES
        assert Element.WATER in ELEMENT_NAMES
        
        for element_id, name in ELEMENT_NAMES.items():
            assert isinstance(name, str)
            assert len(name) > 0
    
    def test_modality_names_completeness(self):
        """Test that all modality constants have names."""
        assert Modality.CARDINAL in MODALITY_NAMES
        assert Modality.FIXED in MODALITY_NAMES
        assert Modality.MUTABLE in MODALITY_NAMES
        
        for modality_id, name in MODALITY_NAMES.items():
            assert isinstance(name, str)
            assert len(name) > 0
    
    def test_consistency_between_functions_and_constants(self):
        """Test consistency between calculation functions and constants."""
        # Test that element calculation matches element classification
        for sign_num in range(1, 13):
            longitude = (sign_num - 1) * 30.0  # Start of each sign
            calculated_element = element(longitude)
            
            # Verify the element is one of the valid constants
            assert calculated_element in [Element.FIRE, Element.EARTH, Element.AIR, Element.WATER]
            
            # Verify the element has a name
            assert calculated_element in ELEMENT_NAMES


@pytest.mark.parametrize("longitude,expected_sign,expected_element,expected_modality", [
    (0.0, 1, Element.FIRE, Modality.CARDINAL),      # Aries
    (30.0, 2, Element.EARTH, Modality.FIXED),       # Taurus
    (60.0, 3, Element.AIR, Modality.MUTABLE),       # Gemini
    (90.0, 4, Element.WATER, Modality.CARDINAL),    # Cancer
    (120.0, 5, Element.FIRE, Modality.FIXED),       # Leo
    (150.0, 6, Element.EARTH, Modality.MUTABLE),    # Virgo
    (180.0, 7, Element.AIR, Modality.CARDINAL),     # Libra
    (210.0, 8, Element.WATER, Modality.FIXED),      # Scorpio
    (240.0, 9, Element.FIRE, Modality.MUTABLE),     # Sagittarius
    (270.0, 10, Element.EARTH, Modality.CARDINAL),  # Capricorn
    (300.0, 11, Element.AIR, Modality.FIXED),       # Aquarius
    (330.0, 12, Element.WATER, Modality.MUTABLE),   # Pisces
])
def test_zodiac_classifications_parametrized(longitude, expected_sign, expected_element, expected_modality):
    """Test zodiac classifications for all signs using parametrization."""
    assert zodiac_sign(longitude) == expected_sign
    assert element(longitude) == expected_element
    assert modality(longitude) == expected_modality