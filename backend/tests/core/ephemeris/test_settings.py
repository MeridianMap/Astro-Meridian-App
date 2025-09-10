"""
Unit tests for the Meridian Ephemeris Engine settings module.
"""

import os
import tempfile
import pytest
import threading
from unittest.mock import patch

from extracted.systems.settings import EphemerisSettings, SettingsSingleton, settings


class TestEphemerisSettings:
    """Test the EphemerisSettings class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = EphemerisSettings()
    
    def test_initialization(self):
        """Test settings initialization with defaults."""
        assert self.settings.default_latitude == 0.0
        assert self.settings.default_longitude == 0.0
        assert self.settings.default_house_system == 'P'
        assert self.settings.enable_cache is True
        assert self.settings.cache_size == 1000
        assert self.settings.coordinate_system == 'tropical'
    
    def test_house_system_mapping(self):
        """Test house system code mapping."""
        assert self.settings.get_house_system_code('placidus') == 'P'
        assert self.settings.get_house_system_code('koch') == 'K'
        assert self.settings.get_house_system_code('equal') == 'E'
        assert self.settings.get_house_system_code('P') == 'P'  # Already a code
        assert self.settings.get_house_system_code('unknown') == 'P'  # Default
    
    def test_ephemeris_path_validation(self):
        """Test ephemeris path setting and validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Valid path should work
            self.settings.ephemeris_path = temp_dir
            assert self.settings.ephemeris_path == temp_dir
            
            # Invalid path should raise FileNotFoundError
            with pytest.raises(FileNotFoundError):
                self.settings.ephemeris_path = "/nonexistent/path"
    
    def test_add_ephemeris_path(self):
        """Test adding additional ephemeris paths."""
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            self.settings.ephemeris_path = temp_dir1
            original_path = self.settings.ephemeris_path
            
            # Add second path
            self.settings.add_ephemeris_path(temp_dir2)
            
            assert temp_dir1 in self.settings.ephemeris_path
            assert temp_dir2 in self.settings.ephemeris_path
            assert os.pathsep in self.settings.ephemeris_path
    
    def test_update_method(self):
        """Test bulk settings update."""
        updates = {
            'default_latitude': 51.5074,
            'default_longitude': -0.1278,
            'cache_size': 2000,
            'enable_cache': False
        }
        
        self.settings.update(**updates)
        
        assert self.settings.default_latitude == 51.5074
        assert self.settings.default_longitude == -0.1278
        assert self.settings.cache_size == 2000
        assert self.settings.enable_cache is False
        
        # Test invalid attribute
        with pytest.raises(AttributeError):
            self.settings.update(invalid_setting='value')
    
    def test_to_dict(self):
        """Test settings export to dictionary."""
        settings_dict = self.settings.to_dict()
        
        assert isinstance(settings_dict, dict)
        assert 'ephemeris_path' in settings_dict
        assert 'default_latitude' in settings_dict
        assert 'default_house_system' in settings_dict
        assert 'swe_flags' in settings_dict
        assert 'default_planets' in settings_dict
        
        # Test that lists are properly copied
        assert isinstance(settings_dict['default_planets'], list)
        assert settings_dict['default_planets'] is not self.settings.default_planets
    
    def test_thread_safety(self):
        """Test thread safety of settings operations."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(100):
                    # Read and write operations
                    lat = self.settings.default_latitude
                    self.settings.default_latitude = worker_id + i * 0.01
                    current_lat = self.settings.default_latitude
                    results.append((worker_id, i, lat, current_lat))
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check no errors occurred
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 500  # 5 threads * 100 operations


class TestSettingsSingleton:
    """Test the SettingsSingleton class."""
    
    def test_singleton_behavior(self):
        """Test that singleton returns the same instance."""
        settings1 = SettingsSingleton()
        settings2 = SettingsSingleton()
        
        assert settings1 is settings2
        
        # Test that changes are reflected across instances
        settings1.default_latitude = 42.0
        assert settings2.default_latitude == 42.0
    
    def test_reset_functionality(self):
        """Test singleton reset functionality."""
        # Modify settings
        settings_instance = SettingsSingleton()
        settings_instance.default_latitude = 99.9
        settings_instance.cache_size = 5000
        
        # Reset
        SettingsSingleton.reset()
        
        # Check defaults are restored
        new_instance = SettingsSingleton()
        assert new_instance.default_latitude == 0.0
        assert new_instance.cache_size == 1000
    
    def test_get_instance(self):
        """Test get_instance class method."""
        instance1 = SettingsSingleton.get_instance()
        instance2 = SettingsSingleton()
        
        assert instance1 is instance2


class TestGlobalSettings:
    """Test the global settings instance."""
    
    def setup_method(self):
        """Reset settings before each test."""
        settings.reset()
    
    def test_global_settings_access(self):
        """Test accessing the global settings instance."""
        assert hasattr(settings, 'default_latitude')
        assert hasattr(settings, 'default_longitude')
        assert hasattr(settings, 'ephemeris_path')
    
    def test_global_settings_modification(self):
        """Test modifying the global settings."""
        original_lat = settings.default_latitude
        settings.default_latitude = 55.7558
        
        # Create new instance to verify singleton behavior
        new_settings = SettingsSingleton()
        assert new_settings.default_latitude == 55.7558
        
        # Reset for cleanup
        settings.default_latitude = original_lat
    
    def test_thread_safety_global(self):
        """Test thread safety of global settings access."""
        results = []
        
        def worker():
            for _ in range(50):
                settings.default_latitude = threading.current_thread().ident
                current_lat = settings.default_latitude
                results.append(current_lat)
        
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have 150 results (3 threads * 50 operations)
        assert len(results) == 150


@pytest.fixture(scope="function")
def temp_settings():
    """Fixture providing a temporary settings instance."""
    original_settings = EphemerisSettings()
    yield original_settings


def test_settings_persistence_simulation(temp_settings):
    """Test that settings maintain state during operation."""
    # Simulate application startup
    temp_settings.update(
        default_latitude=40.7128,
        default_longitude=-74.0060,  # New York
        cache_size=5000
    )
    
    # Verify settings persist
    assert temp_settings.default_latitude == 40.7128
    assert temp_settings.default_longitude == -74.0060
    assert temp_settings.cache_size == 5000
    
    # Simulate settings access from different parts of application
    lat = temp_settings.default_latitude
    lon = temp_settings.default_longitude
    
    assert lat == 40.7128
    assert lon == -74.0060