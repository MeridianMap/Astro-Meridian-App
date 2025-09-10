"""
Production Optimization Features
Production-ready performance features for horizontal scaling and high availability.

Features:
- Connection pool management for databases and Redis
- Request deduplication to reduce redundant calculations
- Auto-scaling triggers based on system metrics
- Performance optimization middleware
- Resource monitoring and alerting
- Health checks and circuit breakers
- Request compression and response optimization
- Production-ready logging and monitoring

Performance Targets:
- Support 1000+ concurrent requests
- Sub-100ms response times under load
- 99.9% uptime with circuit breaker protection
- Automatic scaling based on resource usage
- Efficient connection pooling and reuse
"""

import time
import asyncio
import hashlib
import gzip
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import asynccontextmanager
import logging
import weakref
from collections import defaultdict, deque
import uuid

import redis
import asyncpg
from fastapi import Request, Response, HTTPException
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    # Fallback for older FastAPI versions
    from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import psutil
import asyncio

from app.core.performance.monitoring import get_performance_monitor, AlertSeverity
from app.core.performance.memory_optimizer import get_memory_manager

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class ScalingTrigger(str, Enum):
    """Auto-scaling trigger types."""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    QUEUE_DEPTH = "queue_depth"
    ERROR_RATE = "error_rate"
    CONCURRENT_REQUESTS = "concurrent_requests"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pools."""
    redis_max_connections: int = 50
    redis_min_connections: int = 5
    postgres_max_connections: int = 20
    postgres_min_connections: int = 5
    connection_timeout_seconds: int = 30
    idle_timeout_seconds: int = 300
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    health_check_interval_seconds: int = 60


@dataclass
class AutoScalingConfig:
    """Configuration for auto-scaling triggers."""
    cpu_scale_up_threshold: float = 80.0      # CPU % to scale up
    cpu_scale_down_threshold: float = 30.0    # CPU % to scale down
    memory_scale_up_threshold: float = 85.0   # Memory % to scale up
    memory_scale_down_threshold: float = 40.0 # Memory % to scale down
    response_time_threshold_ms: float = 200.0 # Response time to scale up
    queue_depth_threshold: int = 100          # Queue depth to scale up
    error_rate_threshold: float = 5.0         # Error rate % to scale up
    scale_check_interval_seconds: int = 60    # How often to check
    cooldown_period_seconds: int = 300        # Cooldown between scaling events
    min_replicas: int = 1
    max_replicas: int = 10


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker protection."""
    failure_threshold: int = 5                # Failures before opening
    timeout_seconds: int = 60                 # How long to stay open
    success_threshold: int = 3                # Successes to close from half-open
    monitoring_window_seconds: int = 60       # Window to count failures
    half_open_max_requests: int = 3           # Max requests in half-open state


class ProductionConnectionManager:
    """
    Production-grade connection pool manager.
    
    Manages database and Redis connections with health monitoring,
    automatic recovery, and connection pooling optimizations.
    """
    
    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self._redis_pools: Dict[str, redis.ConnectionPool] = {}
        self._postgres_pools: Dict[str, asyncpg.Pool] = {}
        self._pool_health: Dict[str, bool] = {}
        self._connection_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"created": 0, "reused": 0, "failed": 0, "active": 0}
        )
        self._lock = threading.RLock()
        self._monitoring = True
        self._monitor_task: Optional[asyncio.Task] = None
        
        logger.info("ProductionConnectionManager initialized")
    
    def get_redis_pool(
        self, 
        connection_name: str = "default",
        redis_url: str = "redis://localhost:6379"
    ) -> redis.ConnectionPool:
        """Get or create Redis connection pool."""
        with self._lock:
            if connection_name not in self._redis_pools:
                self._redis_pools[connection_name] = redis.ConnectionPool.from_url(
                    redis_url,
                    max_connections=self.config.redis_max_connections,
                    socket_connect_timeout=self.config.connection_timeout_seconds,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=self.config.health_check_interval_seconds,
                    retry_on_timeout=True
                )
                self._pool_health[f"redis_{connection_name}"] = True
                
            return self._redis_pools[connection_name]
    
    async def get_postgres_pool(
        self, 
        connection_name: str = "default",
        database_url: str = "postgresql://localhost/db"
    ) -> asyncpg.Pool:
        """Get or create PostgreSQL connection pool."""
        pool_key = f"postgres_{connection_name}"
        
        if connection_name not in self._postgres_pools:
            try:
                pool = await asyncpg.create_pool(
                    database_url,
                    min_size=self.config.postgres_min_connections,
                    max_size=self.config.postgres_max_connections,
                    command_timeout=self.config.connection_timeout_seconds,
                    server_settings={
                        'application_name': 'ephemeris_production',
                        'tcp_keepalives_idle': '600',
                        'tcp_keepalives_interval': '30',
                        'tcp_keepalives_count': '3',
                    }
                )
                
                self._postgres_pools[connection_name] = pool
                self._pool_health[pool_key] = True
                
                logger.info(f"Created PostgreSQL pool: {connection_name}")
                
            except Exception as e:
                logger.error(f"Failed to create PostgreSQL pool {connection_name}: {e}")
                self._pool_health[pool_key] = False
                raise
        
        return self._postgres_pools[connection_name]
    
    @asynccontextmanager
    async def get_redis_connection(self, connection_name: str = "default"):
        """Context manager for Redis connections with automatic cleanup."""
        pool = self.get_redis_pool(connection_name)
        connection = None
        
        try:
            connection = redis.Redis(connection_pool=pool)
            self._connection_stats[f"redis_{connection_name}"]["active"] += 1
            yield connection
            self._connection_stats[f"redis_{connection_name}"]["reused"] += 1
            
        except Exception as e:
            self._connection_stats[f"redis_{connection_name}"]["failed"] += 1
            self._pool_health[f"redis_{connection_name}"] = False
            logger.error(f"Redis connection error: {e}")
            raise
        finally:
            if connection:
                self._connection_stats[f"redis_{connection_name}"]["active"] -= 1
    
    @asynccontextmanager
    async def get_postgres_connection(self, connection_name: str = "default"):
        """Context manager for PostgreSQL connections with automatic cleanup."""
        pool = await self.get_postgres_pool(connection_name)
        connection = None
        
        try:
            connection = await pool.acquire()
            self._connection_stats[f"postgres_{connection_name}"]["active"] += 1
            yield connection
            self._connection_stats[f"postgres_{connection_name}"]["reused"] += 1
            
        except Exception as e:
            self._connection_stats[f"postgres_{connection_name}"]["failed"] += 1
            self._pool_health[f"postgres_{connection_name}"] = False
            logger.error(f"PostgreSQL connection error: {e}")
            raise
        finally:
            if connection:
                await pool.release(connection)
                self._connection_stats[f"postgres_{connection_name}"]["active"] -= 1
    
    async def health_check_all_pools(self) -> Dict[str, bool]:
        """Perform health check on all connection pools."""
        health_results = {}
        
        # Check Redis pools
        for name, pool in self._redis_pools.items():
            try:
                conn = redis.Redis(connection_pool=pool)
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, conn.ping),
                    timeout=5.0
                )
                health_results[f"redis_{name}"] = True
                self._pool_health[f"redis_{name}"] = True
            except Exception as e:
                logger.warning(f"Redis pool {name} health check failed: {e}")
                health_results[f"redis_{name}"] = False
                self._pool_health[f"redis_{name}"] = False
        
        # Check PostgreSQL pools
        for name, pool in self._postgres_pools.items():
            try:
                async with pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                health_results[f"postgres_{name}"] = True
                self._pool_health[f"postgres_{name}"] = True
            except Exception as e:
                logger.warning(f"PostgreSQL pool {name} health check failed: {e}")
                health_results[f"postgres_{name}"] = False
                self._pool_health[f"postgres_{name}"] = False
        
        return health_results
    
    def get_connection_stats(self) -> Dict[str, Dict[str, int]]:
        """Get connection usage statistics."""
        with self._lock:
            return dict(self._connection_stats)
    
    def get_pool_health(self) -> Dict[str, bool]:
        """Get pool health status."""
        return dict(self._pool_health)
    
    async def close_all_pools(self) -> None:
        """Close all connection pools."""
        # Close PostgreSQL pools
        for pool in self._postgres_pools.values():
            await pool.close()
        
        # Close Redis pools  
        for pool in self._redis_pools.values():
            pool.disconnect()
        
        self._redis_pools.clear()
        self._postgres_pools.clear()
        
        logger.info("All connection pools closed")


class RequestDeduplicator:
    """
    Request deduplication system to reduce redundant calculations.
    
    Identifies and coalesces identical requests to reduce computational load
    and improve response times for duplicate queries.
    """
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 10000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._pending_requests: Dict[str, asyncio.Event] = {}
        self._request_results: Dict[str, Tuple[Any, datetime]] = {}
        self._request_counts: Dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()
        
        # Cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_expired())
        
        logger.info("RequestDeduplicator initialized")
    
    def _generate_request_key(self, request_data: Dict[str, Any]) -> str:
        """Generate unique key for request deduplication."""
        # Normalize request data for consistent hashing
        normalized_data = self._normalize_request_data(request_data)
        
        # Create hash of normalized data
        request_json = json.dumps(normalized_data, sort_keys=True, default=str)
        return hashlib.sha256(request_json.encode()).hexdigest()
    
    def _normalize_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize request data for consistent deduplication."""
        normalized = {}
        
        for key, value in data.items():
            if key in ['timestamp', 'request_id', 'user_id']:
                continue  # Skip non-deterministic fields
            
            if isinstance(value, float):
                normalized[key] = round(value, 6)  # Round floats for consistency
            elif isinstance(value, dict):
                normalized[key] = self._normalize_request_data(value)
            elif isinstance(value, list):
                normalized[key] = [
                    self._normalize_request_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                normalized[key] = value
        
        return normalized
    
    async def deduplicate_request(
        self,
        request_key: str,
        calculation_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Deduplicate request execution.
        
        If identical request is already in progress, wait for its result.
        If identical request was recently completed, return cached result.
        """
        async with self._lock:
            # Check for cached result
            if request_key in self._request_results:
                result, timestamp = self._request_results[request_key]
                age = (datetime.now() - timestamp).total_seconds()
                
                if age < self.ttl_seconds:
                    self._request_counts[request_key] += 1
                    logger.debug(f"Request deduplication hit: {request_key}")
                    return result
                else:
                    # Remove expired result
                    del self._request_results[request_key]
            
            # Check if request is already in progress
            if request_key in self._pending_requests:
                logger.debug(f"Request already in progress, waiting: {request_key}")
                event = self._pending_requests[request_key]
                
                # Release lock while waiting
                async with self._lock:
                    pass
                
                # Wait for the in-progress request to complete
                await event.wait()
                
                # Get the result
                if request_key in self._request_results:
                    result, _ = self._request_results[request_key]
                    self._request_counts[request_key] += 1
                    return result
                else:
                    # Fallback: execute the request ourselves
                    pass
            
            # Create event for this request
            event = asyncio.Event()
            self._pending_requests[request_key] = event
        
        try:
            # Execute the calculation
            result = await calculation_func(*args, **kwargs)
            
            async with self._lock:
                # Cache the result
                self._request_results[request_key] = (result, datetime.now())
                self._request_counts[request_key] += 1
                
                # Clean up if cache is too large
                if len(self._request_results) > self.max_size:
                    await self._cleanup_oldest_entries()
                
                # Signal completion
                event.set()
                
                # Remove from pending
                del self._pending_requests[request_key]
            
            return result
            
        except Exception as e:
            async with self._lock:
                # Signal completion even on failure
                event.set()
                
                # Remove from pending
                if request_key in self._pending_requests:
                    del self._pending_requests[request_key]
            
            raise
    
    async def _cleanup_expired(self) -> None:
        """Background task to clean up expired entries."""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                
                current_time = datetime.now()
                expired_keys = []
                
                async with self._lock:
                    for key, (_, timestamp) in self._request_results.items():
                        age = (current_time - timestamp).total_seconds()
                        if age > self.ttl_seconds:
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self._request_results[key]
                        if key in self._request_counts:
                            del self._request_counts[key]
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired request cache entries")
                    
            except Exception as e:
                logger.error(f"Request deduplication cleanup error: {e}")
    
    async def _cleanup_oldest_entries(self) -> None:
        """Remove oldest entries when cache is full."""
        # Sort by timestamp and remove oldest 10%
        entries_to_remove = max(1, len(self._request_results) // 10)
        
        sorted_entries = sorted(
            self._request_results.items(),
            key=lambda x: x[1][1]  # Sort by timestamp
        )
        
        for i in range(entries_to_remove):
            key = sorted_entries[i][0]
            del self._request_results[key]
            if key in self._request_counts:
                del self._request_counts[key]
    
    def get_deduplication_stats(self) -> Dict[str, Any]:
        """Get deduplication effectiveness statistics."""
        total_requests = sum(self._request_counts.values())
        unique_requests = len(self._request_counts)
        
        if unique_requests > 0:
            deduplication_ratio = total_requests / unique_requests
        else:
            deduplication_ratio = 1.0
        
        return {
            "total_requests": total_requests,
            "unique_requests": unique_requests,
            "deduplication_ratio": deduplication_ratio,
            "cache_size": len(self._request_results),
            "pending_requests": len(self._pending_requests),
            "cache_hit_rate": max(0.0, 1.0 - (unique_requests / max(total_requests, 1)))
        }


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.
    
    Implements the circuit breaker pattern to prevent repeated calls
    to failing services and allow time for recovery.
    """
    
    def __init__(self, config: CircuitBreakerConfig, name: str = "default"):
        self.config = config
        self.name = name
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_requests = 0
        self.failure_times: deque = deque(maxlen=config.failure_threshold * 2)
        self._lock = threading.RLock()
        
        logger.info(f"CircuitBreaker '{name}' initialized")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        # Check if circuit should be opened
        await self._update_state()
        
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                raise HTTPException(
                    status_code=503,
                    detail=f"Circuit breaker '{self.name}' is OPEN - service unavailable"
                )
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.half_open_requests >= self.config.half_open_max_requests:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Circuit breaker '{self.name}' half-open request limit exceeded"
                    )
                self.half_open_requests += 1
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Record success
            with self._lock:
                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.success_count += 1
                    if self.success_count >= self.config.success_threshold:
                        self._transition_to_closed()
                else:
                    self.failure_count = 0  # Reset failure count on success
            
            return result
            
        except Exception as e:
            # Record failure
            with self._lock:
                self.failure_count += 1
                self.failure_times.append(datetime.now())
                self.last_failure_time = datetime.now()
                
                if self.state == CircuitBreakerState.CLOSED:
                    if self._should_trip():
                        self._transition_to_open()
                elif self.state == CircuitBreakerState.HALF_OPEN:
                    self._transition_to_open()
            
            raise
    
    async def _update_state(self) -> None:
        """Update circuit breaker state based on current conditions."""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self.last_failure_time:
                    time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
                    if time_since_failure >= self.config.timeout_seconds:
                        self._transition_to_half_open()
    
    def _should_trip(self) -> bool:
        """Check if circuit breaker should trip to OPEN state."""
        if self.failure_count >= self.config.failure_threshold:
            # Check if failures are within monitoring window
            now = datetime.now()
            window_start = now - timedelta(seconds=self.config.monitoring_window_seconds)
            
            recent_failures = sum(
                1 for failure_time in self.failure_times 
                if failure_time > window_start
            )
            
            return recent_failures >= self.config.failure_threshold
        
        return False
    
    def _transition_to_open(self) -> None:
        """Transition circuit breaker to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.half_open_requests = 0
        logger.warning(f"Circuit breaker '{self.name}' transitioned to OPEN")
    
    def _transition_to_half_open(self) -> None:
        """Transition circuit breaker to HALF_OPEN state."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.half_open_requests = 0
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")
    
    def _transition_to_closed(self) -> None:
        """Transition circuit breaker to CLOSED state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_requests = 0
        self.failure_times.clear()
        logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        with self._lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "half_open_requests": self.half_open_requests,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "recent_failures": len(self.failure_times)
            }


class AutoScaler:
    """
    Auto-scaling system based on system metrics and performance.
    
    Monitors system resources and application performance to trigger
    scaling events for maintaining optimal performance under load.
    """
    
    def __init__(self, config: AutoScalingConfig):
        self.config = config
        self.performance_monitor = get_performance_monitor()
        self.memory_manager = get_memory_manager()
        self.last_scale_event: Optional[datetime] = None
        self.current_replicas = 1
        self._monitoring = True
        self._monitor_task: Optional[asyncio.Task] = None
        self._scaling_callbacks: List[Callable[[str, int], None]] = []
        
        logger.info("AutoScaler initialized")
    
    def start_monitoring(self) -> None:
        """Start auto-scaling monitoring."""
        if self._monitor_task is None:
            self._monitor_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Auto-scaling monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop auto-scaling monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            self._monitor_task = None
        logger.info("Auto-scaling monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for auto-scaling decisions."""
        while self._monitoring:
            try:
                await self._check_scaling_conditions()
                await asyncio.sleep(self.config.scale_check_interval_seconds)
            except Exception as e:
                logger.error(f"Auto-scaling monitoring error: {e}")
                await asyncio.sleep(self.config.scale_check_interval_seconds)
    
    async def _check_scaling_conditions(self) -> None:
        """Check all scaling conditions and trigger scaling if needed."""
        # Check cooldown period
        if self.last_scale_event:
            time_since_scale = (datetime.now() - self.last_scale_event).total_seconds()
            if time_since_scale < self.config.cooldown_period_seconds:
                return  # Still in cooldown period
        
        # Get current metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_stats = self.memory_manager.monitor_memory_usage()
        memory_usage = memory_stats.memory_percent
        
        # Get performance metrics
        performance_metrics = self.performance_monitor.get_metrics_summary()
        avg_response_time = performance_metrics.get("response_time_p95_ms", 0)
        
        # Determine scaling action
        scale_action = await self._determine_scale_action(
            cpu_usage, memory_usage, avg_response_time
        )
        
        if scale_action:
            await self._execute_scaling(scale_action)
    
    async def _determine_scale_action(
        self,
        cpu_usage: float,
        memory_usage: float,
        avg_response_time: float
    ) -> Optional[str]:
        """Determine if scaling action is needed."""
        scale_up_triggers = []
        scale_down_triggers = []
        
        # CPU usage triggers
        if cpu_usage > self.config.cpu_scale_up_threshold:
            scale_up_triggers.append(f"CPU usage {cpu_usage:.1f}% > {self.config.cpu_scale_up_threshold}%")
        elif cpu_usage < self.config.cpu_scale_down_threshold:
            scale_down_triggers.append(f"CPU usage {cpu_usage:.1f}% < {self.config.cpu_scale_down_threshold}%")
        
        # Memory usage triggers
        if memory_usage > self.config.memory_scale_up_threshold:
            scale_up_triggers.append(f"Memory usage {memory_usage:.1f}% > {self.config.memory_scale_up_threshold}%")
        elif memory_usage < self.config.memory_scale_down_threshold:
            scale_down_triggers.append(f"Memory usage {memory_usage:.1f}% < {self.config.memory_scale_down_threshold}%")
        
        # Response time triggers
        if avg_response_time > self.config.response_time_threshold_ms:
            scale_up_triggers.append(f"Response time {avg_response_time:.1f}ms > {self.config.response_time_threshold_ms}ms")
        
        # Determine action based on triggers
        if scale_up_triggers and self.current_replicas < self.config.max_replicas:
            logger.info(f"Scale up triggered: {', '.join(scale_up_triggers)}")
            return "scale_up"
        elif scale_down_triggers and self.current_replicas > self.config.min_replicas:
            logger.info(f"Scale down triggered: {', '.join(scale_down_triggers)}")
            return "scale_down"
        
        return None
    
    async def _execute_scaling(self, action: str) -> None:
        """Execute scaling action."""
        if action == "scale_up":
            new_replicas = min(self.current_replicas + 1, self.config.max_replicas)
        elif action == "scale_down":
            new_replicas = max(self.current_replicas - 1, self.config.min_replicas)
        else:
            return
        
        if new_replicas != self.current_replicas:
            logger.info(f"Scaling {action}: {self.current_replicas} -> {new_replicas} replicas")
            
            # Notify scaling callbacks
            for callback in self._scaling_callbacks:
                try:
                    callback(action, new_replicas)
                except Exception as e:
                    logger.error(f"Scaling callback failed: {e}")
            
            self.current_replicas = new_replicas
            self.last_scale_event = datetime.now()
    
    def add_scaling_callback(self, callback: Callable[[str, int], None]) -> None:
        """Add callback for scaling events."""
        self._scaling_callbacks.append(callback)
    
    def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status."""
        return {
            "current_replicas": self.current_replicas,
            "min_replicas": self.config.min_replicas,
            "max_replicas": self.config.max_replicas,
            "last_scale_event": self.last_scale_event.isoformat() if self.last_scale_event else None,
            "monitoring_enabled": self._monitoring
        }


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Performance optimization middleware for production.
    
    Provides request/response optimization, compression, caching headers,
    and performance monitoring integration.
    """
    
    def __init__(self, app, enable_compression: bool = True, enable_etags: bool = True):
        super().__init__(app)
        self.enable_compression = enable_compression
        self.enable_etags = enable_etags
        self.performance_monitor = get_performance_monitor()
        self.request_deduplicator = RequestDeduplicator()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with performance optimizations."""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add request ID for tracking
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Apply performance optimizations
            response = await self._optimize_response(request, response)
            
            # Record performance metrics
            duration_ms = (time.time() - start_time) * 1000
            self.performance_monitor.track_calculation_performance(
                "api_request", duration_ms, True, str(request.url.path)
            )
            
            # Add performance headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
            
            return response
            
        except Exception as e:
            # Record failed request
            duration_ms = (time.time() - start_time) * 1000
            self.performance_monitor.track_calculation_performance(
                "api_request", duration_ms, False, str(request.url.path)
            )
            
            logger.error(f"Request {request_id} failed: {e}")
            raise
    
    async def _optimize_response(self, request: Request, response: Response) -> Response:
        """Apply response optimizations."""
        # Apply compression if enabled and appropriate
        if (self.enable_compression and 
            self._should_compress_response(request, response)):
            response = await self._compress_response(response)
        
        # Add caching headers
        response = self._add_cache_headers(response)
        
        # Add ETag if enabled
        if self.enable_etags:
            response = await self._add_etag(response)
        
        return response
    
    def _should_compress_response(self, request: Request, response: Response) -> bool:
        """Check if response should be compressed."""
        # Check Accept-Encoding header
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return False
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        compressible_types = [
            "application/json",
            "text/html",
            "text/plain",
            "application/javascript",
            "text/css"
        ]
        
        return any(ct in content_type for ct in compressible_types)
    
    async def _compress_response(self, response: Response) -> Response:
        """Compress response body."""
        if hasattr(response, 'body') and response.body:
            compressed_body = gzip.compress(response.body)
            
            # Only compress if it reduces size significantly
            if len(compressed_body) < len(response.body) * 0.9:
                response.body = compressed_body
                response.headers["Content-Encoding"] = "gzip"
                response.headers["Content-Length"] = str(len(compressed_body))
        
        return response
    
    def _add_cache_headers(self, response: Response) -> Response:
        """Add appropriate cache headers."""
        # Add cache control headers for API responses
        if response.status_code == 200:
            response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes
        else:
            response.headers["Cache-Control"] = "no-cache"
        
        return response
    
    async def _add_etag(self, response: Response) -> Response:
        """Add ETag header for caching."""
        if hasattr(response, 'body') and response.body:
            etag = hashlib.md5(response.body).hexdigest()
            response.headers["ETag"] = f'"{etag}"'
        
        return response


class ProductionOptimizationManager:
    """
    Comprehensive production optimization manager.
    
    Coordinates all production optimization features including connection
    pooling, request deduplication, auto-scaling, and circuit breakers.
    """
    
    def __init__(
        self,
        connection_config: Optional[ConnectionPoolConfig] = None,
        scaling_config: Optional[AutoScalingConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None
    ):
        self.connection_manager = ProductionConnectionManager(
            connection_config or ConnectionPoolConfig()
        )
        self.request_deduplicator = RequestDeduplicator()
        self.auto_scaler = AutoScaler(scaling_config or AutoScalingConfig())
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Default circuit breaker
        self.circuit_breakers["default"] = CircuitBreaker(
            circuit_breaker_config or CircuitBreakerConfig(),
            "default"
        )
        
        logger.info("ProductionOptimizationManager initialized")
    
    def get_circuit_breaker(self, name: str = "default") -> CircuitBreaker:
        """Get or create circuit breaker by name."""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                CircuitBreakerConfig(), name
            )
        return self.circuit_breakers[name]
    
    async def optimize_database_connections(self) -> Dict[str, Any]:
        """Optimize database connection pools."""
        health_status = await self.connection_manager.health_check_all_pools()
        connection_stats = self.connection_manager.get_connection_stats()
        
        optimization_results = {
            "pool_health": health_status,
            "connection_stats": connection_stats,
            "optimizations_applied": []
        }
        
        # Apply optimizations based on stats
        for pool_name, stats in connection_stats.items():
            if stats["failed"] > stats["reused"] * 0.1:  # More than 10% failure rate
                optimization_results["optimizations_applied"].append(
                    f"High failure rate detected for {pool_name}: {stats['failed']} failures"
                )
        
        return optimization_results
    
    def get_deduplication_effectiveness(self) -> Dict[str, Any]:
        """Get request deduplication effectiveness."""
        return self.request_deduplicator.get_deduplication_stats()
    
    async def start_auto_scaling(self) -> None:
        """Start auto-scaling monitoring."""
        self.auto_scaler.start_monitoring()
    
    async def stop_auto_scaling(self) -> None:
        """Stop auto-scaling monitoring."""
        self.auto_scaler.stop_monitoring()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        return {
            "connection_pools": self.connection_manager.get_pool_health(),
            "circuit_breakers": {
                name: cb.get_status()
                for name, cb in self.circuit_breakers.items()
            },
            "auto_scaling": self.auto_scaler.get_scaling_status(),
            "request_deduplication": self.request_deduplicator.get_deduplication_stats(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self) -> None:
        """Shutdown production optimization manager."""
        await self.connection_manager.close_all_pools()
        await self.auto_scaler.stop_monitoring()
        
        # Cancel cleanup tasks
        if hasattr(self.request_deduplicator, '_cleanup_task'):
            self.request_deduplicator._cleanup_task.cancel()
        
        logger.info("ProductionOptimizationManager shutdown complete")


# Global production optimization manager
_global_production_manager: Optional[ProductionOptimizationManager] = None
_production_manager_lock = asyncio.Lock()


async def get_production_manager() -> ProductionOptimizationManager:
    """Get or create global production optimization manager."""
    global _global_production_manager
    
    if _global_production_manager is None:
        async with _production_manager_lock:
            if _global_production_manager is None:
                _global_production_manager = ProductionOptimizationManager()
    
    return _global_production_manager


# Utility decorators for production features
def with_circuit_breaker(circuit_breaker_name: str = "default"):
    """Decorator to add circuit breaker protection to functions."""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            manager = await get_production_manager()
            circuit_breaker = manager.get_circuit_breaker(circuit_breaker_name)
            
            return await circuit_breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator


def with_request_deduplication(ttl_seconds: int = 300):
    """Decorator to add request deduplication to functions."""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            manager = await get_production_manager()
            
            # Generate request key from function arguments
            request_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            request_key = manager.request_deduplicator._generate_request_key(request_data)
            
            return await manager.request_deduplicator.deduplicate_request(
                request_key, func, *args, **kwargs
            )
        
        return wrapper
    return decorator