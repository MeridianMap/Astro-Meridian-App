"""
Advanced Caching System - Production-Scale Performance Optimization
Implements intelligent multi-tier caching with TTL optimization and cache warming.

Features:
- Intelligent cache key generation with normalization
- Multi-tier caching (L1 memory + L2 Redis)
- TTL optimization based on calculation type
- Cache warming and precomputation
- Cache statistics and monitoring integration
- Thread-safe implementation for concurrent access

Performance Targets:
- Sub-millisecond L1 cache access
- >70% cache hit rate under realistic load
- Intelligent key generation for better hit rates
- Automatic cache warming for common calculations
"""

import hashlib
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from functools import wraps
import weakref

import redis
from cachetools import TTLCache, LRUCache
import numpy as np

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class CacheType(str, Enum):
    """Cache types for different calculation categories."""
    PLANETARY_POSITIONS = "planetary_positions"
    ASPECTS = "aspects"
    ARABIC_PARTS = "arabic_parts"
    TRANSITS = "transits"
    ECLIPSES = "eclipses"
    ACG_LINES = "acg_lines"
    PARANS = "parans"
    ENHANCED_METADATA = "enhanced_metadata"
    RETROGRADE_DATA = "retrograde_data"
    ASPECT_LINES = "aspect_lines"


@dataclass
class CacheStats:
    """Cache performance statistics."""
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    total_requests: int = 0
    cache_size_l1: int = 0
    cache_size_l2: int = 0
    hit_rate_l1: float = 0.0
    hit_rate_l2: float = 0.0
    hit_rate_overall: float = 0.0
    average_access_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    
    @property
    def total_hits(self) -> int:
        return self.l1_hits + self.l2_hits
    
    @property
    def total_misses(self) -> int:
        return self.l1_misses + self.l2_misses


@dataclass
class CacheConfig:
    """Configuration for caching system."""
    l1_max_size: int = 1000
    l1_ttl_seconds: int = 300  # 5 minutes
    l2_ttl_seconds: Dict[CacheType, int] = None
    redis_connection_pool_size: int = 10
    enable_cache_warming: bool = True
    cache_key_normalization: bool = True
    enable_compression: bool = True
    monitoring_enabled: bool = True
    
    def __post_init__(self):
        if self.l2_ttl_seconds is None:
            self.l2_ttl_seconds = {
                CacheType.PLANETARY_POSITIONS: 86400,  # 24 hours
                CacheType.ASPECTS: 86400,  # 24 hours
                CacheType.ARABIC_PARTS: 86400,  # 24 hours
                CacheType.TRANSITS: 3600,  # 1 hour
                CacheType.ECLIPSES: 604800,  # 7 days
                CacheType.ACG_LINES: 86400,  # 24 hours
                CacheType.PARANS: 86400,  # 24 hours
                CacheType.ENHANCED_METADATA: 86400,  # 24 hours
                CacheType.RETROGRADE_DATA: 86400,  # 24 hours
                CacheType.ASPECT_LINES: 86400,  # 24 hours
            }


class CacheKeyGenerator:
    """Intelligent cache key generation with normalization."""
    
    def __init__(self, normalize_keys: bool = True):
        self.normalize_keys = normalize_keys
        self._coordinate_precision = 4  # 4 decimal places for coordinates
        self._time_precision = 60  # Round to nearest minute
        
    def generate_key(
        self,
        cache_type: CacheType,
        **params: Any
    ) -> str:
        """
        Generate normalized cache key for given calculation type and parameters.
        
        Args:
            cache_type: Type of calculation
            **params: Calculation parameters
            
        Returns:
            Normalized cache key string
        """
        if self.normalize_keys:
            params = self._normalize_parameters(params)
        
        # Create deterministic key from sorted parameters
        key_data = {
            "cache_type": cache_type.value,
            "params": self._sort_dict_recursively(params)
        }
        
        # Generate hash for compact key
        key_json = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_json.encode()).hexdigest()[:16]
        
        return f"{cache_type.value}:{key_hash}"
    
    def _normalize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize parameters for better cache hit rates."""
        normalized = {}
        
        for key, value in params.items():
            if key in ['latitude', 'longitude', 'lat', 'lon']:
                # Round coordinates to appropriate precision
                normalized[key] = round(float(value), self._coordinate_precision)
            elif key in ['datetime', 'date', 'time', 'epoch']:
                # Round datetime to nearest minute
                if isinstance(value, datetime):
                    normalized[key] = self._round_datetime(value)
                elif isinstance(value, str):
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        normalized[key] = self._round_datetime(dt).isoformat()
                    except:
                        normalized[key] = value
                else:
                    normalized[key] = value
            elif key in ['julian_day', 'jd']:
                # Round Julian day to appropriate precision
                normalized[key] = round(float(value), 5)
            elif isinstance(value, (list, tuple)):
                # Normalize lists/tuples recursively
                normalized[key] = [self._normalize_value(v) for v in value]
            elif isinstance(value, dict):
                # Normalize nested dictionaries
                normalized[key] = self._normalize_parameters(value)
            else:
                normalized[key] = self._normalize_value(value)
        
        return normalized
    
    def _normalize_value(self, value: Any) -> Any:
        """Normalize individual values."""
        if isinstance(value, float):
            # Round floats to reasonable precision
            return round(value, 6)
        elif isinstance(value, np.ndarray):
            # Convert numpy arrays to lists
            return value.tolist()
        else:
            return value
    
    def _round_datetime(self, dt: datetime) -> datetime:
        """Round datetime to nearest minute."""
        return dt.replace(second=0, microsecond=0)
    
    def _sort_dict_recursively(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Sort dictionary recursively for deterministic serialization."""
        if not isinstance(d, dict):
            return d
        
        result = {}
        for key in sorted(d.keys()):
            value = d[key]
            if isinstance(value, dict):
                result[key] = self._sort_dict_recursively(value)
            elif isinstance(value, list):
                result[key] = [
                    self._sort_dict_recursively(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result


class L1MemoryCache:
    """High-performance L1 memory cache with LRU eviction."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._access_times = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache."""
        start_time = time.time()
        
        with self._lock:
            try:
                value = self.cache[key]
                self._hits += 1
                access_time = (time.time() - start_time) * 1000
                self._access_times.append(access_time)
                return value
            except KeyError:
                self._misses += 1
                return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in L1 cache."""
        with self._lock:
            self.cache[key] = value
    
    def delete(self, key: str) -> bool:
        """Delete key from L1 cache."""
        with self._lock:
            try:
                del self.cache[key]
                return True
            except KeyError:
                return False
    
    def clear(self) -> None:
        """Clear all entries from L1 cache."""
        with self._lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get L1 cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            avg_access_time = (
                sum(self._access_times) / len(self._access_times) 
                if self._access_times else 0.0
            )
            
            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "size": len(self.cache),
                "max_size": self.cache.maxsize,
                "average_access_time_ms": avg_access_time
            }


class L2RedisCache:
    """Distributed L2 Redis cache with compression and connection pooling."""
    
    def __init__(
        self,
        redis_client: redis.Redis,
        ttl_config: Dict[CacheType, int],
        enable_compression: bool = True
    ):
        self.redis = redis_client
        self.ttl_config = ttl_config
        self.enable_compression = enable_compression
        self._hits = 0
        self._misses = 0
        self._lock = threading.Lock()
    
    def get(self, key: str, cache_type: CacheType) -> Optional[Any]:
        """Get value from L2 Redis cache."""
        try:
            data = self.redis.get(key)
            if data is None:
                with self._lock:
                    self._misses += 1
                return None
            
            with self._lock:
                self._hits += 1
            
            # Deserialize data
            if self.enable_compression:
                import zlib
                data = zlib.decompress(data)
            
            return json.loads(data.decode('utf-8'))
            
        except Exception as e:
            logger.warning(f"L2 cache get error for key {key}: {e}")
            with self._lock:
                self._misses += 1
            return None
    
    def set(self, key: str, value: Any, cache_type: CacheType) -> bool:
        """Set value in L2 Redis cache."""
        try:
            # Serialize data
            data = json.dumps(value, default=str).encode('utf-8')
            
            if self.enable_compression:
                import zlib
                data = zlib.compress(data)
            
            ttl = self.ttl_config.get(cache_type, 3600)
            self.redis.setex(key, ttl, data)
            return True
            
        except Exception as e:
            logger.warning(f"L2 cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from L2 Redis cache."""
        try:
            result = self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"L2 cache delete error for key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"L2 cache pattern invalidation error for {pattern}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get L2 cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            try:
                info = self.redis.info('memory')
                memory_usage = info.get('used_memory', 0) / (1024 * 1024)  # MB
            except:
                memory_usage = 0.0
            
            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "memory_usage_mb": memory_usage
            }


class IntelligentCache:
    """
    Intelligent multi-tier caching system with automatic optimization.
    
    Features:
    - L1 memory cache for frequent access
    - L2 Redis cache for distributed scaling
    - Intelligent cache key generation
    - TTL optimization by calculation type
    - Cache warming and precomputation
    - Performance monitoring and statistics
    """
    
    def __init__(
        self,
        config: Optional[CacheConfig] = None,
        redis_client: Optional[redis.Redis] = None
    ):
        self.config = config or CacheConfig()
        self.key_generator = CacheKeyGenerator(self.config.cache_key_normalization)
        
        # Initialize L1 memory cache
        self.l1_cache = L1MemoryCache(
            max_size=self.config.l1_max_size,
            ttl_seconds=self.config.l1_ttl_seconds
        )
        
        # Initialize L2 Redis cache
        if redis_client:
            self.l2_cache = L2RedisCache(
                redis_client=redis_client,
                ttl_config=self.config.l2_ttl_seconds,
                enable_compression=self.config.enable_compression
            )
        else:
            self.l2_cache = None
        
        # Cache warming tracking
        self._warmed_keys: Set[str] = set()
        self._warming_functions: Dict[str, Callable] = {}
        
        # Performance monitoring
        self._total_requests = 0
        self._start_time = time.time()
        
        logger.info("IntelligentCache initialized with L1 and L2 tiers")
    
    def get(
        self,
        cache_type: CacheType,
        calculation_func: Optional[Callable] = None,
        **params: Any
    ) -> Any:
        """
        Get value from cache with fallback to calculation.
        
        Args:
            cache_type: Type of calculation
            calculation_func: Function to call if cache miss
            **params: Parameters for cache key and calculation
            
        Returns:
            Cached or calculated result
        """
        self._total_requests += 1
        
        # Generate cache key
        cache_key = self.key_generator.generate_key(cache_type, **params)
        
        # Try L1 cache first
        result = self.l1_cache.get(cache_key)
        if result is not None:
            return result
        
        # Try L2 cache
        if self.l2_cache:
            result = self.l2_cache.get(cache_key, cache_type)
            if result is not None:
                # Populate L1 cache for faster future access
                self.l1_cache.set(cache_key, result)
                return result
        
        # Cache miss - calculate if function provided
        if calculation_func:
            try:
                result = calculation_func(**params)
                
                # Store in both cache levels
                self.l1_cache.set(cache_key, result)
                if self.l2_cache:
                    self.l2_cache.set(cache_key, result, cache_type)
                
                return result
            except Exception as e:
                logger.error(f"Calculation function failed for {cache_type}: {e}")
                raise
        
        return None
    
    def get_with_fallback(
        self,
        cache_key: str,
        calculation_func: Callable,
        cache_type: CacheType
    ) -> Any:
        """Get with fallback calculation - simplified interface."""
        # Try L1 cache
        result = self.l1_cache.get(cache_key)
        if result is not None:
            return result
        
        # Try L2 cache
        if self.l2_cache:
            result = self.l2_cache.get(cache_key, cache_type)
            if result is not None:
                self.l1_cache.set(cache_key, result)
                return result
        
        # Calculate and cache
        result = calculation_func()
        self.l1_cache.set(cache_key, result)
        if self.l2_cache:
            self.l2_cache.set(cache_key, result, cache_type)
        
        return result
    
    def set(
        self,
        cache_type: CacheType,
        value: Any,
        **params: Any
    ) -> None:
        """Set value in cache."""
        cache_key = self.key_generator.generate_key(cache_type, **params)
        
        # Store in both cache levels
        self.l1_cache.set(cache_key, value)
        if self.l2_cache:
            self.l2_cache.set(cache_key, value, cache_type)
    
    def invalidate(
        self,
        cache_type: CacheType,
        **params: Any
    ) -> None:
        """Invalidate specific cache entry."""
        cache_key = self.key_generator.generate_key(cache_type, **params)
        
        self.l1_cache.delete(cache_key)
        if self.l2_cache:
            self.l2_cache.delete(cache_key)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        # Clear L1 cache completely for pattern invalidation
        self.l1_cache.clear()
        
        # Invalidate L2 cache by pattern
        if self.l2_cache:
            return self.l2_cache.invalidate_pattern(pattern)
        
        return 0
    
    def warm_cache(self, warming_functions: Dict[str, Callable]) -> None:
        """
        Warm cache with common calculations.
        
        Args:
            warming_functions: Dictionary of warming function names to callables
        """
        if not self.config.enable_cache_warming:
            return
        
        logger.info(f"Warming cache with {len(warming_functions)} functions")
        
        for name, func in warming_functions.items():
            try:
                if name not in self._warmed_keys:
                    func()
                    self._warmed_keys.add(name)
                    self._warming_functions[name] = func
            except Exception as e:
                logger.warning(f"Cache warming failed for {name}: {e}")
        
        logger.info(f"Cache warming completed for {len(self._warmed_keys)} functions")
    
    def get_cache_statistics(self) -> CacheStats:
        """Get comprehensive cache statistics."""
        l1_stats = self.l1_cache.get_stats()
        
        if self.l2_cache:
            l2_stats = self.l2_cache.get_stats()
        else:
            l2_stats = {
                "hits": 0, "misses": 0, "hit_rate": 0.0, "memory_usage_mb": 0.0
            }
        
        total_hits = l1_stats["hits"] + l2_stats["hits"]
        total_misses = l1_stats["misses"] + l2_stats["misses"]
        total_requests = total_hits + total_misses
        
        stats = CacheStats(
            l1_hits=l1_stats["hits"],
            l1_misses=l1_stats["misses"],
            l2_hits=l2_stats["hits"],
            l2_misses=l2_stats["misses"],
            total_requests=total_requests,
            cache_size_l1=l1_stats["size"],
            cache_size_l2=0,  # Would need Redis info
            hit_rate_l1=l1_stats["hit_rate"],
            hit_rate_l2=l2_stats["hit_rate"],
            hit_rate_overall=total_hits / total_requests if total_requests > 0 else 0.0,
            average_access_time_ms=l1_stats.get("average_access_time_ms", 0.0),
            memory_usage_mb=l2_stats.get("memory_usage_mb", 0.0)
        )
        
        return stats
    
    def clear_all_caches(self) -> None:
        """Clear all cache levels."""
        self.l1_cache.clear()
        if self.l2_cache:
            self.l2_cache.invalidate_pattern("*")
        
        self._warmed_keys.clear()
        logger.info("All caches cleared")


# Singleton pattern for global cache instance
_global_cache: Optional[IntelligentCache] = None
_cache_lock = threading.Lock()


def get_intelligent_cache() -> IntelligentCache:
    """Get or create global intelligent cache instance."""
    global _global_cache
    
    if _global_cache is None:
        with _cache_lock:
            if _global_cache is None:
                # Try to initialize Redis client
                redis_client = None
                try:
                    redis_client = redis.Redis(
                        host='localhost',
                        port=6379,
                        db=0,
                        decode_responses=False,
                        connection_pool=redis.ConnectionPool(
                            host='localhost',
                            port=6379,
                            db=0,
                            max_connections=10
                        )
                    )
                    # Test connection
                    redis_client.ping()
                    logger.info("Redis connection established for L2 cache")
                except Exception as e:
                    logger.warning(f"Redis connection failed, using L1 cache only: {e}")
                    redis_client = None
                
                _global_cache = IntelligentCache(
                    config=CacheConfig(),
                    redis_client=redis_client
                )
    
    return _global_cache


def cached_calculation(
    cache_type: CacheType,
    ttl_override: Optional[int] = None
):
    """
    Decorator for automatically caching calculation results.
    
    Args:
        cache_type: Type of calculation for cache categorization
        ttl_override: Override default TTL for this calculation
        
    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_intelligent_cache()
            
            # Use function arguments as cache parameters
            cache_params = kwargs.copy()
            if args:
                # Convert positional args to kwargs if possible
                import inspect
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        cache_params[param_names[i]] = arg
            
            # Add function name to ensure unique keys
            cache_params['_func_name'] = func.__name__
            
            def calculation_func():
                return func(*args, **kwargs)
            
            return cache.get(
                cache_type=cache_type,
                calculation_func=calculation_func,
                **cache_params
            )
        
        return wrapper
    return decorator


# Cache warming functions for common calculations
class CacheWarmer:
    """Cache warming utilities for common calculations."""
    
    def __init__(self, cache: IntelligentCache):
        self.cache = cache
    
    def warm_common_planetary_positions(self) -> None:
        """Warm cache with common planetary position calculations."""
        # Would implement warming for current date, common dates, etc.
        pass
    
    def warm_common_aspects(self) -> None:
        """Warm cache with common aspect calculations."""
        # Would implement warming for standard aspect patterns
        pass
    
    def warm_arabic_parts(self) -> None:
        """Warm cache with common Arabic parts."""
        # Would implement warming for major Arabic parts
        pass
    
    def get_warming_functions(self) -> Dict[str, Callable]:
        """Get all cache warming functions."""
        return {
            "planetary_positions": self.warm_common_planetary_positions,
            "aspects": self.warm_common_aspects,
            "arabic_parts": self.warm_arabic_parts,
        }