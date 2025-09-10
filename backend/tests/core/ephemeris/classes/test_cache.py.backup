"""
Unit tests for the Meridian Ephemeris Engine cache module.
"""

import time
import threading
import pytest
from unittest.mock import patch

from app.core.ephemeris.classes.cache import (
    CacheEntry, EphemerisCache, CacheDecorator, cached,
    get_global_cache, reset_global_cache
)


class TestCacheEntry:
    """Test the CacheEntry class."""
    
    def test_cache_entry_creation(self):
        """Test cache entry creation and basic properties."""
        value = "test_value"
        entry = CacheEntry(value)
        
        assert entry.value == value
        assert entry.ttl is None
        assert entry.access_count == 1
        assert isinstance(entry.created_at, float)
        assert entry.last_accessed == entry.created_at
    
    def test_cache_entry_with_ttl(self):
        """Test cache entry with TTL."""
        value = "test_value"
        ttl = 10.0
        entry = CacheEntry(value, ttl)
        
        assert entry.ttl == ttl
        assert not entry.is_expired()
        
        # Mock time to test expiration
        with patch('time.time', return_value=entry.created_at + ttl + 1):
            assert entry.is_expired()
    
    def test_cache_entry_touch(self):
        """Test cache entry access tracking."""
        entry = CacheEntry("test")
        original_access_count = entry.access_count
        original_last_accessed = entry.last_accessed
        
        time.sleep(0.001)  # Small delay to ensure different timestamp
        
        value = entry.touch()
        
        assert value == "test"
        assert entry.access_count == original_access_count + 1
        assert entry.last_accessed > original_last_accessed


class TestEphemerisCache:
    """Test the EphemerisCache class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cache = EphemerisCache(max_size=5, default_ttl=10.0)
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        assert self.cache.max_size == 5
        assert self.cache.default_ttl == 10.0
        assert self.cache.size() == 0
        assert not self.cache.is_full()
    
    def test_basic_put_get(self):
        """Test basic cache put and get operations."""
        key = "test_key"
        value = "test_value"
        
        # Initially empty
        assert self.cache.get(key) is None
        
        # Put and retrieve
        self.cache.put(key, value)
        assert self.cache.get(key) == value
        assert self.cache.size() == 1
    
    def test_cache_statistics(self):
        """Test cache hit/miss statistics."""
        key = "test_key"
        value = "test_value"
        
        # Initial stats
        stats = self.cache.stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['hit_rate'] == 0.0
        
        # Miss
        self.cache.get(key)
        stats = self.cache.stats()
        assert stats['misses'] == 1
        
        # Put and hit
        self.cache.put(key, value)
        self.cache.get(key)
        stats = self.cache.stats()
        assert stats['hits'] == 1
        assert stats['hit_rate'] == 0.5  # 1 hit out of 2 total requests
    
    def test_cache_eviction(self):
        """Test LRU cache eviction when at capacity."""
        # Fill cache to capacity
        for i in range(5):
            self.cache.put(f"key_{i}", f"value_{i}")
        
        assert self.cache.size() == 5
        assert self.cache.is_full()
        
        # Add one more item (should evict oldest)
        self.cache.put("new_key", "new_value")
        
        assert self.cache.size() == 5  # Still at max
        assert self.cache.get("key_0") is None  # First item evicted
        assert self.cache.get("new_key") == "new_value"
    
    def test_ttl_expiration(self):
        """Test TTL-based expiration."""
        key = "test_key"
        value = "test_value"
        short_ttl = 0.1
        
        self.cache.put(key, value, ttl=short_ttl)
        assert self.cache.get(key) == value
        
        # Wait for expiration
        time.sleep(short_ttl + 0.05)
        
        assert self.cache.get(key) is None
    
    def test_lru_ordering(self):
        """Test LRU ordering with access patterns."""
        # Fill cache
        for i in range(5):
            self.cache.put(f"key_{i}", f"value_{i}")
        
        # Access key_0 to make it most recently used
        self.cache.get("key_0")
        
        # Add new item (should evict key_1, not key_0)
        self.cache.put("new_key", "new_value")
        
        assert self.cache.get("key_0") == "value_0"  # Still present
        assert self.cache.get("key_1") is None  # Evicted
    
    def test_cache_invalidation(self):
        """Test cache key invalidation."""
        key = "test_key"
        value = "test_value"
        
        self.cache.put(key, value)
        assert self.cache.get(key) == value
        
        # Invalidate specific key
        result = self.cache.invalidate(key)
        assert result is True
        assert self.cache.get(key) is None
        
        # Try to invalidate non-existent key
        result = self.cache.invalidate("non_existent")
        assert result is False
    
    def test_pattern_invalidation(self):
        """Test pattern-based cache invalidation."""
        # Add various keys
        self.cache.put("user_1_data", "data1")
        self.cache.put("user_2_data", "data2")
        self.cache.put("system_config", "config")
        self.cache.put("user_3_profile", "profile")
        
        # Invalidate all user-related keys
        count = self.cache.invalidate_pattern("user_")
        assert count == 3
        
        # Check results
        assert self.cache.get("user_1_data") is None
        assert self.cache.get("user_2_data") is None
        assert self.cache.get("user_3_profile") is None
        assert self.cache.get("system_config") == "config"  # Not invalidated
    
    def test_cache_clear(self):
        """Test cache clearing."""
        # Add items
        for i in range(3):
            self.cache.put(f"key_{i}", f"value_{i}")
        
        assert self.cache.size() == 3
        
        # Clear cache
        self.cache.clear()
        
        assert self.cache.size() == 0
        stats = self.cache.stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        short_ttl = 0.1
        
        # Add items with short TTL
        for i in range(3):
            self.cache.put(f"key_{i}", f"value_{i}", ttl=short_ttl)
        
        # Add one item without TTL
        self.cache.put("persistent", "value")
        
        assert self.cache.size() == 4
        
        # Wait for expiration
        time.sleep(short_ttl + 0.05)
        
        # Cleanup expired items
        cleaned_count = self.cache.cleanup()
        assert cleaned_count == 3
        assert self.cache.size() == 1
        assert self.cache.get("persistent") == "value"
    
    def test_cached_call(self):
        """Test cached function call functionality."""
        call_count = 0
        
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call should execute function
        result1 = self.cache.cached_call(expensive_function, 1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call with same args should return cached result
        result2 = self.cache.cached_call(expensive_function, 1, 2)
        assert result2 == 3
        assert call_count == 1  # Function not called again
        
        # Different args should call function
        result3 = self.cache.cached_call(expensive_function, 2, 3)
        assert result3 == 5
        assert call_count == 2
    
    def test_thread_safety(self):
        """Test thread safety of cache operations."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(50):
                    key = f"worker_{worker_id}_item_{i}"
                    value = f"value_{worker_id}_{i}"
                    
                    # Put item
                    self.cache.put(key, value)
                    
                    # Get item
                    retrieved = self.cache.get(key)
                    
                    # Verify consistency
                    if retrieved != value:
                        errors.append(f"Worker {worker_id}, item {i}: expected {value}, got {retrieved}")
                    else:
                        results.append((worker_id, i, True))
            except Exception as e:
                errors.append(f"Worker {worker_id}: {str(e)}")
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"


class TestCacheDecorator:
    """Test the CacheDecorator class."""
    
    def test_decorator_basic_functionality(self):
        """Test basic decorator functionality."""
        call_count = 0
        
        @CacheDecorator()
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = test_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call (should be cached)
        result2 = test_function(5)
        assert result2 == 10
        assert call_count == 1
        
        # Different argument
        result3 = test_function(10)
        assert result3 == 20
        assert call_count == 2
    
    def test_decorator_with_custom_cache(self):
        """Test decorator with custom cache instance."""
        custom_cache = EphemerisCache(max_size=2)
        
        @CacheDecorator(cache=custom_cache)
        def test_function(x):
            return x ** 2
        
        # Use the function
        assert test_function(2) == 4
        assert test_function(3) == 9
        
        # Check custom cache was used
        assert custom_cache.size() == 2
    
    def test_decorator_ttl(self):
        """Test decorator with TTL."""
        call_count = 0
        
        @CacheDecorator(ttl=0.1)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 3
        
        # First call
        result1 = test_function(4)
        assert result1 == 12
        assert call_count == 1
        
        # Second call (cached)
        result2 = test_function(4)
        assert result2 == 12
        assert call_count == 1
        
        # Wait for expiration
        time.sleep(0.15)
        
        # Third call (should execute again)
        result3 = test_function(4)
        assert result3 == 12
        assert call_count == 2


class TestCachedDecorator:
    """Test the @cached decorator."""
    
    def test_cached_decorator_default(self):
        """Test @cached decorator with default settings."""
        call_count = 0
        
        @cached()
        def test_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call
        result1 = test_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call (cached)
        result2 = test_function(1, 2)
        assert result2 == 3
        assert call_count == 1
    
    def test_cached_decorator_with_ttl(self):
        """Test @cached decorator with custom TTL."""
        call_count = 0
        
        @cached(ttl=0.1)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 4
        
        # Test caching and expiration
        assert test_function(5) == 20
        assert call_count == 1
        
        assert test_function(5) == 20  # Cached
        assert call_count == 1
        
        time.sleep(0.15)  # Wait for expiration
        
        assert test_function(5) == 20  # Re-executed
        assert call_count == 2


class TestGlobalCache:
    """Test global cache functionality."""
    
    def setup_method(self):
        """Reset global cache before each test."""
        reset_global_cache()
    
    def test_global_cache_singleton(self):
        """Test global cache singleton behavior."""
        cache1 = get_global_cache()
        cache2 = get_global_cache()
        
        assert cache1 is cache2
    
    def test_global_cache_functionality(self):
        """Test global cache basic functionality."""
        cache = get_global_cache()
        
        cache.put("test", "value")
        assert cache.get("test") == "value"
    
    def test_global_cache_reset(self):
        """Test global cache reset functionality."""
        cache = get_global_cache()
        cache.put("test", "value")
        
        assert cache.get("test") == "value"
        
        reset_global_cache()
        
        # Should still be the same instance but cleared
        same_cache = get_global_cache()
        assert same_cache is cache
        assert same_cache.get("test") is None
    
    def test_cached_decorator_uses_global_cache(self):
        """Test that @cached uses global cache."""
        call_count = 0
        
        @cached()
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x
        
        # Call function
        test_function(10)
        assert call_count == 1
        
        # Check global cache has the result
        global_cache = get_global_cache()
        assert global_cache.size() > 0
        
        # Call again (should use cache)
        test_function(10)
        assert call_count == 1