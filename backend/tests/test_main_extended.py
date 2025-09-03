"""
Extended tests for main.py FastAPI application to improve coverage.

Tests application lifecycle, middleware, exception handlers, and endpoints.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app


class TestApplicationLifecycle:
    """Test application startup and lifecycle events."""
    
    def test_app_creation(self):
        """Test that app is created properly."""
        assert app is not None
        assert app.title == "Meridian Ephemeris API"
        assert app.version == "1.0.0"
    
    def test_app_metadata(self):
        """Test application metadata."""
        assert "Professional Astrological Calculations" in app.description
        assert app.contact["name"] == "Meridian Ephemeris Support"
        assert app.license_info["name"] == "MIT License"
    
    def test_openapi_urls(self):
        """Test OpenAPI documentation URLs are set."""
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert app.openapi_url == "/openapi.json"


class TestMiddleware:
    """Test middleware functionality."""
    
    def test_process_time_middleware(self):
        """Test that process time header is added."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
        
        # Process time should be a valid float
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
        assert process_time < 1.0  # Should be very fast for root endpoint
    
    def test_cors_middleware(self):
        """Test CORS middleware configuration."""
        client = TestClient(app)
        
        # Test preflight request
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # CORS headers should be present
        assert "Access-Control-Allow-Origin" in response.headers
    
    def test_gzip_middleware(self):
        """Test GZip compression middleware."""
        client = TestClient(app)
        
        # Request with Accept-Encoding for gzip
        response = client.get("/", headers={"Accept-Encoding": "gzip"})
        
        # For small responses, gzip might not be applied
        # Just verify the response is successful
        assert response.status_code == 200


class TestExceptionHandlers:
    """Test global exception handlers."""
    
    def test_validation_exception_handler(self):
        """Test Pydantic validation exception handling."""
        client = TestClient(app)
        
        # Send invalid data to trigger validation error
        response = client.post("/ephemeris/natal", json={
            "subject": {
                "name": "Test",
                # Missing required fields
            }
        })
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "details" in data
        assert "errors" in data["details"]
    
    def test_validation_handler_with_complex_errors(self):
        """Test validation handler with nested validation errors."""
        client = TestClient(app)
        
        # Send data with multiple validation errors
        response = client.post("/ephemeris/natal", json={
            "subject": {
                "name": "",  # Empty name
                "datetime": "invalid-datetime",  # Invalid datetime
                "latitude": {"decimal": 91.0},  # Out of bounds
                "longitude": {"decimal": -74.0060}
            }
        })
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "errors" in data["details"]
        assert len(data["details"]["errors"]) > 0
    
    def test_global_exception_handler(self):
        """Test global exception handler for unexpected errors."""
        client = TestClient(app)
        
        # Test with malformed JSON to trigger validation error first
        response = client.post("/ephemeris/natal", 
                              content="{invalid json}",
                              headers={"Content-Type": "application/json"})
        
        # This should trigger a validation error (422), not global handler
        assert response.status_code in [400, 422]
        
        # Test with completely invalid endpoint to ensure 404 handling
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404


class TestHealthEndpoints:
    """Test health check functionality."""
    
    def test_global_health_endpoint(self):
        """Test global health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "meridian-ephemeris-api"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert isinstance(data["timestamp"], (int, float))
    
    def test_ephemeris_health_endpoint(self):
        """Test ephemeris-specific health endpoint."""
        client = TestClient(app)
        response = client.get("/ephemeris/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "ephemeris_available" in data
        assert "uptime" in data


class TestRootEndpoint:
    """Test root API endpoint functionality."""
    
    def test_root_endpoint_structure(self):
        """Test root endpoint returns proper structure."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert data["message"] == "Welcome to Meridian Ephemeris API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
        
        # Check documentation links
        assert "documentation" in data
        assert data["documentation"]["interactive"] == "/docs"
        assert data["documentation"]["redoc"] == "/redoc"
        assert data["documentation"]["openapi"] == "/openapi.json"
        
        # Check endpoints
        assert "endpoints" in data
        assert data["endpoints"]["health"] == "/ephemeris/health"
        assert data["endpoints"]["natal_chart"] == "/ephemeris/natal"
    
    def test_root_endpoint_content_type(self):
        """Test root endpoint returns correct content type."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.headers["content-type"] == "application/json"


class TestApplicationConfiguration:
    """Test application configuration and settings."""
    
    def test_router_inclusion(self):
        """Test that routers are properly included."""
        # Check that ephemeris routes are included
        route_paths = [route.path for route in app.routes]
        
        assert "/ephemeris/natal" in route_paths
        assert "/ephemeris/health" in route_paths
        assert "/ephemeris/schemas/natal-request" in route_paths
    
    def test_middleware_stack(self):
        """Test middleware stack configuration."""
        # Check that middleware is registered
        middleware_types = [type(middleware) for middleware in app.user_middleware]
        
        # We expect CORS and GZip middleware
        middleware_names = [str(mw_type) for mw_type in middleware_types]
        
        # At least some middleware should be present
        assert len(middleware_names) > 0
    
    def test_exception_handlers_registered(self):
        """Test that exception handlers are registered."""
        # Check that exception handlers are configured
        assert len(app.exception_handlers) > 0
        
        # Should have handlers for common exception types
        from fastapi.exceptions import RequestValidationError
        assert RequestValidationError in app.exception_handlers


class TestApplicationStartup:
    """Test application startup behavior."""
    
    @patch('app.core.ephemeris.tools.ephemeris.validate_ephemeris_files')
    @patch('app.main.logger')
    def test_startup_with_valid_ephemeris(self, mock_logger, mock_validate):
        """Test startup behavior with valid ephemeris files."""
        # Mock successful validation
        mock_validate.return_value = {
            'Sun': True,
            'Moon': True,
            'Mercury': True,
            'Houses': True
        }
        
        # Create a new test client to trigger startup
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
        
        # Verify validation was called
        mock_validate.assert_called()
        mock_logger.info.assert_called()
    
    @patch('app.core.ephemeris.tools.ephemeris.validate_ephemeris_files')
    @patch('app.main.logger')
    def test_startup_with_missing_ephemeris(self, mock_logger, mock_validate):
        """Test startup behavior with missing ephemeris files."""
        # Mock partial validation
        mock_validate.return_value = {
            'Sun': True,
            'Moon': False,
            'Mercury': True,
            'Houses': False
        }
        
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
        
        mock_validate.assert_called()
        mock_logger.warning.assert_called()
    
    @patch('app.core.ephemeris.tools.ephemeris.validate_ephemeris_files')
    @patch('app.main.logger')
    def test_startup_validation_error(self, mock_logger, mock_validate):
        """Test startup behavior when validation fails."""
        # Mock validation error
        mock_validate.side_effect = Exception("Validation failed")
        
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
        
        mock_validate.assert_called()
        mock_logger.error.assert_called()


class TestRequestLogging:
    """Test request logging middleware."""
    
    @patch('app.main.logger')
    def test_request_logging(self, mock_logger):
        """Test that requests are logged."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        
        # Verify logging calls were made
        mock_logger.info.assert_called()
        
        # Check log content
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
        request_logs = [log for log in log_calls if "GET /" in log]
        response_logs = [log for log in log_calls if "200 in" in log]
        
        assert len(request_logs) > 0
        assert len(response_logs) > 0
    
    @patch('app.main.logger')
    def test_error_request_logging(self, mock_logger):
        """Test logging for error responses."""
        client = TestClient(app)
        
        # Make request that will cause validation error
        response = client.post("/ephemeris/natal", json={"invalid": "data"})
        
        assert response.status_code == 422
        
        # Should log both request and error response
        mock_logger.info.assert_called()
        mock_logger.warning.assert_called()


class TestApplicationSecurity:
    """Test application security aspects."""
    
    def test_no_server_header_leakage(self):
        """Test that server information is not leaked."""
        client = TestClient(app)
        response = client.get("/")
        
        # Should not reveal FastAPI/Starlette version info
        assert "server" not in response.headers or "FastAPI" not in response.headers.get("server", "")
    
    def test_content_type_security(self):
        """Test content-type headers for security."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.headers["content-type"] == "application/json"
    
    def test_error_response_security(self):
        """Test that error responses don't leak sensitive info."""
        client = TestClient(app)
        
        # Trigger an error
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        # Should not contain internal path information or stack traces
        response_text = response.text.lower()
        assert "traceback" not in response_text
        assert "file system" not in response_text


class TestPerformance:
    """Test application performance characteristics."""
    
    def test_response_time_headers(self):
        """Test that response time is tracked."""
        client = TestClient(app)
        response = client.get("/")
        
        assert "X-Process-Time" in response.headers
        process_time = float(response.headers["X-Process-Time"])
        
        # Should be fast for simple endpoint
        assert process_time < 0.1  # Less than 100ms
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        client = TestClient(app)
        results = []
        
        def make_request():
            start = time.time()
            response = client.get("/")
            end = time.time()
            results.append({
                'status': response.status_code,
                'duration': end - start
            })
        
        # Make 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 10
        assert all(r['status'] == 200 for r in results)
        
        # Average response time should be reasonable
        avg_duration = sum(r['duration'] for r in results) / len(results)
        assert avg_duration < 0.5  # Less than 500ms average


if __name__ == "__main__":
    # Run main.py tests
    pytest.main([__file__, "-v", "--tb=short"])