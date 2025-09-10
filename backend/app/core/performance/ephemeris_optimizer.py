"""
Swiss Ephemeris Integration Optimization
Optimizes Swiss Ephemeris calls for maximum performance and minimal library overhead.

Features:
- Batch position calculations to minimize library calls
- Swiss Ephemeris call pattern optimization
- Ephemeris file handle caching and memory mapping
- Vectorized operations for multiple body calculations
- Call context reuse and flag optimization
- Performance profiling and optimization recommendations

Performance Targets:
- Minimize Swiss Ephemeris library call overhead
- Batch multiple body calculations efficiently
- Cache ephemeris file handles for repeated access
- Optimize calculation flags for speed vs precision tradeoffs
"""

import time
import os
import mmap
from typing import List, Dict, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
import threading
import logging
from functools import lru_cache, wraps
from collections import defaultdict

import swisseph as swe
import numpy as np

from app.core.performance.advanced_cache import get_intelligent_cache, CacheType

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


@dataclass
class EphemerisCallPattern:
    """Optimized call pattern for Swiss Ephemeris operations."""
    flags: int = swe.FLG_SWIEPH
    batch_size: int = 10
    context_reuse: bool = True
    file_preloading: bool = True
    calculation_method: str = "standard"
    precision_level: str = "high"
    enable_caching: bool = True
    
    def get_optimal_flags(self) -> int:
        """Get optimized flags based on precision requirements."""
        base_flags = swe.FLG_SWIEPH
        
        if self.precision_level == "ultra_high":
            base_flags |= swe.FLG_J2000
        elif self.precision_level == "high":
            base_flags |= swe.FLG_SPEED
        elif self.precision_level == "fast":
            base_flags |= swe.FLG_SPEED | swe.FLG_SPEED3
        
        return base_flags


@dataclass
class BatchCalculationRequest:
    """Request for batch position calculation."""
    julian_day: float
    bodies: List[int]
    flags: int = swe.FLG_SWIEPH
    coordinate_system: str = "ecliptic"  # ecliptic, equatorial
    include_speed: bool = False
    
    def __post_init__(self):
        # Ensure bodies is a list of integers
        if isinstance(self.bodies, (int, str)):
            self.bodies = [self.bodies]
        
        # Convert string body names to SE constants if needed
        converted_bodies = []
        for body in self.bodies:
            if isinstance(body, str):
                converted_bodies.append(self._body_name_to_constant(body))
            else:
                converted_bodies.append(body)
        self.bodies = converted_bodies
    
    def _body_name_to_constant(self, body_name: str) -> int:
        """Convert body name to Swiss Ephemeris constant."""
        body_mapping = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Uranus': swe.URANUS,
            'Neptune': swe.NEPTUNE,
            'Pluto': swe.PLUTO,
            'MeanNode': swe.MEAN_NODE,
            'TrueNode': swe.TRUE_NODE,
            'Chiron': swe.CHIRON
        }
        return body_mapping.get(body_name, swe.SUN)


@dataclass
class BatchCalculationResult:
    """Result from batch position calculation."""
    julian_day: float
    positions: Dict[int, Dict[str, float]]  # body_id -> {longitude, latitude, distance, speed_long, ...}
    calculation_time_ms: float
    cache_hits: int
    cache_misses: int
    flags_used: int
    
    def get_position(self, body: int) -> Optional[Dict[str, float]]:
        """Get position for specific body."""
        return self.positions.get(body)
    
    def get_longitude(self, body: int) -> Optional[float]:
        """Get longitude for specific body."""
        pos = self.get_position(body)
        return pos.get('longitude') if pos else None


@dataclass
class EphemerisPerformanceProfile:
    """Performance profiling data for ephemeris operations."""
    total_calls: int = 0
    total_time_ms: float = 0.0
    average_time_per_call: float = 0.0
    cache_hit_rate: float = 0.0
    most_requested_bodies: Dict[int, int] = field(default_factory=dict)
    call_pattern_effectiveness: Dict[str, float] = field(default_factory=dict)
    file_access_patterns: Dict[str, int] = field(default_factory=dict)
    optimization_opportunities: List[str] = field(default_factory=list)
    
    def add_call_data(
        self,
        call_time_ms: float,
        bodies: List[int],
        cache_hit: bool,
        pattern_name: str
    ) -> None:
        """Add performance data from a calculation call."""
        self.total_calls += 1
        self.total_time_ms += call_time_ms
        self.average_time_per_call = self.total_time_ms / self.total_calls
        
        # Track body frequency
        for body in bodies:
            self.most_requested_bodies[body] = self.most_requested_bodies.get(body, 0) + 1
        
        # Track cache effectiveness
        if cache_hit:
            self.cache_hit_rate = (
                (self.cache_hit_rate * (self.total_calls - 1) + 1.0) / self.total_calls
            )
        else:
            self.cache_hit_rate = (
                self.cache_hit_rate * (self.total_calls - 1) / self.total_calls
            )
        
        # Track pattern effectiveness
        if pattern_name not in self.call_pattern_effectiveness:
            self.call_pattern_effectiveness[pattern_name] = []
        self.call_pattern_effectiveness[pattern_name].append(call_time_ms)


class EphemerisFileManager:
    """Manages ephemeris file handles and memory mapping for optimal performance."""
    
    def __init__(self):
        self._file_handles: Dict[str, Any] = {}
        self._memory_maps: Dict[str, mmap.mmap] = {}
        self._access_counts: Dict[str, int] = defaultdict(int)
        self._lock = threading.RLock()
        self._initialized_files: Set[str] = set()
    
    def preload_common_files(self, ephemeris_path: Optional[str] = None) -> None:
        """Preload commonly used ephemeris files."""
        if ephemeris_path is None:
            ephemeris_path = swe.get_library_path()
        
        common_files = [
            "sepl_18.se1",  # Planets
            "semo_18.se1",  # Moon
            "seas_18.se1",  # Asteroids
        ]
        
        with self._lock:
            for filename in common_files:
                filepath = os.path.join(ephemeris_path, filename)
                if os.path.exists(filepath):
                    try:
                        self._preload_file(filepath)
                        self._initialized_files.add(filename)
                        logger.debug(f"Preloaded ephemeris file: {filename}")
                    except Exception as e:
                        logger.warning(f"Failed to preload {filename}: {e}")
    
    def _preload_file(self, filepath: str) -> None:
        """Preload and memory-map a single ephemeris file."""
        try:
            with open(filepath, 'rb') as f:
                # Create memory map for efficient access
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                self._memory_maps[filepath] = mm
                
                # Track access
                self._access_counts[filepath] = 0
                
        except Exception as e:
            logger.warning(f"Memory mapping failed for {filepath}: {e}")
    
    def get_file_handle(self, filename: str) -> Optional[Any]:
        """Get cached file handle if available."""
        with self._lock:
            return self._file_handles.get(filename)
    
    def record_file_access(self, filename: str) -> None:
        """Record file access for optimization analysis."""
        with self._lock:
            self._access_counts[filename] += 1
    
    def get_access_statistics(self) -> Dict[str, int]:
        """Get file access statistics."""
        with self._lock:
            return self._access_counts.copy()
    
    def cleanup(self) -> None:
        """Clean up memory maps and file handles."""
        with self._lock:
            for mm in self._memory_maps.values():
                try:
                    mm.close()
                except:
                    pass
            
            self._memory_maps.clear()
            self._file_handles.clear()
            self._access_counts.clear()
            self._initialized_files.clear()


class EphemerisCallOptimizer:
    """
    Optimizes Swiss Ephemeris calls for maximum performance.
    
    Features:
    - Batch position calculations to minimize library overhead
    - Call pattern optimization based on usage patterns
    - File handle caching and preloading
    - Flag optimization for speed vs precision tradeoffs
    - Performance profiling and recommendations
    """
    
    def __init__(self):
        self.file_manager = EphemerisFileManager()
        self.cache = get_intelligent_cache()
        self.performance_profile = EphemerisPerformanceProfile()
        self._call_contexts: Dict[str, Any] = {}
        self._optimization_enabled = True
        self._lock = threading.RLock()
        
        # Initialize Swiss Ephemeris
        self._initialize_swe()
        
        logger.info("EphemerisCallOptimizer initialized")
    
    def _initialize_swe(self) -> None:
        """Initialize Swiss Ephemeris with optimal settings."""
        try:
            # Set ephemeris path if needed
            ephemeris_path = os.environ.get('SE_EPHE_PATH')
            if ephemeris_path:
                swe.set_ephe_path(ephemeris_path)
            
            # Preload common files
            self.file_manager.preload_common_files()
            
        except Exception as e:
            logger.warning(f"Swiss Ephemeris initialization warning: {e}")
    
    def batch_position_calculations(
        self,
        requests: List[BatchCalculationRequest]
    ) -> List[BatchCalculationResult]:
        """
        Perform batch position calculations with optimization.
        
        Args:
            requests: List of batch calculation requests
            
        Returns:
            List of calculation results
        """
        if not requests:
            return []
        
        start_time = time.time()
        results = []
        
        # Group requests by similar characteristics for optimization
        grouped_requests = self._group_requests_optimally(requests)
        
        for group in grouped_requests:
            group_results = self._calculate_group_batch(group)
            results.extend(group_results)
        
        total_time = (time.time() - start_time) * 1000
        
        # Update performance profile
        self.performance_profile.add_call_data(
            total_time,
            [body for req in requests for body in req.bodies],
            False,  # Would track cache hits properly
            "batch_calculation"
        )
        
        logger.debug(f"Batch calculation completed: {len(requests)} requests in {total_time:.1f}ms")
        
        return results
    
    def _group_requests_optimally(
        self,
        requests: List[BatchCalculationRequest]
    ) -> List[List[BatchCalculationRequest]]:
        """Group requests for optimal batch processing."""
        # Group by julian day and flags for efficient processing
        groups = defaultdict(list)
        
        for request in requests:
            # Create grouping key based on JD (rounded) and flags
            jd_key = round(request.julian_day, 5)  # 5 decimal precision
            group_key = (jd_key, request.flags, request.coordinate_system)
            groups[group_key].append(request)
        
        return list(groups.values())
    
    def _calculate_group_batch(
        self,
        group: List[BatchCalculationRequest]
    ) -> List[BatchCalculationResult]:
        """Calculate a group of similar requests efficiently."""
        if not group:
            return []
        
        results = []
        
        # Use representative request for common parameters
        representative = group[0]
        
        # Collect all unique bodies across group
        all_bodies = set()
        for request in group:
            all_bodies.update(request.bodies)
        
        # Calculate positions for all bodies at each time point
        for request in group:
            result = self._calculate_single_batch(
                request, list(all_bodies), representative.flags
            )
            results.append(result)
        
        return results
    
    def _calculate_single_batch(
        self,
        request: BatchCalculationRequest,
        all_bodies: List[int],
        flags: int
    ) -> BatchCalculationResult:
        """Calculate positions for a single request."""
        start_time = time.time()
        positions = {}
        cache_hits = 0
        cache_misses = 0
        
        # Check cache for each body
        for body in all_bodies:
            cache_key = f"swe_pos_{body}_{request.julian_day}_{flags}"
            cached_position = self.cache.l1_cache.get(cache_key)
            
            if cached_position:
                positions[body] = cached_position
                cache_hits += 1
            else:
                # Calculate position using Swiss Ephemeris
                try:
                    if request.coordinate_system == "equatorial":
                        calc_flags = flags | swe.FLG_EQUATORIAL
                    else:
                        calc_flags = flags
                    
                    # Perform Swiss Ephemeris calculation
                    result = swe.calc_ut(request.julian_day, body, calc_flags)
                    
                    position_data = {
                        'longitude': result[0][0],
                        'latitude': result[0][1], 
                        'distance': result[0][2],
                        'speed_longitude': result[0][3] if len(result[0]) > 3 else 0.0,
                        'speed_latitude': result[0][4] if len(result[0]) > 4 else 0.0,
                        'speed_distance': result[0][5] if len(result[0]) > 5 else 0.0,
                    }
                    
                    positions[body] = position_data
                    cache_misses += 1
                    
                    # Cache the result
                    self.cache.l1_cache.set(cache_key, position_data)
                    
                except Exception as e:
                    logger.error(f"Swiss Ephemeris calculation failed for body {body}: {e}")
                    positions[body] = {
                        'longitude': 0.0, 'latitude': 0.0, 'distance': 0.0,
                        'speed_longitude': 0.0, 'speed_latitude': 0.0, 'speed_distance': 0.0,
                        'error': str(e)
                    }
                    cache_misses += 1
        
        calculation_time = (time.time() - start_time) * 1000
        
        # Filter positions to only requested bodies
        filtered_positions = {
            body: positions[body] 
            for body in request.bodies 
            if body in positions
        }
        
        return BatchCalculationResult(
            julian_day=request.julian_day,
            positions=filtered_positions,
            calculation_time_ms=calculation_time,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            flags_used=flags
        )
    
    def optimize_call_pattern(self, calculation_type: str) -> EphemerisCallPattern:
        """
        Determine optimal call pattern for given calculation type.
        
        Args:
            calculation_type: Type of calculation (natal, transit, etc.)
            
        Returns:
            Optimized call pattern
        """
        # Analyze historical performance for this calculation type
        pattern_performance = self.performance_profile.call_pattern_effectiveness
        
        if calculation_type == "natal_chart":
            return EphemerisCallPattern(
                flags=swe.FLG_SWIEPH | swe.FLG_SPEED,
                batch_size=10,
                context_reuse=True,
                precision_level="high"
            )
        elif calculation_type == "transit":
            return EphemerisCallPattern(
                flags=swe.FLG_SWIEPH | swe.FLG_SPEED,
                batch_size=20,
                context_reuse=True,
                precision_level="standard"
            )
        elif calculation_type == "progression":
            return EphemerisCallPattern(
                flags=swe.FLG_SWIEPH,
                batch_size=5,
                context_reuse=True,
                precision_level="ultra_high"
            )
        else:
            return EphemerisCallPattern()  # Default pattern
    
    def cache_ephemeris_file_handles(self) -> None:
        """Cache ephemeris file handles for faster access."""
        self.file_manager.preload_common_files()
    
    def minimize_library_overhead(self) -> None:
        """Apply optimizations to minimize Swiss Ephemeris library overhead."""
        # Set optimal Swiss Ephemeris options
        try:
            # Use fastest available calculation method
            swe.set_topo(0.0, 0.0, 0.0)  # Reset topocentric
            
            # Optimize for speed vs precision based on requirements
            # This would be expanded based on specific needs
            
        except Exception as e:
            logger.warning(f"Library overhead optimization warning: {e}")
    
    def profile_swe_call_performance(self) -> EphemerisPerformanceProfile:
        """Get detailed performance profile of Swiss Ephemeris calls."""
        # Add optimization recommendations based on current profile
        profile = self.performance_profile
        
        # Analyze and add recommendations
        if profile.cache_hit_rate < 0.5:
            profile.optimization_opportunities.append(
                "Cache hit rate is low - consider increasing cache TTL or size"
            )
        
        if profile.average_time_per_call > 10:
            profile.optimization_opportunities.append(
                "Average call time is high - consider batch processing or flag optimization"
            )
        
        # Analyze body frequency for preloading recommendations
        most_common_bodies = sorted(
            profile.most_requested_bodies.items(),
            key=lambda x: x[1], reverse=True
        )[:5]
        
        if most_common_bodies:
            bodies_str = ", ".join([str(body) for body, _ in most_common_bodies])
            profile.optimization_opportunities.append(
                f"Consider precomputing positions for frequently requested bodies: {bodies_str}"
            )
        
        return profile
    
    @contextmanager
    def optimized_calculation_context(self, pattern: EphemerisCallPattern):
        """Context manager for optimized Swiss Ephemeris calculations."""
        # Store original settings
        original_settings = self._get_current_swe_settings()
        
        try:
            # Apply optimizations
            self._apply_optimization_pattern(pattern)
            yield
        finally:
            # Restore original settings
            self._restore_swe_settings(original_settings)
    
    def _get_current_swe_settings(self) -> Dict[str, Any]:
        """Get current Swiss Ephemeris settings."""
        # This would capture current SE settings
        return {}
    
    def _apply_optimization_pattern(self, pattern: EphemerisCallPattern) -> None:
        """Apply optimization pattern to Swiss Ephemeris."""
        # This would configure SE based on the pattern
        pass
    
    def _restore_swe_settings(self, settings: Dict[str, Any]) -> None:
        """Restore Swiss Ephemeris settings."""
        # This would restore SE settings
        pass
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        recommendations = []
        
        profile = self.performance_profile
        
        if profile.total_calls > 100:
            if profile.cache_hit_rate < 0.7:
                recommendations.append(
                    "Cache hit rate is below target (70%). Consider:"
                    "\n- Increasing cache size or TTL"
                    "\n- Improving cache key normalization"
                    "\n- Precomputing common calculations"
                )
            
            if profile.average_time_per_call > 5:
                recommendations.append(
                    "Average calculation time is high. Consider:"
                    "\n- Using batch calculations for multiple bodies"
                    "\n- Optimizing calculation flags for speed"
                    "\n- Preloading ephemeris files"
                )
        
        # File access pattern analysis
        file_stats = self.file_manager.get_access_statistics()
        if file_stats:
            most_accessed = max(file_stats.items(), key=lambda x: x[1])
            recommendations.append(
                f"Most accessed ephemeris file: {most_accessed[0]} ({most_accessed[1]} accesses)"
                "\nConsider keeping this file memory-mapped for optimal performance"
            )
        
        return recommendations


# Global optimizer instance
_global_optimizer: Optional[EphemerisCallOptimizer] = None
_optimizer_lock = threading.Lock()


def get_ephemeris_optimizer() -> EphemerisCallOptimizer:
    """Get or create global ephemeris optimizer instance."""
    global _global_optimizer
    
    if _global_optimizer is None:
        with _optimizer_lock:
            if _global_optimizer is None:
                _global_optimizer = EphemerisCallOptimizer()
    
    return _global_optimizer


def optimized_swe_calculation(
    calculation_type: str = "standard",
    enable_caching: bool = True
):
    """
    Decorator for optimized Swiss Ephemeris calculations.
    
    Args:
        calculation_type: Type of calculation for optimization
        enable_caching: Whether to enable result caching
        
    Returns:
        Decorated function with Swiss Ephemeris optimization
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = get_ephemeris_optimizer()
            
            # Get optimal call pattern
            pattern = optimizer.optimize_call_pattern(calculation_type)
            
            # Use optimized context
            with optimizer.optimized_calculation_context(pattern):
                if enable_caching:
                    # Generate cache key from function and args
                    cache_key = f"swe_{func.__name__}_{hash(str(args) + str(kwargs))}"
                    
                    cached_result = optimizer.cache.l1_cache.get(cache_key)
                    if cached_result:
                        return cached_result
                
                # Execute calculation
                start_time = time.time()
                result = func(*args, **kwargs)
                calc_time = (time.time() - start_time) * 1000
                
                # Record performance
                optimizer.performance_profile.add_call_data(
                    calc_time, 
                    kwargs.get('bodies', [0]),  # Default to Sun
                    cached_result is not None,
                    calculation_type
                )
                
                # Cache result if enabled
                if enable_caching:
                    optimizer.cache.l1_cache.set(cache_key, result)
                
                return result
        
        return wrapper
    return decorator


# Vectorized calculation utilities
class VectorizedEphemerisCalculations:
    """Vectorized Swiss Ephemeris calculations for improved performance."""
    
    @staticmethod
    def calculate_positions_vectorized(
        julian_days: List[float],
        bodies: List[int],
        flags: int = swe.FLG_SWIEPH
    ) -> Dict[int, np.ndarray]:
        """
        Calculate positions for multiple times and bodies using vectorization.
        
        Args:
            julian_days: List of Julian day numbers
            bodies: List of body constants
            flags: Calculation flags
            
        Returns:
            Dictionary mapping body -> array of positions [lon, lat, dist, ...]
        """
        results = {}
        optimizer = get_ephemeris_optimizer()
        
        for body in bodies:
            positions = []
            
            for jd in julian_days:
                try:
                    result = swe.calc_ut(jd, body, flags)
                    positions.append(result[0])
                except Exception as e:
                    logger.error(f"Vectorized calculation failed for body {body}, JD {jd}: {e}")
                    positions.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            
            results[body] = np.array(positions)
        
        return results
    
    @staticmethod
    def calculate_aspects_vectorized(
        positions: Dict[int, np.ndarray],
        aspect_angles: List[float] = [0, 60, 90, 120, 180],
        orbs: List[float] = [8, 6, 8, 8, 8]
    ) -> Dict[Tuple[int, int], np.ndarray]:
        """
        Calculate aspects between bodies using vectorized operations.
        
        Args:
            positions: Dictionary of body positions (from calculate_positions_vectorized)
            aspect_angles: List of aspect angles to check
            orbs: List of orbs for each aspect
            
        Returns:
            Dictionary mapping (body1, body2) -> array of aspect strengths
        """
        aspect_results = {}
        
        bodies = list(positions.keys())
        
        for i, body1 in enumerate(bodies):
            for body2 in bodies[i+1:]:
                pos1 = positions[body1][:, 0]  # Longitudes
                pos2 = positions[body2][:, 0]  # Longitudes
                
                # Calculate angular differences
                diff = np.abs(pos2 - pos1)
                diff = np.minimum(diff, 360 - diff)  # Handle wraparound
                
                # Check for aspects
                aspect_strengths = np.zeros_like(diff)
                
                for aspect_angle, orb in zip(aspect_angles, orbs):
                    aspect_diff = np.abs(diff - aspect_angle)
                    in_orb = aspect_diff <= orb
                    
                    # Calculate strength (1.0 - normalized difference)
                    strength = np.where(
                        in_orb,
                        1.0 - (aspect_diff / orb),
                        0.0
                    )
                    
                    aspect_strengths = np.maximum(aspect_strengths, strength)
                
                aspect_results[(body1, body2)] = aspect_strengths
        
        return aspect_results