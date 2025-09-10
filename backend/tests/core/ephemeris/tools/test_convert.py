"""
Unit tests for the Meridian Ephemeris Engine coordinate conversion utilities.
"""

import pytest
import math
from extracted.systems.convert import (
    dms_to_decimal, decimal_to_dms, dms_to_string, string_to_dms,
    decimal_to_string, string_to_decimal, to_decimal, to_dms, to_string,
    coordinates, normalize_longitude, normalize_latitude,
    distance_between_coordinates, degrees_to_hours, hours_to_degrees,
    Format, RoundTo
)


class TestDMSDecimalConversions:
    """Test DMS ↔ decimal conversions."""
    
    def test_dms_to_decimal_basic(self):
        """Test basic DMS to decimal conversion."""
        # 45°30'30" = 45.508333...
        dms = ["+", 45, 30, 30.0]
        result = dms_to_decimal(dms)
        expected = 45.0 + 30/60.0 + 30/3600.0
        assert abs(result - expected) < 0.000001
    
    def test_dms_to_decimal_negative(self):
        """Test negative DMS to decimal conversion."""
        dms = ["-", 45, 30, 30.0]
        result = dms_to_decimal(dms)
        expected = -(45.0 + 30/60.0 + 30/3600.0)
        assert abs(result - expected) < 0.000001
    
    def test_decimal_to_dms_positive(self):
        """Test positive decimal to DMS conversion."""
        decimal = 45.508333333
        result = decimal_to_dms(decimal)
        assert result[0] == "+"
        assert result[1] == 45
        assert result[2] == 30
        assert abs(result[3] - 30.0) < 0.1  # Allow small floating point error
    
    def test_decimal_to_dms_negative(self):
        """Test negative decimal to DMS conversion."""
        decimal = -45.508333333
        result = decimal_to_dms(decimal)
        assert result[0] == "-"
        assert result[1] == 45
        assert result[2] == 30
        assert abs(result[3] - 30.0) < 0.1
    
    def test_decimal_to_dms_rounding(self):
        """Test different rounding precisions."""
        decimal = 45.508333333
        
        # Round to degrees
        result = decimal_to_dms(decimal, RoundTo.DEGREE)
        assert len(result) == 2
        assert result[1] == 46  # Should round up
        
        # Round to minutes
        result = decimal_to_dms(decimal, RoundTo.MINUTE)
        assert len(result) == 3
        assert result[2] == 30  # Should be 30 minutes
    
    def test_round_trip_conversion(self):
        """Test that DMS → decimal → DMS preserves value."""
        original_dms = ["+", 120, 15, 45.7]
        decimal = dms_to_decimal(original_dms)
        result_dms = decimal_to_dms(decimal)
        
        # Compare the decimal values
        original_decimal = dms_to_decimal(original_dms)
        result_decimal = dms_to_decimal(result_dms)
        assert abs(original_decimal - result_decimal) < 0.001


class TestStringConversions:
    """Test string parsing and formatting."""
    
    def test_string_to_decimal_simple_decimal(self):
        """Test parsing simple decimal string."""
        assert string_to_decimal("45.5") == 45.5
        assert string_to_decimal("-123.75") == -123.75
    
    def test_string_to_decimal_dms_symbols(self):
        """Test parsing DMS with symbols."""
        result = string_to_decimal("45°30'15\"")
        expected = 45 + 30/60.0 + 15/3600.0
        assert abs(result - expected) < 0.000001
    
    def test_string_to_decimal_colon_format(self):
        """Test parsing colon-separated format."""
        result = string_to_decimal("45:30:15")
        expected = 45 + 30/60.0 + 15/3600.0
        assert abs(result - expected) < 0.000001
    
    def test_string_to_decimal_latitude_format(self):
        """Test parsing latitude format."""
        result = string_to_decimal("45N30.5")
        expected = 45 + 30.5/60.0
        assert abs(result - expected) < 0.000001
        
        result = string_to_decimal("45S30.5")
        expected = -(45 + 30.5/60.0)
        assert abs(result - expected) < 0.000001
    
    def test_string_to_decimal_longitude_format(self):
        """Test parsing longitude format."""
        result = string_to_decimal("120E15.5")
        expected = 120 + 15.5/60.0
        assert abs(result - expected) < 0.000001
        
        result = string_to_decimal("120W15.5")
        expected = -(120 + 15.5/60.0)
        assert abs(result - expected) < 0.000001
    
    def test_dms_to_string_formats(self):
        """Test different string output formats."""
        dms = ["+", 45, 30, 15.5]
        
        # DMS format
        result = dms_to_string(dms, Format.DMS)
        assert "45°" in result and "30'" in result and "15.5\"" in result
        
        # Time format
        result = dms_to_string(dms, Format.TIME)
        assert "45:30" in result
        
        # Latitude format
        result = dms_to_string(dms, Format.LAT)
        assert "45N" in result
        
        # Longitude format  
        result = dms_to_string(dms, Format.LON)
        assert "45E" in result
    
    def test_decimal_to_string_formats(self):
        """Test decimal to string in various formats."""
        decimal = 45.508333
        
        result = decimal_to_string(decimal, Format.DMS)
        assert "45°" in result
        
        result = decimal_to_string(decimal, Format.LAT)
        assert "45N" in result
        
        result = decimal_to_string(-decimal, Format.LAT)
        assert "45S" in result


class TestUniversalConverters:
    """Test universal converter functions."""
    
    def test_to_decimal_various_inputs(self):
        """Test to_decimal with different input types."""
        # Float input
        assert to_decimal(45.5) == 45.5
        
        # DMS input
        assert abs(to_decimal(["+", 45, 30, 0]) - 45.5) < 0.001
        
        # String input
        assert to_decimal("45.5") == 45.5
        assert abs(to_decimal("45°30'") - 45.5) < 0.001
        
        # Invalid input
        assert to_decimal("invalid") is None
        assert to_decimal(None) is None
    
    def test_to_dms_various_inputs(self):
        """Test to_dms with different input types."""
        # Float input
        result = to_dms(45.5)
        assert result[0] == "+"
        assert result[1] == 45
        assert result[2] == 30
        
        # String input
        result = to_dms("45°30'")
        assert abs(dms_to_decimal(result) - 45.5) < 0.001
        
        # Already DMS
        original = ["+", 45, 30, 0]
        result = to_dms(original)
        assert abs(dms_to_decimal(result) - dms_to_decimal(original)) < 0.001
    
    def test_to_string_various_inputs(self):
        """Test to_string with different input types."""
        # Float input
        result = to_string(45.5, Format.DMS)
        assert "45°" in result and "30'" in result
        
        # DMS input
        result = to_string(["+", 45, 30, 0], Format.DMS)
        assert "45°" in result and "30'" in result
        
        # String input
        result = to_string("45.5", Format.LAT)
        assert "45N" in result


class TestCoordinateHelpers:
    """Test coordinate helper functions."""
    
    def test_coordinates_function(self):
        """Test coordinate pair conversion."""
        lat, lon = coordinates("45°30'N", "120°15'W")
        assert abs(lat - 45.5) < 0.001
        assert abs(lon - (-120.25)) < 0.001
    
    def test_normalize_longitude(self):
        """Test longitude normalization."""
        assert normalize_longitude(0) == 0
        assert normalize_longitude(180) == 180
        assert normalize_longitude(360) == 0
        assert normalize_longitude(450) == 90
        assert normalize_longitude(-90) == 270
        assert normalize_longitude(-180) == 180
    
    def test_normalize_latitude(self):
        """Test latitude clamping."""
        assert normalize_latitude(45) == 45
        assert normalize_latitude(90) == 90
        assert normalize_latitude(-90) == -90
        assert normalize_latitude(100) == 90  # Clamp to 90
        assert normalize_latitude(-100) == -90  # Clamp to -90
    
    def test_degrees_hours_conversion(self):
        """Test degrees ↔ hours conversion."""
        assert degrees_to_hours(180) == 12
        assert degrees_to_hours(360) == 24
        assert hours_to_degrees(12) == 180
        assert hours_to_degrees(24) == 360
        
        # Round trip
        degrees = 123.45
        hours = degrees_to_hours(degrees)
        back_to_degrees = hours_to_degrees(hours)
        assert abs(degrees - back_to_degrees) < 0.0001
    
    def test_distance_between_coordinates(self):
        """Test great circle distance calculation."""
        # Distance from London to Paris (approximately 344 km)
        london_lat, london_lon = 51.5074, -0.1278
        paris_lat, paris_lon = 48.8566, 2.3522
        
        distance = distance_between_coordinates(london_lat, london_lon, paris_lat, paris_lon)
        
        # Should be approximately 344 km
        assert 300 < distance < 400
        
        # Distance from a point to itself should be 0
        distance = distance_between_coordinates(london_lat, london_lon, london_lat, london_lon)
        assert abs(distance) < 0.001


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_dms_to_decimal_edge_cases(self):
        """Test edge cases for DMS conversion."""
        # Empty or short DMS
        with pytest.raises(ValueError):
            dms_to_decimal([])
        
        with pytest.raises(ValueError):
            dms_to_decimal(["+"])
    
    def test_string_to_decimal_invalid_input(self):
        """Test invalid string inputs."""
        with pytest.raises(ValueError):
            string_to_decimal("not a number")
        
        with pytest.raises(ValueError):
            string_to_decimal("")
    
    def test_boundary_values(self):
        """Test boundary values."""
        # 0 degrees
        assert dms_to_decimal(["+", 0, 0, 0]) == 0.0
        assert decimal_to_dms(0.0)[1] == 0
        
        # 360 degrees (should normalize)
        result = normalize_longitude(360.0)
        assert result == 0.0
        
        # Very small values
        small_decimal = 0.000001
        dms = decimal_to_dms(small_decimal)
        back_to_decimal = dms_to_decimal(dms)
        assert abs(small_decimal - back_to_decimal) < 0.000002  # Allow for rounding
    
    def test_large_values(self):
        """Test handling of large coordinate values."""
        large_value = 987654.321
        dms = decimal_to_dms(large_value)
        back_to_decimal = dms_to_decimal(dms)
        assert abs(large_value - back_to_decimal) < 0.001
    
    @pytest.mark.parametrize("input_str,expected", [
        ("0", 0.0),
        ("90", 90.0),
        ("-180", -180.0),
        ("45.123456", 45.123456),
        ("0.0", 0.0),
    ])
    def test_numeric_string_parsing(self, input_str, expected):
        """Test parsing of various numeric strings."""
        result = string_to_decimal(input_str)
        assert abs(result - expected) < 0.000001


class TestCompatibilityWithImmanuel:
    """Test compatibility with Immanuel reference implementation."""
    
    def test_dms_format_compatibility(self):
        """Test that DMS format matches Immanuel expectations."""
        # Test case: 45°30'15" should parse and format consistently
        original_string = "45°30'15\""
        decimal = string_to_decimal(original_string)
        dms = decimal_to_dms(decimal)
        formatted = dms_to_string(dms, Format.DMS)
        
        # Should contain the same numeric values
        assert "45°" in formatted
        assert "30'" in formatted
        assert "15" in formatted
    
    def test_coordinate_format_compatibility(self):
        """Test coordinate format compatibility."""
        # Latitude format
        lat_decimal = string_to_decimal("45N30.5")
        lat_formatted = decimal_to_string(lat_decimal, Format.LAT)
        assert "45N" in lat_formatted
        
        # Longitude format
        lon_decimal = string_to_decimal("120W15.5")
        lon_formatted = decimal_to_string(lon_decimal, Format.LON)
        assert "120W" in lon_formatted
    
    def test_precision_matching(self):
        """Test that precision matches Immanuel expectations."""
        # Test with various precision levels
        decimal = 45.123456789
        
        # Second precision (default)
        dms_sec = decimal_to_dms(decimal, RoundTo.SECOND)
        back_decimal = dms_to_decimal(dms_sec)
        assert abs(decimal - back_decimal) < 0.001
        
        # Minute precision
        dms_min = decimal_to_dms(decimal, RoundTo.MINUTE)
        back_decimal = dms_to_decimal(dms_min)
        assert abs(decimal - back_decimal) < 0.01