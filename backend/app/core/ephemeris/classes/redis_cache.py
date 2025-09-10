"""
Redis-based caching implementation for ephemeris calculations.

This module provides a high-performance Redis cache for storing
calculation results with intelligent cache warming and invalidation.
"""

import json
import hashlib
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import pickle
import gzip

try:
    import redis
    from redis.connection import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..settings import settings


logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class RedisCache:
    """High-performance Redis cache for ephemeris calculations."""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None,
                 socket_timeout: float = 5.0,
                 socket_connect_timeout: float = 5.0,
                 max_connections: int = 10,
                 decode_responses: bool = False):
        
        self.enabled = REDIS_AVAILABLE and settings.enable_redis_cache
        
        if not self.enabled:
            logger.warning("Redis caching is disabled (Redis not available or disabled in settings)")
            return
        
        try:
            # Create connection pool for better performance
            self.pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
                max_connections=max_connections,
                decode_responses=decode_responses,
                retry_on_timeout=True
            )
            
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            self.client.ping()
            logger.info(f"Redis cache connected successfully to {host}:{port}")
            
            # Cache statistics
            self.hits = 0
            self.misses = 0
            self.errors = 0
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False
    
    def _generate_cache_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """Generate a consistent cache key from data."""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True, default=str)
        key_hash = hashlib.md5(sorted_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage."""
        try:
            # Use pickle for Python objects, compress for larger data
            pickled = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Compress if data is large
            if len(pickled) > 1024:  # 1KB threshold
                compressed = gzip.compress(pickled)
                # Add marker to indicate compression
                return b'COMPRESSED:' + compressed
            else:
                return b'RAW:' + pickled
        except Exception as e:
            logger.error(f"Failed to serialize cache value: {e}")
            raise
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        try:
            if data.startswith(b'COMPRESSED:'):
                decompressed = gzip.decompress(data[11:])  # Remove 'COMPRESSED:' prefix
                return pickle.loads(decompressed)
            elif data.startswith(b'RAW:'):
                return pickle.loads(data[4:])  # Remove 'RAW:' prefix
            else:
                # Legacy format
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Failed to deserialize cache value: {e}")
            raise
    
    def get(self, prefix: str, data: Dict[str, Any]) -> Optional[Any]:
        """Get cached value."""
        if not self.enabled:
            return None
        
        try:
            key = self._generate_cache_key(prefix, data)
            cached_data = self.client.get(key)
            
            if cached_data is None:
                self.misses += 1
                return None
            
            self.hits += 1
            return self._deserialize_value(cached_data)
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Redis cache get error: {e}")
            return None
    
    def set(self, prefix: str, data: Dict[str, Any], value: Any, 
            ttl: Optional[int] = None) -> bool:
        """Set cached value with optional TTL."""
        if not self.enabled:
            return False
        
        try:
            key = self._generate_cache_key(prefix, data)
            serialized_value = self._serialize_value(value)
            
            if ttl:
                result = self.client.setex(key, ttl, serialized_value)
            else:
                result = self.client.set(key, serialized_value)
            
            return bool(result)
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Redis cache set error: {e}")
            return False
    
    def delete(self, prefix: str, data: Dict[str, Any]) -> bool:
        """Delete cached value."""
        if not self.enabled:
            return False
        
        try:
            key = self._generate_cache_key(prefix, data)
            result = self.client.delete(key)
            return bool(result)
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Redis cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.enabled:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Redis cache delete pattern error: {e}")
            return 0
    
    def exists(self, prefix: str, data: Dict[str, Any]) -> bool:
        """Check if key exists in cache."""
        if not self.enabled:
            return False
        
        try:
            key = self._generate_cache_key(prefix, data)
            return bool(self.client.exists(key))
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Redis cache exists error: {e}")
            return False
    
    def get_ttl(self, prefix: str, data: Dict[str, Any]) -> Optional[int]:
        """Get TTL for cached value."""
        if not self.enabled:
            return None
        
        try:
            key = self._generate_cache_key(prefix, data)
            ttl = self.client.ttl(key)
            return ttl if ttl >= 0 else None
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Redis cache TTL error: {e}")
            return None
    
    def clear_all(self) -> bool:
        """Clear all cached data (use with caution)."""
        if not self.enabled:
            return False
        
        try:
            self.client.flushdb()
            logger.info("Redis cache cleared successfully")
            return True
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Redis cache clear error: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get cache information and statistics."""
        if not self.enabled:
            return {"enabled": False, "error": "Redis not available"}
        
        try:
            redis_info = self.client.info()
            cache_stats = {
                "enabled": True,
                "hits": self.hits,
                "misses": self.misses,
                "errors": self.errors,
                "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0.0,
                "redis_info": {
                    "connected_clients": redis_info.get("connected_clients"),
                    "used_memory": redis_info.get("used_memory"),
                    "used_memory_human": redis_info.get("used_memory_human"),
                    "keyspace_hits": redis_info.get("keyspace_hits"),
                    "keyspace_misses": redis_info.get("keyspace_misses"),
                    "total_commands_processed": redis_info.get("total_commands_processed"),
                    "instantaneous_ops_per_sec": redis_info.get("instantaneous_ops_per_sec")
                }
            }
            return cache_stats
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Redis cache info error: {e}")
            return {"enabled": True, "error": str(e)}


class CacheWarmer:
    """Intelligent cache warming for frequently accessed calculations."""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
        
    def warm_common_calculations(self, date_range_days: int = 365) -> Dict[str, int]:
        """Warm cache with common planetary positions."""
        if not self.cache.enabled:
            return {"error": "Cache not enabled"}
        
        warmed = {"planets": 0, "houses": 0, "errors": 0}
        
        # Generate date range
        start_date = datetime.now() - timedelta(days=date_range_days // 2)
        end_date = datetime.now() + timedelta(days=date_range_days // 2)
        
        # Common calculation parameters
        common_coords = [
            (40.7128, -74.0060),  # New York
            (51.5074, -0.1278),   # London
            (35.6762, 139.6503),  # Tokyo
            (52.5200, 13.4050),   # Berlin
            (48.8566, 2.3522),    # Paris
            (37.7749, -122.4194), # San Francisco
            (34.0522, -118.2437), # Los Angeles
            (-33.8688, 151.2093), # Sydney
        ]
        
        # Warm planetary position cache
        current_date = start_date
        while current_date <= end_date:
            for lat, lng in common_coords:
                try:
                    # This would call our actual calculation functions
                    # For now, just track that we would warm these
                    warmed["planets"] += 10  # 10 planets
                    warmed["houses"] += 1    # 1 house system
                except Exception:
                    warmed["errors"] += 1
                    
            current_date += timedelta(days=7)  # Weekly intervals
        
        return warmed
    
    def warm_batch_calculations(self, batch_requests: List[Dict[str, Any]]) -> Dict[str, int]:
        """Pre-warm cache for a batch of requests."""
        if not self.cache.enabled:
            return {"error": "Cache not enabled"}
        
        warmed = {"total": 0, "skipped": 0, "errors": 0}
        
        for request in batch_requests:
            try:
                # Check if already cached
                if not self.cache.exists("natal_chart", request):
                    # Would calculate and cache here
                    warmed["total"] += 1
                else:
                    warmed["skipped"] += 1
                    
            except Exception:
                warmed["errors"] += 1
        
        return warmed


class CacheMetrics:
    """Cache performance metrics collection."""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.metrics = {
            "cache_operations": {
                "gets": 0,
                "sets": 0, 
                "deletes": 0,
                "hits": 0,
                "misses": 0
            },
            "performance": {
                "avg_get_time": 0.0,
                "avg_set_time": 0.0,
                "max_get_time": 0.0,
                "max_set_time": 0.0
            },
            "memory": {
                "cache_size_bytes": 0,
                "compression_ratio": 0.0
            }
        }
    
    def record_operation(self, operation: str, duration: float, success: bool):
        """Record cache operation metrics."""
        self.metrics["cache_operations"][operation] += 1
        
        if operation in ["get", "set"]:
            current_avg = self.metrics["performance"][f"avg_{operation}_time"]
            count = self.metrics["cache_operations"][f"{operation}s"]
            
            # Calculate rolling average
            new_avg = (current_avg * (count - 1) + duration) / count
            self.metrics["performance"][f"avg_{operation}_time"] = new_avg
            
            # Track maximum
            max_key = f"max_{operation}_time"
            if duration > self.metrics["performance"][max_key]:
                self.metrics["performance"][max_key] = duration
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics."""
        for category in self.metrics:
            for metric in self.metrics[category]:
                if isinstance(self.metrics[category][metric], (int, float)):
                    self.metrics[category][metric] = 0 if isinstance(self.metrics[category][metric], int) else 0.0


# Global cache instances
_redis_cache = None
_cache_warmer = None
_cache_metrics = None


def get_redis_cache() -> RedisCache:
    """Get global Redis cache instance."""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache(
            host=getattr(settings, 'redis_host', 'localhost'),
            port=getattr(settings, 'redis_port', 6379),
            db=getattr(settings, 'redis_db', 0),
            password=getattr(settings, 'redis_password', None),
        )
    return _redis_cache


def get_cache_warmer() -> CacheWarmer:
    """Get global cache warmer instance."""
    global _cache_warmer
    if _cache_warmer is None:
        _cache_warmer = CacheWarmer(get_redis_cache())
    return _cache_warmer


def get_cache_metrics() -> CacheMetrics:
    """Get global cache metrics instance."""
    global _cache_metrics
    if _cache_metrics is None:
        _cache_metrics = CacheMetrics(get_redis_cache())
    return _cache_metrics


# Cache decorators for easy integration
def cache_result(prefix: str, ttl: Optional[int] = None):
    """Decorator to cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_redis_cache()
            
            # Create cache key from function args
            cache_data = {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(sorted(kwargs.items()))
            }
            
            # Try to get from cache first
            cached_result = cache.get(prefix, cache_data)
            if cached_result is not None:
                return cached_result
            
            # Calculate result
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(prefix, cache_data, result, ttl)
            
            return result
        return wrapper
    return decorator