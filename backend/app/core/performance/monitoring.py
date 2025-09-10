"""
Performance Monitoring System
Comprehensive performance monitoring with real-time metrics, alerting, and optimization.

Features:
- Real-time calculation performance tracking
- Cache effectiveness monitoring
- Performance degradation detection
- Automated optimization recommendations
- Metrics collection and aggregation
- Alert system for performance thresholds
- Performance trend analysis and reporting

Performance Targets:
- Track response time percentiles (p50, p95, p99)
- Monitor throughput and error rates
- Detect performance degradation patterns
- Provide actionable optimization insights
- Alert on SLA violations
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import statistics
import logging
import json
from contextlib import contextmanager

import numpy as np

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of performance metrics."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    QUEUE_DEPTH = "queue_depth"


@dataclass
class PerformanceMetric:
    """Individual performance metric data point."""
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    calculation_type: str = ""
    endpoint: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "calculation_type": self.calculation_type,
            "endpoint": self.endpoint
        }


@dataclass
class PerformanceAlert:
    """Performance alert data structure."""
    alert_id: str
    severity: AlertSeverity
    message: str
    metric_type: MetricType
    threshold_value: float
    actual_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "message": self.message,
            "metric_type": self.metric_type.value,
            "threshold_value": self.threshold_value,
            "actual_value": self.actual_value,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolution_timestamp": self.resolution_timestamp.isoformat() if self.resolution_timestamp else None
        }


@dataclass
class PerformanceThresholds:
    """Performance alert thresholds."""
    response_time_p95_ms: float = 150.0
    response_time_p99_ms: float = 500.0
    error_rate_percent: float = 1.0
    cache_hit_rate_percent: float = 70.0
    memory_usage_percent: float = 85.0
    cpu_usage_percent: float = 80.0
    throughput_min_per_second: float = 10.0


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    total_requests: int = 0
    hits: int = 0
    misses: int = 0
    average_access_time_ms: float = 0.0
    cache_size: int = 0
    evictions: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceReport:
    """Comprehensive performance report."""
    report_id: str
    start_time: datetime
    end_time: datetime
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    throughput_per_second: float = 0.0
    error_rate_percent: float = 0.0
    cache_metrics: Optional[CacheMetrics] = None
    optimization_recommendations: List[str] = field(default_factory=list)
    alerts_generated: List[PerformanceAlert] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "report_id": self.report_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "average_response_time_ms": self.average_response_time_ms,
            "p50_response_time_ms": self.p50_response_time_ms,
            "p95_response_time_ms": self.p95_response_time_ms,
            "p99_response_time_ms": self.p99_response_time_ms,
            "throughput_per_second": self.throughput_per_second,
            "error_rate_percent": self.error_rate_percent,
            "cache_metrics": self.cache_metrics.__dict__ if self.cache_metrics else None,
            "optimization_recommendations": self.optimization_recommendations,
            "alerts_count": len(self.alerts_generated)
        }


class MetricAggregator:
    """Aggregates and analyzes performance metrics."""
    
    def __init__(self, window_size_minutes: int = 60):
        self.window_size = timedelta(minutes=window_size_minutes)
        self.metrics: Dict[MetricType, deque] = defaultdict(lambda: deque())
        self._lock = threading.RLock()
    
    def add_metric(self, metric: PerformanceMetric) -> None:
        """Add a metric data point."""
        with self._lock:
            metrics_deque = self.metrics[metric.metric_type]
            metrics_deque.append(metric)
            
            # Remove old metrics outside window
            cutoff_time = datetime.now() - self.window_size
            while metrics_deque and metrics_deque[0].timestamp < cutoff_time:
                metrics_deque.popleft()
    
    def get_percentiles(
        self, 
        metric_type: MetricType, 
        percentiles: List[float] = [50, 95, 99]
    ) -> Dict[float, float]:
        """Calculate percentiles for a metric type."""
        with self._lock:
            values = [m.value for m in self.metrics[metric_type]]
            
            if not values:
                return {p: 0.0 for p in percentiles}
            
            return {
                p: float(np.percentile(values, p))
                for p in percentiles
            }
    
    def get_average(self, metric_type: MetricType) -> float:
        """Get average value for a metric type."""
        with self._lock:
            values = [m.value for m in self.metrics[metric_type]]
            return statistics.mean(values) if values else 0.0
    
    def get_rate(self, metric_type: MetricType) -> float:
        """Get rate (count per minute) for a metric type."""
        with self._lock:
            count = len(self.metrics[metric_type])
            window_minutes = self.window_size.total_seconds() / 60
            return count / window_minutes if window_minutes > 0 else 0.0
    
    def get_trend(self, metric_type: MetricType) -> str:
        """Analyze trend for a metric type."""
        with self._lock:
            values = [m.value for m in self.metrics[metric_type]]
            
            if len(values) < 10:
                return "insufficient_data"
            
            # Simple trend analysis using linear regression
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            if slope > 0.1:
                return "increasing"
            elif slope < -0.1:
                return "decreasing"
            else:
                return "stable"


class PerformanceDegradationDetector:
    """Detects performance degradation patterns."""
    
    def __init__(self):
        self.baseline_metrics: Dict[str, float] = {}
        self.degradation_threshold = 0.2  # 20% degradation
        self.baseline_window_minutes = 60
        self._lock = threading.RLock()
    
    def update_baseline(self, calculation_type: str, response_time_ms: float) -> None:
        """Update baseline performance for calculation type."""
        with self._lock:
            if calculation_type not in self.baseline_metrics:
                self.baseline_metrics[calculation_type] = response_time_ms
            else:
                # Exponential moving average
                alpha = 0.1
                self.baseline_metrics[calculation_type] = (
                    alpha * response_time_ms + 
                    (1 - alpha) * self.baseline_metrics[calculation_type]
                )
    
    def detect_degradation(
        self, 
        calculation_type: str, 
        current_response_time_ms: float
    ) -> Optional[Dict[str, Any]]:
        """Detect if performance has degraded significantly."""
        with self._lock:
            if calculation_type not in self.baseline_metrics:
                return None
            
            baseline = self.baseline_metrics[calculation_type]
            if baseline <= 0:
                return None
            
            degradation_ratio = (current_response_time_ms - baseline) / baseline
            
            if degradation_ratio > self.degradation_threshold:
                return {
                    "calculation_type": calculation_type,
                    "baseline_ms": baseline,
                    "current_ms": current_response_time_ms,
                    "degradation_percent": degradation_ratio * 100,
                    "severity": "critical" if degradation_ratio > 0.5 else "warning"
                }
            
            return None


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    
    Tracks calculation performance, cache effectiveness, resource usage,
    and generates alerts and optimization recommendations.
    """
    
    def __init__(self, thresholds: Optional[PerformanceThresholds] = None):
        self.thresholds = thresholds or PerformanceThresholds()
        self.metric_aggregator = MetricAggregator()
        self.degradation_detector = PerformanceDegradationDetector()
        
        # Storage
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: List[PerformanceAlert] = []
        self.calculation_times: Dict[str, List[float]] = defaultdict(list)
        self.cache_stats_history: List[CacheMetrics] = []
        
        # Monitoring state
        self._monitoring_enabled = True
        self._alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        self._lock = threading.RLock()
        
        logger.info("PerformanceMonitor initialized")
    
    def track_calculation_performance(
        self, 
        calculation_type: str, 
        duration_ms: float,
        success: bool = True,
        endpoint: str = ""
    ) -> None:
        """Track performance of a calculation."""
        if not self._monitoring_enabled:
            return
        
        # Add response time metric
        metric = PerformanceMetric(
            metric_type=MetricType.RESPONSE_TIME,
            value=duration_ms,
            calculation_type=calculation_type,
            endpoint=endpoint,
            tags={"success": str(success)}
        )
        self.metric_aggregator.add_metric(metric)
        
        # Track in calculation times
        with self._lock:
            self.calculation_times[calculation_type].append(duration_ms)
            # Keep only recent times (last 1000)
            if len(self.calculation_times[calculation_type]) > 1000:
                self.calculation_times[calculation_type] = \
                    self.calculation_times[calculation_type][-1000:]
        
        # Update baseline and check for degradation
        if success:
            self.degradation_detector.update_baseline(calculation_type, duration_ms)
            degradation = self.degradation_detector.detect_degradation(
                calculation_type, duration_ms
            )
            if degradation:
                self._generate_degradation_alert(degradation)
        
        # Check response time thresholds
        self._check_response_time_thresholds(calculation_type, duration_ms)
    
    def monitor_cache_effectiveness(self, cache_metrics: CacheMetrics) -> None:
        """Monitor cache performance metrics."""
        if not self._monitoring_enabled:
            return
        
        # Store cache metrics
        with self._lock:
            self.cache_stats_history.append(cache_metrics)
            # Keep only recent history (last 100)
            if len(self.cache_stats_history) > 100:
                self.cache_stats_history.pop(0)
        
        # Add cache hit rate metric
        metric = PerformanceMetric(
            metric_type=MetricType.CACHE_HIT_RATE,
            value=cache_metrics.hit_rate * 100,  # Convert to percentage
            tags={"cache_size": str(cache_metrics.cache_size)}
        )
        self.metric_aggregator.add_metric(metric)
        
        # Check cache hit rate threshold
        if cache_metrics.hit_rate * 100 < self.thresholds.cache_hit_rate_percent:
            self._generate_alert(
                "cache_hit_rate_low",
                AlertSeverity.WARNING,
                f"Cache hit rate is {cache_metrics.hit_rate*100:.1f}%, "
                f"below threshold of {self.thresholds.cache_hit_rate_percent}%",
                MetricType.CACHE_HIT_RATE,
                self.thresholds.cache_hit_rate_percent,
                cache_metrics.hit_rate * 100
            )
    
    def detect_performance_degradation(self) -> List[Dict[str, Any]]:
        """Detect overall performance degradation."""
        degradations = []
        
        with self._lock:
            for calc_type, times in self.calculation_times.items():
                if len(times) < 10:
                    continue
                
                recent_times = times[-10:]  # Last 10 calculations
                historical_times = times[:-10] if len(times) > 20 else []
                
                if not historical_times:
                    continue
                
                recent_avg = statistics.mean(recent_times)
                historical_avg = statistics.mean(historical_times)
                
                if historical_avg > 0:
                    degradation_ratio = (recent_avg - historical_avg) / historical_avg
                    
                    if degradation_ratio > 0.3:  # 30% degradation
                        degradations.append({
                            "calculation_type": calc_type,
                            "historical_avg_ms": historical_avg,
                            "recent_avg_ms": recent_avg,
                            "degradation_percent": degradation_ratio * 100,
                            "sample_size": len(times)
                        })
        
        return degradations
    
    def generate_performance_report(
        self, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> PerformanceReport:
        """Generate comprehensive performance report."""
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(hours=1)
        
        report_id = f"perf_report_{int(time.time())}"
        
        # Calculate response time statistics
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        with self._lock:
            for times in self.calculation_times.values():
                response_times.extend(times)
                successful_requests += len(times)
            
            # Get recent cache metrics
            recent_cache_metrics = (
                self.cache_stats_history[-1] 
                if self.cache_stats_history else None
            )
        
        # Calculate percentiles
        percentiles = {}
        if response_times:
            percentiles = {
                50: float(np.percentile(response_times, 50)),
                95: float(np.percentile(response_times, 95)),
                99: float(np.percentile(response_times, 99))
            }
        
        # Calculate throughput
        duration_hours = (end_time - start_time).total_seconds() / 3600
        throughput = successful_requests / duration_hours if duration_hours > 0 else 0
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(
            response_times, recent_cache_metrics
        )
        
        # Get recent alerts
        recent_alerts = [
            alert for alert in self.alert_history 
            if start_time <= alert.timestamp <= end_time
        ]
        
        report = PerformanceReport(
            report_id=report_id,
            start_time=start_time,
            end_time=end_time,
            total_requests=successful_requests + failed_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time_ms=statistics.mean(response_times) if response_times else 0,
            p50_response_time_ms=percentiles.get(50, 0),
            p95_response_time_ms=percentiles.get(95, 0),
            p99_response_time_ms=percentiles.get(99, 0),
            throughput_per_second=throughput / 3600,  # Convert to per second
            error_rate_percent=(failed_requests / max(successful_requests + failed_requests, 1)) * 100,
            cache_metrics=recent_cache_metrics,
            optimization_recommendations=recommendations,
            alerts_generated=recent_alerts
        )
        
        return report
    
    def optimize_based_on_metrics(self) -> List[str]:
        """Generate optimization actions based on current metrics."""
        optimizations = []
        
        # Analyze response times by calculation type
        with self._lock:
            for calc_type, times in self.calculation_times.items():
                if not times:
                    continue
                
                avg_time = statistics.mean(times)
                
                if avg_time > 200:  # > 200ms
                    optimizations.append(
                        f"High response time for {calc_type} ({avg_time:.1f}ms avg): "
                        "Consider caching, batch processing, or algorithm optimization"
                    )
                
                if len(times) > 10:
                    p95_time = np.percentile(times, 95)
                    if p95_time > 500:  # > 500ms p95
                        optimizations.append(
                            f"High p95 response time for {calc_type} ({p95_time:.1f}ms): "
                            "Check for outlier calculations or resource contention"
                        )
        
        # Analyze cache effectiveness
        if self.cache_stats_history:
            recent_cache = self.cache_stats_history[-1]
            if recent_cache.hit_rate < 0.7:  # < 70%
                optimizations.append(
                    f"Low cache hit rate ({recent_cache.hit_rate*100:.1f}%): "
                    "Consider increasing cache size, TTL, or improving key patterns"
                )
        
        # Check for performance degradation
        degradations = self.detect_performance_degradation()
        for degradation in degradations:
            optimizations.append(
                f"Performance degradation detected in {degradation['calculation_type']}: "
                f"{degradation['degradation_percent']:.1f}% slower than baseline"
            )
        
        return optimizations
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """Add callback function for alerts."""
        self._alert_callbacks.append(callback)
    
    def _check_response_time_thresholds(
        self, 
        calculation_type: str, 
        duration_ms: float
    ) -> None:
        """Check response time against thresholds."""
        if duration_ms > self.thresholds.response_time_p99_ms:
            self._generate_alert(
                f"response_time_high_{calculation_type}",
                AlertSeverity.ERROR,
                f"{calculation_type} response time {duration_ms:.1f}ms exceeds p99 threshold "
                f"of {self.thresholds.response_time_p99_ms}ms",
                MetricType.RESPONSE_TIME,
                self.thresholds.response_time_p99_ms,
                duration_ms
            )
        elif duration_ms > self.thresholds.response_time_p95_ms:
            self._generate_alert(
                f"response_time_elevated_{calculation_type}",
                AlertSeverity.WARNING,
                f"{calculation_type} response time {duration_ms:.1f}ms exceeds p95 threshold "
                f"of {self.thresholds.response_time_p95_ms}ms",
                MetricType.RESPONSE_TIME,
                self.thresholds.response_time_p95_ms,
                duration_ms
            )
    
    def _generate_degradation_alert(self, degradation: Dict[str, Any]) -> None:
        """Generate alert for performance degradation."""
        severity = (
            AlertSeverity.CRITICAL if degradation["severity"] == "critical" 
            else AlertSeverity.WARNING
        )
        
        self._generate_alert(
            f"performance_degradation_{degradation['calculation_type']}",
            severity,
            f"Performance degradation detected in {degradation['calculation_type']}: "
            f"{degradation['degradation_percent']:.1f}% slower than baseline "
            f"({degradation['current_ms']:.1f}ms vs {degradation['baseline_ms']:.1f}ms)",
            MetricType.RESPONSE_TIME,
            degradation['baseline_ms'],
            degradation['current_ms']
        )
    
    def _generate_alert(
        self,
        alert_id: str,
        severity: AlertSeverity,
        message: str,
        metric_type: MetricType,
        threshold_value: float,
        actual_value: float
    ) -> None:
        """Generate and store performance alert."""
        # Check if alert already exists and is active
        if alert_id in self.active_alerts and not self.active_alerts[alert_id].resolved:
            return  # Don't duplicate active alerts
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            severity=severity,
            message=message,
            metric_type=metric_type,
            threshold_value=threshold_value,
            actual_value=actual_value
        )
        
        with self._lock:
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Keep alert history manageable
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
        
        # Notify callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        logger.warning(f"Performance alert generated: {alert.message}")
    
    def _generate_optimization_recommendations(
        self,
        response_times: List[float],
        cache_metrics: Optional[CacheMetrics]
    ) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []
        
        if response_times:
            avg_time = statistics.mean(response_times)
            p95_time = float(np.percentile(response_times, 95))
            
            if avg_time > 100:
                recommendations.append(
                    f"Average response time is {avg_time:.1f}ms. "
                    "Consider implementing caching or batch processing."
                )
            
            if p95_time > 300:
                recommendations.append(
                    f"95th percentile response time is {p95_time:.1f}ms. "
                    "Investigate outlier calculations and optimize slow paths."
                )
        
        if cache_metrics and cache_metrics.hit_rate < 0.7:
            recommendations.append(
                f"Cache hit rate is {cache_metrics.hit_rate*100:.1f}%. "
                "Consider increasing cache size, improving key patterns, "
                "or extending TTL values."
            )
        
        return recommendations
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        with self._lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolution_timestamp = datetime.now()
                del self.active_alerts[alert_id]
                logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get all active alerts."""
        with self._lock:
            return list(self.active_alerts.values())
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current performance metrics."""
        response_time_percentiles = self.metric_aggregator.get_percentiles(
            MetricType.RESPONSE_TIME
        )
        cache_hit_rate = self.metric_aggregator.get_average(MetricType.CACHE_HIT_RATE)
        
        return {
            "response_time_p50_ms": response_time_percentiles.get(50, 0),
            "response_time_p95_ms": response_time_percentiles.get(95, 0),
            "response_time_p99_ms": response_time_percentiles.get(99, 0),
            "cache_hit_rate_percent": cache_hit_rate,
            "active_alerts_count": len(self.active_alerts),
            "total_alerts_today": len([
                a for a in self.alert_history 
                if a.timestamp.date() == datetime.now().date()
            ]),
            "monitoring_enabled": self._monitoring_enabled
        }
    
    def enable_monitoring(self) -> None:
        """Enable performance monitoring."""
        self._monitoring_enabled = True
        logger.info("Performance monitoring enabled")
    
    def disable_monitoring(self) -> None:
        """Disable performance monitoring."""
        self._monitoring_enabled = False
        logger.info("Performance monitoring disabled")


# Global performance monitor instance
_global_performance_monitor: Optional[PerformanceMonitor] = None
_monitor_lock = threading.Lock()


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor instance."""
    global _global_performance_monitor
    
    if _global_performance_monitor is None:
        with _monitor_lock:
            if _global_performance_monitor is None:
                _global_performance_monitor = PerformanceMonitor()
    
    return _global_performance_monitor


@contextmanager
def performance_tracking(calculation_type: str, endpoint: str = ""):
    """Context manager for automatic performance tracking."""
    monitor = get_performance_monitor()
    start_time = time.time()
    success = True
    
    try:
        yield
    except Exception as e:
        success = False
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        monitor.track_calculation_performance(
            calculation_type, duration_ms, success, endpoint
        )


def performance_tracked(calculation_type: str):
    """Decorator for automatic performance tracking."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            with performance_tracking(calculation_type, func.__name__):
                return func(*args, **kwargs)
        return wrapper
    return decorator