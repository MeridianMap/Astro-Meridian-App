"""
Tests for PRP-EPHEMERIS-001: Retrograde Indicators Implementation

Validates that all planets include explicit retrograde flags (is_retrograde, motion_type)
in API responses, eliminating the need for clients to calculate retrograde status.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestRetrogradeIndicators:
    """Test suite for retrograde indicator functionality."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_retrograde_indicators_present(self):
        """Test that all planets include retrograde indicators in API response."""
        # Use test data from PRP (1990-06-15 14:30 NYC has known retrograde planets)
        request_data = {
            "subject": {
                "name": "Retrograde Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["success"] is True
        
        # Verify all planets have retrograde fields
        planets = data["planets"]
        assert len(planets) > 0
        
        for planet_name, planet_data in planets.items():
            assert "is_retrograde" in planet_data, f"{planet_name} missing is_retrograde field"
            assert "motion_type" in planet_data, f"{planet_name} missing motion_type field"
            assert isinstance(planet_data["is_retrograde"], bool)
            assert planet_data["motion_type"] in ["direct", "retrograde", "stationary", "unknown"]
    
    def test_retrograde_accuracy_known_case(self):
        """Test retrograde detection accuracy against known retrograde planets."""
        # 1990-06-15 case has Saturn, Uranus, Neptune, Pluto retrograde based on Swiss Ephemeris
        request_data = {
            "subject": {
                "name": "Retrograde Accuracy Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        planets = response.model_dump_json()["planets"]
        
        # Verify known retrograde planets from PRP analysis
        expected_retrograde = ["Saturn", "Uranus", "Neptune", "Pluto"]
        for planet_name in expected_retrograde:
            if planet_name in planets:
                planet = planets[planet_name]
                assert planet["is_retrograde"] is True, f"{planet_name} should be retrograde"
                assert planet["motion_type"] == "retrograde", f"{planet_name} motion_type should be retrograde"
                assert planet["longitude_speed"] < 0, f"{planet_name} should have negative longitude_speed"
        
        # Verify known direct motion planets (Sun, Moon never retrograde)
        expected_direct = ["Sun", "Moon"]
        for planet_name in expected_direct:
            if planet_name in planets:
                planet = planets[planet_name]
                assert planet["is_retrograde"] is False, f"{planet_name} should not be retrograde"
                assert planet["motion_type"] == "direct", f"{planet_name} motion_type should be direct"
    
    def test_retrograde_consistency_with_longitude_speed(self):
        """Test that retrograde flags are consistent with longitude_speed values."""
        request_data = {
            "subject": {
                "name": "Consistency Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        planets = response.model_dump_json()["planets"]
        
        for planet_name, planet_data in planets.items():
            longitude_speed = planet_data.get("longitude_speed")
            is_retrograde = planet_data.get("is_retrograde")
            motion_type = planet_data.get("motion_type")
            
            if longitude_speed is not None:
                # Check consistency between longitude_speed and retrograde flags
                expected_retrograde = longitude_speed < 0
                
                assert is_retrograde == expected_retrograde, (
                    f"{planet_name}: is_retrograde ({is_retrograde}) inconsistent with "
                    f"longitude_speed ({longitude_speed})"
                )
                
                if expected_retrograde:
                    assert motion_type == "retrograde", (
                        f"{planet_name}: motion_type should be 'retrograde' for negative longitude_speed"
                    )
                else:
                    # Could be direct or stationary for positive/zero speed
                    assert motion_type in ["direct", "stationary"], (
                        f"{planet_name}: motion_type should be 'direct' or 'stationary' for non-negative speed"
                    )
    
    def test_stationary_planet_detection(self):
        """Test that nearly stationary planets are detected correctly."""
        # This test might need a different date/time where planets are nearly stationary
        # For now, we test the logic with the threshold from PlanetPosition.motion_type
        request_data = {
            "subject": {
                "name": "Stationary Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        planets = response.model_dump_json()["planets"]
        
        # Verify that the motion_type logic is working
        for planet_name, planet_data in planets.items():
            longitude_speed = planet_data.get("longitude_speed")
            motion_type = planet_data.get("motion_type")
            
            if longitude_speed is not None:
                # Based on PlanetPosition.motion_type threshold (< 0.001 degrees/day)
                if abs(longitude_speed) < 0.001:
                    assert motion_type == "stationary", (
                        f"{planet_name}: motion_type should be 'stationary' for speed {longitude_speed}"
                    )
                elif longitude_speed < 0:
                    assert motion_type == "retrograde"
                else:
                    assert motion_type == "direct"
    
    def test_backward_compatibility(self):
        """Test that existing API structure is maintained."""
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
        
        data = response.model_dump_json()
        
        # Verify core response structure is maintained
        assert "success" in data
        assert "subject" in data
        assert "planets" in data
        assert "houses" in data
        assert "angles" in data
        assert "aspects" in data
        
        # Verify planets have all expected fields (including new retrograde fields)
        if data["planets"]:
            sample_planet = next(iter(data["planets"].values()))
            required_fields = [
                "name", "longitude", "latitude", "distance", "longitude_speed",
                "is_retrograde", "motion_type", "sign_name", "sign_longitude", "house_number"
            ]
            
            for field in required_fields:
                assert field in sample_planet, f"Required field '{field}' missing from planet response"