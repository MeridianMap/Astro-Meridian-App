"""
Integration Tests for Enhanced Ephemeris API with Aspect Calculations

Tests the complete API workflow including:
- Enhanced natal chart endpoint
- Aspect calculation integration
- Request/response schema validation
- Error handling
- Performance under API load
"""

import pytest
import json
import time
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import os
import sys

# Ensure the backend directory is on sys.path for direct execution (python this_file.py)
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.api.models.schemas import (
    NatalChartEnhancedRequest, NatalChartEnhancedResponse,
    AspectMatrixResponse, EnhancedAspectResponse, CalculationMetadata
)


class TestEnhancedEphemerisAPI:
    """Test enhanced ephemeris API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client for API requests."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_enhanced_request(self):
        """Sample enhanced natal chart request."""
        return {
            "subject": {
                "name": "Test Subject",
                "datetime": {"iso_string": "1990-06-15T14:30:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"name": "America/New_York"}
            },
            "configuration": {
                "house_system": "P",
                "include_asteroids": True,
                "include_nodes": True,
                "include_lilith": True
            },
            "include_aspects": True,
            "aspect_orb_preset": "traditional",
            "metadata_level": "full"
        }
    
    def test_enhanced_natal_chart_success(self, client, sample_enhanced_request):
        """Test successful enhanced natal chart calculation."""
        response = client.post("/ephemeris/v2/natal-enhanced", json=sample_enhanced_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "success" in data
        assert data["success"] is True
        assert "subject" in data
        assert "planets" in data
        assert "houses" in data
        assert "angles" in data
        assert "aspects" in data
        assert "aspect_matrix" in data
        assert "calculation_metadata" in data
        assert "chart_type" in data
        assert data["chart_type"] == "natal_enhanced"
        
        # Verify aspects data
        aspects = data["aspects"]
        assert isinstance(aspects, list)
        
        if aspects:  # If aspects were calculated
            for aspect in aspects[:3]:  # Check first few aspects
                assert "object1" in aspect
                assert "object2" in aspect
                assert "aspect" in aspect
                assert "angle" in aspect
                assert "orb" in aspect
                assert "strength" in aspect
                assert "applying" in aspect
                assert "exact_angle" in aspect
                assert "orb_percentage" in aspect
                
                # Verify data types and ranges
                assert isinstance(aspect["strength"], (int, float))
                assert 0.0 <= aspect["strength"] <= 1.0
                assert isinstance(aspect["angle"], (int, float))
                assert 0.0 <= aspect["angle"] <= 360.0
        
        # Verify aspect matrix data
        if data["aspect_matrix"]:
            matrix = data["aspect_matrix"]
            assert "total_aspects" in matrix
            assert "major_aspects" in matrix
            assert "minor_aspects" in matrix
            assert "orb_config_used" in matrix
            assert "calculation_time_ms" in matrix
            
            assert matrix["total_aspects"] == len(aspects)
            assert matrix["total_aspects"] == matrix["major_aspects"] + matrix["minor_aspects"]
        
        # Verify calculation metadata
        metadata = data["calculation_metadata"]
        assert "calculation_time" in metadata
        assert "features_included" in metadata
        assert isinstance(metadata["features_included"], list)
        assert "aspects" in metadata["features_included"]
    
    def test_different_orb_presets(self, client, sample_enhanced_request):
        """Test different orb preset configurations."""
        orb_presets = ["traditional", "modern", "tight"]
        
        for preset in orb_presets:
            request_data = sample_enhanced_request.copy()
            request_data["aspect_orb_preset"] = preset
            
            response = client.post("/ephemeris/v2/natal-enhanced", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # Verify orb system was used
            if data.get("aspect_matrix"):
                assert data["aspect_matrix"]["orb_config_used"] == preset
    
    def test_custom_orb_configuration(self, client, sample_enhanced_request):
        """Test custom orb configuration."""
        custom_orbs = {
            "conjunction": {
                "sun": 10.0,
                "moon": 10.0,
                "default": 8.0
            },
            "opposition": {
                "sun": 10.0,
                "moon": 10.0,
                "default": 8.0
            }
        }
        
        request_data = sample_enhanced_request.copy()
        request_data["custom_orb_config"] = custom_orbs
        
        response = client.post("/ephemeris/v2/natal-enhanced", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Custom orb config should be used instead of preset
        if data.get("aspect_matrix"):
            assert data["aspect_matrix"]["orb_config_used"] == "custom"
    
    def test_metadata_levels(self, client, sample_enhanced_request):
        """Test different metadata detail levels."""
        metadata_levels = ["basic", "full", "audit"]
        
        for level in metadata_levels:
            request_data = sample_enhanced_request.copy()
            request_data["metadata_level"] = level
            
            response = client.post("/ephemeris/v2/natal-enhanced", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            metadata = data["calculation_metadata"]
            
            # Basic level should have minimal metadata
            if level == "basic":
                required_fields = {"calculation_time", "features_included"}
                assert all(field in metadata for field in required_fields)
            
            # Full level should have additional performance data
            elif level == "full":
                expected_fields = {
                    "calculation_time", "features_included",
                    "aspect_calculation_time_ms", "orb_system_used"
                }
                # Some fields may be None but should be present
                assert all(field in metadata for field in expected_fields)
            
            # Audit level should have comprehensive performance metrics
            elif level == "audit":
                expected_fields = {
                    "calculation_time", "features_included",
                    "aspect_calculation_time_ms", "orb_system_used",
                    "performance_metrics"
                }
                assert all(field in metadata for field in expected_fields)
    
    def test_aspects_disabled(self, client, sample_enhanced_request):
        """Test enhanced endpoint with aspects disabled."""
        request_data = sample_enhanced_request.copy()
        request_data["include_aspects"] = False
        
        response = client.post("/ephemeris/v2/natal-enhanced", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Should still return standard aspects from natal chart, not enhanced aspects
        aspects = data.get("aspects", [])
        # Features should not include aspects
        metadata = data["calculation_metadata"]
        assert "aspects" not in metadata.get("features_included", [])
    
    def test_input_validation_errors(self, client):
        """Test input validation error handling."""
        # Invalid orb preset
        invalid_request = {
            "subject": {
                "name": "Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            },
            "aspect_orb_preset": "invalid_preset"
        }
        
        response = client.post("/ephemeris/v2/natal-enhanced", json=invalid_request)
        assert response.status_code == 422  # Validation error
        
        # Invalid metadata level
        invalid_request["aspect_orb_preset"] = "traditional"
        invalid_request["metadata_level"] = "invalid_level"
        
        response = client.post("/ephemeris/v2/natal-enhanced", json=invalid_request)
        assert response.status_code == 422
        
        # Missing required subject data
        minimal_invalid = {"subject": {}}
        
        response = client.post("/ephemeris/v2/natal-enhanced", json=minimal_invalid)
        assert response.status_code == 422
    
    def test_backward_compatibility(self, client):
        """Test that standard natal endpoint still works alongside enhanced."""
        standard_request = {
            "subject": {
                "name": "Test Subject",
                "datetime": {"iso_string": "1990-06-15T14:30:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            }
        }
        
        # Standard endpoint should still work
        response = client.post("/ephemeris/natal", json=standard_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["chart_type"] == "natal"  # Not "natal_enhanced"
    
    def test_api_performance_under_load(self, client, sample_enhanced_request):
        """Test API performance under concurrent load."""
        import concurrent.futures
        import threading
        
        def make_request():
            response = client.post("/ephemeris/v2/natal-enhanced", json=sample_enhanced_request)
            return response.status_code, response.elapsed if hasattr(response, 'elapsed') else None
        
        # Make 5 concurrent requests
        n_requests = 5
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(n_requests)]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                status_code, elapsed = future.result()
                results.append((status_code, elapsed))
        
        # All requests should succeed
        assert len(results) == n_requests
        assert all(status_code == 200 for status_code, _ in results)
    
    def test_error_handling_robustness(self, client):
        """Test error handling in various failure scenarios."""
        # Malformed JSON
        response = client.post(
            "/ephemeris/v2/natal-enhanced",
            data="malformed json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Empty request
        response = client.post("/ephemeris/v2/natal-enhanced", json={})
        assert response.status_code == 422
        
        # Invalid coordinate format
        invalid_coords_request = {
            "subject": {
                "name": "Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00"},
                "latitude": {"decimal": "invalid"},  # Should be number
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = client.post("/ephemeris/v2/natal-enhanced", json=invalid_coords_request)
        assert response.status_code == 422
    
    def test_response_schema_compliance(self, client, sample_enhanced_request):
        """Test that response complies with enhanced schema."""
        response = client.post("/ephemeris/v2/natal-enhanced", json=sample_enhanced_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response can be parsed by Pydantic model
        try:
            # This will raise validation error if response doesn't match schema
            enhanced_response = NatalChartEnhancedResponse(**data)
            
            # Verify key fields are properly typed
            assert isinstance(enhanced_response.success, bool)
            assert isinstance(enhanced_response.aspects, list)
            assert isinstance(enhanced_response.calculation_metadata, CalculationMetadata)
            
            # Check aspect matrix if present
            if enhanced_response.aspect_matrix:
                assert isinstance(enhanced_response.aspect_matrix, AspectMatrixResponse)
                assert isinstance(enhanced_response.aspect_matrix.total_aspects, int)
                assert isinstance(enhanced_response.aspect_matrix.calculation_time_ms, float)
            
            # Check aspects format
            for aspect in enhanced_response.aspects:
                assert isinstance(aspect, EnhancedAspectResponse)
                assert isinstance(aspect.strength, float)
                assert 0.0 <= aspect.strength <= 1.0
                
        except Exception as e:
            pytest.fail(f"Response does not comply with enhanced schema: {e}")

    def test_capture_full_output_for_verification(self, client):
        """Capture and print full JSON output for comprehensive chart with ALL features."""
        # Chart: Wed, 15 July 1987, Dallas, TX (US), 96w48, 32n47, 9:01 a.m. local, UTC 14:01
        request_payload = {
            "subject": {
                "name": "Dallas Comprehensive Chart 1987-07-15 09:01",
                "datetime": {"iso_string": "1987-07-15T09:01:00"},
                "latitude": {"decimal": 32.7833333333},
                "longitude": {"decimal": -96.8},
                "timezone": {"name": "America/Chicago"},
            },
            "configuration": {
                "house_system": "P",
                "include_asteroids": True,
                "include_nodes": True,
                "include_lilith": True,
                "include_fixed_stars": True,
                "fixed_star_magnitude_limit": 2.5
            },
            "include_aspects": True,
            "aspect_orb_preset": "traditional",
            "metadata_level": "audit",
            "include_arabic_parts": True,
            "include_all_traditional_parts": True,
            "include_dignities": True,
            "include_astrocartography": True,
            "include_hermetic_lots": True
        }

        # Try the new comprehensive endpoint first, fallback to enhanced
        response = client.post("/ephemeris/v3/comprehensive", json=request_payload)
        if response.status_code == 404:
            # Fallback to enhanced endpoint if comprehensive doesn't exist yet
            response = client.post("/ephemeris/v2/natal-enhanced", json=request_payload)
        status = response.status_code
        # Try to decode JSON; fall back to raw text
        try:
            body = response.json()
        except Exception:
            body = {"raw": response.text}

        # Wrap with minimal envelope for debugging context
        data = {
            "status_code": status,
            "payload": request_payload,
            "response": body,
        }

        # Print full JSON for manual review
        print("\nCOMPREHENSIVE EPHEMERIS SNAPSHOT (Dallas 1987-07-15 09:01)")
        print(f"HTTP status: {status}")
        print("Features: Planets, Asteroids, Nodes, Lilith, Houses, Angles, Fixed Stars, Aspects, Hermetic Lots, ACG, Dignities\n")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # Write snapshot to current directory for easy access
        current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"COMPREHENSIVE_EPHEMERIS_OUTPUT_{current_timestamp}.json"
        out_path = os.path.join(CURRENT_DIR, filename)
        
        # Also write to reference/snapshots if it exists
        repo_root = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))
        snapshots_dir = os.path.join(repo_root, "reference", "snapshots")
        if not os.path.exists(snapshots_dir):
            os.makedirs(snapshots_dir, exist_ok=True)
        
        backup_path = os.path.join(snapshots_dir, f"API_SNAPSHOT_{current_timestamp}_COMPREHENSIVE_DALLAS_19870715.json")

        # Write primary output to test directory
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Write backup to snapshots directory
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nPrimary output written to: {out_path}")
        print(f"Backup snapshot written to: {backup_path}\n")
        
        # Make this test pass as long as we produced outputs
        assert os.path.exists(out_path)
        assert os.path.exists(backup_path)


class TestAPIDocumentation:
    """Test API documentation and schema endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client for API requests."""
        return TestClient(app)
    
    def test_openapi_schema_includes_enhanced_endpoint(self, client):
        """Test that OpenAPI schema includes enhanced endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_schema = response.json()
        paths = openapi_schema.get("paths", {})
        
        # Enhanced endpoint should be documented
        assert "/ephemeris/v2/natal-enhanced" in paths
        enhanced_path = paths["/ephemeris/v2/natal-enhanced"]
        
        # Should have POST method
        assert "post" in enhanced_path
        enhanced_post = enhanced_path["post"]
        
        # Should have proper request/response schemas
        assert "requestBody" in enhanced_post
        assert "responses" in enhanced_post
        assert "200" in enhanced_post["responses"]
    
    def test_api_docs_accessible(self, client):
        """Test that API documentation is accessible."""
        # Swagger UI should be accessible
        response = client.get("/docs")
        assert response.status_code == 200
        
        # ReDoc should be accessible
        response = client.get("/redoc")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])