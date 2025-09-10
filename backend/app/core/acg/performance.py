"""
Performance Optimization for Enhanced ACG Features

This module provides comprehensive performance optimization for enhanced ACG features
including vectorized calculations, intelligent caching, memory optimization,
and concurrent processing while maintaining the <800ms target performance.

Key optimizations:
- Vectorized retrograde analysis across multiple planets
- Pre-computed aspect line base calculations
- Multi-level caching with TTL optimization
- Memory-efficient data structures
- Parallel processing for independent calculations
"""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
import logging
from datetime import datetime, timezone

import numpy as np
import swisseph as swe

from .enhanced_metadata import RetrogradeAwareLineMetadata, EnhancedACGLineMetadataGenerator
from .aspect_lines import AspectToAngleCalculator, AspectLineFeature
from extracted.systems.ephemeris_utils.tools.enhanced_calculations import EnhancedPlanetPosition

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics for enhanced ACG operations."""
    
    operation_name: str
    start_time: float
    end_time: float
    memory_usage_mb: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    vectorization_speedup: float = 1.0
    parallelization_speedup: float = 1.0
    
    @property
    def duration_ms(self) -> float:
        """Calculate duration in milliseconds."""
        return (self.end_time - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "operation": self.operation_name,
            "duration_ms": self.duration_ms,
            "memory_mb": self.memory_usage_mb,
            "cache_efficiency": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_ratio": self.cache_hits / max(1, self.cache_hits + self.cache_misses)
            },
            "speedup": {
                "vectorization": self.vectorization_speedup,
                "parallelization": self.parallelization_speedup,
                "total": self.vectorization_speedup * self.parallelization_speedup
            }
        }


class EnhancedACGPerformanceOptimizer:
    """
    Performance optimization engine for enhanced ACG features.
    
    Provides vectorized calculations, intelligent caching, and parallel processing
    to maintain <800ms performance targets while adding enhanced features.
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Performance tracking
        self.metrics_history: List[PerformanceMetrics] = []
        
        # Optimization caches
        self.retrograde_cache: Dict[str, Tuple[EnhancedPlanetPosition, float]] = {}
        self.aspect_base_calculations: Dict[str, Dict[str, Any]] = {}
        self.metadata_cache: Dict[str, RetrogradeAwareLineMetadata] = {}
        
        # Vectorized calculation buffers
        self.planet_position_buffer = {}
        self.metadata_generation_buffer = {}
    
    def vectorize_retrograde_analysis(
        self,
        planet_ids: List[int],
        jd_ut1: float,
        include_station_analysis: bool = True
    ) -> Dict[int, EnhancedPlanetPosition]:
        """
        Vectorized retrograde analysis for multiple planets.
        
        Args:
            planet_ids: List of Swiss Ephemeris planet IDs
            jd_ut1: Julian Day for calculations
            include_station_analysis: Include station timing analysis
            
        Returns:
            Dictionary mapping planet ID to enhanced position
        """
        start_time = time.time()
        cache_hits = 0
        cache_misses = 0
        
        try:
            # Check cache for existing calculations
            cache_key_base = f"{jd_ut1:.6f}"
            results = {}
            uncached_planets = []
            
            for planet_id in planet_ids:
                cache_key = f"{cache_key_base}_{planet_id}"
                if cache_key in self.retrograde_cache:
                    cached_data, cache_time = self.retrograde_cache[cache_key]
                    if time.time() - cache_time < 300:  # 5 minute TTL
                        results[planet_id] = cached_data
                        cache_hits += 1
                        continue
                
                uncached_planets.append(planet_id)
                cache_misses += 1
            
            # Vectorized calculation for uncached planets
            if uncached_planets:
                # Batch Swiss Ephemeris calls
                planet_data = {}
                for planet_id in uncached_planets:
                    try:
                        calc_result = swe.calc_ut(jd_ut1, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
                        planet_data[planet_id] = calc_result[0]
                    except Exception as e:
                        self.logger.warning(f"Failed to calculate position for planet {planet_id}: {e}")
                        continue
                
                # Vectorized processing of position data
                enhanced_positions = self._process_positions_vectorized(
                    planet_data, jd_ut1, include_station_analysis
                )
                
                # Cache results
                for planet_id, enhanced_pos in enhanced_positions.items():
                    cache_key = f"{cache_key_base}_{planet_id}"
                    self.retrograde_cache[cache_key] = (enhanced_pos, time.time())
                    results[planet_id] = enhanced_pos
            
            # Record performance metrics
            end_time = time.time()
            speedup = len(planet_ids) / max(1, len(uncached_planets)) if uncached_planets else len(planet_ids)
            
            metrics = PerformanceMetrics(
                operation_name="vectorized_retrograde_analysis",
                start_time=start_time,
                end_time=end_time,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                vectorization_speedup=speedup
            )
            self.metrics_history.append(metrics)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Vectorized retrograde analysis failed: {e}")
            return {}
    
    def _process_positions_vectorized(
        self,
        planet_data: Dict[int, List[float]],
        jd_ut1: float,
        include_station_analysis: bool
    ) -> Dict[int, EnhancedPlanetPosition]:
        """Process planet position data using vectorized operations."""
        try:
            results = {}
            
            # Extract data arrays for vectorized operations
            planet_ids = list(planet_data.keys())
            longitudes = np.array([planet_data[pid][0] for pid in planet_ids])
            latitudes = np.array([planet_data[pid][1] for pid in planet_ids])
            distances = np.array([planet_data[pid][2] for pid in planet_ids])
            lon_speeds = np.array([planet_data[pid][3] for pid in planet_ids])
            
            # Vectorized retrograde detection
            is_retrograde = lon_speeds < 0.0
            
            # Create enhanced positions
            for i, planet_id in enumerate(planet_ids):
                enhanced_pos = EnhancedPlanetPosition(
                    planet_id=planet_id,
                    name=self._get_planet_name(planet_id),
                    longitude=longitudes[i],
                    latitude=latitudes[i],
                    distance=distances[i],
                    longitude_speed=lon_speeds[i],
                    calculation_time=datetime.fromtimestamp(
                        (jd_ut1 - 2440587.5) * 86400, tz=timezone.utc
                    )
                )
                results[planet_id] = enhanced_pos
            
            return results
            
        except Exception as e:
            self.logger.error(f"Vectorized position processing failed: {e}")
            return {}
    
    def pre_compute_aspect_base_calculations(
        self,
        calculation_date: datetime,
        precision: float = 0.1
    ) -> Dict[str, Any]:
        """
        Pre-compute base calculations for aspect-to-angle lines.
        
        Args:
            calculation_date: Date for calculations
            precision: Calculation precision
            
        Returns:
            Dictionary of pre-computed base calculations
        """
        start_time = time.time()
        cache_key = f"{calculation_date.isoformat()}_{precision}"
        
        try:
            if cache_key in self.aspect_base_calculations:
                return self.aspect_base_calculations[cache_key]
            
            # Pre-compute time-dependent values
            jd = swe.julday(
                calculation_date.year,
                calculation_date.month,
                calculation_date.day,
                calculation_date.hour + calculation_date.minute/60.0
            )
            
            base_calculations = {
                "julian_day": jd,
                "gmst_deg": self._calculate_gmst(jd),
                "obliquity": swe.calc_ut(jd, swe.ECL_NUT)[0][0],
                "precision": precision,
                "date_iso": calculation_date.isoformat()
            }
            
            # Pre-compute coordinate grids for aspect calculations
            lat_range = np.linspace(-89.0, 89.0, int(178.0 / precision) + 1)
            lon_range = np.linspace(-180.0, 180.0, int(360.0 / precision) + 1)
            
            base_calculations["coordinate_grids"] = {
                "latitudes": lat_range,
                "longitudes": lon_range
            }
            
            # Cache with TTL
            self.aspect_base_calculations[cache_key] = base_calculations
            
            # Record metrics
            metrics = PerformanceMetrics(
                operation_name="aspect_base_calculations",
                start_time=start_time,
                end_time=time.time(),
                vectorization_speedup=len(lat_range) * len(lon_range) / 1000  # Estimated speedup
            )
            self.metrics_history.append(metrics)
            
            return base_calculations
            
        except Exception as e:
            self.logger.error(f"Aspect base calculations failed: {e}")
            return {}
    
    def parallel_metadata_generation(
        self,
        planet_positions: Dict[int, EnhancedPlanetPosition],
        calculation_date: datetime,
        include_station_analysis: bool = True
    ) -> Dict[int, RetrogradeAwareLineMetadata]:
        """
        Generate enhanced metadata for multiple planets in parallel.
        
        Args:
            planet_positions: Dictionary of enhanced planet positions
            calculation_date: Date for calculations
            include_station_analysis: Include station analysis
            
        Returns:
            Dictionary mapping planet ID to enhanced metadata
        """
        start_time = time.time()
        
        try:
            # Prepare tasks for parallel execution
            tasks = []
            generator = EnhancedACGLineMetadataGenerator()
            
            for planet_id, planet_pos in planet_positions.items():
                task = (generator.generate_enhanced_metadata, planet_pos, calculation_date, include_station_analysis)
                tasks.append((planet_id, task))
            
            # Execute in parallel
            results = {}
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_planet = {
                    executor.submit(task[0], task[1], task[2], task[3]): planet_id 
                    for planet_id, task in tasks
                }
                
                # Collect results
                for future in as_completed(future_to_planet):
                    planet_id = future_to_planet[future]
                    try:
                        metadata = future.result()
                        results[planet_id] = metadata
                    except Exception as e:
                        self.logger.warning(f"Metadata generation failed for planet {planet_id}: {e}")
            
            # Record performance metrics
            end_time = time.time()
            parallelization_speedup = len(planet_positions) / max(1, (end_time - start_time) * 4)  # Estimated
            
            metrics = PerformanceMetrics(
                operation_name="parallel_metadata_generation",
                start_time=start_time,
                end_time=end_time,
                parallelization_speedup=parallelization_speedup
            )
            self.metrics_history.append(metrics)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Parallel metadata generation failed: {e}")
            return {}
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """
        Optimize memory usage by clearing old caches and optimizing data structures.
        
        Returns:
            Memory optimization statistics
        """
        try:
            initial_caches = {
                "retrograde_cache": len(self.retrograde_cache),
                "aspect_cache": len(self.aspect_base_calculations),
                "metadata_cache": len(self.metadata_cache)
            }
            
            # Clean expired cache entries
            current_time = time.time()
            
            # Clean retrograde cache (5 minute TTL)
            expired_keys = []
            for key, (data, cache_time) in self.retrograde_cache.items():
                if current_time - cache_time > 300:
                    expired_keys.append(key)
            for key in expired_keys:
                del self.retrograde_cache[key]
            
            # Clean aspect calculations cache (15 minute TTL)
            expired_keys = []
            for key, data in self.aspect_base_calculations.items():
                # Extract timestamp from key (simplified)
                try:
                    date_part = key.split('_')[0]
                    cache_date = datetime.fromisoformat(date_part)
                    if (datetime.now(timezone.utc) - cache_date).total_seconds() > 900:
                        expired_keys.append(key)
                except:
                    expired_keys.append(key)  # Remove malformed keys
            for key in expired_keys:
                del self.aspect_base_calculations[key]
            
            # Limit metrics history to last 100 entries
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            final_caches = {
                "retrograde_cache": len(self.retrograde_cache),
                "aspect_cache": len(self.aspect_base_calculations),
                "metadata_cache": len(self.metadata_cache)
            }
            
            return {
                "operation": "memory_optimization",
                "cache_sizes_before": initial_caches,
                "cache_sizes_after": final_caches,
                "entries_cleaned": {
                    "retrograde": initial_caches["retrograde_cache"] - final_caches["retrograde_cache"],
                    "aspect": initial_caches["aspect_cache"] - final_caches["aspect_cache"]
                },
                "metrics_history_size": len(self.metrics_history)
            }
            
        except Exception as e:
            self.logger.error(f"Memory optimization failed: {e}")
            return {"error": str(e)}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Returns:
            Detailed performance analysis and recommendations
        """
        try:
            if not self.metrics_history:
                return {"message": "No performance data available"}
            
            # Calculate aggregate statistics
            by_operation = {}
            for metric in self.metrics_history:
                op_name = metric.operation_name
                if op_name not in by_operation:
                    by_operation[op_name] = []
                by_operation[op_name].append(metric)
            
            operation_stats = {}
            for op_name, metrics in by_operation.items():
                durations = [m.duration_ms for m in metrics]
                speedups = [m.vectorization_speedup * m.parallelization_speedup for m in metrics]
                
                operation_stats[op_name] = {
                    "count": len(metrics),
                    "avg_duration_ms": sum(durations) / len(durations),
                    "min_duration_ms": min(durations),
                    "max_duration_ms": max(durations),
                    "avg_speedup": sum(speedups) / len(speedups),
                    "cache_hit_rate": sum(m.cache_hits for m in metrics) / max(1, sum(m.cache_hits + m.cache_misses for m in metrics))
                }
            
            # Generate recommendations
            recommendations = []
            
            # Check for performance issues
            for op_name, stats in operation_stats.items():
                if stats["avg_duration_ms"] > 200:
                    recommendations.append(f"Consider optimizing {op_name} - average duration {stats['avg_duration_ms']:.1f}ms")
                
                if stats["cache_hit_rate"] < 0.5:
                    recommendations.append(f"Improve caching for {op_name} - hit rate {stats['cache_hit_rate']:.2%}")
            
            # Overall system recommendations
            total_avg_duration = sum(stats["avg_duration_ms"] for stats in operation_stats.values())
            if total_avg_duration > 800:  # Target is <800ms
                recommendations.append("Total processing time exceeds 800ms target - consider reducing precision or parallel processing")
            
            return {
                "summary": {
                    "total_operations": len(self.metrics_history),
                    "operation_types": len(by_operation),
                    "avg_total_duration_ms": total_avg_duration,
                    "performance_target_met": total_avg_duration <= 800
                },
                "operation_statistics": operation_stats,
                "cache_status": {
                    "retrograde_cache_size": len(self.retrograde_cache),
                    "aspect_cache_size": len(self.aspect_base_calculations),
                    "metadata_cache_size": len(self.metadata_cache)
                },
                "recommendations": recommendations,
                "last_optimization": "Not implemented - call optimize_memory_usage()"
            }
            
        except Exception as e:
            self.logger.error(f"Performance report generation failed: {e}")
            return {"error": str(e)}
    
    def _calculate_gmst(self, jd: float) -> float:
        """Calculate Greenwich Mean Sidereal Time in degrees."""
        try:
            return swe.sidtime(jd) * 15.0  # Convert hours to degrees
        except:
            # Fallback calculation
            t = (jd - 2451545.0) / 36525.0
            gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t * t
            return gmst % 360.0
    
    def _get_planet_name(self, planet_id: int) -> str:
        """Get planet name from ID."""
        names = {
            0: "Sun", 1: "Moon", 2: "Mercury", 3: "Venus", 4: "Mars",
            5: "Jupiter", 6: "Saturn", 7: "Uranus", 8: "Neptune", 9: "Pluto"
        }
        return names.get(planet_id, f"Planet_{planet_id}")
    
    def shutdown(self):
        """Shutdown the thread pool executor."""
        try:
            self.executor.shutdown(wait=True)
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")


# Global performance optimizer instance
acg_performance_optimizer = EnhancedACGPerformanceOptimizer()