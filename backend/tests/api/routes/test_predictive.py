"""
Integration Tests for Predictive API Routes

Comprehensive integration testing for all predictive astrology API endpoints
including eclipse predictions, transit calculations, and optimization features.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from app.main import app
from extracted.systems.predictive_models import (
    SolarEclipse, LunarEclipse, Transit, SignIngress, EclipseVisibility,
    EclipseType, LunarEclipseType, RetrogradeStatus, GeographicLocation
)
from extracted.services.predictive_service import predictive_service


class TestEclipseAPIEndpoints:
    """Integration tests for eclipse API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)
    
    def test_find_next_solar_eclipse_success(self, client):
        """Test successful solar eclipse search."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z",
            "eclipse_type": "total"
        }
        
        with patch.object(predictive_service, 'find_next_solar_eclipse') as mock_service:
            mock_eclipse = SolarEclipse(
                eclipse_type=EclipseType.TOTAL,
                maximum_eclipse_time=datetime(2024, 4, 8, 18, 17, 16),
                eclipse_magnitude=1.0566,
                eclipse_obscuration=100.0,
                saros_series=139,
                gamma=0.3431
            )
            mock_service.return_value = mock_eclipse
            
            response = client.post("/v2/eclipses/next-solar", json=request_data)
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert data["eclipse"] is not None
            assert "metadata" in data
            assert data["metadata"]["nasa_validated"] is True
    
    def test_find_next_solar_eclipse_no_result(self, client):
        """Test solar eclipse search with no results."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(predictive_service, 'find_next_solar_eclipse') as mock_service:
            mock_service.return_value = None
            
            response = client.post("/v2/eclipses/next-solar", json=request_data)
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert data["eclipse"] is None
            assert "No solar eclipse found" in data["message"]
    
    def test_find_next_solar_eclipse_invalid_type(self, client):
        """Test solar eclipse search with invalid eclipse type."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z",
            "eclipse_type": "invalid_type"
        }
        
        response = client.post("/v2/eclipses/next-solar", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "Invalid eclipse type" in data["message"]
    
    def test_find_next_lunar_eclipse_success(self, client):
        """Test successful lunar eclipse search."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z",
            "eclipse_type": "partial"
        }
        
        with patch.object(predictive_service, 'find_next_lunar_eclipse') as mock_service:
            mock_eclipse = LunarEclipse(
                eclipse_type=LunarEclipseType.PARTIAL,
                maximum_eclipse_time=datetime(2024, 9, 18, 2, 44, 3),
                eclipse_magnitude=0.0855,
                penumbral_magnitude=1.1025,
                umbral_duration=45.2,
                penumbral_duration=268.7
            )
            mock_service.return_value = mock_eclipse
            
            response = client.post("/v2/eclipses/next-lunar", json=request_data)
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert data["eclipse"] is not None
    
    def test_find_next_lunar_eclipse_invalid_type(self, client):
        """Test lunar eclipse search with invalid eclipse type."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z",
            "eclipse_type": "total_solar"  # Invalid for lunar eclipse
        }
        
        response = client.post("/v2/eclipses/next-lunar", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
    
    def test_search_eclipses_success(self, client):
        """Test successful eclipse range search."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-12-31T23:59:59Z",
            "eclipse_types": ["total", "partial"]
        }
        
        with patch.object(predictive_service, 'search_eclipses_in_range') as mock_service:
            mock_solar = SolarEclipse(
                eclipse_type=EclipseType.TOTAL,
                maximum_eclipse_time=datetime(2024, 4, 8, 18, 17, 16),
                eclipse_magnitude=1.0566,
                eclipse_obscuration=100.0
            )
            mock_lunar = LunarEclipse(
                eclipse_type=LunarEclipseType.PARTIAL,
                maximum_eclipse_time=datetime(2024, 9, 18, 2, 44, 3),
                eclipse_magnitude=0.0855,
                penumbral_magnitude=1.1025
            )
            mock_service.return_value = {
                "solar": [mock_solar],
                "lunar": [mock_lunar]
            }
            
            response = client.post("/v2/eclipses/search", json=request_data)
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert data["total_count"] == 2
            assert data["search_range_years"] == 1.0
    
    def test_search_eclipses_invalid_date_range(self, client):
        """Test eclipse search with invalid date range."""
        request_data = {
            "start_date": "2024-12-31T00:00:00Z",
            "end_date": "2024-01-01T00:00:00Z"  # End before start
        }
        
        response = client.post("/v2/eclipses/search", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "End date must be after start date" in data["message"]
    
    def test_search_eclipses_range_too_large(self, client):
        """Test eclipse search with date range too large."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2040-01-01T00:00:00Z"  # 16 years - too large
        }
        
        response = client.post("/v2/eclipses/search", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "range too large" in data["message"]
    
    def test_calculate_eclipse_visibility_success(self, client):
        """Test successful eclipse visibility calculation."""
        request_data = {
            "eclipse_time": "2024-04-08T18:17:16Z",
            "eclipse_type": "solar",
            "location": {
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "elevation": 10.0
            }
        }
        
        with patch.object(predictive_service, 'calculate_eclipse_visibility') as mock_service:
            mock_visibility = EclipseVisibility(
                is_visible=True,
                eclipse_type_at_location="partial",
                maximum_eclipse_time=datetime(2024, 4, 8, 18, 17, 16),
                eclipse_magnitude_at_location=0.85,
                contact_times={
                    "first_contact": datetime(2024, 4, 8, 17, 15, 0),
                    "maximum_eclipse": datetime(2024, 4, 8, 18, 17, 16),
                    "last_contact": datetime(2024, 4, 8, 19, 20, 0)
                },
                sun_altitude_at_maximum=45.0,
                sun_azimuth_at_maximum=180.0
            )
            mock_service.return_value = mock_visibility
            
            response = client.post("/v2/eclipses/visibility", json=request_data)
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert data["visibility"] is not None
    
    def test_calculate_eclipse_visibility_invalid_type(self, client):
        """Test eclipse visibility with invalid eclipse type."""
        request_data = {
            "eclipse_time": "2024-04-08T18:17:16Z",
            "eclipse_type": "invalid",
            "location": {
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060}
            }
        }
        
        response = client.post("/v2/eclipses/visibility", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"


class TestTransitAPIEndpoints:
    """Integration tests for transit API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)
    
    def test_calculate_planet_transit_success(self, client):
        """Test successful planet transit calculation."""
        request_data = {
            "planet_name": "Mars",
            "target_degree": 90.0,
            "start_date": "2024-01-01T00:00:00Z",
            "max_crossings": 1
        }
        
        with patch.object(predictive_service, 'find_planet_transit') as mock_service:
            mock_transit = Transit(
                planet_id=4,  # Mars
                planet_name="Mars",
                target_longitude=90.0,
                exact_time=datetime(2024, 6, 15, 12, 0, 0),
                is_retrograde=False,
                transit_speed=0.5,
                approach_duration=30.0,
                separation_duration=30.0
            )
            mock_service.return_value = [mock_transit]
            
            response = client.post("/v2/transits/planet-to-degree", json=request_data)
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert data["total_count"] == 1
            assert len(data["transits"]) == 1
    
    def test_calculate_planet_transit_invalid_planet(self, client):
        """Test planet transit with invalid planet name."""
        request_data = {
            "planet_name": "InvalidPlanet",
            "target_degree": 90.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        response = client.post("/v2/transits/planet-to-degree", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "Invalid planet name" in data["message"]
    
    def test_calculate_planet_transit_invalid_degree(self, client):
        """Test planet transit with invalid target degree."""
        request_data = {
            "planet_name": "Mars",
            "target_degree": 500.0,  # Invalid - must be 0-360
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        response = client.post("/v2/transits/planet-to-degree", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "Target degree must be between 0 and 360" in data["message"]
    
    def test_calculate_sign_ingresses_success(self, client):
        """Test successful sign ingress calculation."""
        request_data = {
            "planet_names": ["Jupiter", "Saturn"],
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2025-01-01T00:00:00Z"
        }
        
        with patch.object(predictive_service, 'find_sign_ingresses') as mock_service:
            mock_jupiter_ingress = SignIngress(
                planet_id=5,
                planet_name="Jupiter",
                from_sign="Taurus",
                to_sign="Gemini",
                ingress_time=datetime(2024, 5, 26, 8, 15, 0),
                retrograde_status=RetrogradeStatus.DIRECT
            )
            mock_saturn_ingress = SignIngress(
                planet_id=6,
                planet_name="Saturn",
                from_sign="Pisces",
                to_sign="Aries",
                ingress_time=datetime(2025, 5, 25, 15, 30, 0),
                retrograde_status=RetrogradeStatus.DIRECT
            )
            mock_service.return_value = {
                "Jupiter": [mock_jupiter_ingress],
                "Saturn": [mock_saturn_ingress]
            }
            
            response = client.post("/v2/transits/sign-ingresses", json=request_data)
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert data["total_count"] == 2
            assert "Jupiter" in data["ingresses"]
            assert "Saturn" in data["ingresses"]
    
    def test_calculate_sign_ingresses_invalid_planet(self, client):
        """Test sign ingresses with invalid planet name."""
        request_data = {
            "planet_names": ["Jupiter", "InvalidPlanet"],
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2025-01-01T00:00:00Z"
        }
        
        response = client.post("/v2/transits/sign-ingresses", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "Invalid planet names" in data["message"]
    
    def test_search_transits_success(self, client):
        """Test successful general transit search."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-06-01T00:00:00Z",
            "planet_names": ["Mars"],
            "target_degrees": [0.0, 90.0, 180.0, 270.0],
            "search_criteria": {
                "include_retrograde": True,
                "orb_degrees": 1.0
            }
        }
        
        with patch.object(predictive_service, 'search_transits') as mock_service:
            mock_transit = Transit(
                planet_id=4,
                planet_name="Mars",
                target_longitude=0.0,
                exact_time=datetime(2024, 3, 15, 6, 30, 0),
                is_retrograde=False,
                transit_speed=0.5,
                approach_duration=5.0,
                separation_duration=5.0
            )
            mock_service.return_value = {
                "transits": [mock_transit],
                "ingresses": [],
                "stations": [],
                "metadata": {
                    "search_range_days": 151,
                    "planets_searched": ["Mars"],
                    "degrees_searched": [0.0, 90.0, 180.0, 270.0],
                    "total_results": 1
                }
            }
            
            response = client.post("/v2/transits/search", json=request_data)
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert "results" in data
            assert data["search_range_years"] == pytest.approx(0.4, rel=0.1)
    
    def test_search_transits_invalid_date_range(self, client):
        """Test transit search with invalid date range."""
        request_data = {
            "start_date": "2024-06-01T00:00:00Z",
            "end_date": "2024-01-01T00:00:00Z"  # End before start
        }
        
        response = client.post("/v2/transits/search", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "End date must be after start date" in data["message"]
    
    def test_search_transits_range_too_large(self, client):
        """Test transit search with date range too large."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2030-01-01T00:00:00Z"  # 6 years - too large for transit search
        }
        
        response = client.post("/v2/transits/search", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
        assert data["error"] == "validation_error"
        assert "range too large" in data["message"]


class TestOptimizationAPIEndpoints:
    """Integration tests for optimization and performance endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client fixture.""" 
        return TestClient(app)
    
    def test_get_optimization_status_success(self, client):
        """Test successful optimization status retrieval."""
        with patch.object(predictive_service, 'get_optimization_status') as mock_service:
            mock_service.return_value = {
                'performance_metrics': {
                    'cache_hit_rate': 0.73,
                    'memory_usage_mb': 42.8,
                    'l1_cache_size': 150,
                    'recent_computation_time_ms': 45.2
                },
                'optimization_status': {
                    'vectorization_enabled': True,
                    'intelligent_caching_enabled': True,
                    'parallel_processing_enabled': True,
                    'memory_optimization_enabled': True,
                    'redis_cache_enabled': True
                },
                'recommendations': ['System is well optimized'],
                'system_info': {
                    'max_workers': 4,
                    'cache_memory_limit_mb': 100.0,
                    'optimization_level': 'production'
                }
            }
            
            response = client.get("/v2/optimization/status")
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert "optimization_status" in data
            assert "features" in data
            assert "performance_targets" in data
    
    def test_clear_optimization_cache_success(self, client):
        """Test successful optimization cache clearing."""
        with patch.object(predictive_service, 'clear_optimization_cache') as mock_service:
            mock_service.return_value = True
            
            response = client.post("/v2/optimization/clear-cache")
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert "cache cleared" in data["message"]
            assert "cache_types_available" in data
    
    def test_clear_optimization_cache_with_type(self, client):
        """Test optimization cache clearing with specific cache type."""
        with patch.object(predictive_service, 'clear_optimization_cache') as mock_service:
            mock_service.return_value = True
            
            response = client.post("/v2/optimization/clear-cache?cache_type=eclipse_search")
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert "eclipse_search" in data["message"]
    
    def test_clear_optimization_cache_failure(self, client):
        """Test optimization cache clearing failure."""
        with patch.object(predictive_service, 'clear_optimization_cache') as mock_service:
            mock_service.return_value = False
            
            response = client.post("/v2/optimization/clear-cache")
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is False
            assert data["error"] == "cache_clear_failed"
    
    def test_get_performance_benchmarks(self, client):
        """Test performance benchmarks endpoint."""
        response = client.get("/v2/optimization/benchmarks")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["success"] is True
        assert "benchmarks" in data
        assert "eclipse_calculations" in data["benchmarks"]
        assert "transit_calculations" in data["benchmarks"]
        assert "optimization_effectiveness" in data
        assert "production_readiness" in data


class TestHealthAndInfoEndpoints:
    """Integration tests for health and information endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)
    
    def test_predictive_health_check(self, client):
        """Test predictive service health check."""
        response = client.get("/v2/health")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["success"] is True
        assert data["service"] == "predictive_astrology"
        assert "features" in data
        assert "capabilities" in data
        assert "performance_targets" in data
    
    def test_rate_limits_info(self, client):
        """Test rate limits information endpoint."""
        response = client.get("/v2/rate-limits")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["success"] is True
        assert "rate_limits" in data
        assert "eclipse_searches" in data["rate_limits"]
        assert "transit_calculations" in data["rate_limits"]
        assert "batch_operations" in data["rate_limits"]
        assert "recommendations" in data


class TestAPIErrorHandling:
    """Tests for API error handling and edge cases."""
    
    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON in request."""
        response = client.post("/v2/eclipses/next-solar", data="invalid json")
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        request_data = {
            # Missing start_date
            "eclipse_type": "total"
        }
        
        response = client.post("/v2/eclipses/next-solar", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False
    
    def test_service_error_handling(self, client):
        """Test handling of service layer errors."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(predictive_service, 'find_next_solar_eclipse') as mock_service:
            mock_service.side_effect = Exception("Service error")
            
            response = client.post("/v2/eclipses/next-solar", json=request_data)
            
            assert response.status_code == 500
            data = response.model_dump_json()
            assert data["success"] is False
            assert data["error"] == "internal_server_error"
    
    def test_invalid_date_format(self, client):
        """Test handling of invalid date formats."""
        request_data = {
            "start_date": "invalid-date-format"
        }
        
        response = client.post("/v2/eclipses/next-solar", json=request_data)
        
        assert response.status_code == 422
        data = response.model_dump_json()
        assert data["success"] is False


class TestAPIPerformance:
    """Performance tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)
    
    @pytest.mark.benchmark(group="api_performance")
    def test_eclipse_endpoint_performance(self, benchmark, client):
        """Benchmark eclipse endpoint performance."""
        request_data = {
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(predictive_service, 'find_next_solar_eclipse') as mock_service:
            mock_eclipse = SolarEclipse(
                eclipse_type=EclipseType.TOTAL,
                maximum_eclipse_time=datetime(2024, 4, 8, 18, 17, 16),
                eclipse_magnitude=1.0566,
                eclipse_obscuration=100.0
            )
            mock_service.return_value = mock_eclipse
            
            def api_call():
                return client.post("/v2/eclipses/next-solar", json=request_data)
            
            response = benchmark(api_call)
            assert response.status_code == 200
    
    @pytest.mark.benchmark(group="api_performance")
    def test_transit_endpoint_performance(self, benchmark, client):
        """Benchmark transit endpoint performance."""
        request_data = {
            "planet_name": "Mars",
            "target_degree": 90.0,
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(predictive_service, 'find_planet_transit') as mock_service:
            mock_transit = Transit(
                planet_id=4,
                planet_name="Mars",
                target_longitude=90.0,
                exact_time=datetime(2024, 6, 15, 12, 0, 0),
                is_retrograde=False,
                transit_speed=0.5,
                approach_duration=30.0,
                separation_duration=30.0
            )
            mock_service.return_value = [mock_transit]
            
            def api_call():
                return client.post("/v2/transits/planet-to-degree", json=request_data)
            
            response = benchmark(api_call)
            assert response.status_code == 200


# Test configuration for integration tests
@pytest.mark.asyncio
class TestAsyncAPIBehavior:
    """Test async behavior of API endpoints."""
    
    async def test_concurrent_eclipse_requests(self):
        """Test handling of concurrent eclipse requests."""
        client = TestClient(app)
        
        request_data = {
            "start_date": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(predictive_service, 'find_next_solar_eclipse') as mock_service:
            mock_eclipse = SolarEclipse(
                eclipse_type=EclipseType.TOTAL,
                maximum_eclipse_time=datetime(2024, 4, 8, 18, 17, 16),
                eclipse_magnitude=1.0566,
                eclipse_obscuration=100.0
            )
            mock_service.return_value = mock_eclipse
            
            # Make concurrent requests
            tasks = []
            for _ in range(5):
                task = asyncio.create_task(
                    asyncio.to_thread(
                        client.post, "/v2/eclipses/next-solar", json=request_data
                    )
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.model_dump_json()
                assert data["success"] is True


# Mark for different test categories
pytest.mark.api_integration = pytest.mark.api_integration
pytest.mark.api_performance = pytest.mark.api_performance