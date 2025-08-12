"""
Unit tests for the Meridian Ephemeris Engine Subject data model.
"""

import pytest
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from app.core.ephemeris.charts.subject import Subject, SubjectData


class TestSubjectDataValidation:
    """Test SubjectData validation and constraints."""
    
    def test_valid_subject_data_creation(self):
        """Test creating valid SubjectData."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        subject_data = SubjectData(
            name="Test Subject",
            datetime=dt,
            julian_day=2451545.0,
            latitude=40.7128,
            longitude=-74.0060
        )
        
        assert subject_data.name == "Test Subject"
        assert subject_data.latitude == 40.7128
        assert subject_data.longitude == -74.0060
        assert subject_data.julian_day == 2451545.0
    
    def test_invalid_latitude_bounds(self):
        """Test latitude validation."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        with pytest.raises(ValueError, match="Latitude .* must be between -90 and 90"):
            SubjectData(
                name="Test",
                datetime=dt,
                julian_day=2451545.0,
                latitude=100.0,  # Invalid
                longitude=0.0
            )
    
    def test_invalid_longitude_bounds(self):
        """Test longitude validation."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        with pytest.raises(ValueError, match="Longitude .* must be between -180 and 180"):
            SubjectData(
                name="Test", 
                datetime=dt,
                julian_day=2451545.0,
                latitude=0.0,
                longitude=200.0  # Invalid
            )
    
    def test_timezone_naive_datetime_rejected(self):
        """Test that timezone-naive datetime is rejected."""
        dt = datetime(2000, 1, 1, 12, 0, 0)  # No timezone
        
        with pytest.raises(ValueError, match="datetime must be timezone-aware"):
            SubjectData(
                name="Test",
                datetime=dt,
                julian_day=2451545.0,
                latitude=0.0,
                longitude=0.0
            )
    
    def test_julian_day_bounds(self):
        """Test Julian Day reasonable bounds."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        with pytest.raises(ValueError, match="Julian Day .* is outside reasonable astronomical range"):
            SubjectData(
                name="Test",
                datetime=dt,
                julian_day=100.0,  # Too small
                latitude=0.0,
                longitude=0.0
            )


class TestSubjectInputNormalization:
    """Test Subject input parsing and normalization."""
    
    def test_basic_subject_creation(self):
        """Test creating Subject with basic inputs."""
        subject = Subject(
            name="John Doe",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        assert data.name == "John Doe"
        assert abs(data.latitude - 40.7128) < 0.0001
        assert abs(data.longitude - (-74.0060)) < 0.0001
    
    def test_coordinate_string_parsing(self):
        """Test parsing coordinate strings."""
        subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00",
            latitude="40°42'46\"N",
            longitude="74°00'22\"W"
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        assert abs(data.latitude - 40.7128) < 0.01
        assert abs(data.longitude - (-74.0061)) < 0.01
    
    def test_timezone_string_parsing(self):
        """Test parsing timezone strings."""
        subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        assert data.timezone_name == "America/New_York"
    
    def test_utc_offset_parsing(self):
        """Test parsing UTC offset."""
        subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060,
            timezone=-5.0
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        assert data.utc_offset == -5.0
    
    def test_julian_day_input(self):
        """Test using Julian Day as datetime input."""
        subject = Subject(
            name="Test",
            datetime=2451545.0,  # J2000.0
            latitude=0.0,
            longitude=0.0
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        assert data.julian_day == 2451545.0
        assert data.datetime.year == 2000
        assert data.datetime.month == 1
        assert data.datetime.day == 1
    
    def test_datetime_object_input(self):
        """Test using datetime object as input."""
        dt = datetime(2000, 6, 15, 14, 30, 0, tzinfo=ZoneInfo("UTC"))
        subject = Subject(
            name="Test",
            datetime=dt,
            latitude=0.0,
            longitude=0.0
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        assert data.datetime == dt


class TestSubjectValidation:
    """Test Subject validation and error handling."""
    
    def test_invalid_name_types(self):
        """Test invalid name input types."""
        with pytest.raises(ValueError, match="Subject validation failed"):
            Subject(
                name=123,  # Not a string
                datetime="2000-01-01T12:00:00",
                latitude=0.0,
                longitude=0.0
            )
    
    def test_empty_name(self):
        """Test empty name validation."""
        with pytest.raises(ValueError, match="Subject validation failed"):
            Subject(
                name="   ",  # Empty after strip
                datetime="2000-01-01T12:00:00",
                latitude=0.0,
                longitude=0.0
            )
    
    def test_invalid_coordinate_string(self):
        """Test invalid coordinate string."""
        with pytest.raises(ValueError, match="Subject validation failed"):
            Subject(
                name="Test",
                datetime="2000-01-01T12:00:00",
                latitude="invalid coordinate",
                longitude=0.0
            )
    
    def test_invalid_datetime_string(self):
        """Test invalid datetime string."""
        with pytest.raises(ValueError, match="Subject validation failed"):
            Subject(
                name="Test",
                datetime="not a date",
                latitude=0.0,
                longitude=0.0
            )
    
    def test_invalid_timezone_string(self):
        """Test invalid timezone string."""
        with pytest.raises(ValueError, match="Subject validation failed"):
            Subject(
                name="Test",
                datetime="2000-01-01T12:00:00",
                latitude=0.0,
                longitude=0.0,
                timezone="Invalid/Timezone"
            )
    
    def test_validation_errors_tracking(self):
        """Test that validation errors are properly tracked."""
        try:
            subject = Subject(
                name="",  # Invalid
                datetime="invalid date",  # Invalid
                latitude="invalid",  # Invalid
                longitude=0.0
            )
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
    
    def test_is_valid_method(self):
        """Test is_valid() method."""
        # Valid subject
        valid_subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00",
            latitude=0.0,
            longitude=0.0
        )
        assert valid_subject.is_valid() is True
        
        # Invalid subject (we can't easily create one that doesn't raise)
        # since validation happens in __init__


class TestSubjectSerialization:
    """Test Subject serialization and deserialization."""
    
    def test_to_dict(self):
        """Test converting Subject to dictionary."""
        subject = Subject(
            name="John Doe",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060,
            altitude=100.0,
            timezone="America/New_York"
        )
        
        data_dict = subject.to_dict()
        
        assert data_dict['valid'] is True
        assert data_dict['name'] == "John Doe"
        assert data_dict['latitude'] == 40.7128
        assert abs(data_dict['longitude'] - (-74.0060)) < 0.0001
        assert data_dict['altitude'] == 100.0
        assert data_dict['timezone_name'] == "America/New_York"
        assert 'datetime' in data_dict
        assert 'julian_day' in data_dict
    
    def test_from_dict(self):
        """Test creating Subject from dictionary."""
        data_dict = {
            'name': 'Jane Doe',
            'datetime': '2000-06-15T14:30:00',
            'latitude': 51.5074,
            'longitude': -0.1278,
            'altitude': 50.0,
            'timezone_name': 'Europe/London'
        }
        
        subject = Subject.from_dict(data_dict)
        
        assert subject.is_valid()
        subject_data = subject.get_data()
        assert subject_data.name == 'Jane Doe'
        assert subject_data.latitude == 51.5074
        assert abs(subject_data.longitude - (-0.1278)) < 0.0001
        assert subject_data.altitude == 50.0
    
    def test_round_trip_serialization(self):
        """Test serialization round-trip consistency."""
        original = Subject(
            name="Test Subject",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="UTC"
        )
        
        # Convert to dict and back
        data_dict = original.to_dict()
        restored = Subject.from_dict(data_dict)
        
        # Compare data
        original_data = original.get_data()
        restored_data = restored.get_data()
        
        assert original_data.name == restored_data.name
        assert abs(original_data.latitude - restored_data.latitude) < 0.0001
        assert abs(original_data.longitude - restored_data.longitude) < 0.0001
        assert abs(original_data.julian_day - restored_data.julian_day) < 0.001


class TestSubjectRepresentation:
    """Test Subject string representation."""
    
    def test_repr_valid_subject(self):
        """Test __repr__ for valid subject."""
        subject = Subject(
            name="John Doe",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        repr_str = repr(subject)
        assert "John Doe" in repr_str
        assert "40.7128" in repr_str
        assert "-74.0060" in repr_str
        assert "2000-01-01" in repr_str


class TestSubjectEdgeCases:
    """Test Subject edge cases and boundary conditions."""
    
    def test_coordinate_normalization(self):
        """Test coordinate normalization."""
        subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00",
            latitude=90.0,  # North pole
            longitude=180.0  # International date line
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        assert data.latitude == 90.0
        assert data.longitude == 180.0
    
    def test_coordinate_wrapping(self):
        """Test coordinate wrapping for longitude."""
        subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00", 
            latitude=0.0,
            longitude=190.0  # Should wrap to -170
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        # Note: normalize_longitude should handle this
        assert -180 <= data.longitude <= 180
    
    def test_timezone_coordinate_lookup(self):
        """Test timezone lookup by coordinates."""
        # New York coordinates - should detect EST/EDT
        subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00",
            latitude=40.7128,
            longitude=-74.0060
            # No explicit timezone - should be looked up
        )
        
        assert subject.is_valid()
        # Should work even without explicit timezone
    
    def test_altitude_handling(self):
        """Test altitude parameter handling."""
        subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00",
            latitude=0.0,
            longitude=0.0,
            altitude=8848.0  # Mount Everest
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        assert data.altitude == 8848.0
    
    def test_default_altitude(self):
        """Test default altitude value."""
        subject = Subject(
            name="Test",
            datetime="2000-01-01T12:00:00",
            latitude=0.0,
            longitude=0.0
        )
        
        assert subject.is_valid()
        data = subject.get_data()
        assert data.altitude == 0.0