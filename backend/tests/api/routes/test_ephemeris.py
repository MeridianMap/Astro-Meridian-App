"""
Integration tests for Meridian Ephemeris API endpoints.

Tests the complete API functionality including input validation,
chart calculation, and response formatting.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.api.models.schemas import NatalChartRequest, SubjectRequest, DateTimeInput, CoordinateInput, TimezoneInput


# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_global_health_check(self):
        """Test global health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "meridian-ephemeris-api"
        assert "timestamp" in data
    
    def test_ephemeris_health_check(self):
        """Test ephemeris health endpoint."""
        response = client.get("/ephemeris/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "ephemeris_available" in data
        assert "uptime" in data


class TestRootEndpoint:
    """Test root API endpoint."""
    
    def test_root_endpoint(self):
        """Test API root endpoint returns proper information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Meridian Ephemeris API"
        assert data["version"] == "1.0.0"
        assert "documentation" in data
        assert "endpoints" in data
        assert data["status"] == "operational"


class TestSchemaEndpoints:
    """Test API schema and reference endpoints."""
    
    def test_natal_request_schema(self):
        """Test natal chart request schema endpoint."""
        response = client.get("/ephemeris/schemas/natal-request")
        
        assert response.status_code == 200
        data = response.json()
        assert "schema" in data
        assert "examples" in data
        assert "basic" in data["examples"]
        assert "dms_coordinates" in data["examples"]
    
    def test_natal_response_schema(self):
        """Test natal chart response schema endpoint."""
        response = client.get("/ephemeris/schemas/natal-response")
        
        assert response.status_code == 200
        data = response.json()
        assert "schema" in data
        assert "description" in data
    
    def test_house_systems_endpoint(self):
        """Test house systems reference endpoint."""
        response = client.get("/ephemeris/house-systems")
        
        assert response.status_code == 200
        data = response.json()
        assert "house_systems" in data
        assert "P" in data["house_systems"]  # Placidus
        assert data["house_systems"]["P"] == "Placidus"
        assert data["default"] == "P"
    
    def test_supported_objects_endpoint(self):
        """Test supported objects reference endpoint."""
        response = client.get("/ephemeris/supported-objects")
        
        assert response.status_code == 200
        data = response.json()
        assert "planets" in data
        assert "asteroids" in data
        assert "nodes" in data
        assert "lilith" in data
        assert "configuration" in data


class TestNatalChartEndpoint:
    """Test natal chart calculation endpoint."""
    
    def get_basic_natal_request(self):
        """Get basic natal chart request for testing."""
        return {
            "subject": {
                "name": "Test Subject",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"name": "America/New_York"}
            }
        }
    
    def test_natal_chart_basic_request(self):
        """Test basic natal chart calculation."""
        request_data = self.get_basic_natal_request()
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["success"] is True
        assert "subject" in data
        assert "planets" in data
        assert "houses" in data
        assert "angles" in data
        assert "aspects" in data
        assert "calculation_time" in data
        assert data["chart_type"] == "natal"
        
        # Verify subject data
        assert data["subject"]["name"] == "Test Subject"
        assert abs(data["subject"]["latitude"] - 40.7128) < 0.0001
        assert abs(data["subject"]["longitude"] - (-74.0060)) < 0.0001
        
        # Verify planets data
        assert len(data["planets"]) > 0
        assert "Sun" in data["planets"]
        assert "Moon" in data["planets"]
        
        # Verify planet structure
        sun_data = data["planets"]["Sun"]
        assert "longitude" in sun_data
        assert "latitude" in sun_data
        assert "sign_name" in sun_data
        
        # Verify houses data
        assert "system" in data["houses"]
        assert "cusps" in data["houses"]
        assert len(data["houses"]["cusps"]) == 12
        
        # Verify angles data
        assert "ascendant" in data["angles"]
        assert "midheaven" in data["angles"]
        assert "descendant" in data["angles"]
        assert "imum_coeli" in data["angles"]
    
    def test_natal_chart_dms_coordinates(self):
        """Test natal chart with DMS coordinate format."""
        request_data = {
            "subject": {
                "name": "DMS Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00"},
                "latitude": {"dms": "40°42'46\"N"},
                "longitude": {"dms": "74°00'22\"W"},
                "timezone": {"name": "America/New_York"}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["subject"]["name"] == "DMS Test"
    
    def test_natal_chart_component_coordinates(self):
        """Test natal chart with component coordinate format."""
        request_data = {
            "subject": {
                "name": "Component Test",
                "datetime": {"iso_string": "1985-03-21T09:15:00"},
                "latitude": {
                    "components": {
                        "degrees": 51,
                        "minutes": 30,
                        "seconds": 26,
                        "direction": "N"
                    }
                },
                "longitude": {
                    "components": {
                        "degrees": 0,
                        "minutes": 7,
                        "seconds": 39,
                        "direction": "W"
                    }
                },
                "timezone": {"name": "Europe/London"}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["subject"]["name"] == "Component Test"
    
    def test_natal_chart_julian_day_input(self):
        """Test natal chart with Julian Day datetime input."""
        request_data = {
            "subject": {
                "name": "Julian Day Test",
                "datetime": {"julian_day": 2451545.0},  # J2000.0
                "latitude": {"decimal": 48.8566},
                "longitude": {"decimal": 2.3522},
                "timezone": {"name": "Europe/Paris"}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["subject"]["name"] == "Julian Day Test"
    
    def test_natal_chart_with_configuration(self):
        """Test natal chart with custom configuration."""
        request_data = {
            "subject": {
                "name": "Config Test",
                "datetime": {"iso_string": "2000-12-25T18:30:00"},
                "latitude": {"decimal": 34.0522},
                "longitude": {"decimal": -118.2437},
                "timezone": {"utc_offset": -8.0}
            },
            "configuration": {
                "house_system": "K",  # Koch
                "include_asteroids": False,
                "include_nodes": True,
                "include_lilith": False,
                "aspect_orbs": {
                    "Conjunction": 10.0,
                    "Opposition": 10.0
                }
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["houses"]["system"] == "K"  # Koch system
    
    def test_natal_chart_utc_offset_timezone(self):
        """Test natal chart with UTC offset timezone."""
        request_data = {
            "subject": {
                "name": "UTC Offset Test",
                "datetime": {"iso_string": "2000-06-21T15:45:00"},
                "latitude": {"decimal": 35.6762},
                "longitude": {"decimal": 139.6503},
                "timezone": {"utc_offset": 9.0}  # JST
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["subject"]["utc_offset"] == 9.0


class TestInputValidation:
    """Test API input validation."""
    
    def test_empty_request(self):
        """Test empty request returns validation error."""
        response = client.post("/ephemeris/natal", json={})
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
    
    def test_missing_subject_name(self):
        """Test missing subject name validation."""
        request_data = {
            "subject": {
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
    
    def test_invalid_coordinate_format(self):
        """Test invalid coordinate format validation."""
        request_data = {
            "subject": {
                "name": "Invalid Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.7128, "dms": "40°N"},  # Multiple formats
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
    
    def test_invalid_datetime_format(self):
        """Test invalid datetime format validation."""
        request_data = {
            "subject": {
                "name": "Invalid DateTime",
                "datetime": {"iso_string": "invalid-date", "julian_day": 2451545.0},  # Multiple formats
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
    
    def test_out_of_bounds_coordinates(self):
        """Test out of bounds coordinates validation."""
        request_data = {
            "subject": {
                "name": "Out of Bounds",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 100.0},  # Invalid latitude
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        # Out of bounds coordinates may be caught by Subject validation (400) 
        # or passed through and fail during calculation (500)
        assert response.status_code in [400, 422, 500]
        data = response.json()
        assert data["success"] is False
    
    def test_invalid_house_system(self):
        """Test invalid house system validation."""
        request_data = {
            "subject": {
                "name": "Invalid House System",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            },
            "configuration": {
                "house_system": "INVALID"
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "validation_error"


class TestErrorHandling:
    """Test API error handling."""
    
    @patch('app.services.ephemeris_service.ephemeris_service.calculate_natal_chart')
    def test_calculation_error_handling(self, mock_calculate):
        """Test calculation error handling."""
        from app.services.ephemeris_service import CalculationError
        
        # Mock a calculation error
        mock_calculate.side_effect = CalculationError("Mock calculation error")
        
        request_data = {
            "subject": {
                "name": "Error Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "calculation_error"
        assert "Mock calculation error" in data["message"]
    
    @patch('app.services.ephemeris_service.ephemeris_service.calculate_natal_chart')
    def test_input_validation_error_handling(self, mock_calculate):
        """Test input validation error handling."""
        from app.services.ephemeris_service import InputValidationError
        
        # Mock an input validation error
        mock_calculate.side_effect = InputValidationError("Mock validation error")
        
        request_data = {
            "subject": {
                "name": "Validation Error Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "Mock validation error" in data["message"]
    
    @patch('app.services.ephemeris_service.ephemeris_service.calculate_natal_chart')
    def test_unexpected_error_handling(self, mock_calculate):
        """Test unexpected error handling."""
        # Mock an unexpected error
        mock_calculate.side_effect = RuntimeError("Mock unexpected error")
        
        request_data = {
            "subject": {
                "name": "Unexpected Error Test", 
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "internal_error"


class TestResponseFormat:
    """Test API response formatting."""
    
    def test_response_headers(self):
        """Test that responses include proper headers."""
        request_data = {
            "subject": {
                "name": "Header Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 0.0},
                "longitude": {"decimal": 0.0}
            }
        }
        
        response = client.post("/ephemeris/natal", json=request_data)
        
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"
    
    def test_response_consistency(self):
        """Test that responses are consistent across multiple requests."""
        request_data = {
            "subject": {
                "name": "Consistency Test",
                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            }
        }
        
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = client.post("/ephemeris/natal", json=request_data)
            assert response.status_code == 200
            responses.append(response.json())
        
        # Compare key data points (should be identical)
        base_response = responses[0]
        for response in responses[1:]:
            assert response["subject"]["julian_day"] == base_response["subject"]["julian_day"]
            assert response["planets"]["Sun"]["longitude"] == base_response["planets"]["Sun"]["longitude"]
            assert response["angles"]["ascendant"] == base_response["angles"]["ascendant"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])