"""
Tests for Critical Data Consistency Fixes

Validates immediate data consistency issues including:
- Fixed stars count field naming consistency
- Standardized house system terminology
- API response consistency
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestCriticalFixes:
    """Test suite for critical data consistency fixes."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_house_system_terminology_consistency(self):
        """Test that house system returns consistent codes, not converted names."""
        request_data = {
            "subject": {
                "name": "House System Test",
                "datetime": {"iso_string": "2000-12-25T18:30:00"},
                "latitude": {"decimal": 34.0522},
                "longitude": {"decimal": -118.2437},
                "timezone": {"utc_offset": -8.0}
            },
            "configuration": {
                "house_system": "K"  # Koch system code
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        data = response.model_dump_json()
        assert data["success"] is True
        
        # Verify house system returns the original code, not converted name
        assert data["houses"]["system"] == "K"  # Should be code, not "koch"
    
    def test_different_house_systems_consistency(self):
        """Test that different house system codes are returned consistently."""
        house_systems_to_test = [
            ("P", "Placidus"),
            ("K", "Koch"), 
            ("O", "Porphyrius"),
            ("R", "Regiomontanus"),
            ("C", "Campanus"),
            ("E", "Equal")
        ]
        
        for system_code, system_name in house_systems_to_test:
            request_data = {
                "subject": {
                    "name": f"{system_name} Test",
                    "datetime": {"iso_string": "2000-01-01T12:00:00"},
                    "latitude": {"decimal": 40.0},
                    "longitude": {"decimal": -74.0}
                },
                "configuration": {
                    "house_system": system_code
                }
            }
            
            response = self.client.post("/ephemeris/natal", json=request_data)
            assert response.status_code == 200
            
            data = response.model_dump_json()
            # Should return the code, not the full name
            assert data["houses"]["system"] == system_code, (
                f"House system {system_code} should return code, not name"
            )
    
    def test_fixed_stars_field_naming(self):
        """Test that fixed stars use proper field naming (not foundation_24_count)."""
        # This test would need to be updated when fixed stars functionality is enabled
        # For now, just verify the basic response structure doesn't contain the old field name
        request_data = {
            "subject": {
                "name": "Fixed Stars Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.0},
                "longitude": {"decimal": -74.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        data = response.model_dump_json()
        
        # Verify response doesn't contain old field name anywhere
        response_str = str(data)
        assert "foundation_24_count" not in response_str, (
            "Response should not contain deprecated 'foundation_24_count' field"
        )
        
        # If fixed stars are present in response, verify new naming
        # (This depends on whether fixed stars are enabled in the current configuration)
        if "fixed_stars" in data:
            fixed_stars = data["fixed_stars"]
            if isinstance(fixed_stars, dict):
                # Should have 'selected_stars_count' instead of 'foundation_24_count'
                assert "foundation_24_count" not in fixed_stars, (
                    "Fixed stars should not use deprecated 'foundation_24_count' field"
                )
                # If it has a count field, it should be the new name
                if "selected_stars_count" in fixed_stars:
                    assert isinstance(fixed_stars["selected_stars_count"], int)
    
    def test_api_response_consistency(self):
        """Test overall API response consistency and structure."""
        request_data = {
            "subject": {
                "name": "Consistency Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.0},
                "longitude": {"decimal": -74.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        data = response.model_dump_json()
        
        # Verify core response structure
        required_top_level_fields = ["success", "subject", "planets", "houses", "angles", "aspects"]
        for field in required_top_level_fields:
            assert field in data, f"Required field '{field}' missing from response"
        
        # Verify houses structure consistency
        houses = data["houses"]
        assert "system" in houses, "Houses missing 'system' field"
        assert "cusps" in houses, "Houses missing 'cusps' field"
        assert isinstance(houses["system"], str), "House system should be string"
        assert isinstance(houses["cusps"], list), "House cusps should be list"
        
        # Verify angles structure
        angles = data["angles"] 
        angle_fields = ["ascendant", "midheaven", "descendant", "imum_coeli"]
        for field in angle_fields:
            assert field in angles, f"Angles missing '{field}' field"
            assert isinstance(angles[field], (int, float)), f"Angle '{field}' should be numeric"
    
    def test_backward_compatibility_maintained(self):
        """Test that critical fixes don't break existing API contracts."""
        # Test with minimal request (should work exactly as before)
        request_data = {
            "subject": {
                "name": "Backward Compatibility Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.0},
                "longitude": {"decimal": -74.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=request_data)
        assert response.status_code == 200
        
        data = response.model_dump_json()
        assert data["success"] is True
        
        # Verify all expected fields are still present
        assert len(data["planets"]) > 0, "Should have planets in response"
        assert len(data["houses"]["cusps"]) == 12, "Should have 12 house cusps"
        assert len(data["aspects"]) >= 0, "Should have aspects list (even if empty)"
        
        # Verify planet structure hasn't changed (except for new retrograde fields)
        sample_planet = next(iter(data["planets"].values()))
        expected_planet_fields = [
            "name", "longitude", "latitude", "distance", "longitude_speed",
            "is_retrograde", "motion_type",  # New retrograde fields should be present
            "sign_name", "sign_longitude", "house_number"
        ]
        
        for field in expected_planet_fields:
            assert field in sample_planet, f"Planet missing expected field '{field}'"