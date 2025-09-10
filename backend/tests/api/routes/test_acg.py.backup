"""
Test Suite for ACG API Endpoints (PRP 2)

Comprehensive tests for ACG REST API endpoints including:
- /acg/lines - Single chart ACG calculation
- /acg/batch - Batch ACG calculations
- /acg/features - Supported features and capabilities
- /acg/schema - Metadata schema
- /acg/animate - Animation frames
- /acg/health - Service health check

Tests cover request validation, response formats, error handling, and performance.
"""

import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.acg.acg_types import ACGResult, ACGBody, ACGBodyType, ACGOptions


class TestACGAPIEndpoints:
    """Test ACG API endpoints basic functionality."""
    
    @pytest.fixture
    def client(self):
        """Test client for ACG API."""
        return TestClient(app)
    
    @pytest.fixture
    def valid_acg_request(self):
        """Valid ACG request for testing."""
        return {
            "epoch": "2000-01-01T12:00:00Z",
            "bodies": [
                {"id": "Sun", "type": "planet"},
                {"id": "Moon", "type": "planet"}
            ],
            "options": {
                "line_types": ["MC", "IC"],
                "include_parans": False,
                "orb_deg": 1.0
            },
            "natal": {
                "birthplace_lat": 40.7128,
                "birthplace_lon": -74.0060
            }
        }
    
    def test_acg_health_endpoint(self, client):
        """Test ACG health check endpoint."""
        response = client.get("/acg/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["service"] == "acg"
        assert "supported_bodies" in data
        assert "se_version" in data
        assert "timestamp" in data
    
    def test_acg_features_endpoint(self, client):
        """Test ACG features endpoint.""" 
        response = client.get("/acg/features")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "bodies" in data
        assert "line_types" in data
        assert "aspects" in data
        assert "defaults" in data
        assert "metadata_keys" in data
        
        # Check that we have expected bodies
        body_ids = [body["id"] for body in data["bodies"]]
        assert "Sun" in body_ids
        assert "Moon" in body_ids
        
        # Check line types
        assert "MC" in data["line_types"]
        assert "IC" in data["line_types"]
        assert "AC" in data["line_types"]
        assert "DC" in data["line_types"]
        
        # Check aspects
        assert "square" in data["aspects"]
        assert "trine" in data["aspects"]
    
    def test_acg_schema_endpoint(self, client):
        """Test ACG schema endpoint."""
        response = client.get("/acg/schema")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        schema = response.json()
        
        assert "$schema" in schema
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert "title" in schema
        assert "properties" in schema
        assert "required" in schema
        
        # Check required properties
        assert "id" in schema["properties"]
        assert "type" in schema["properties"]
        assert "coords" in schema["properties"]
        assert "line" in schema["properties"]
    
    @patch('app.api.routes.acg.acg_engine.calculate_acg_lines')
    def test_acg_lines_endpoint_success(self, mock_calculate, client, valid_acg_request):
        """Test successful ACG lines calculation."""
        # Mock the calculation result
        mock_result = ACGResult(
            type="FeatureCollection",
            features=[
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[-180, -90], [180, 90]]
                    },
                    "properties": {
                        "id": "Sun",
                        "type": "body",
                        "line": {"line_type": "MC"},
                        "source": "Meridian-ACG"
                    }
                }
            ]
        )
        mock_calculate.return_value = mock_result
        
        response = client.post("/acg/lines", json=valid_acg_request)
        
        assert response.status_code == 200
        assert "application/geo+json" in response.headers.get("content-type", "")
        assert "X-Calculation-Time" in response.headers
        assert "X-Features-Count" in response.headers
        
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert len(data["features"]) == 1
        
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        assert "properties" in feature
        assert feature["properties"]["id"] == "Sun"
    
    def test_acg_lines_endpoint_validation_error(self, client):
        """Test ACG lines endpoint with invalid request."""
        invalid_request = {
            "epoch": "invalid-date-format",
            "bodies": []
        }
        
        response = client.post("/acg/lines", json=invalid_request)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @patch('app.api.routes.acg.acg_engine.calculate_acg_lines')
    def test_acg_lines_endpoint_calculation_error(self, mock_calculate, client, valid_acg_request):
        """Test ACG lines endpoint with calculation error."""
        mock_calculate.side_effect = RuntimeError("Calculation failed")
        
        response = client.post("/acg/lines", json=valid_acg_request)
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "calculation_error"
        assert "calculation failed" in data["detail"]["message"].lower()
    
    @patch('app.api.routes.acg.acg_engine.calculate_acg_lines')
    def test_acg_batch_endpoint_success(self, mock_calculate, client, valid_acg_request):
        """Test successful ACG batch calculation."""
        # Mock successful calculation
        mock_result = ACGResult(
            type="FeatureCollection",
            features=[
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                    "properties": {"id": "Sun", "source": "Meridian-ACG"}
                }
            ]
        )
        mock_calculate.return_value = mock_result
        
        batch_request = {
            "requests": [
                {**valid_acg_request, "correlation_id": "test-1"},
                {**valid_acg_request, "correlation_id": "test-2"}
            ]
        }
        
        response = client.post("/acg/batch", json=batch_request)
        
        assert response.status_code == 200
        assert "X-Calculation-Time" in response.headers
        assert "X-Batch-Size" in response.headers
        assert "X-Success-Count" in response.headers
        
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        
        for i, result in enumerate(data["results"]):
            assert result["correlation_id"] == f"test-{i+1}"
            assert "response" in result
            assert "error" not in result
    
    @patch('app.api.routes.acg.acg_engine.calculate_acg_lines')
    def test_acg_batch_endpoint_mixed_results(self, mock_calculate, client, valid_acg_request):
        """Test ACG batch with some successful and some failed calculations."""
        # First call succeeds, second fails
        mock_calculate.side_effect = [
            ACGResult(type="FeatureCollection", features=[]),
            RuntimeError("Second calculation failed")
        ]
        
        batch_request = {
            "requests": [
                {**valid_acg_request, "correlation_id": "success"},
                {**valid_acg_request, "correlation_id": "failure"}
            ]
        }
        
        response = client.post("/acg/batch", json=batch_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["results"]) == 2
        
        # First result should be successful
        success_result = next(r for r in data["results"] if r["correlation_id"] == "success")
        assert "response" in success_result
        assert "error" not in success_result
        
        # Second result should have error
        error_result = next(r for r in data["results"] if r["correlation_id"] == "failure")
        assert "error" in error_result
        assert "response" not in error_result
    
    @patch('app.api.routes.acg.acg_engine.calculate_acg_lines')
    def test_acg_animate_endpoint_success(self, mock_calculate, client, valid_acg_request):
        """Test successful ACG animation calculation."""
        mock_result = ACGResult(type="FeatureCollection", features=[])
        mock_calculate.return_value = mock_result
        
        animate_request = {
            "epoch_start": "2000-01-01T12:00:00Z",
            "epoch_end": "2000-01-01T14:00:00Z",  # 2 hour period
            "step_minutes": 60,  # 1 hour steps = 2 frames
            "bodies": [{"id": "Sun", "type": "planet"}],
            "options": {"line_types": ["MC"]}
        }
        
        response = client.post("/acg/animate", json=animate_request)
        
        assert response.status_code == 200
        assert "X-Calculation-Time" in response.headers
        assert "X-Frame-Count" in response.headers
        
        data = response.json()
        assert "frames" in data
        
        # Should have 2 frames (start time + 60 minutes)
        assert len(data["frames"]) == 2
        
        for frame in data["frames"]:
            assert "epoch" in frame
            assert "jd" in frame
            assert "data" in frame
    
    def test_acg_animate_endpoint_invalid_time_range(self, client):
        """Test ACG animate with invalid time range."""
        invalid_request = {
            "epoch_start": "2000-01-01T14:00:00Z",
            "epoch_end": "2000-01-01T12:00:00Z",  # End before start
            "step_minutes": 60
        }
        
        response = client.post("/acg/animate", json=invalid_request)
        
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"] == "validation_error"
        assert "start time must be before end time" in data["detail"]["message"].lower()


class TestACGAPIValidation:
    """Test API request validation and error handling."""
    
    @pytest.fixture
    def client(self):
        """Test client for ACG API."""
        return TestClient(app)
    
    def test_acg_lines_missing_epoch(self, client):
        """Test validation error for missing epoch."""
        invalid_request = {
            "bodies": [{"id": "Sun", "type": "planet"}]
            # Missing required 'epoch' field
        }
        
        response = client.post("/acg/lines", json=invalid_request)
        assert response.status_code == 422
    
    def test_acg_lines_invalid_epoch_format(self, client):
        """Test validation error for invalid epoch format."""
        invalid_request = {
            "epoch": "not-a-date",
            "bodies": [{"id": "Sun", "type": "planet"}]
        }
        
        response = client.post("/acg/lines", json=invalid_request)
        assert response.status_code == 422
    
    def test_acg_lines_invalid_body_type(self, client):
        """Test validation error for invalid body type."""
        invalid_request = {
            "epoch": "2000-01-01T12:00:00Z",
            "bodies": [{"id": "Sun", "type": "invalid_type"}]
        }
        
        response = client.post("/acg/lines", json=invalid_request)
        assert response.status_code == 422
    
    def test_acg_lines_invalid_natal_coordinates(self, client):
        """Test validation error for invalid natal coordinates."""
        invalid_request = {
            "epoch": "2000-01-01T12:00:00Z",
            "natal": {
                "birthplace_lat": 95.0,  # Invalid: > 90
                "birthplace_lon": -200.0  # Invalid: < -180
            }
        }
        
        response = client.post("/acg/lines", json=invalid_request)
        assert response.status_code == 422
    
    def test_acg_batch_empty_requests(self, client):
        """Test validation error for empty batch requests."""
        invalid_request = {
            "requests": []  # Empty array
        }
        
        response = client.post("/acg/batch", json=invalid_request)
        assert response.status_code == 422
    
    def test_acg_animate_invalid_step(self, client):
        """Test validation error for invalid animation step."""
        invalid_request = {
            "epoch_start": "2000-01-01T12:00:00Z",
            "epoch_end": "2000-01-01T14:00:00Z",
            "step_minutes": 0  # Invalid: must be >= 1
        }
        
        response = client.post("/acg/animate", json=invalid_request)
        assert response.status_code == 422
    
    def test_acg_animate_step_too_large(self, client):
        """Test validation error for animation step too large."""
        invalid_request = {
            "epoch_start": "2000-01-01T12:00:00Z",
            "epoch_end": "2000-01-01T14:00:00Z", 
            "step_minutes": 50000  # Invalid: > 43200 (30 days)
        }
        
        response = client.post("/acg/animate", json=invalid_request)
        assert response.status_code == 422


class TestACGAPIResponseFormats:
    """Test API response formats and structure."""
    
    @pytest.fixture
    def client(self):
        """Test client for ACG API."""
        return TestClient(app)
    
    def test_acg_features_response_structure(self, client):
        """Test ACG features response has correct structure."""
        response = client.get("/acg/features")
        data = response.json()
        
        # Validate bodies structure
        assert isinstance(data["bodies"], list)
        if data["bodies"]:
            body = data["bodies"][0]
            assert "id" in body
            assert "type" in body
            assert body["type"] in ["planet", "asteroid", "lot", "node", "fixed_star", "point", "dwarf"]
        
        # Validate line_types
        assert isinstance(data["line_types"], list)
        assert all(isinstance(lt, str) for lt in data["line_types"])
        
        # Validate aspects
        assert isinstance(data["aspects"], list)
        assert all(isinstance(aspect, str) for aspect in data["aspects"])
        
        # Validate defaults
        assert "defaults" in data
        defaults = data["defaults"]
        assert "orb_deg" in defaults
        assert "include_parans" in defaults
        assert "include_fixed_stars" in defaults
        
        # Validate metadata_keys
        assert isinstance(data["metadata_keys"], list)
        assert "id" in data["metadata_keys"]
        assert "type" in data["metadata_keys"]
        assert "coords" in data["metadata_keys"]
    
    def test_acg_schema_response_structure(self, client):
        """Test ACG schema response has valid JSON Schema structure."""
        response = client.get("/acg/schema")
        schema = response.json()
        
        # Basic JSON Schema structure
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert "title" in schema
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        
        # Check specific property schemas
        properties = schema["properties"]
        
        # Coordinate schema
        assert "coords" in properties
        coords_schema = properties["coords"]
        assert coords_schema["type"] == "object"
        assert "properties" in coords_schema
        assert "ra" in coords_schema["properties"]
        assert "dec" in coords_schema["properties"]
        
        # Line schema
        assert "line" in properties
        line_schema = properties["line"]
        assert line_schema["type"] == "object"
        assert "angle" in line_schema["properties"]
        assert "line_type" in line_schema["properties"]
    
    @patch('app.api.routes.acg.acg_engine.calculate_acg_lines')
    def test_acg_lines_geojson_compliance(self, mock_calculate, client):
        """Test that ACG lines response is valid GeoJSON."""
        mock_result = ACGResult(
            type="FeatureCollection",
            features=[
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[-180, -90], [0, 0], [180, 90]]
                    },
                    "properties": {
                        "id": "Sun",
                        "type": "body",
                        "line": {"line_type": "MC"},
                        "source": "Meridian-ACG"
                    }
                }
            ]
        )
        mock_calculate.return_value = mock_result
        
        request_data = {
            "epoch": "2000-01-01T12:00:00Z",
            "bodies": [{"id": "Sun", "type": "planet"}]
        }
        
        response = client.post("/acg/lines", json=request_data)
        data = response.json()
        
        # Validate GeoJSON FeatureCollection structure
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        
        # Validate Feature structure
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        assert "properties" in feature
        
        # Validate Geometry structure
        geometry = feature["geometry"]
        assert "type" in geometry
        assert geometry["type"] in ["Point", "LineString", "MultiLineString", "Polygon"]
        assert "coordinates" in geometry
        
        # Validate coordinates are numbers
        coords = geometry["coordinates"]
        if geometry["type"] == "LineString":
            assert all(isinstance(coord, list) and len(coord) == 2 for coord in coords)
            assert all(isinstance(coord[0], (int, float)) and isinstance(coord[1], (int, float)) 
                      for coord in coords)


class TestACGAPIPerformance:
    """Test API performance characteristics and headers."""
    
    @pytest.fixture
    def client(self):
        """Test client for ACG API."""
        return TestClient(app)
    
    @patch('app.api.routes.acg.acg_engine.calculate_acg_lines')
    def test_acg_lines_performance_headers(self, mock_calculate, client):
        """Test that performance headers are present."""
        mock_calculate.return_value = ACGResult(type="FeatureCollection", features=[])
        
        request_data = {
            "epoch": "2000-01-01T12:00:00Z",
            "bodies": [{"id": "Sun", "type": "planet"}]
        }
        
        response = client.post("/acg/lines", json=request_data)
        
        assert "X-Calculation-Time" in response.headers
        assert "X-Features-Count" in response.headers
        assert "X-Process-Time" in response.headers  # From middleware
        
        # Check calculation time format
        calc_time = response.headers["X-Calculation-Time"]
        assert calc_time.endswith("ms")
        assert float(calc_time[:-2]) >= 0  # Should be positive number
    
    @patch('app.api.routes.acg.acg_engine.calculate_acg_lines')
    def test_acg_batch_performance_headers(self, mock_calculate, client):
        """Test that batch performance headers are present."""
        mock_calculate.return_value = ACGResult(type="FeatureCollection", features=[])
        
        batch_request = {
            "requests": [
                {"epoch": "2000-01-01T12:00:00Z", "bodies": [{"id": "Sun", "type": "planet"}]},
                {"epoch": "2000-01-01T12:00:00Z", "bodies": [{"id": "Moon", "type": "planet"}]}
            ]
        }
        
        response = client.post("/acg/batch", json=batch_request)
        
        assert "X-Calculation-Time" in response.headers
        assert "X-Batch-Size" in response.headers
        assert "X-Success-Count" in response.headers
        
        assert response.headers["X-Batch-Size"] == "2"
        assert response.headers["X-Success-Count"] == "2"
    
    @patch('app.api.routes.acg.acg_engine.calculate_acg_lines')
    def test_acg_animate_performance_headers(self, mock_calculate, client):
        """Test that animate performance headers are present."""
        mock_calculate.return_value = ACGResult(type="FeatureCollection", features=[])
        
        animate_request = {
            "epoch_start": "2000-01-01T12:00:00Z",
            "epoch_end": "2000-01-01T13:00:00Z",
            "step_minutes": 30
        }
        
        response = client.post("/acg/animate", json=animate_request)
        
        assert "X-Calculation-Time" in response.headers
        assert "X-Frame-Count" in response.headers
        
        frame_count = int(response.headers["X-Frame-Count"])
        assert frame_count >= 2  # At least start and end frames


if __name__ == "__main__":
    pytest.main([__file__, "-v"])