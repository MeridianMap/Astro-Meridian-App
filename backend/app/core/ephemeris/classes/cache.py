"""
Meridian Ephemeris Engine - Thread-Safe Cache Module

Provides high-performance, thread-safe caching for ephemeris calculations
with TTL (Time To Live) support and configurable size limits.
"""

import hashlib
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple, Union


class CacheEntry:
    """Individual cache entry with TTL support."""
    
    def __init__(self, value: Any, ttl: Optional[float] = None) -> None:
        """Initialize cache entry with optional TTL."""
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 1
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self) -> Any:
        """Mark entry as accessed and return value."""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value


class EphemerisCache:
    """Thread-safe LRU cache with TTL support for ephemeris calculations."""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = 3600) -> None:
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of entries to cache
            default_ttl: Default TTL in seconds (None for no expiration)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a hash key from arguments."""
        # Convert all arguments to a string representation
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _evict_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            self._evictions += 1
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._cache:
            self._cache.popitem(last=False)  # Remove oldest entry
            self._evictions += 1
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache by key."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired():
                    del self._cache[key]
                    self._misses += 1
                    return None
                
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                self._hits += 1
                return entry.touch()
            
            self._misses += 1
            return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put value into cache with optional TTL."""
        with self._lock:
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Remove expired entries periodically
            if len(self._cache) % 100 == 0:  # Every 100th operation
                self._evict_expired()
            
            # Evict LRU if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            # Add or update entry
            self._cache[key] = CacheEntry(value, ttl)
            self._cache.move_to_end(key)  # Mark as most recently used
    
    def cached_call(self, func, *args, ttl: Optional[float] = None, **kwargs) -> Any:
        """
        Cache the result of a function call.
        
        Args:
            func: Function to call
            *args: Function arguments
            ttl: TTL for this specific cache entry
            **kwargs: Function keyword arguments
        
        Returns:
            Function result (cached or fresh)
        """
        # Generate cache key including function name
        key = self._generate_key(func.__name__, *args, **kwargs)
        
        # Try to get from cache first
        cached_result = self.get(key)
        if cached_result is not None:
            return cached_result
        
        # Call function and cache result
        result = func(*args, **kwargs)
        self.put(key, result, ttl)
        return result
    
    def invalidate(self, key: str) -> bool:
        """Remove specific key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Remove all keys containing the pattern."""
        with self._lock:
            keys_to_remove = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self._cache[key]
            return len(keys_to_remove)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
    
    def cleanup(self) -> int:
        """Remove all expired entries and return count."""
        with self._lock:
            initial_size = len(self._cache)
            self._evict_expired()
            return initial_size - len(self._cache)
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def is_full(self) -> bool:
        """Check if cache is at maximum capacity."""
        with self._lock:
            return len(self._cache) >= self.max_size
    
    def stats(self) -> Dict[str, Union[int, float]]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'evictions': self._evictions,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }
    
    def keys(self) -> list:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache (does not count as access)."""
        with self._lock:
            return key in self._cache and not self._cache[key].is_expired()
    
    def __len__(self) -> int:
        """Get cache size."""
        return self.size()


class CacheDecorator:
    """Decorator for automatic function result caching."""
    
    def __init__(self, cache: Optional[EphemerisCache] = None, ttl: Optional[float] = None):
        """
        Initialize cache decorator.
        
        Args:
            cache: Cache instance to use (creates new if None)
            ttl: TTL for cached results
        """
        # Important: don't use truthiness here because EphemerisCache defines __len__,
        # which makes empty caches evaluate to False. Use explicit None check.
        self.cache = cache if cache is not None else EphemerisCache()
        self.ttl = ttl
    
    def __call__(self, func):
        """Decorate function with caching."""
        def wrapper(*args, **kwargs):
            # Build a cache key consistent with EphemerisCache
            key = self.cache._generate_key(func.__name__, *args, **kwargs)  # type: ignore[attr-defined]

            # Try cache first
            cached_value = self.cache.get(key)
            if cached_value is not None:
                return cached_value

            # Compute and store
            result = func(*args, **kwargs)
            self.cache.put(key, result, ttl=self.ttl)
            return result
        
        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.cache = self.cache  # Expose cache for manual management
        
        return wrapper


# Global cache instance for the ephemeris engine
_global_cache: Optional[EphemerisCache] = None
_cache_lock = threading.Lock()


def get_global_cache() -> EphemerisCache:
    """Get or create the global cache instance."""
    global _global_cache
    
    if _global_cache is None:
        with _cache_lock:
            if _global_cache is None:
                # Import settings here to avoid circular imports
                try:
                    from ..settings import settings
                    max_size = settings.cache_size
                    ttl = settings.cache_ttl if settings.enable_cache else None
                except ImportError:
                    max_size = 1000
                    ttl = 3600
                
                _global_cache = EphemerisCache(max_size=max_size, default_ttl=ttl)
    
    return _global_cache


def reset_global_cache() -> None:
    """Reset the global cache instance."""
    global _global_cache
    with _cache_lock:
        if _global_cache is not None:
            _global_cache.clear()


def cached(ttl: Optional[float] = None):
    """
    Decorator for caching function results using global cache.
    
    Args:
        ttl: TTL for cached results (uses global setting if None)
    
    Example:
        @cached(ttl=300)  # Cache for 5 minutes
        def expensive_calculation(a, b):
            return a ** b
    """
    return CacheDecorator(cache=get_global_cache(), ttl=ttl)