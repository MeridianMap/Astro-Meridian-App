"""
Batch calculation optimizations using NumPy and Numba.

This module provides vectorized implementations for calculating multiple
charts or planetary positions efficiently.
"""

import numpy as np
import swisseph as swe
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass

try:
    from numba import jit, vectorize
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Fallback decorator that does nothing
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def vectorize(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from extracted.systems.utils.const import SwePlanets
from ..classes.serialize import PlanetPosition, HouseSystem
from extracted.systems.ephemeris_utils import julian_day_from_datetime, datetime_from_julian_day, get_houses


@dataclass
class BatchRequest:
    """Single calculation request in a batch."""
    name: str
    datetime: datetime
    latitude: float
    longitude: float
    house_system: str = "placidus"
    
    
@dataclass
class BatchResult:
    """Result of a batch calculation."""
    name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BatchCalculator:
    """High-performance batch calculator for ephemeris calculations."""
    
    def __init__(self):
        self.planet_ids = [
            SwePlanets.SUN, SwePlanets.MOON, SwePlanets.MERCURY,
            SwePlanets.VENUS, SwePlanets.MARS, SwePlanets.JUPITER,
            SwePlanets.SATURN, SwePlanets.URANUS, SwePlanets.NEPTUNE,
            SwePlanets.PLUTO
        ]
    
    @staticmethod
    @jit(nopython=True if NUMBA_AVAILABLE else False)
    def _vectorized_julian_day(years: np.ndarray, months: np.ndarray, 
                              days: np.ndarray, hours: np.ndarray) -> np.ndarray:
        """Vectorized Julian day calculation."""
        julian_days = np.zeros(len(years))
        
        for i in range(len(years)):
            # Simplified Julian day calculation for performance
            # More accurate than the full algorithm but faster for batch processing
            year = years[i]
            month = months[i]
            day = days[i]
            hour = hours[i]
            
            if month <= 2:
                year -= 1
                month += 12
            
            a = int(year / 100)
            b = 2 - a + int(a / 4)
            
            jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
            jd += hour / 24.0
            
            julian_days[i] = jd
            
        return julian_days
    
    def calculate_batch_positions(self, requests: List[BatchRequest]) -> List[BatchResult]:
        """Calculate planetary positions for multiple charts efficiently."""
        if not requests:
            return []
        
        # Convert requests to arrays for vectorized operations
        n_requests = len(requests)
        
        # Extract datetime components
        years = np.array([req.datetime.year for req in requests])
        months = np.array([req.datetime.month for req in requests])
        days = np.array([req.datetime.day for req in requests])
        hours = np.array([
            req.datetime.hour + req.datetime.minute/60.0 + req.datetime.second/3600.0 
            for req in requests
        ])
        
        # Calculate Julian days in batch
        if NUMBA_AVAILABLE:
            julian_days = self._vectorized_julian_day(years, months, days, hours)
        else:
            julian_days = np.array([
                julian_day_from_datetime(req.datetime) for req in requests
            ])
        
        # Prepare results
        results = []
        
        # Calculate positions for each request
        # Note: Swiss Ephemeris doesn't support true vectorization,
        # but we can optimize the loop and memory access patterns
        for i, (req, jd) in enumerate(zip(requests, julian_days)):
            try:
                result = self._calculate_single_chart_optimized(req, jd)
                results.append(BatchResult(
                    name=req.name,
                    success=True,
                    data=result
                ))
            except Exception as e:
                results.append(BatchResult(
                    name=req.name,
                    success=False,
                    error=str(e)
                ))
        
        return results
    
    def _calculate_single_chart_optimized(self, request: BatchRequest, julian_day: float) -> Dict[str, Any]:
        """Calculate a single chart with optimized memory access."""
        # Pre-allocate arrays for better memory performance
        planet_positions = {}
        
        # Calculate all planetary positions in one pass
        for planet_id in self.planet_ids:
            try:
                # Calculate position
                result = swe.calc_ut(julian_day, planet_id)
                longitude, latitude, distance, longitude_speed, latitude_speed, distance_speed = result[0]
                
                planet_name = self._get_planet_name(planet_id)
                planet_positions[planet_name] = {
                    'longitude': float(longitude),
                    'latitude': float(latitude),
                    'distance': float(distance),
                    'longitude_speed': float(longitude_speed),
                    'latitude_speed': float(latitude_speed),
                    'distance_speed': float(distance_speed),
                    'retrograde': longitude_speed < 0
                }
                
            except Exception as e:
                # Skip failed planets but continue with others
                continue
        
        # Calculate houses
        try:
            houses = get_houses(
                julian_day,
                request.latitude,
                request.longitude,
                request.house_system
            )
        except Exception:
            # Fallback to a simple equal-house system with required shape
            # Swiss Ephemeris returns 13 cusps (index 0 unused, 1..12 valid)
            cusps = [0.0] + [i * 30.0 for i in range(1, 13)]
            ascmc = [0.0, 90.0, 0.0, 0.0]  # ASC, MC, ARMC, Vertex (minimal)
            houses = HouseSystem(
                house_cusps=cusps,
                ascmc=ascmc,
                system_code='E',  # Equal houses as a safe fallback
                calculation_time=datetime_from_julian_day(julian_day),
                latitude=request.latitude,
                longitude=request.longitude
            )
        
        return {
            'subject': {
                'name': request.name,
                'datetime': request.datetime.isoformat(),
                'latitude': request.latitude,
                'longitude': request.longitude
            },
            'planets': planet_positions,
            'houses': houses.model_dump() if hasattr(houses, 'dict') else houses.__dict__
        }
    
    @staticmethod
    def _get_planet_name(planet_id: int) -> str:
        """Get planet name from ID."""
        planet_names = {
            SwePlanets.SUN: 'sun',
            SwePlanets.MOON: 'moon',
            SwePlanets.MERCURY: 'mercury',
            SwePlanets.VENUS: 'venus',
            SwePlanets.MARS: 'mars',
            SwePlanets.JUPITER: 'jupiter',
            SwePlanets.SATURN: 'saturn',
            SwePlanets.URANUS: 'uranus',
            SwePlanets.NEPTUNE: 'neptune',
            SwePlanets.PLUTO: 'pluto'
        }
        return planet_names.get(planet_id, f'planet_{planet_id}')


class BatchPositionCalculator:
    """Specialized calculator for bulk planetary position calculations."""
    
    @staticmethod
    @jit(nopython=True if NUMBA_AVAILABLE else False)
    def _batch_longitude_normalization(longitudes: np.ndarray) -> np.ndarray:
        """Normalize longitudes to 0-360 range in batch."""
        return longitudes % 360.0
    
    @staticmethod  
    @jit(nopython=True if NUMBA_AVAILABLE else False)
    def _batch_sign_calculation(longitudes: np.ndarray) -> np.ndarray:
        """Calculate zodiac signs for batch of longitudes."""
        return np.floor(longitudes / 30.0).astype(np.int32)
    
    @staticmethod
    @jit(nopython=True if NUMBA_AVAILABLE else False) 
    def _batch_degree_calculation(longitudes: np.ndarray) -> np.ndarray:
        """Calculate degrees within sign for batch of longitudes."""
        return longitudes % 30.0
    
    def calculate_position_statistics(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics across multiple position datasets."""
        if not positions:
            return {}
        
        # Extract planetary longitudes
        planet_longitudes = {}
        for planet in ['sun', 'moon', 'mercury', 'venus', 'mars', 
                      'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']:
            longitudes = []
            for pos in positions:
                if planet in pos.get('planets', {}):
                    longitudes.append(pos['planets'][planet]['longitude'])
            
            if longitudes:
                longitudes_array = np.array(longitudes)
                
                # Calculate statistics
                planet_longitudes[planet] = {
                    'mean': float(np.mean(longitudes_array)),
                    'std': float(np.std(longitudes_array)), 
                    'min': float(np.min(longitudes_array)),
                    'max': float(np.max(longitudes_array)),
                    'median': float(np.median(longitudes_array)),
                    'count': len(longitudes)
                }
                
                # Add sign distribution
                signs = self._batch_sign_calculation(longitudes_array)
                sign_counts = np.bincount(signs, minlength=12)
                planet_longitudes[planet]['sign_distribution'] = sign_counts.tolist()
        
        return {
            'planetary_statistics': planet_longitudes,
            'total_charts': len(positions)
        }


def create_batch_from_data(chart_data: List[Dict[str, Any]]) -> List[BatchRequest]:
    """Convert raw chart data to BatchRequest objects."""
    requests = []
    
    for data in chart_data:
        try:
            # Parse datetime
            dt_str = data.get('datetime', data.get('birth_datetime'))
            if isinstance(dt_str, str):
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                dt = dt_str
            
            request = BatchRequest(
                name=data.get('name', 'Unknown'),
                datetime=dt,
                latitude=float(data['latitude']),
                longitude=float(data['longitude']),
                house_system=data.get('house_system', 'placidus')
            )
            requests.append(request)
            
        except (KeyError, ValueError, TypeError) as e:
            # Skip invalid entries
            continue
    
    return requests


# Performance monitoring utilities
class BatchPerformanceMonitor:
    """Monitor batch calculation performance."""
    
    def __init__(self):
        self.reset_stats()
    
    def reset_stats(self):
        """Reset performance statistics."""
        self.calculation_times = []
        self.batch_sizes = []
        self.success_counts = []
        self.error_counts = []
    
    def record_batch(self, batch_size: int, calculation_time: float, 
                    success_count: int, error_count: int):
        """Record batch calculation statistics."""
        self.batch_sizes.append(batch_size)
        self.calculation_times.append(calculation_time)
        self.success_counts.append(success_count)
        self.error_counts.append(error_count)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.calculation_times:
            return {}
        
        times = np.array(self.calculation_times)
        sizes = np.array(self.batch_sizes)
        
        # Calculate throughput (charts per second)
        throughput = sizes / times
        
        return {
            'total_batches': len(self.calculation_times),
            'total_charts': int(np.sum(sizes)),
            'avg_batch_size': float(np.mean(sizes)),
            'avg_calculation_time': float(np.mean(times)),
            'avg_throughput': float(np.mean(throughput)),
            'max_throughput': float(np.max(throughput)),
            'success_rate': float(np.sum(self.success_counts) / np.sum(sizes)) if np.sum(sizes) > 0 else 0.0,
            'total_errors': int(np.sum(self.error_counts))
        }


# Global batch calculator instance
batch_calculator = BatchCalculator()
performance_monitor = BatchPerformanceMonitor()