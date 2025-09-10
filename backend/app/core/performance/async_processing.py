"""
Async Processing Architecture
High-performance async processing with streaming responses and background jobs.

Features:
- Async calculation processing with job queues
- Streaming responses for large datasets
- WebSocket support for real-time updates
- Background job processing with Celery integration
- Progress tracking and status updates
- Result persistence and retrieval
- Connection pooling for database operations
- Non-blocking Redis operations

Performance Targets:
- Support 100+ concurrent users without degradation
- Stream large results with minimal memory usage
- Background job processing for long-running calculations
- Real-time progress updates via WebSocket
- Efficient connection pooling and resource management
"""

import asyncio
import uuid
import json
import time
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from contextlib import asynccontextmanager
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import weakref

import aioredis
import asyncpg
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from celery import Celery
from pydantic import BaseModel

from app.core.performance.monitoring import get_performance_monitor

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(str, Enum):
    """Job priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AsyncJobConfig:
    """Configuration for async job processing."""
    max_workers: int = 10
    job_timeout_seconds: int = 3600  # 1 hour
    retry_attempts: int = 3
    retry_delay_seconds: int = 60
    result_ttl_seconds: int = 86400  # 24 hours
    enable_progress_tracking: bool = True
    enable_websocket_updates: bool = True
    redis_url: str = "redis://localhost:6379"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"


@dataclass
class JobProgress:
    """Job progress tracking."""
    job_id: str
    current_step: int = 0
    total_steps: int = 1
    message: str = ""
    percentage: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
    
    def update(
        self, 
        current_step: int, 
        message: str = "",
        estimated_completion: Optional[datetime] = None
    ) -> None:
        """Update progress information."""
        self.current_step = current_step
        self.message = message
        self.percentage = (current_step / max(self.total_steps, 1)) * 100
        self.last_updated = datetime.now()
        if estimated_completion:
            self.estimated_completion = estimated_completion


class AsyncResult(BaseModel):
    """Async operation result."""
    job_id: str
    status: JobStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConnectionPool:
    """Async connection pool manager for database and Redis operations."""
    
    def __init__(self):
        self._redis_pool: Optional[aioredis.ConnectionPool] = None
        self._postgres_pool: Optional[asyncpg.Pool] = None
        self._lock = asyncio.Lock()
        
    async def get_redis_connection(self, redis_url: str = "redis://localhost:6379") -> aioredis.Redis:
        """Get Redis connection from pool."""
        if self._redis_pool is None:
            async with self._lock:
                if self._redis_pool is None:
                    self._redis_pool = aioredis.ConnectionPool.from_url(
                        redis_url,
                        max_connections=20,
                        retry_on_timeout=True,
                        socket_keepalive=True
                    )
        
        return aioredis.Redis(connection_pool=self._redis_pool)
    
    async def get_postgres_connection(
        self, 
        database_url: str = "postgresql://user:password@localhost/db"
    ) -> asyncpg.Pool:
        """Get PostgreSQL connection pool."""
        if self._postgres_pool is None:
            async with self._lock:
                if self._postgres_pool is None:
                    self._postgres_pool = await asyncpg.create_pool(
                        database_url,
                        min_size=5,
                        max_size=20,
                        command_timeout=60
                    )
        
        return self._postgres_pool
    
    async def close_connections(self) -> None:
        """Close all connection pools."""
        if self._redis_pool:
            await self._redis_pool.disconnect()
        
        if self._postgres_pool:
            await self._postgres_pool.close()


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.job_subscriptions: Dict[str, Set[str]] = {}  # job_id -> set of connection_ids
        self._lock = threading.RLock()
        
    async def connect(self, websocket: WebSocket, connection_id: str) -> None:
        """Accept WebSocket connection."""
        await websocket.accept()
        
        with self._lock:
            if connection_id not in self.active_connections:
                self.active_connections[connection_id] = []
            self.active_connections[connection_id].append(websocket)
        
        logger.info(f"WebSocket connection established: {connection_id}")
    
    def disconnect(self, connection_id: str, websocket: WebSocket) -> None:
        """Remove WebSocket connection."""
        with self._lock:
            if connection_id in self.active_connections:
                try:
                    self.active_connections[connection_id].remove(websocket)
                    if not self.active_connections[connection_id]:
                        del self.active_connections[connection_id]
                except ValueError:
                    pass
        
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    def subscribe_to_job(self, connection_id: str, job_id: str) -> None:
        """Subscribe connection to job updates."""
        with self._lock:
            if job_id not in self.job_subscriptions:
                self.job_subscriptions[job_id] = set()
            self.job_subscriptions[job_id].add(connection_id)
    
    def unsubscribe_from_job(self, connection_id: str, job_id: str) -> None:
        """Unsubscribe connection from job updates."""
        with self._lock:
            if job_id in self.job_subscriptions:
                self.job_subscriptions[job_id].discard(connection_id)
                if not self.job_subscriptions[job_id]:
                    del self.job_subscriptions[job_id]
    
    async def broadcast_job_update(self, job_id: str, update: Dict[str, Any]) -> None:
        """Broadcast job update to subscribed connections."""
        message = json.dumps({
            "type": "job_update",
            "job_id": job_id,
            "data": update
        })
        
        with self._lock:
            if job_id not in self.job_subscriptions:
                return
            
            connection_ids = list(self.job_subscriptions[job_id])
        
        # Send to all subscribed connections
        for connection_id in connection_ids:
            await self._send_to_connection(connection_id, message)
    
    async def _send_to_connection(self, connection_id: str, message: str) -> None:
        """Send message to specific connection."""
        with self._lock:
            websockets = self.active_connections.get(connection_id, [])
        
        # Send to all WebSockets for this connection
        for websocket in websockets[:]:  # Copy list to avoid modification during iteration
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection_id, websocket)
            except Exception as e:
                logger.error(f"Failed to send WebSocket message: {e}")
                self.disconnect(connection_id, websocket)


class AsyncJobManager:
    """Manages async job execution with progress tracking and result storage."""
    
    def __init__(self, config: AsyncJobConfig):
        self.config = config
        self.connection_pool = ConnectionPool()
        self.websocket_manager = WebSocketManager()
        
        # Job tracking
        self.active_jobs: Dict[str, AsyncResult] = {}
        self.job_progress: Dict[str, JobProgress] = {}
        self._executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self._lock = threading.RLock()
        
        # Celery setup for background jobs
        self.celery_app = self._setup_celery()
        
        logger.info("AsyncJobManager initialized")
    
    def _setup_celery(self) -> Celery:
        """Setup Celery for background job processing."""
        celery_app = Celery(
            'ephemeris_async',
            broker=self.config.celery_broker_url,
            backend=self.config.celery_result_backend
        )
        
        celery_app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_track_started=True,
            task_time_limit=self.config.job_timeout_seconds,
            task_soft_time_limit=self.config.job_timeout_seconds - 60,
            worker_prefetch_multiplier=1,
            task_acks_late=True,
            worker_disable_rate_limits=False,
            task_default_retry_delay=self.config.retry_delay_seconds,
            task_max_retries=self.config.retry_attempts,
        )
        
        return celery_app
    
    async def submit_job(
        self,
        job_function: Callable,
        job_args: Tuple = (),
        job_kwargs: Dict[str, Any] = None,
        job_id: Optional[str] = None,
        priority: JobPriority = JobPriority.NORMAL,
        use_background: bool = False
    ) -> AsyncResult:
        """Submit job for async execution."""
        if job_id is None:
            job_id = str(uuid.uuid4())
        
        if job_kwargs is None:
            job_kwargs = {}
        
        # Create async result
        async_result = AsyncResult(
            job_id=job_id,
            status=JobStatus.PENDING,
            metadata={
                "priority": priority.value,
                "use_background": use_background,
                "submitted_at": datetime.now().isoformat()
            }
        )
        
        with self._lock:
            self.active_jobs[job_id] = async_result
        
        # Initialize progress tracking
        if self.config.enable_progress_tracking:
            self.job_progress[job_id] = JobProgress(job_id=job_id)
        
        if use_background:
            # Submit to Celery for background processing
            task = self.celery_app.send_task(
                'ephemeris_calculation',
                args=(job_function.__name__, job_args, job_kwargs),
                kwargs={'job_id': job_id},
                priority=self._get_celery_priority(priority)
            )
            async_result.metadata['celery_task_id'] = task.id
        else:
            # Submit to thread pool for immediate processing
            future = self._executor.submit(
                self._execute_job_wrapper,
                job_id, job_function, job_args, job_kwargs
            )
            async_result.metadata['future_id'] = id(future)
        
        # Store in Redis for persistence
        await self._store_job_result(async_result)
        
        logger.info(f"Job submitted: {job_id} (background={use_background})")
        return async_result
    
    async def get_job_status(self, job_id: str) -> Optional[AsyncResult]:
        """Get current job status."""
        # Check local cache first
        with self._lock:
            if job_id in self.active_jobs:
                return self.active_jobs[job_id]
        
        # Check Redis storage
        redis = await self.connection_pool.get_redis_connection()
        try:
            job_data = await redis.get(f"job_result:{job_id}")
            if job_data:
                return AsyncResult.parse_raw(job_data)
        except Exception as e:
            logger.error(f"Failed to get job status from Redis: {e}")
        
        return None
    
    async def get_job_progress(self, job_id: str) -> Optional[JobProgress]:
        """Get job progress information."""
        return self.job_progress.get(job_id)
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job."""
        async_result = await self.get_job_status(job_id)
        if not async_result:
            return False
        
        if async_result.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False  # Already finished
        
        # Cancel Celery task if background job
        if 'celery_task_id' in async_result.metadata:
            self.celery_app.control.revoke(
                async_result.metadata['celery_task_id'],
                terminate=True
            )
        
        # Update status
        async_result.status = JobStatus.CANCELLED
        async_result.completed_at = datetime.now()
        
        with self._lock:
            self.active_jobs[job_id] = async_result
        
        await self._store_job_result(async_result)
        await self._notify_job_update(job_id, {"status": JobStatus.CANCELLED})
        
        logger.info(f"Job cancelled: {job_id}")
        return True
    
    async def stream_results(self, job_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream job results as they become available."""
        while True:
            async_result = await self.get_job_status(job_id)
            if not async_result:
                yield {"error": "Job not found"}
                break
            
            yield {
                "job_id": job_id,
                "status": async_result.status.value,
                "progress": self.job_progress.get(job_id).__dict__ if job_id in self.job_progress else None
            }
            
            if async_result.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                yield {
                    "job_id": job_id,
                    "status": async_result.status.value,
                    "result": async_result.result,
                    "error": async_result.error,
                    "final": True
                }
                break
            
            # Wait before next update
            await asyncio.sleep(1.0)
    
    def _execute_job_wrapper(
        self,
        job_id: str,
        job_function: Callable,
        args: Tuple,
        kwargs: Dict[str, Any]
    ) -> Any:
        """Wrapper for job execution with progress tracking."""
        try:
            # Update status to running
            asyncio.create_task(self._update_job_status(job_id, JobStatus.RUNNING))
            
            # Execute the job function
            if self.config.enable_progress_tracking:
                # Inject progress callback if function supports it
                if 'progress_callback' in kwargs:
                    progress_callback = kwargs['progress_callback']
                else:
                    progress_callback = lambda current, total, message="": asyncio.create_task(
                        self._update_job_progress(job_id, current, total, message)
                    )
                    kwargs['progress_callback'] = progress_callback
            
            result = job_function(*args, **kwargs)
            
            # Update status to completed
            asyncio.create_task(self._update_job_status(job_id, JobStatus.COMPLETED, result))
            
            return result
            
        except Exception as e:
            logger.error(f"Job execution failed {job_id}: {e}")
            asyncio.create_task(self._update_job_status(job_id, JobStatus.FAILED, error=str(e)))
            raise
    
    async def _update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Any = None,
        error: Optional[str] = None
    ) -> None:
        """Update job status and notify subscribers."""
        with self._lock:
            if job_id in self.active_jobs:
                async_result = self.active_jobs[job_id]
                async_result.status = status
                
                if status == JobStatus.RUNNING and async_result.started_at is None:
                    async_result.started_at = datetime.now()
                
                if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    async_result.completed_at = datetime.now()
                
                if result is not None:
                    async_result.result = result
                
                if error is not None:
                    async_result.error = error
        
        # Store updated result
        await self._store_job_result(async_result)
        
        # Notify WebSocket subscribers
        await self._notify_job_update(job_id, {
            "status": status.value,
            "result": result,
            "error": error
        })
    
    async def _update_job_progress(
        self,
        job_id: str,
        current_step: int,
        total_steps: int,
        message: str = ""
    ) -> None:
        """Update job progress and notify subscribers."""
        if job_id in self.job_progress:
            progress = self.job_progress[job_id]
            progress.total_steps = total_steps
            progress.update(current_step, message)
            
            # Store progress in Redis
            redis = await self.connection_pool.get_redis_connection()
            try:
                await redis.setex(
                    f"job_progress:{job_id}",
                    3600,  # 1 hour TTL
                    json.dumps(asdict(progress), default=str)
                )
            except Exception as e:
                logger.error(f"Failed to store job progress: {e}")
            
            # Notify WebSocket subscribers
            await self._notify_job_update(job_id, {
                "progress": {
                    "current_step": current_step,
                    "total_steps": total_steps,
                    "percentage": progress.percentage,
                    "message": message
                }
            })
    
    async def _store_job_result(self, async_result: AsyncResult) -> None:
        """Store job result in Redis."""
        redis = await self.connection_pool.get_redis_connection()
        try:
            await redis.setex(
                f"job_result:{async_result.job_id}",
                self.config.result_ttl_seconds,
                async_result.model_dump_json()
            )
        except Exception as e:
            logger.error(f"Failed to store job result: {e}")
    
    async def _notify_job_update(self, job_id: str, update: Dict[str, Any]) -> None:
        """Notify WebSocket subscribers of job update."""
        if self.config.enable_websocket_updates:
            await self.websocket_manager.broadcast_job_update(job_id, update)
    
    def _get_celery_priority(self, priority: JobPriority) -> int:
        """Convert job priority to Celery priority."""
        priority_mapping = {
            JobPriority.LOW: 1,
            JobPriority.NORMAL: 5,
            JobPriority.HIGH: 7,
            JobPriority.CRITICAL: 9
        }
        return priority_mapping[priority]
    
    async def cleanup_expired_jobs(self) -> int:
        """Clean up expired jobs and return count."""
        cutoff_time = datetime.now() - timedelta(seconds=self.config.result_ttl_seconds)
        cleaned_count = 0
        
        with self._lock:
            expired_jobs = [
                job_id for job_id, result in self.active_jobs.items()
                if result.completed_at and result.completed_at < cutoff_time
            ]
            
            for job_id in expired_jobs:
                del self.active_jobs[job_id]
                if job_id in self.job_progress:
                    del self.job_progress[job_id]
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} expired jobs")
        return cleaned_count
    
    async def shutdown(self) -> None:
        """Shutdown async job manager."""
        self._executor.shutdown(wait=True)
        await self.connection_pool.close_connections()
        logger.info("AsyncJobManager shutdown complete")


class StreamingCalculationResponse:
    """Streaming response for large calculation results."""
    
    def __init__(
        self,
        calculation_function: Callable,
        chunk_size: int = 100,
        media_type: str = "application/json"
    ):
        self.calculation_function = calculation_function
        self.chunk_size = chunk_size
        self.media_type = media_type
    
    async def generate_response(self, *args, **kwargs) -> AsyncGenerator[bytes, None]:
        """Generate streaming response chunks."""
        try:
            # Start performance monitoring
            monitor = get_performance_monitor()
            start_time = time.time()
            
            # Stream header
            yield b'{"status": "streaming", "data": ['
            
            first_chunk = True
            total_items = 0
            
            # Execute calculation with streaming
            async for chunk in self._stream_calculation_chunks(*args, **kwargs):
                if not first_chunk:
                    yield b','
                else:
                    first_chunk = False
                
                chunk_json = json.dumps(chunk, default=str).encode('utf-8')
                yield chunk_json
                total_items += 1
                
                # Yield control periodically
                if total_items % self.chunk_size == 0:
                    await asyncio.sleep(0.01)  # Small delay to prevent blocking
            
            # Stream footer with metadata
            end_time = time.time()
            metadata = {
                "total_items": total_items,
                "calculation_time_ms": (end_time - start_time) * 1000,
                "streaming_complete": True
            }
            
            yield f'], "metadata": {json.dumps(metadata)}'.encode('utf-8')
            yield b'}'
            
            # Record performance metrics
            monitor.track_calculation_performance(
                "streaming_calculation",
                (end_time - start_time) * 1000,
                True
            )
            
        except Exception as e:
            logger.error(f"Streaming response failed: {e}")
            error_response = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(error_response).encode('utf-8')
    
    async def _stream_calculation_chunks(self, *args, **kwargs) -> AsyncGenerator[Any, None]:
        """Stream calculation results in chunks."""
        # This would be implemented based on specific calculation requirements
        # For demonstration, yielding placeholder chunks
        for i in range(10):  # Replace with actual calculation logic
            chunk = {
                "chunk_id": i,
                "data": f"calculation_result_{i}",
                "timestamp": datetime.now().isoformat()
            }
            yield chunk
            await asyncio.sleep(0.1)  # Simulate calculation time
    
    def create_streaming_response(self, *args, **kwargs) -> StreamingResponse:
        """Create FastAPI StreamingResponse."""
        return StreamingResponse(
            self.generate_response(*args, **kwargs),
            media_type=self.media_type
        )


class AsyncCalculationProcessor:
    """
    High-level async calculation processor with job management and streaming.
    
    Provides unified interface for async calculations, job queuing,
    progress tracking, and result streaming.
    """
    
    def __init__(self, config: Optional[AsyncJobConfig] = None):
        self.config = config or AsyncJobConfig()
        self.job_manager = AsyncJobManager(self.config)
        self.performance_monitor = get_performance_monitor()
        
        logger.info("AsyncCalculationProcessor initialized")
    
    async def process_calculation_async(
        self,
        calculation_type: str,
        calculation_function: Callable,
        *args,
        **kwargs
    ) -> AsyncResult:
        """Process calculation asynchronously."""
        return await self.job_manager.submit_job(
            calculation_function,
            args,
            kwargs,
            priority=JobPriority.NORMAL
        )
    
    async def queue_batch_calculation(
        self,
        requests: List[Dict[str, Any]],
        calculation_function: Callable,
        priority: JobPriority = JobPriority.NORMAL
    ) -> str:
        """Queue batch calculation job."""
        job_id = str(uuid.uuid4())
        
        async_result = await self.job_manager.submit_job(
            calculation_function,
            (requests,),
            {"batch_mode": True},
            job_id=job_id,
            priority=priority,
            use_background=True
        )
        
        return job_id
    
    async def get_calculation_status(self, job_id: str) -> Optional[AsyncResult]:
        """Get calculation job status."""
        return await self.job_manager.get_job_status(job_id)
    
    async def stream_results(self, job_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream calculation results."""
        async for result in self.job_manager.stream_results(job_id):
            yield result
    
    async def cancel_calculation(self, job_id: str) -> bool:
        """Cancel calculation job."""
        return await self.job_manager.cancel_job(job_id)
    
    def create_streaming_response(
        self,
        calculation_function: Callable,
        chunk_size: int = 100
    ) -> StreamingCalculationResponse:
        """Create streaming response for large calculations."""
        return StreamingCalculationResponse(
            calculation_function,
            chunk_size=chunk_size
        )
    
    @asynccontextmanager
    async def websocket_connection(self, websocket: WebSocket, connection_id: str):
        """Context manager for WebSocket connections."""
        await self.job_manager.websocket_manager.connect(websocket, connection_id)
        try:
            yield self.job_manager.websocket_manager
        finally:
            self.job_manager.websocket_manager.disconnect(connection_id, websocket)
    
    async def subscribe_to_job_updates(
        self,
        connection_id: str,
        job_id: str
    ) -> None:
        """Subscribe WebSocket connection to job updates."""
        self.job_manager.websocket_manager.subscribe_to_job(connection_id, job_id)
    
    async def get_active_jobs(self) -> List[AsyncResult]:
        """Get all active jobs."""
        with self.job_manager._lock:
            return list(self.job_manager.active_jobs.values())
    
    async def cleanup_expired_jobs(self) -> int:
        """Clean up expired jobs."""
        return await self.job_manager.cleanup_expired_jobs()
    
    async def shutdown(self) -> None:
        """Shutdown async processor."""
        await self.job_manager.shutdown()


# Global async processor instance
_global_async_processor: Optional[AsyncCalculationProcessor] = None
_async_processor_lock = asyncio.Lock()


async def get_async_processor() -> AsyncCalculationProcessor:
    """Get or create global async processor instance."""
    global _global_async_processor
    
    if _global_async_processor is None:
        async with _async_processor_lock:
            if _global_async_processor is None:
                _global_async_processor = AsyncCalculationProcessor()
    
    return _global_async_processor


def async_calculation(
    calculation_type: str,
    use_background: bool = False,
    priority: JobPriority = JobPriority.NORMAL
):
    """
    Decorator for async calculation processing.
    
    Args:
        calculation_type: Type of calculation for monitoring
        use_background: Whether to use background job processing
        priority: Job priority level
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            processor = await get_async_processor()
            
            if use_background:
                # Submit as background job
                return await processor.job_manager.submit_job(
                    func, args, kwargs,
                    priority=priority,
                    use_background=True
                )
            else:
                # Execute immediately with async processing
                return await processor.process_calculation_async(
                    calculation_type, func, *args, **kwargs
                )
        
        return wrapper
    return decorator


# Celery task definitions for background processing
@celery_app.task(bind=True)
def ephemeris_calculation(self, function_name: str, args: Tuple, kwargs: Dict[str, Any], job_id: str):
    """Celery task for background ephemeris calculations."""
    try:
        # Import and execute the calculation function
        # This would need to be implemented based on available calculation functions
        result = {"message": f"Background calculation {function_name} completed", "job_id": job_id}
        return result
    except Exception as e:
        logger.error(f"Background calculation failed: {e}")
        raise


# Create global Celery app instance
celery_app = Celery(
    'ephemeris_async',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)