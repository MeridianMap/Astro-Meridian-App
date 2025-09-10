"""
Prometheus metrics collection for Meridian Ephemeris API.

This module provides comprehensive monitoring of API performance,
cache hit rates, calculation times, and system health.
"""

import time
import functools
from typing import Dict, Any, Optional, Callable
import logging

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Dummy classes for when Prometheus is not available
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
    
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def time(self): return self
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def observe(self, *args): pass
    
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args): pass
        def inc(self, *args): pass
        def dec(self, *args): pass
    
    class Info:
        def __init__(self, *args, **kwargs): pass
        def info(self, *args): pass

    class Instrumentator:
        @staticmethod
        def instrument(app): return app
        def expose(self, *args, **kwargs): pass


logger = logging.getLogger(__name__)


class MeridianMetrics:
    """Centralized metrics collection for Meridian Ephemeris."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and PROMETHEUS_AVAILABLE
        
        if not self.enabled:
            logger.warning("Metrics collection is disabled (Prometheus not available)")
            return
        
        # API Request Metrics
        self.api_requests_total = Counter(
            'meridian_api_requests_total',
            'Total number of API requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.api_request_duration = Histogram(
            'meridian_api_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint']
        )
        
        # Ephemeris Calculation Metrics
        self.calculations_total = Counter(
            'meridian_calculations_total',
            'Total number of ephemeris calculations',
            ['calculation_type', 'success']
        )
        
        self.calculation_duration = Histogram(
            'meridian_calculation_duration_seconds',
            'Calculation duration in seconds',
            ['calculation_type'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
        )
        
        # Cache Metrics
        self.cache_operations_total = Counter(
            'meridian_cache_operations_total',
            'Total cache operations',
            ['operation', 'cache_type', 'result']
        )
        
        self.cache_hit_rate = Gauge(
            'meridian_cache_hit_rate',
            'Cache hit rate percentage',
            ['cache_type']
        )
        
        self.cache_size = Gauge(
            'meridian_cache_size_items',
            'Number of items in cache',
            ['cache_type']
        )
        
        # Swiss Ephemeris Metrics
        self.swiss_ephemeris_calls = Counter(
            'meridian_swiss_ephemeris_calls_total',
            'Total Swiss Ephemeris function calls',
            ['function_name', 'success']
        )
        
        self.swiss_ephemeris_duration = Histogram(
            'meridian_swiss_ephemeris_duration_seconds',
            'Swiss Ephemeris call duration',
            ['function_name']
        )
        
        # Batch Processing Metrics
        self.batch_calculations_total = Counter(
            'meridian_batch_calculations_total',
            'Total batch calculations processed',
            ['batch_size_range']
        )
        
        self.batch_processing_duration = Histogram(
            'meridian_batch_processing_duration_seconds',
            'Batch processing duration',
            ['batch_size_range']
        )
        
        self.batch_success_rate = Gauge(
            'meridian_batch_success_rate',
            'Batch calculation success rate',
            ['batch_size_range']
        )
        
        # System Health Metrics
        self.system_health = Gauge(
            'meridian_system_health',
            'System health status (1=healthy, 0=unhealthy)',
            ['component']
        )
        
        self.active_connections = Gauge(
            'meridian_active_connections',
            'Number of active connections'
        )
        
        # Error Metrics
        self.errors_total = Counter(
            'meridian_errors_total',
            'Total number of errors',
            ['error_type', 'endpoint']
        )
        
        # Application Info
        self.app_info = Info(
            'meridian_app_info',
            'Application information'
        )
        
        logger.info("Prometheus metrics initialized successfully")
    
    def record_api_request(self, method: str, endpoint: str, 
                          status_code: int, duration: float):
        """Record API request metrics."""
        if not self.enabled:
            return
        
        self.api_requests_total.labels(
            method=method, 
            endpoint=endpoint, 
            status_code=status_code
        ).inc()
        
        self.api_request_duration.labels(
            method=method, 
            endpoint=endpoint
        ).observe(duration)
    
    def record_calculation(self, calc_type: str, duration: float, success: bool):
        """Record ephemeris calculation metrics."""
        if not self.enabled:
            return
        
        self.calculations_total.labels(
            calculation_type=calc_type,
            success=str(success).lower()
        ).inc()
        
        if success:
            self.calculation_duration.labels(
                calculation_type=calc_type
            ).observe(duration)
    
    def record_cache_operation(self, operation: str, cache_type: str, 
                             result: str, duration: Optional[float] = None):
        """Record cache operation metrics."""
        if not self.enabled:
            return
        
        self.cache_operations_total.labels(
            operation=operation,
            cache_type=cache_type,
            result=result
        ).inc()
    
    def update_cache_hit_rate(self, cache_type: str, hit_rate: float):
        """Update cache hit rate metrics."""
        if not self.enabled:
            return
        
        self.cache_hit_rate.labels(cache_type=cache_type).set(hit_rate * 100)
    
    def update_cache_size(self, cache_type: str, size: int):
        """Update cache size metrics."""
        if not self.enabled:
            return
        
        self.cache_size.labels(cache_type=cache_type).set(size)
    
    def record_swiss_ephemeris_call(self, function_name: str, 
                                   duration: float, success: bool):
        """Record Swiss Ephemeris function call metrics."""
        if not self.enabled:
            return
        
        self.swiss_ephemeris_calls.labels(
            function_name=function_name,
            success=str(success).lower()
        ).inc()
        
        if success:
            self.swiss_ephemeris_duration.labels(
                function_name=function_name
            ).observe(duration)
    
    def record_batch_processing(self, batch_size: int, duration: float, 
                              success_rate: float):
        """Record batch processing metrics."""
        if not self.enabled:
            return
        
        # Categorize batch size
        if batch_size <= 10:
            size_range = "small"
        elif batch_size <= 100:
            size_range = "medium"
        elif batch_size <= 1000:
            size_range = "large"
        else:
            size_range = "xlarge"
        
        self.batch_calculations_total.labels(
            batch_size_range=size_range
        ).inc()
        
        self.batch_processing_duration.labels(
            batch_size_range=size_range
        ).observe(duration)
        
        self.batch_success_rate.labels(
            batch_size_range=size_range
        ).set(success_rate * 100)
    
    def update_system_health(self, component: str, healthy: bool):
        """Update system health status."""
        if not self.enabled:
            return
        
        self.system_health.labels(component=component).set(1 if healthy else 0)
    
    def record_error(self, error_type: str, endpoint: str):
        """Record error occurrence."""
        if not self.enabled:
            return
        
        self.errors_total.labels(
            error_type=error_type,
            endpoint=endpoint
        ).inc()
    
    def set_app_info(self, info: Dict[str, str]):
        """Set application information."""
        if not self.enabled:
            return
        
        self.app_info.info(info)
    
    def update_active_connections(self, count: int):
        """Update active connection count."""
        if not self.enabled:
            return
        
        self.active_connections.set(count)


# Global metrics instance
_metrics = None


def get_metrics() -> MeridianMetrics:
    """Get global metrics instance."""
    global _metrics
    if _metrics is None:
        _metrics = MeridianMetrics()
    return _metrics


# Decorators for automatic metrics collection
def timed_calculation(calculation_type: str):
    """Decorator to time ephemeris calculations."""
    def decorator(func: Callable) -> Callable:
        import asyncio
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            success = False
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception:
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_calculation(calculation_type, duration, success)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception:
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_calculation(calculation_type, duration, success)
        
        # Check if the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def timed_swiss_ephemeris(function_name: str):
    """Decorator to time Swiss Ephemeris function calls."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception:
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_swiss_ephemeris_call(function_name, duration, success)
        
        return wrapper
    return decorator


def cache_metric(cache_type: str):
    """Decorator to record cache operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            operation = func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Determine result type
                if operation == 'get':
                    result_type = 'hit' if result is not None else 'miss'
                else:
                    result_type = 'success'
                
                duration = time.time() - start_time
                metrics.record_cache_operation(operation, cache_type, result_type, duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_cache_operation(operation, cache_type, 'error', duration)
                raise
        
        return wrapper
    return decorator


# FastAPI instrumentator setup
def setup_metrics_middleware(app):
    """Set up Prometheus metrics middleware for FastAPI."""
    if not PROMETHEUS_AVAILABLE:
        logger.warning("Prometheus not available, skipping metrics middleware setup")
        return app
    
    try:
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/docs", "/redoc", "/openapi.json", "/favicon.ico"],
            env_var_name="ENABLE_METRICS",
            inprogress_name="meridian_requests_inprogress",
            inprogress_labels=True,
        )
        
        instrumentator.instrument(app)
        instrumentator.expose(app, endpoint="/metrics")
        
        logger.info("Prometheus metrics middleware set up successfully")
        
    except Exception as e:
        logger.error(f"Failed to set up metrics middleware: {e}")
    
    return app


# Health check integration
def update_health_metrics():
    """Update system health metrics."""
    metrics = get_metrics()
    
    # Check various system components
    try:
        # Check Redis connection
        from ..ephemeris.classes.redis_cache import get_redis_cache
        redis_cache = get_redis_cache()
        redis_healthy = redis_cache.enabled
        metrics.update_system_health("redis", redis_healthy)
        
        # Check Swiss Ephemeris availability
        import swisseph as swe
        try:
            swe.julday(2000, 1, 1, 12.0)  # Simple test calculation
            metrics.update_system_health("swiss_ephemeris", True)
        except:
            metrics.update_system_health("swiss_ephemeris", False)
        
        # Update cache statistics
        if redis_healthy:
            cache_info = redis_cache.get_info()
            if 'hit_rate' in cache_info:
                metrics.update_cache_hit_rate("redis", cache_info['hit_rate'])
    
    except Exception as e:
        logger.error(f"Error updating health metrics: {e}")


# Utility functions for manual metric collection
def track_active_connections(count: int):
    """Track active connection count."""
    get_metrics().update_active_connections(count)


def track_error(error_type: str, endpoint: str):
    """Track error occurrence."""
    get_metrics().record_error(error_type, endpoint)