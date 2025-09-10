"""
Memory Optimization System
Comprehensive memory management with object pools, leak prevention, and optimization.

Features:
- Memory usage monitoring and profiling
- Object pool management for frequently created classes
- Garbage collection optimization
- Memory leak detection and prevention
- Data structure optimization with __slots__
- Weak references for cache-like structures
- Memory-efficient data processing patterns

Performance Targets:
- <1MB memory usage per calculation
- Prevent memory leaks under sustained load
- Optimize object allocation patterns
- Monitor memory usage patterns and alerts
- Automatic cleanup and garbage collection optimization
"""

import gc
import sys
import time
import threading
import psutil
import weakref
from typing import Dict, List, Any, Optional, Type, Callable, Set, Union, Generic, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from contextlib import contextmanager
import logging

import numpy as np

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)

T = TypeVar('T')


@dataclass
class MemoryStats:
    """Memory usage statistics."""
    total_memory_mb: float = 0.0
    available_memory_mb: float = 0.0
    process_memory_mb: float = 0.0
    memory_percent: float = 0.0
    peak_memory_mb: float = 0.0
    gc_collections: Dict[int, int] = field(default_factory=dict)
    object_counts: Dict[str, int] = field(default_factory=dict)
    pool_usage: Dict[str, Dict[str, int]] = field(default_factory=dict)
    memory_growth_rate_mb_per_hour: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def memory_pressure_level(self) -> str:
        """Determine memory pressure level."""
        if self.memory_percent < 50:
            return "low"
        elif self.memory_percent < 75:
            return "medium"
        elif self.memory_percent < 90:
            return "high"
        else:
            return "critical"


@dataclass
class MemoryProfile:
    """Memory usage profiling data."""
    function_name: str
    memory_before_mb: float
    memory_after_mb: float
    memory_delta_mb: float
    execution_time_ms: float
    objects_created: int
    objects_deleted: int
    gc_triggered: bool
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def memory_efficiency(self) -> float:
        """Calculate memory efficiency score (0-1)."""
        if self.execution_time_ms == 0:
            return 1.0
        
        # Lower memory delta and higher cleanup = better efficiency
        cleanup_ratio = self.objects_deleted / max(self.objects_created, 1)
        time_factor = min(1.0, 1000.0 / max(self.execution_time_ms, 1))
        memory_factor = max(0.0, 1.0 - (self.memory_delta_mb / 10.0))  # 10MB baseline
        
        return (cleanup_ratio * 0.4 + time_factor * 0.3 + memory_factor * 0.3)


class ObjectPool(Generic[T]):
    """
    High-performance object pool for frequently created objects.
    
    Reduces memory allocation overhead and garbage collection pressure
    by reusing objects instead of creating new instances.
    """
    
    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 100,
        reset_func: Optional[Callable[[T], None]] = None
    ):
        self.factory = factory
        self.max_size = max_size
        self.reset_func = reset_func
        self._pool = deque()
        self._created_count = 0
        self._reused_count = 0
        self._lock = threading.RLock()
    
    def acquire(self) -> T:
        """Acquire an object from the pool."""
        with self._lock:
            if self._pool:
                obj = self._pool.popleft()
                self._reused_count += 1
                return obj
            else:
                obj = self.factory()
                self._created_count += 1
                return obj
    
    def release(self, obj: T) -> None:
        """Release an object back to the pool."""
        with self._lock:
            if len(self._pool) < self.max_size:
                # Reset object state if reset function provided
                if self.reset_func:
                    try:
                        self.reset_func(obj)
                    except Exception as e:
                        logger.warning(f"Object reset failed: {e}")
                        return  # Don't pool objects that failed to reset
                
                self._pool.append(obj)
    
    @contextmanager
    def pooled_object(self):
        """Context manager for automatic object acquisition and release."""
        obj = self.acquire()
        try:
            yield obj
        finally:
            self.release(obj)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool usage statistics."""
        with self._lock:
            total_requests = self._created_count + self._reused_count
            reuse_rate = self._reused_count / total_requests if total_requests > 0 else 0.0
            
            return {
                "pool_size": len(self._pool),
                "max_size": self.max_size,
                "created_count": self._created_count,
                "reused_count": self._reused_count,
                "reuse_rate": reuse_rate,
                "total_requests": total_requests
            }
    
    def clear(self) -> None:
        """Clear the pool."""
        with self._lock:
            self._pool.clear()


class MemoryEfficientDataStructures:
    """
    Memory-optimized data structures for astronomical calculations.
    
    Uses __slots__, numpy arrays, and other optimization techniques
    to minimize memory usage.
    """
    
    class PlanetPosition:
        """Memory-efficient planet position with __slots__."""
        __slots__ = ['planet_id', 'longitude', 'latitude', 'distance', 
                     'speed_long', 'speed_lat', 'speed_dist', '_hash']
        
        def __init__(
            self, 
            planet_id: int, 
            longitude: float, 
            latitude: float, 
            distance: float,
            speed_long: float = 0.0,
            speed_lat: float = 0.0,
            speed_dist: float = 0.0
        ):
            self.planet_id = planet_id
            self.longitude = longitude
            self.latitude = latitude
            self.distance = distance
            self.speed_long = speed_long
            self.speed_lat = speed_lat
            self.speed_dist = speed_dist
            self._hash = None
        
        def __hash__(self) -> int:
            if self._hash is None:
                self._hash = hash((
                    self.planet_id, self.longitude, self.latitude, self.distance
                ))
            return self._hash
        
        def reset(self) -> None:
            """Reset object for pool reuse."""
            self.planet_id = 0
            self.longitude = 0.0
            self.latitude = 0.0
            self.distance = 0.0
            self.speed_long = 0.0
            self.speed_lat = 0.0
            self.speed_dist = 0.0
            self._hash = None
    
    class Aspect:
        """Memory-efficient aspect with __slots__."""
        __slots__ = ['planet_a', 'planet_b', 'aspect_type', 'orb', 'strength', '_hash']
        
        def __init__(
            self,
            planet_a: int,
            planet_b: int,
            aspect_type: str,
            orb: float,
            strength: float = 1.0
        ):
            self.planet_a = planet_a
            self.planet_b = planet_b
            self.aspect_type = aspect_type
            self.orb = orb
            self.strength = strength
            self._hash = None
        
        def __hash__(self) -> int:
            if self._hash is None:
                self._hash = hash((self.planet_a, self.planet_b, self.aspect_type))
            return self._hash
        
        def reset(self) -> None:
            """Reset object for pool reuse."""
            self.planet_a = 0
            self.planet_b = 0
            self.aspect_type = ""
            self.orb = 0.0
            self.strength = 0.0
            self._hash = None
    
    class ArabicPart:
        """Memory-efficient Arabic part with __slots__."""
        __slots__ = ['name', 'longitude', 'house', 'formula_parts', '_hash']
        
        def __init__(self, name: str, longitude: float, house: int, formula_parts: tuple):
            self.name = name
            self.longitude = longitude
            self.house = house
            self.formula_parts = formula_parts
            self._hash = None
        
        def __hash__(self) -> int:
            if self._hash is None:
                self._hash = hash((self.name, self.longitude, self.house))
            return self._hash
        
        def reset(self) -> None:
            """Reset object for pool reuse."""
            self.name = ""
            self.longitude = 0.0
            self.house = 0
            self.formula_parts = tuple()
            self._hash = None


class MemoryLeakDetector:
    """
    Detects and prevents memory leaks in the ephemeris system.
    
    Monitors object creation patterns, reference cycles, and
    growing collections that may indicate memory leaks.
    """
    
    def __init__(self, check_interval_seconds: int = 300):  # 5 minutes
        self.check_interval = check_interval_seconds
        self.baseline_counts: Dict[str, int] = {}
        self.growth_tracking: Dict[str, List[int]] = defaultdict(list)
        self.weak_refs: Set[weakref.ref] = set()
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        
        # Thresholds for leak detection
        self.growth_threshold = 1.5  # 50% growth triggers investigation
        self.max_growth_history = 10
    
    def start_monitoring(self) -> None:
        """Start memory leak monitoring."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("Memory leak monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop memory leak monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
        logger.info("Memory leak monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring:
            try:
                self._check_for_leaks()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Memory leak monitoring error: {e}")
                time.sleep(self.check_interval)
    
    def _check_for_leaks(self) -> None:
        """Check for potential memory leaks."""
        current_counts = self._get_object_counts()
        
        with self._lock:
            # Initialize baseline if first run
            if not self.baseline_counts:
                self.baseline_counts = current_counts.copy()
                return
            
            # Check for growing object counts
            for obj_type, count in current_counts.items():
                baseline = self.baseline_counts.get(obj_type, 0)
                
                if baseline > 0:
                    growth_ratio = count / baseline
                    
                    # Track growth history
                    self.growth_tracking[obj_type].append(count)
                    if len(self.growth_tracking[obj_type]) > self.max_growth_history:
                        self.growth_tracking[obj_type].pop(0)
                    
                    # Check for sustained growth
                    if growth_ratio > self.growth_threshold:
                        self._investigate_potential_leak(obj_type, growth_ratio, count)
            
            # Update baseline periodically
            if len(current_counts) > len(self.baseline_counts):
                self.baseline_counts.update(current_counts)
    
    def _get_object_counts(self) -> Dict[str, int]:
        """Get current object counts by type."""
        counts = defaultdict(int)
        
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            counts[obj_type] += 1
        
        return dict(counts)
    
    def _investigate_potential_leak(
        self, 
        obj_type: str, 
        growth_ratio: float, 
        current_count: int
    ) -> None:
        """Investigate potential memory leak."""
        # Check if growth is sustained
        history = self.growth_tracking[obj_type]
        if len(history) >= 3:
            recent_growth = all(
                history[i] < history[i+1] 
                for i in range(len(history)-3, len(history)-1)
            )
            
            if recent_growth:
                logger.warning(
                    f"Potential memory leak detected: {obj_type} "
                    f"count grew {growth_ratio:.2f}x to {current_count} objects"
                )
                
                # Trigger garbage collection
                collected = gc.collect()
                logger.info(f"Garbage collection freed {collected} objects")
                
                # Update tracking after cleanup
                new_count = sum(1 for obj in gc.get_objects() 
                               if type(obj).__name__ == obj_type)
                self.growth_tracking[obj_type].append(new_count)
    
    def register_weak_reference(self, obj: Any) -> None:
        """Register weak reference for tracking."""
        def cleanup_callback(ref):
            self.weak_refs.discard(ref)
        
        weak_ref = weakref.ref(obj, cleanup_callback)
        self.weak_refs.add(weak_ref)
    
    def get_leak_report(self) -> Dict[str, Any]:
        """Get comprehensive leak detection report."""
        current_counts = self._get_object_counts()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_objects": sum(current_counts.values()),
            "object_types": len(current_counts),
            "top_object_types": sorted(
                current_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            "weak_references_tracked": len(self.weak_refs),
            "growth_patterns": {}
        }
        
        # Add growth pattern analysis
        for obj_type, history in self.growth_tracking.items():
            if len(history) >= 2:
                growth_rate = (history[-1] - history[0]) / len(history)
                report["growth_patterns"][obj_type] = {
                    "current_count": history[-1],
                    "growth_rate_per_check": growth_rate,
                    "history_length": len(history)
                }
        
        return report


class MemoryManager:
    """
    Comprehensive memory management system.
    
    Provides memory monitoring, object pooling, garbage collection optimization,
    and memory leak prevention for the ephemeris system.
    """
    
    def __init__(self):
        self.leak_detector = MemoryLeakDetector()
        self.object_pools: Dict[str, ObjectPool] = {}
        self.memory_history: List[MemoryStats] = []
        self.memory_profiles: List[MemoryProfile] = []
        self._gc_stats_before: Dict[int, int] = {}
        self._monitoring_enabled = True
        self._lock = threading.RLock()
        
        # Initialize object pools
        self._initialize_pools()
        
        # Start monitoring
        self.leak_detector.start_monitoring()
        
        logger.info("MemoryManager initialized")
    
    def _initialize_pools(self) -> None:
        """Initialize object pools for common classes."""
        # Planet position pool
        self.object_pools['planet_position'] = ObjectPool(
            factory=lambda: MemoryEfficientDataStructures.PlanetPosition(0, 0, 0, 0),
            max_size=200,
            reset_func=lambda obj: obj.reset()
        )
        
        # Aspect pool
        self.object_pools['aspect'] = ObjectPool(
            factory=lambda: MemoryEfficientDataStructures.Aspect(0, 0, "", 0),
            max_size=500,
            reset_func=lambda obj: obj.reset()
        )
        
        # Arabic part pool
        self.object_pools['arabic_part'] = ObjectPool(
            factory=lambda: MemoryEfficientDataStructures.ArabicPart("", 0, 0, tuple()),
            max_size=100,
            reset_func=lambda obj: obj.reset()
        )
    
    def monitor_memory_usage(self) -> MemoryStats:
        """Get current memory usage statistics."""
        try:
            # System memory info
            virtual_memory = psutil.virtual_memory()
            
            # Process memory info
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # Garbage collection stats
            gc_stats = {}
            for generation in range(3):
                gc_stats[generation] = len(gc.get_objects(generation))
            
            # Object counts by type
            object_counts = defaultdict(int)
            for obj in gc.get_objects():
                object_counts[type(obj).__name__] += 1
            
            # Pool usage stats
            pool_usage = {}
            for pool_name, pool in self.object_pools.items():
                pool_usage[pool_name] = pool.get_stats()
            
            stats = MemoryStats(
                total_memory_mb=virtual_memory.total / (1024 * 1024),
                available_memory_mb=virtual_memory.available / (1024 * 1024),
                process_memory_mb=process_memory.rss / (1024 * 1024),
                memory_percent=virtual_memory.percent,
                gc_collections=gc_stats,
                object_counts=dict(object_counts),
                pool_usage=pool_usage
            )
            
            # Update peak memory tracking
            if hasattr(self, '_peak_memory'):
                if stats.process_memory_mb > self._peak_memory:
                    self._peak_memory = stats.process_memory_mb
            else:
                self._peak_memory = stats.process_memory_mb
            stats.peak_memory_mb = self._peak_memory
            
            # Calculate growth rate
            if len(self.memory_history) > 0:
                prev_stats = self.memory_history[-1]
                time_diff = (stats.timestamp - prev_stats.timestamp).total_seconds() / 3600
                if time_diff > 0:
                    memory_diff = stats.process_memory_mb - prev_stats.process_memory_mb
                    stats.memory_growth_rate_mb_per_hour = memory_diff / time_diff
            
            # Store history (keep last 100 entries)
            with self._lock:
                self.memory_history.append(stats)
                if len(self.memory_history) > 100:
                    self.memory_history.pop(0)
            
            return stats
            
        except Exception as e:
            logger.error(f"Memory monitoring failed: {e}")
            return MemoryStats()
    
    def optimize_object_allocation(self, calculation_type: str) -> None:
        """Optimize object allocation patterns for specific calculation types."""
        if calculation_type == "natal_chart":
            # Pre-populate pools for natal chart calculations
            for _ in range(20):  # Pre-create 20 planet positions
                obj = self.object_pools['planet_position'].acquire()
                self.object_pools['planet_position'].release(obj)
        
        elif calculation_type == "aspects":
            # Pre-populate aspect pool
            for _ in range(100):  # Pre-create 100 aspects
                obj = self.object_pools['aspect'].acquire()
                self.object_pools['aspect'].release(obj)
    
    def implement_memory_pools(self) -> None:
        """Ensure memory pools are properly implemented and warmed."""
        for pool_name, pool in self.object_pools.items():
            # Warm up pools
            temp_objects = []
            for _ in range(min(10, pool.max_size // 2)):
                temp_objects.append(pool.acquire())
            
            for obj in temp_objects:
                pool.release(obj)
            
            logger.debug(f"Warmed up {pool_name} pool: {pool.get_stats()}")
    
    def garbage_collect_optimized(self) -> Dict[str, int]:
        """Perform optimized garbage collection."""
        # Record stats before collection
        before_stats = self.monitor_memory_usage()
        
        # Perform collection with timing
        start_time = time.time()
        collected = {}
        
        # Collect in generations (0, 1, 2)
        for generation in range(3):
            collected[generation] = gc.collect(generation)
        
        collection_time = (time.time() - start_time) * 1000
        
        # Record stats after collection
        after_stats = self.monitor_memory_usage()
        memory_freed = before_stats.process_memory_mb - after_stats.process_memory_mb
        
        logger.info(
            f"Garbage collection completed in {collection_time:.1f}ms: "
            f"freed {memory_freed:.1f}MB, collected {sum(collected.values())} objects"
        )
        
        return {
            "collection_time_ms": collection_time,
            "memory_freed_mb": memory_freed,
            "objects_collected": collected,
            "total_collected": sum(collected.values())
        }
    
    @contextmanager
    def memory_profiler(self, function_name: str):
        """Context manager for profiling memory usage of functions."""
        if not self._monitoring_enabled:
            yield
            return
        
        # Record before state
        before_stats = self.monitor_memory_usage()
        before_objects = len(gc.get_objects())
        start_time = time.time()
        
        # Store GC stats before
        gc_before = {i: len(gc.get_objects(i)) for i in range(3)}
        
        try:
            yield
        finally:
            # Record after state
            end_time = time.time()
            after_stats = self.monitor_memory_usage()
            after_objects = len(gc.get_objects())
            
            # Check if GC was triggered
            gc_after = {i: len(gc.get_objects(i)) for i in range(3)}
            gc_triggered = any(gc_after[i] < gc_before[i] for i in range(3))
            
            # Create memory profile
            profile = MemoryProfile(
                function_name=function_name,
                memory_before_mb=before_stats.process_memory_mb,
                memory_after_mb=after_stats.process_memory_mb,
                memory_delta_mb=after_stats.process_memory_mb - before_stats.process_memory_mb,
                execution_time_ms=(end_time - start_time) * 1000,
                objects_created=max(0, after_objects - before_objects),
                objects_deleted=max(0, before_objects - after_objects),
                gc_triggered=gc_triggered
            )
            
            # Store profile
            with self._lock:
                self.memory_profiles.append(profile)
                if len(self.memory_profiles) > 1000:  # Keep last 1000 profiles
                    self.memory_profiles.pop(0)
    
    def profile_memory_patterns(self) -> Dict[str, Any]:
        """Generate comprehensive memory usage patterns report."""
        if not self.memory_profiles:
            return {"error": "No memory profiles available"}
        
        # Analyze profiles
        total_profiles = len(self.memory_profiles)
        
        # Group by function
        function_stats = defaultdict(list)
        for profile in self.memory_profiles:
            function_stats[profile.function_name].append(profile)
        
        # Calculate statistics
        pattern_analysis = {}
        
        for func_name, profiles in function_stats.items():
            memory_deltas = [p.memory_delta_mb for p in profiles]
            efficiency_scores = [p.memory_efficiency for p in profiles]
            
            pattern_analysis[func_name] = {
                "call_count": len(profiles),
                "avg_memory_delta_mb": np.mean(memory_deltas),
                "max_memory_delta_mb": np.max(memory_deltas),
                "avg_efficiency": np.mean(efficiency_scores),
                "memory_leak_risk": np.mean(memory_deltas) > 0.5 and np.std(memory_deltas) > 0.2
            }
        
        # Overall statistics
        all_deltas = [p.memory_delta_mb for p in self.memory_profiles]
        all_efficiencies = [p.memory_efficiency for p in self.memory_profiles]
        
        return {
            "total_profiles": total_profiles,
            "avg_memory_delta_mb": np.mean(all_deltas),
            "avg_efficiency": np.mean(all_efficiencies),
            "function_patterns": pattern_analysis,
            "memory_leak_candidates": [
                func for func, stats in pattern_analysis.items()
                if stats["memory_leak_risk"]
            ],
            "most_efficient_functions": sorted(
                pattern_analysis.items(),
                key=lambda x: x[1]["avg_efficiency"],
                reverse=True
            )[:5],
            "pool_statistics": {
                name: pool.get_stats() 
                for name, pool in self.object_pools.items()
            }
        }
    
    def detect_memory_anomalies(self) -> List[Dict[str, Any]]:
        """Detect memory usage anomalies."""
        anomalies = []
        
        if len(self.memory_history) < 10:
            return anomalies
        
        # Calculate memory usage trends
        recent_memory = [stats.process_memory_mb for stats in self.memory_history[-10:]]
        memory_trend = np.polyfit(range(len(recent_memory)), recent_memory, 1)[0]
        
        # Check for rapid memory growth
        if memory_trend > 5.0:  # >5MB per measurement
            anomalies.append({
                "type": "rapid_memory_growth",
                "severity": "high",
                "trend_mb_per_measurement": memory_trend,
                "description": f"Memory growing rapidly at {memory_trend:.2f}MB per measurement"
            })
        
        # Check for high memory pressure
        current_stats = self.memory_history[-1]
        if current_stats.memory_percent > 85:
            anomalies.append({
                "type": "high_memory_pressure",
                "severity": "critical" if current_stats.memory_percent > 95 else "high",
                "memory_percent": current_stats.memory_percent,
                "description": f"System memory usage at {current_stats.memory_percent:.1f}%"
            })
        
        # Check pool efficiency
        for pool_name, pool in self.object_pools.items():
            stats = pool.get_stats()
            if stats["reuse_rate"] < 0.3 and stats["total_requests"] > 50:
                anomalies.append({
                    "type": "low_pool_efficiency",
                    "severity": "medium",
                    "pool_name": pool_name,
                    "reuse_rate": stats["reuse_rate"],
                    "description": f"Object pool {pool_name} has low reuse rate: {stats['reuse_rate']:.2f}"
                })
        
        return anomalies
    
    def get_pool(self, pool_name: str) -> Optional[ObjectPool]:
        """Get object pool by name."""
        return self.object_pools.get(pool_name)
    
    def clear_pools(self) -> None:
        """Clear all object pools."""
        for pool in self.object_pools.values():
            pool.clear()
        logger.info("All object pools cleared")
    
    def shutdown(self) -> None:
        """Shutdown memory manager."""
        self.leak_detector.stop_monitoring()
        self.clear_pools()
        logger.info("MemoryManager shutdown complete")


# Global memory manager instance
_global_memory_manager: Optional[MemoryManager] = None
_memory_manager_lock = threading.Lock()


def get_memory_manager() -> MemoryManager:
    """Get or create global memory manager instance."""
    global _global_memory_manager
    
    if _global_memory_manager is None:
        with _memory_manager_lock:
            if _global_memory_manager is None:
                _global_memory_manager = MemoryManager()
    
    return _global_memory_manager


def memory_optimized(pool_name: Optional[str] = None):
    """
    Decorator for memory-optimized function execution.
    
    Args:
        pool_name: Optional object pool to use for optimization
        
    Returns:
        Decorated function with memory optimization
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            memory_manager = get_memory_manager()
            
            # Use memory profiling
            with memory_manager.memory_profiler(func.__name__):
                # Pre-optimize if pool specified
                if pool_name and pool_name in memory_manager.object_pools:
                    memory_manager.optimize_object_allocation(pool_name)
                
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def memory_efficient_generator(chunk_size: int = 1000):
    """
    Decorator to convert functions to memory-efficient generators.
    
    Args:
        chunk_size: Size of chunks to process at a time
        
    Returns:
        Generator function that processes data in chunks
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(data_list: List[Any], *args, **kwargs):
            for i in range(0, len(data_list), chunk_size):
                chunk = data_list[i:i + chunk_size]
                yield func(chunk, *args, **kwargs)
                
                # Force garbage collection between chunks for large datasets
                if len(data_list) > 10000:
                    gc.collect()
        
        return wrapper
    return decorator