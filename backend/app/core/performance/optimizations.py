"""
Critical path optimizations for Meridian Ephemeris.

This module contains optimized implementations of frequently used
calculations and provides performance-critical path alternatives.
"""

import time
import functools
import threading
from typing import Dict, Any, List, Optional, Callable, Tuple, Union
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

import numpy as np
import swisseph as swe

try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range

from extracted.systems.ephemeris_utils.const import SwePlanets, SweObjects
from extracted.systems.ephemeris_utils.classes.serialize import PlanetPosition
from extracted.systems.ephemeris_utils.tools.ephemeris import julian_day_from_datetime
from ..monitoring.metrics import get_metrics, timed_calculation


logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class PerformanceOptimizer:
    """Main performance optimization coordinator."""
    
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self._planet_cache = {}
        self._cache_lock = threading.RLock()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.thread_pool.shutdown(wait=True)


class OptimizedCalculations:
    """High-performance implementations of core calculations."""
    
    @staticmethod
    @jit(nopython=True if NUMBA_AVAILABLE else False)
    def fast_longitude_normalization(longitude: float) -> float:
        """Fast longitude normalization to 0-360 range."""
        while longitude < 0:
            longitude += 360.0
        while longitude >= 360:
            longitude -= 360.0
        return longitude
    
    @staticmethod
    @jit(nopython=True if NUMBA_AVAILABLE else False)
    def fast_sign_calculation(longitude: float) -> int:
        """Fast zodiac sign calculation."""
        normalized = longitude % 360.0
        return int(normalized // 30.0)
    
    @staticmethod
    @jit(nopython=True if NUMBA_AVAILABLE else False)
    def fast_degree_in_sign(longitude: float) -> float:
        """Fast calculation of degrees within zodiac sign."""
        return longitude % 30.0
    
    @staticmethod
    @jit(nopython=True if NUMBA_AVAILABLE else False, parallel=True if NUMBA_AVAILABLE else False)
    def batch_longitude_operations(longitudes: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Vectorized longitude operations for batch processing."""
        n = len(longitudes)
        normalized = np.zeros(n)
        signs = np.zeros(n, dtype=np.int32)
        degrees = np.zeros(n)
        
        for i in prange(n):
            # Normalize longitude
            lng = longitudes[i]
            while lng < 0:
                lng += 360.0
            while lng >= 360:
                lng -= 360.0
            normalized[i] = lng
            
            # Calculate sign and degree
            signs[i] = int(lng // 30.0)
            degrees[i] = lng % 30.0
        
        return normalized, signs, degrees
    
    @staticmethod
    @jit(nopython=True if NUMBA_AVAILABLE else False)
    def fast_julian_day(year: int, month: int, day: int, hour: float) -> float:
        """Optimized Julian day calculation."""
        if month <= 2:
            year -= 1
            month += 12
        
        a = int(year / 100)
        b = 2 - a + int(a / 4)
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        jd += hour / 24.0
        
        return jd


class ConcurrentCalculator:
    """Concurrent calculation engine for parallel processing."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (threading.active_count() or 1) + 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
    
    def calculate_planets_concurrent(self, julian_day: float, 
                                   planets: List[int]) -> Dict[int, PlanetPosition]:
        """Calculate multiple planets concurrently."""
        futures = {}
        
        # Submit all calculations
        for planet in planets:
            future = self.executor.submit(self._safe_planet_calculation, planet, julian_day)
            futures[planet] = future
        
        # Collect results
        results = {}
        for planet, future in futures.items():
            try:
                result = future.result(timeout=5.0)  # 5 second timeout per calculation
                if result:
                    results[planet] = result
            except Exception as e:
                logger.warning(f"Failed to calculate planet {planet}: {e}")
        
        return results
    
    def _safe_planet_calculation(self, planet: int, julian_day: float) -> Optional[PlanetPosition]:
        """Thread-safe planet calculation."""
        try:
            result = swe.calc_ut(julian_day, planet)
            longitude, latitude, distance, longitude_speed, latitude_speed, distance_speed = result[0]
            
            return PlanetPosition(
                longitude=float(longitude),
                latitude=float(latitude),
                distance=float(distance),
                longitude_speed=float(longitude_speed),
                latitude_speed=float(latitude_speed),
                distance_speed=float(distance_speed),
                retrograde=longitude_speed < 0
            )
        except Exception as e:
            logger.error(f"Error calculating planet {planet}: {e}")
            return None


class MemoryOptimizations:
    """Memory usage optimizations for large-scale processing."""
    
    @staticmethod
    def create_memory_pool(size: int = 1000):
        """Create a pre-allocated memory pool for frequent allocations."""
        return {
            'planet_positions': [None] * size,
            'calculation_results': [None] * size,
            'coordinate_arrays': [np.zeros(100) for _ in range(10)]
        }
    
    @staticmethod
    def optimize_array_operations(data: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """Convert list of dicts to structure of arrays for better memory access."""
        if not data:
            return {}
        
        # Extract all keys from first item
        keys = data[0].keys()
        arrays = {}
        
        for key in keys:
            values = [item.get(key) for item in data]
            # Try to convert to numpy array if all values are numeric
            try:
                if all(isinstance(v, (int, float)) for v in values if v is not None):
                    arrays[key] = np.array(values)
                else:
                    arrays[key] = values
            except (ValueError, TypeError):
                arrays[key] = values
        
        return arrays


class CacheOptimizations:
    """Advanced caching strategies for performance."""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache = {}
        self._access_order = []
        self._lock = threading.RLock()
    
    def get_or_calculate(self, key: str, calculation_func: Callable, *args, **kwargs):
        """Get cached result or calculate and cache."""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                return self._cache[key]
            
            # Calculate and cache
            result = calculation_func(*args, **kwargs)
            
            # Add to cache
            self._cache[key] = result
            self._access_order.append(key)
            
            # Evict oldest if necessary
            while len(self._cache) > self.max_size:
                oldest = self._access_order.pop(0)
                del self._cache[oldest]
            
            return result
    
    def warm_cache(self, calculations: List[Tuple[str, Callable, tuple, dict]]):
        """Pre-warm cache with common calculations."""
        for key, func, args, kwargs in calculations:
            if key not in self._cache:
                try:
                    self.get_or_calculate(key, func, *args, **kwargs)
                except Exception as e:
                    logger.warning(f"Failed to warm cache for {key}: {e}")


class BatchOptimizer:
    """Optimizations specifically for batch processing."""
    
    @staticmethod
    def optimize_batch_size(total_items: int, max_memory_mb: int = 100) -> int:
        """Calculate optimal batch size based on available memory."""
        # Estimate memory per item (rough calculation)
        estimated_memory_per_item = 0.01  # 10KB per calculation result
        max_items_in_memory = int((max_memory_mb * 1024 * 1024) / (estimated_memory_per_item * 1024 * 1024))
        
        # Choose batch size
        if total_items <= max_items_in_memory:
            return total_items
        
        # Find good batch size (power of 2 or multiple of 10)
        optimal_size = min(max_items_in_memory, 1000)
        
        # Round to nice numbers
        if optimal_size >= 100:
            optimal_size = (optimal_size // 100) * 100
        elif optimal_size >= 10:
            optimal_size = (optimal_size // 10) * 10
        
        return max(10, optimal_size)  # At least 10 items per batch
    
    @staticmethod
    def create_processing_chunks(items: List[Any], chunk_size: int) -> List[List[Any]]:
        """Split items into optimally-sized chunks for processing."""
        return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    
    @staticmethod
    def balance_workload(items: List[Any], num_workers: int) -> List[List[Any]]:
        """Balance workload across available workers."""
        chunk_size = max(1, len(items) // num_workers)
        remainder = len(items) % num_workers
        
        chunks = []
        start = 0
        
        for i in range(num_workers):
            # Add one extra item to first 'remainder' chunks
            current_chunk_size = chunk_size + (1 if i < remainder else 0)
            if start < len(items):
                chunks.append(items[start:start + current_chunk_size])
                start += current_chunk_size
        
        return [chunk for chunk in chunks if chunk]  # Remove empty chunks


# Performance monitoring and profiling utilities
class PerformanceProfiler:
    """Profiling utilities for performance analysis."""
    
    def __init__(self):
        self.profiles = {}
        self._lock = threading.Lock()
    
    def profile_function(self, name: str):
        """Decorator to profile function execution."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                start_memory = self._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    success = False
                    raise
                finally:
                    end_time = time.perf_counter()
                    end_memory = self._get_memory_usage()
                    
                    duration = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    self._record_profile(name, duration, memory_delta, success)
            
            return wrapper
        return decorator
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def _record_profile(self, name: str, duration: float, memory_delta: float, success: bool):
        """Record profiling data."""
        with self._lock:
            if name not in self.profiles:
                self.profiles[name] = {
                    'call_count': 0,
                    'total_duration': 0.0,
                    'total_memory': 0.0,
                    'success_count': 0,
                    'min_duration': float('inf'),
                    'max_duration': 0.0
                }
            
            profile = self.profiles[name]
            profile['call_count'] += 1
            profile['total_duration'] += duration
            profile['total_memory'] += memory_delta
            
            if success:
                profile['success_count'] += 1
            
            profile['min_duration'] = min(profile['min_duration'], duration)
            profile['max_duration'] = max(profile['max_duration'], duration)
    
    def get_profile_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary of all profiling data."""
        summary = {}
        
        with self._lock:
            for name, profile in self.profiles.items():
                if profile['call_count'] > 0:
                    summary[name] = {
                        'avg_duration': profile['total_duration'] / profile['call_count'],
                        'avg_memory': profile['total_memory'] / profile['call_count'],
                        'success_rate': profile['success_count'] / profile['call_count'],
                        'min_duration': profile['min_duration'],
                        'max_duration': profile['max_duration'],
                        'call_count': profile['call_count']
                    }
        
        return summary


# Global instances
_performance_optimizer = None
_profiler = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


def get_profiler() -> PerformanceProfiler:
    """Get global profiler instance."""
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler


# Convenience decorators
def optimize_performance(func: Callable) -> Callable:
    """Decorator to apply performance optimizations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with get_performance_optimizer():
            return func(*args, **kwargs)
    return wrapper


def profile_performance(name: str = None):
    """Decorator to profile function performance."""
    def decorator(func: Callable) -> Callable:
        profile_name = name or f"{func.__module__}.{func.__name__}"
        return get_profiler().profile_function(profile_name)(func)
    return decorator