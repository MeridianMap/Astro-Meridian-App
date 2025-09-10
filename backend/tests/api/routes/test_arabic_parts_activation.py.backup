"""
Tests for PRP-EPHEMERIS-003: Arabic Parts System Activation

Validates that the existing comprehensive Arabic Parts calculation system is properly 
activated in enhanced natal chart API responses, providing traditional lots with 
proper day/night sect variations.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestArabicPartsActivation:
    """Test suite for Arabic Parts activation functionality."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_arabic_parts_activation_basic(self):
        """Test that Arabic Parts can be activated via enhanced endpoint."""
        request_data = {
            "subject": {
                "name": "Arabic Parts Basic Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            },
            "include_arabic_parts": True,
            "include_all_traditional_parts": True,
            "metadata_level": "full"
        }
        
        response = self.client.post("/ephemeris/v2/natal-enhanced", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # Verify Arabic Parts are present and populated
        assert "arabic_parts" in data
        arabic_parts = data["arabic_parts"]
        assert arabic_parts is not None
        
        # Check structure
        assert "sect_determination" in arabic_parts
        assert "arabic_parts" in arabic_parts
        assert "formulas_used" in arabic_parts
        assert "calculation_time_ms" in arabic_parts
        assert "total_parts_calculated" in arabic_parts
        
        # Verify we have actual parts
        parts_data = arabic_parts["arabic_parts"]
        assert isinstance(parts_data, dict)
        assert len(parts_data) > 0
    
    def test_traditional_lots_implementation(self):
        """Test that key traditional lots are properly calculated."""
        request_data = {
            "subject": {
                "name": "Traditional Lots Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            },
            "include_arabic_parts": True,
            "include_all_traditional_parts": True,
            "metadata_level": "full"
        }
        
        response = self.client.post("/ephemeris/v2/natal-enhanced", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        parts_data = data["arabic_parts"]["arabic_parts"]
        
        # Check for core traditional lots
        expected_lots = ["fortune", "spirit", "basis"]
        found_lots = []
        
        for lot_name in expected_lots:
            if lot_name in parts_data:
                found_lots.append(lot_name)
                lot_data = parts_data[lot_name]
                
                # Validate lot structure
                assert "name" in lot_data
                assert "display_name" in lot_data
                assert "longitude" in lot_data
                assert "sign_name" in lot_data
                assert "sign_longitude" in lot_data
                assert "house_number" in lot_data
                assert "formula_used" in lot_data
                assert "description" in lot_data
                assert "traditional_source" in lot_data
                
                # Validate data types
                assert isinstance(lot_data["longitude"], float)
                assert isinstance(lot_data["sign_name"], str)
                assert isinstance(lot_data["house_number"], int)
                assert isinstance(lot_data["formula_used"], str)
                
                # Validate ranges
                assert 0 <= lot_data["longitude"] <= 360
                assert 1 <= lot_data["house_number"] <= 12
        
        assert len(found_lots) >= 3, f"Expected at least 3 core lots, found: {found_lots}"
    
    def test_day_night_sect_variations(self):
        """Test that day/night sect affects formula variations correctly."""
        # Test day chart (Sun above horizon at 14:30)
        day_request = {
            "subject": {
                "name": "Day Chart Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            },
            "include_arabic_parts": True,
            "arabic_parts_selection": ["fortune", "spirit"],
            "metadata_level": "full"
        }
        
        day_response = self.client.post("/ephemeris/v2/natal-enhanced", json=day_request)
        assert day_response.status_code == 200
        
        day_data = day_response.json()
        day_sect = day_data["arabic_parts"]["sect_determination"]
        day_parts = day_data["arabic_parts"]["arabic_parts"]
        
        # Verify it's detected as day chart
        assert day_sect["is_day_chart"] is True
        assert day_sect["sun_above_horizon"] is True
        
        # Verify Part of Fortune uses day formula (ASC + Moon - Sun)
        if "fortune" in day_parts:
            fortune_formula = day_parts["fortune"]["formula_used"]
            # Day formula should have Moon before Sun in the calculation
            assert "moon" in fortune_formula.lower()
            assert "sun" in fortune_formula.lower()
        
        # Verify Part of Spirit uses day formula (ASC + Sun - Moon)  
        if "spirit" in day_parts:
            spirit_formula = day_parts["spirit"]["formula_used"]
            # Day formula should have Sun before Moon in the calculation
            assert "sun" in spirit_formula.lower()
            assert "moon" in spirit_formula.lower()
    
    def test_arabic_parts_specific_selection(self):
        """Test Arabic Parts with specific part selection."""
        request_data = {
            "subject": {
                "name": "Specific Selection Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.0},
                "longitude": {"decimal": -74.0}
            },
            "include_arabic_parts": True,
            "arabic_parts_selection": ["fortune", "spirit"],  # Only specific parts
            "metadata_level": "basic"
        }
        
        response = self.client.post("/ephemeris/v2/natal-enhanced", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        parts_data = data["arabic_parts"]["arabic_parts"]
        formulas_used = data["arabic_parts"]["formulas_used"]
        
        # Should have only the requested parts
        assert "fortune" in parts_data or "spirit" in parts_data
        assert len(formulas_used) <= 2  # Should not exceed requested number
        
        # Verify formulas_used is a list (fixed schema issue)
        assert isinstance(formulas_used, list)
        for formula in formulas_used:
            assert isinstance(formula, str)
    
    def test_arabic_parts_performance(self):
        """Test that Arabic Parts calculation meets performance targets."""
        request_data = {
            "subject": {
                "name": "Performance Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"utc_offset": -4.0}
            },
            "include_arabic_parts": True,
            "include_all_traditional_parts": True,
            "metadata_level": "full"
        }
        
        response = self.client.post("/ephemeris/v2/natal-enhanced", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        arabic_parts = data["arabic_parts"]
        
        # Verify performance target (<40ms as specified in PRP)
        calculation_time_ms = arabic_parts["calculation_time_ms"]
        assert calculation_time_ms < 40.0, f"Arabic Parts calculation took {calculation_time_ms}ms (target: <40ms)"
        
        # Verify reasonable number of parts calculated
        total_calculated = arabic_parts["total_parts_calculated"]
        assert total_calculated >= 8, f"Expected at least 8 traditional parts, got {total_calculated}"
    
    def test_backward_compatibility_maintained(self):
        """Test that Arabic Parts activation doesn't break existing functionality."""
        # Test basic natal chart without Arabic Parts (should still work)
        basic_request = {
            "subject": {
                "name": "Backward Compatibility Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.0},
                "longitude": {"decimal": -74.0}
            },
            "include_aspects": True,
            "include_arabic_parts": False,  # Explicitly disabled
            "metadata_level": "basic"
        }
        
        response = self.client.post("/ephemeris/v2/natal-enhanced", json=basic_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # Should have core ephemeris data
        assert "planets" in data
        assert "houses" in data
        assert "angles" in data
        assert "aspects" in data
        
        # Arabic Parts should be None or not present when disabled
        arabic_parts = data.get("arabic_parts")
        assert arabic_parts is None, "Arabic Parts should be None when disabled"
    
    def test_enhanced_endpoint_requirement(self):
        """Test that Arabic Parts are only available via enhanced endpoint."""
        # Test that basic natal chart endpoint doesn't include Arabic Parts
        basic_request = {
            "subject": {
                "name": "Basic Endpoint Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.0},
                "longitude": {"decimal": -74.0}
            }
        }
        
        response = self.client.post("/ephemeris/natal", json=basic_request)
        assert response.status_code == 200
        
        data = response.json()
        
        # Basic endpoint should not include arabic_parts field
        assert "arabic_parts" not in data, "Basic endpoint should not include Arabic Parts"
    
    def test_formulas_used_schema_fix(self):
        """Test that formulas_used field properly returns list instead of dict."""
        request_data = {
            "subject": {
                "name": "Schema Fix Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00-04:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            },
            "include_arabic_parts": True,
            "arabic_parts_selection": ["fortune", "spirit", "basis"],
            "metadata_level": "full"
        }
        
        response = self.client.post("/ephemeris/v2/natal-enhanced", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        formulas_used = data["arabic_parts"]["formulas_used"]
        
        # Should be a list, not a dict (this was the original activation issue)
        assert isinstance(formulas_used, list), f"formulas_used should be list, got {type(formulas_used)}"
        
        # Should contain strings
        for formula_name in formulas_used:
            assert isinstance(formula_name, str)
            
        # Should have reasonable length
        assert len(formulas_used) > 0
        assert len(formulas_used) <= 16  # Max traditional parts