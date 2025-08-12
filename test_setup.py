"""
Test script to validate the development environment setup.
"""

def test_swisseph_import():
    """Test that pyswisseph can be imported and used."""
    import swisseph as swe
    
    # Test basic functionality - get Julian day for a date
    jd = swe.julday(2024, 1, 1, 12.0)
    assert jd > 0
    print(f"Julian Day for 2024-01-01 12:00: {jd}")

def test_numpy_import():
    """Test that numpy is available."""
    import numpy as np
    arr = np.array([1, 2, 3])
    assert len(arr) == 3
    print("NumPy import: OK")

def test_timezonefinder():
    """Test timezone functionality."""
    from timezonefinder import TimezoneFinder
    tf = TimezoneFinder()
    tz = tf.timezone_at(lng=-122.4194, lat=37.7749)  # San Francisco
    assert tz == "America/Los_Angeles"
    print(f"Timezone for SF: {tz}")

if __name__ == "__main__":
    test_swisseph_import()
    test_numpy_import() 
    test_timezonefinder()
    print("All tests passed! Environment setup complete.")