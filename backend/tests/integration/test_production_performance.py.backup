"""
Integration tests for production performance optimization system.

Tests complete workflow of production-ready performance features including:
- Connection pooling and resource management
- Request deduplication and circuit breakers
- Auto-scaling triggers and system health monitoring
- End-to-end performance validation
"""

import pytest
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.performance.production_optimization import (
    get_production_optimizer,
    ProductionOptimizationManager
)


class TestProductionPerformanceIntegration:
    """Integration tests for production performance optimization."""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        return TestClient(app)
    
    @pytest.fixture
    async def production_optimizer(self):
        """Production optimizer instance."""
        optimizer = get_production_optimizer()
        await optimizer.initialize()
        yield optimizer
        await optimizer.shutdown()
    
    def test_production_middleware_integration(self, client):
        """Test production middleware is properly integrated."""
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check for production optimization headers
        headers = response.headers
        assert "X-Request-ID" in headers or "Request-ID" in headers
        
    @pytest.mark.asyncio
    async def test_connection_pool_management(self, production_optimizer):
        """Test connection pool creation and management."""
        # Verify connection pool is created
        assert hasattr(production_optimizer, 'connection_pools')
        
        # Test pool acquisition
        pool_config = {
            'min_connections': 5,
            'max_connections': 20,
            'connection_timeout': 5.0
        }
        
        pool = await production_optimizer._create_connection_pool(
            "test_service", pool_config
        )
        assert pool is not None
        
    def test_request_deduplication(self, client):
        """Test request deduplication functionality."""
        # Make identical requests simultaneously
        def make_request():
            return client.post("/ephemeris/natal", json={
                "subject": {
                    "name": "Test Subject",
                    "datetime": {"iso_string": "2000-01-01T12:00:00"},
                    "latitude": {"decimal": 40.7128},
                    "longitude": {"decimal": -74.0060},
                    "timezone": {"name": "America/New_York"}
                }
            })
        
        # Execute multiple identical requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in as_completed(futures)]
        
        # All requests should succeed (deduplication should work silently)
        assert all(response.status_code == 200 for response in responses)
        
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, production_optimizer):
        """Test circuit breaker protection."""
        # Simulate service failures
        service_name = "test_service"
        
        # Record failures to trigger circuit breaker
        for _ in range(6):  # Exceed failure threshold
            await production_optimizer._record_service_failure(service_name)
        
        # Circuit breaker should be open
        is_open = await production_optimizer._is_circuit_breaker_open(service_name)
        assert is_open
        
    def test_concurrent_request_handling(self, client):
        """Test system handles high concurrent load."""
        num_requests = 50
        max_workers = 10
        
        def make_natal_request(i):
            return client.post("/ephemeris/natal", json={
                "subject": {
                    "name": f"Subject {i}",
                    "datetime": {"iso_string": "2000-01-01T12:00:00"},
                    "latitude": {"decimal": 40.7128 + (i % 10) * 0.01},
                    "longitude": {"decimal": -74.0060 + (i % 10) * 0.01},
                    "timezone": {"name": "America/New_York"}
                }
            })
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(make_natal_request, i) 
                for i in range(num_requests)
            ]
            
            responses = []
            for future in as_completed(futures):
                try:
                    response = future.result(timeout=10)  # 10s timeout
                    responses.append(response)
                except Exception as e:
                    pytest.fail(f"Request failed: {e}")
        
        total_time = time.time() - start_time
        
        # Verify all requests succeeded
        success_responses = [r for r in responses if r.status_code == 200]
        success_rate = len(success_responses) / len(responses)
        
        assert success_rate >= 0.95, f"Success rate too low: {success_rate}"
        assert total_time < 30, f"Total time too high: {total_time}s"
        
        # Verify average response time is reasonable
        avg_response_time = total_time / num_requests
        assert avg_response_time < 0.6, f"Average response time too high: {avg_response_time}s"
        
    @pytest.mark.asyncio
    async def test_auto_scaling_triggers(self, production_optimizer):
        """Test auto-scaling trigger detection."""
        # Simulate high CPU usage
        metrics = {
            'cpu_percent': 85.0,
            'memory_percent': 60.0,
            'response_time_p95': 120.0,  # ms
            'active_connections': 150
        }
        
        should_scale = await production_optimizer._should_trigger_scaling(metrics)
        assert should_scale
        
        # Simulate normal conditions
        metrics = {
            'cpu_percent': 45.0,
            'memory_percent': 40.0,
            'response_time_p95': 50.0,  # ms
            'active_connections': 50
        }
        
        should_scale = await production_optimizer._should_trigger_scaling(metrics)
        assert not should_scale
        
    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, production_optimizer):
        """Test comprehensive system health monitoring."""
        health_report = await production_optimizer.get_system_health()
        
        # Verify health report structure
        assert 'system_metrics' in health_report
        assert 'service_status' in health_report
        assert 'performance_metrics' in health_report
        assert 'alert_status' in health_report
        
        # Verify metrics are reasonable
        system_metrics = health_report['system_metrics']
        assert 0 <= system_metrics['cpu_percent'] <= 100
        assert 0 <= system_metrics['memory_percent'] <= 100
        assert system_metrics['disk_usage_percent'] >= 0
        
    def test_performance_middleware_headers(self, client):
        """Test performance middleware adds appropriate headers."""
        response = client.get("/health")
        
        headers = response.headers
        
        # Check for performance-related headers
        assert "X-Process-Time" in headers
        
        # Verify process time is reasonable
        process_time = float(headers["X-Process-Time"])
        assert 0 < process_time < 1.0  # Should be sub-second
        
    @pytest.mark.asyncio
    async def test_resource_cleanup(self, production_optimizer):
        """Test proper resource cleanup and shutdown."""
        # Verify clean shutdown
        await production_optimizer.shutdown()
        
        # Verify resources are cleaned up
        assert production_optimizer._shutdown_complete.is_set()
        
    def test_production_optimization_end_to_end(self, client):
        """End-to-end test of production optimization features."""
        # Test complex calculation that exercises all optimizations
        response = client.post("/ephemeris/natal", json={
            "subject": {
                "name": "Production Test",
                "datetime": {"iso_string": "1990-06-15T14:30:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"name": "America/New_York"}
            },
            "options": {
                "house_system": "placidus",
                "include_aspects": True,
                "aspect_orbs": {
                    "sun": 8.0,
                    "moon": 8.0,
                    "mercury": 6.0,
                    "venus": 6.0,
                    "mars": 6.0,
                    "jupiter": 6.0,
                    "saturn": 6.0,
                    "uranus": 4.0,
                    "neptune": 4.0,
                    "pluto": 4.0
                }
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data
        
        # Verify performance metadata
        metadata = data["metadata"]
        assert "processing_time_ms" in metadata
        
        processing_time = metadata["processing_time_ms"]
        assert processing_time < 100  # Sub-100ms target


class TestProductionOptimizationStress:
    """Stress tests for production optimization system."""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        return TestClient(app)
    
    @pytest.mark.slow
    def test_sustained_load_handling(self, client):
        """Test system handles sustained load over time."""
        duration = 30  # 30 second test
        requests_per_second = 10
        
        def make_request():
            return client.post("/ephemeris/natal", json={
                "subject": {
                    "name": "Load Test",
                    "datetime": {"iso_string": "2000-01-01T12:00:00"},
                    "latitude": {"decimal": 40.7128},
                    "longitude": {"decimal": -74.0060},
                    "timezone": {"name": "America/New_York"}
                }
            })
        
        start_time = time.time()
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        while time.time() - start_time < duration:
            batch_start = time.time()
            
            # Make requests for this second
            with ThreadPoolExecutor(max_workers=requests_per_second) as executor:
                futures = [
                    executor.submit(make_request) 
                    for _ in range(requests_per_second)
                ]
                
                for future in as_completed(futures):
                    try:
                        response = future.result(timeout=5)
                        if response.status_code == 200:
                            successful_requests += 1
                        else:
                            failed_requests += 1
                    except Exception:
                        failed_requests += 1
            
            # Wait for next second
            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
        
        # Verify system maintained performance
        total_requests = successful_requests + failed_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        assert success_rate >= 0.95, f"Success rate too low: {success_rate}"
        assert successful_requests > duration * requests_per_second * 0.8, \
               "Throughput too low"
        
    @pytest.mark.slow
    def test_memory_stability_under_load(self, client):
        """Test memory remains stable under sustained load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run load test
        for batch in range(10):  # 10 batches
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [
                    executor.submit(
                        client.post,
                        "/ephemeris/natal",
                        json={
                            "subject": {
                                "name": f"Memory Test {batch}-{i}",
                                "datetime": {"iso_string": "2000-01-01T12:00:00"},
                                "latitude": {"decimal": 40.7128 + i * 0.01},
                                "longitude": {"decimal": -74.0060 + i * 0.01},
                                "timezone": {"name": "America/New_York"}
                            }
                        }
                    )
                    for i in range(50)
                ]
                
                for future in as_completed(futures):
                    future.result(timeout=10)
            
            # Check memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = current_memory - initial_memory
            
            # Memory growth should be reasonable (< 50MB per batch)
            assert memory_growth < 50 * (batch + 1), \
                   f"Excessive memory growth: {memory_growth}MB"
        
        # Final memory check
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_growth = final_memory - initial_memory
        
        # Total memory growth should be reasonable (< 200MB for entire test)
        assert total_growth < 200, f"Total memory growth too high: {total_growth}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])