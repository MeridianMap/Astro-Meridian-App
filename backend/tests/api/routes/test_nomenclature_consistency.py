"""
Tests for PRP-EPHEMERIS-002: Nomenclature Consistency Implementation

Validates that all celestial objects display proper IAU-compliant astronomical names
instead of generic "Object X" or "Planet X" references.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.ephemeris.const import PLANET_NAMES


class TestNomenclatureConsistency:
    """Test suite for nomenclature consistency functionality."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_no_generic_names_in_response(self):
        """Test that no 'Object X' or 'Planet X' names appear in API responses."""
        request_data = {
            "subject": {
                "name": "Nomenclature Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        planets = data["planets"]
        
        # Check that no generic names are present
        for planet_name in planets.keys():
            assert not planet_name.startswith("Object "), f"Found generic 'Object' name: {planet_name}"
            assert not planet_name.startswith("Planet "), f"Found generic 'Planet' name: {planet_name}"
    
    def test_major_asteroids_have_proper_names(self):
        """Test that major asteroids have proper IAU names."""
        request_data = {
            "subject": {
                "name": "Asteroid Names Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        planets = response.json()["planets"]
        
        # Expected asteroid names based on PLANET_NAMES dictionary
        expected_asteroids = {
            "Ceres": 17,    # (1) Ceres - first asteroid
            "Pallas": 18,   # (2) Pallas - second asteroid
            "Juno": 19,     # (3) Juno - third asteroid
            "Vesta": 20,    # (4) Vesta - fourth asteroid
        }
        
        for asteroid_name, planet_id in expected_asteroids.items():
            if asteroid_name in planets:
                planet = planets[asteroid_name]
                assert planet["name"] == asteroid_name, f"Name field mismatch for {asteroid_name}"
                
                # Verify this matches our PLANET_NAMES dictionary
                assert PLANET_NAMES[planet_id] == asteroid_name, f"Dictionary mismatch for ID {planet_id}"
    
    def test_centaurs_have_proper_names(self):
        """Test that centaurs have proper names."""
        request_data = {
            "subject": {
                "name": "Centaur Names Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        planets = response.json()["planets"]
        
        # Expected centaur names
        expected_centaurs = {
            "Chiron": 15,   # (2060) Chiron
            "Pholus": 16,   # (5145) Pholus
        }
        
        for centaur_name, planet_id in expected_centaurs.items():
            if centaur_name in planets:
                planet = planets[centaur_name]
                assert planet["name"] == centaur_name, f"Name field mismatch for {centaur_name}"
                
                # Verify this matches our PLANET_NAMES dictionary
                assert PLANET_NAMES[planet_id] == centaur_name, f"Dictionary mismatch for ID {planet_id}"
    
    def test_planet_names_dictionary_completeness(self):
        """Test that PLANET_NAMES dictionary includes all expected objects."""
        # Verify that the key objects from the PRP are in the dictionary
        required_objects = {
            16: "Pholus",
            17: "Ceres", 
            18: "Pallas",
            19: "Juno",
            20: "Vesta",
        }
        
        for planet_id, expected_name in required_objects.items():
            assert planet_id in PLANET_NAMES, f"Planet ID {planet_id} missing from PLANET_NAMES"
            assert PLANET_NAMES[planet_id] == expected_name, (
                f"Planet ID {planet_id}: expected '{expected_name}', got '{PLANET_NAMES[planet_id]}'"
            )
    
    def test_nomenclature_consistency_across_requests(self):
        """Test that nomenclature is consistent across different requests."""
        # Test multiple dates to ensure consistency
        test_dates = [
            "1990-06-15T14:30:00-04:00",
            "2000-01-01T12:00:00",
            "2020-12-21T18:00:00"
        ]
        
        expected_proper_names = {"Ceres", "Pallas", "Juno", "Vesta", "Chiron", "Pholus"}
        
        for date in test_dates:
            request_data = {
                "subject": {
                    "name": f"Consistency Test {date}",
                    "datetime": {"iso_string": date},
                    "latitude": {"decimal": 40.0},
                    "longitude": {"decimal": -74.0}
                }
            }
            
            response = self.client.post("/ephemeris/natal", json=request_data)
            assert response.status_code == 200
            
            planets = response.json()["planets"]
            
            # Check that any expected names present are consistent
            for planet_name in planets.keys():
                if planet_name in expected_proper_names:
                    # Verify the name field matches the key
                    assert planets[planet_name]["name"] == planet_name
                
                # Ensure no generic names
                assert not planet_name.startswith("Object "), f"Generic name in {date}: {planet_name}"
                assert not planet_name.startswith("Planet "), f"Generic name in {date}: {planet_name}"
    
    def test_backward_compatibility_maintained(self):
        """Test that nomenclature changes don't break existing functionality."""
        request_data = {
            "subject": {
                "name": "Compatibility Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.0},
                "longitude": {"decimal": -74.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify core response structure maintained
        assert "success" in data
        assert "subject" in data  
        assert "planets" in data
        assert "houses" in data
        assert "angles" in data
        assert "aspects" in data
        
        # Verify traditional planets still have proper names
        traditional_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
        planets = data["planets"]
        
        for traditional_name in traditional_planets:
            if traditional_name in planets:
                assert planets[traditional_name]["name"] == traditional_name
                # Name should match what's in PLANET_NAMES
                matching_id = None
                for pid, pname in PLANET_NAMES.items():
                    if pname == traditional_name:
                        matching_id = pid
                        break
                assert matching_id is not None, f"Traditional planet {traditional_name} not found in PLANET_NAMES"