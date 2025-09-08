"""Performance monitoring and optimization utilities."""

import asyncio
import functools
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from app.utils.logger import logger

# Try to import psutil, fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.logger.warning("psutil not available, performance monitoring limited")


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""

    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics = defaultdict(list)
        self.slow_operations = deque(maxlen=100)
        self.memory_usage = deque(maxlen=100)
        self.cpu_usage = deque(maxlen=100)
        self.start_time = time.time()

        # Performance thresholds
        self.slow_query_threshold = 1.0  # seconds
        self.memory_warning_threshold = 100 * 1024 * 1024  # 100MB
        self.cpu_warning_threshold = 80.0  # percentage

    def record_operation(
        self, operation_name: str, duration: float, metadata: Dict[str, Any] = None
    ) -> None:
        """Record an operation's performance metrics."""
        try:
            timestamp = datetime.now()
            operation_data = {
                "operation": operation_name,
                "duration": duration,
                "timestamp": timestamp,
                "metadata": metadata or {},
            }

            self.metrics[operation_name].append(operation_data)

            # Track slow operations
            if duration > self.slow_query_threshold:
                self.slow_operations.append(operation_data)

            # Record system metrics if available
            if PSUTIL_AVAILABLE:
                self._record_system_metrics()

        except Exception as e:
            logger.log_error(e, {"operation": "record_operation"})

    def _record_system_metrics(self) -> None:
        """Record current system metrics."""
        try:
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                memory_info = process.memory_info()

                self.memory_usage.append({
                    "timestamp": datetime.now(),
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "percent": process.memory_percent(),
                })

                self.cpu_usage.append({
                    "timestamp": datetime.now(),
                    "percent": psutil.cpu_percent(),
                })

        except Exception as e:
            logger.log_error(e, {"operation": "record_system_metrics"})

    def get_operation_stats(
        self, operation_name: str, time_window: timedelta = None
    ) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        try:
            if operation_name not in self.metrics:
                return {}

            operations = self.metrics[operation_name]

            if time_window:
                cutoff_time = datetime.now() - time_window
                operations = [
                    op for op in operations if op["timestamp"] > cutoff_time
                ]

            if not operations:
                return {}

            durations = [op["duration"] for op in operations]

            return {
                "count": len(operations),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "p95_duration": sorted(durations)[int(len(durations) * 0.95)],
                "p99_duration": sorted(durations)[int(len(durations) * 0.99)],
                "time_window": time_window.total_seconds() if time_window else None,
            }

        except Exception as e:
            logger.log_error(e, {"operation": "get_operation_stats"})
            return {}

    def get_slow_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow operations."""
        return list(self.slow_operations)[-limit:]

    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                "uptime": time.time() - self.start_time,
                "memory": {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "percent": process.memory_percent(),
                },
                "cpu": {
                    "percent": psutil.cpu_percent(),
                    "count": psutil.cpu_count(),
                },
                "disk": {
                    "usage": psutil.disk_usage("/").percent,
                },
            }
        else:
            return {
                "uptime": time.time() - self.start_time,
                "memory": {
                    "rss": 0,
                    "vms": 0,
                    "percent": 0,
                },
                "cpu": {
                    "percent": 0,
                    "count": 1,
                },
                "disk": {
                    "usage": 0,
                },
                "note": "psutil not available",
            }

    def cleanup_old_metrics(self, max_age: timedelta = timedelta(days=7)) -> None:
        """Clean up old metrics to prevent memory leaks."""
        cutoff_time = datetime.now() - max_age

        for operation_name in list(self.metrics.keys()):
            self.metrics[operation_name] = [
                op for op in self.metrics[operation_name]
                if op["timestamp"] > cutoff_time
            ]

            # Remove empty operation lists
            if not self.metrics[operation_name]:
                del self.metrics[operation_name]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        try:
            summary = {
                "uptime": time.time() - self.start_time,
                "total_operations": sum(len(ops) for ops in self.metrics.values()),
                "slow_operations_count": len(self.slow_operations),
                "operations": {},
                "system": self.get_system_stats(),
            }

            # Get stats for each operation type
            for operation_name in self.metrics.keys():
                summary["operations"][operation_name] = self.get_operation_stats(
                    operation_name
                )

            return summary

        except Exception as e:
            logger.log_error(e, {"operation": "get_performance_summary"})
            return {}

    def check_performance_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts and warnings."""
        alerts = []

        try:
            # Check for slow operations
            if len(self.slow_operations) > 10:
                alerts.append({
                    "type": "warning",
                    "message": f"High number of slow operations: {len(self.slow_operations)}",
                    "timestamp": datetime.now(),
                })

            # Check system metrics if available
            if PSUTIL_AVAILABLE:
                system_stats = self.get_system_stats()

                # Memory usage alert
                if system_stats["memory"]["percent"] > 90:
                    alerts.append({
                        "type": "critical",
                        "message": f"High memory usage: {system_stats['memory']['percent']:.1f}%",
                        "timestamp": datetime.now(),
                    })

                # CPU usage alert
                if system_stats["cpu"]["percent"] > 90:
                    alerts.append({
                        "type": "critical",
                        "message": f"High CPU usage: {system_stats['cpu']['percent']:.1f}%",
                        "timestamp": datetime.now(),
                    })

                # Disk usage alert
                if system_stats["disk"]["usage"] > 90:
                    alerts.append({
                        "type": "warning",
                        "message": f"High disk usage: {system_stats['disk']['usage']:.1f}%",
                        "timestamp": datetime.now(),
                    })

        except Exception as e:
            logger.log_error(e, {"operation": "check_performance_alerts"})

        return alerts


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: str):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    performance_monitor.record_operation(
                        operation_name, duration, {"function": func.__name__}
                    )
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    performance_monitor.record_operation(
                        operation_name, duration, {"function": func.__name__}
                    )
            return sync_wrapper
    return decorator


class RateLimiter:
    """Enhanced rate limiter with performance monitoring."""

    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """Initialize the rate limiter."""
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)

    def is_rate_limited(self, user_id: int, operation: str = "default") -> bool:
        """Check if user is rate limited."""
        try:
            current_time = time.time()
            key = f"{user_id}:{operation}"
            user_requests = self.requests[key]

            # Remove old requests outside the time window
            user_requests[:] = [
                req_time for req_time in user_requests
                if current_time - req_time < self.time_window
            ]

            # Check if user has exceeded the limit
            if len(user_requests) >= self.max_requests:
                return True

            # Record this request
            user_requests.append(current_time)
            return False

        except Exception as e:
            logger.log_error(e, {"operation": "is_rate_limited"})
            return False

    def get_remaining_requests(self, user_id: int, operation: str = "default") -> int:
        """Get remaining requests for user."""
        try:
            current_time = time.time()
            key = f"{user_id}:{operation}"
            user_requests = self.requests[key]

            # Remove old requests
            user_requests[:] = [
                req_time for req_time in user_requests
                if current_time - req_time < self.time_window
            ]

            return max(0, self.max_requests - len(user_requests))

        except Exception as e:
            logger.log_error(e, {"operation": "get_remaining_requests"})
            return 0

    def reset_user_limits(self, user_id: int) -> None:
        """Reset rate limits for a specific user."""
        try:
            keys_to_remove = [key for key in self.requests.keys() if key.startswith(f"{user_id}:")]
            for key in keys_to_remove:
                del self.requests[key]
        except Exception as e:
            logger.log_error(e, {"operation": "reset_user_limits"})


# Global rate limiter instance
enhanced_rate_limiter = RateLimiter()


async def start_performance_monitoring() -> None:
    """Start background performance monitoring tasks."""
    try:
        # Start cleanup task
        async def cleanup_task():
            while True:
                await asyncio.sleep(3600)  # Run every hour
                performance_monitor.cleanup_old_metrics()

        # Start alert checking task
        async def alert_task():
            while True:
                await asyncio.sleep(300)  # Check every 5 minutes
                alerts = performance_monitor.check_performance_alerts()
                for alert in alerts:
                    logger.logger.warning(f"Performance alert: {alert['message']}")

        # Start the background tasks
        asyncio.create_task(cleanup_task())
        asyncio.create_task(alert_task())

        logger.logger.info("Performance monitoring started")

    except Exception as e:
        logger.log_error(e, {"operation": "start_performance_monitoring"})


def get_performance_report() -> Dict[str, Any]:
    """Get a comprehensive performance report."""
    return performance_monitor.get_performance_summary()


def get_system_health() -> Dict[str, Any]:
    """Get system health status."""
    try:
        system_stats = performance_monitor.get_system_stats()
        alerts = performance_monitor.check_performance_alerts()

        health_score = 100

        # Deduct points for alerts
        for alert in alerts:
            if alert["type"] == "critical":
                health_score -= 20
            elif alert["type"] == "warning":
                health_score -= 10

        # Deduct points for high resource usage
        if PSUTIL_AVAILABLE:
            if system_stats["memory"]["percent"] > 80:
                health_score -= 15
            if system_stats["cpu"]["percent"] > 80:
                health_score -= 15
            if system_stats["disk"]["usage"] > 80:
                health_score -= 10

        return {
            "health_score": max(0, health_score),
            "status": "healthy" if health_score > 80 else "warning" if health_score > 60 else "critical",
            "system_stats": system_stats,
            "alerts": alerts,
            "uptime": system_stats["uptime"],
        }

    except Exception as e:
        logger.log_error(e, {"operation": "get_system_health"})
        return {
            "health_score": 0,
            "status": "error",
            "error": str(e),
        }