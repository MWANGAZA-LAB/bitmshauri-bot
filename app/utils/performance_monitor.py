"""
Performance monitoring and optimization utilities
"""

import time
import asyncio
import functools
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from app.utils.logger import logger

# Try to import psutil, fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.logger.warning("psutil not available, performance monitoring limited")


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.slow_operations = deque(maxlen=100)
        self.memory_usage = deque(maxlen=100)
        self.cpu_usage = deque(maxlen=100)
        self.start_time = time.time()
        
        # Performance thresholds
        self.slow_query_threshold = 1.0  # seconds
        self.memory_warning_threshold = 100 * 1024 * 1024  # 100MB
        self.cpu_warning_threshold = 80.0  # percentage
    
    def record_operation(self, operation_name: str, duration: float, 
                        metadata: Dict = None):
        """Record operation performance"""
        self.metrics[operation_name].append({
            'duration': duration,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        })
        
        # Track slow operations
        if duration > self.slow_query_threshold:
            self.slow_operations.append({
                'operation': operation_name,
                'duration': duration,
                'timestamp': datetime.now(),
                'metadata': metadata or {}
            })
            
            logger.log_performance(
                operation_name, 
                duration, 
                metadata.get('user_id') if metadata else None
            )
    
    def record_memory_usage(self):
        """Record current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        self.memory_usage.append({
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'timestamp': datetime.now()
        })
        
        # Check for memory warnings
        if memory_info.rss > self.memory_warning_threshold:
            logger.logger.warning(
                f"High memory usage detected: {memory_info.rss / 1024 / 1024:.2f}MB"
            )
    
    def record_cpu_usage(self):
        """Record current CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.append({
            'cpu_percent': cpu_percent,
            'timestamp': datetime.now()
        })
        
        # Check for CPU warnings
        if cpu_percent > self.cpu_warning_threshold:
            logger.logger.warning(
                f"High CPU usage detected: {cpu_percent:.2f}%"
            )
    
    def get_operation_stats(self, operation_name: str, 
                          time_window: timedelta = timedelta(hours=1)) -> Dict:
        """Get statistics for a specific operation"""
        cutoff_time = datetime.now() - time_window
        operations = [
            op for op in self.metrics[operation_name]
            if op['timestamp'] > cutoff_time
        ]
        
        if not operations:
            return {}
        
        durations = [op['duration'] for op in operations]
        
        return {
            'count': len(operations),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'p95_duration': sorted(durations)[int(len(durations) * 0.95)],
            'p99_duration': sorted(durations)[int(len(durations) * 0.99)],
            'time_window': time_window.total_seconds()
        }
    
    def get_slow_operations(self, limit: int = 10) -> List[Dict]:
        """Get recent slow operations"""
        return list(self.slow_operations)[-limit:]
    
    def get_system_stats(self) -> Dict:
        """Get current system statistics"""
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'uptime': time.time() - self.start_time,
                'memory': {
                    'rss': memory_info.rss,
                    'vms': memory_info.vms,
                    'percent': process.memory_percent()
                },
                'cpu': {
                    'percent': psutil.cpu_percent(),
                    'count': psutil.cpu_count()
                },
                'disk': {
                    'usage': psutil.disk_usage('/').percent
                }
            }
        else:
            return {
                'uptime': time.time() - self.start_time,
                'memory': {
                    'rss': 0,
                    'vms': 0,
                    'percent': 0
                },
                'cpu': {
                    'percent': 0,
                    'count': 1
                },
                'disk': {
                    'usage': 0
                },
                'note': 'psutil not available'
            }
    
    def cleanup_old_metrics(self, max_age: timedelta = timedelta(days=7)):
        """Clean up old metrics to prevent memory leaks"""
        cutoff_time = datetime.now() - max_age
        
        for operation_name in list(self.metrics.keys()):
            self.metrics[operation_name] = [
                op for op in self.metrics[operation_name]
                if op['timestamp'] > cutoff_time
            ]
            
            # Remove empty lists
            if not self.metrics[operation_name]:
                del self.metrics[operation_name]


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Extract metadata
                metadata = {}
                if args and hasattr(args[0], 'effective_user'):
                    metadata['user_id'] = args[0].effective_user.id
                elif args and hasattr(args[0], 'message'):
                    metadata['user_id'] = args[0].message.from_user.id
                
                performance_monitor.record_operation(operation, duration, metadata)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metadata = {'error': str(e)}
                performance_monitor.record_operation(operation, duration, metadata)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Extract metadata
                metadata = {}
                if args and hasattr(args[0], 'effective_user'):
                    metadata['user_id'] = args[0].effective_user.id
                elif args and hasattr(args[0], 'message'):
                    metadata['user_id'] = args[0].message.from_user.id
                
                performance_monitor.record_operation(operation, duration, metadata)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metadata = {'error': str(e)}
                performance_monitor.record_operation(operation, duration, metadata)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


class CacheManager:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.default_ttl = default_ttl
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check TTL
        if time.time() - self.access_times[key] > self.default_ttl:
            del self.cache[key]
            del self.access_times[key]
            return None
        
        self.access_times[key] = time.time()
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        self.cache[key] = value
        self.access_times[key] = time.time() + (ttl or self.default_ttl)
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.access_times.clear()
    
    def cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, expire_time in self.access_times.items()
            if current_time > expire_time
        ]
        
        for key in expired_keys:
            del self.cache[key]
            del self.access_times[key]


# Global cache manager instance
cache_manager = CacheManager()


def cached(ttl: int = 300, key_func: Callable = None):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


class RateLimiter:
    """Enhanced rate limiter with sliding window"""
    
    def __init__(self):
        self.requests = defaultdict(lambda: deque())
        self.penalties = defaultdict(float)
        
        # Rate limits
        self.limits = {
            'message': {'count': 20, 'window': 60},  # 20 messages per minute
            'quiz': {'count': 5, 'window': 3600},    # 5 quizzes per hour
            'api_call': {'count': 10, 'window': 60}, # 10 API calls per minute
            'audio': {'count': 15, 'window': 3600},  # 15 audio requests per hour
        }
        
        self.penalty_duration = 300  # 5 minutes
    
    def is_rate_limited(self, user_id: int, action_type: str = "message") -> bool:
        """Check if user is rate limited"""
        current_time = time.time()
        
        # Check penalty
        if self.penalties[user_id] > current_time:
            return True
        
        # Clean old requests
        self._cleanup_old_requests(user_id, current_time)
        
        # Check rate limit
        limit_config = self.limits.get(action_type, self.limits['message'])
        recent_requests = len([
            req_time for req_time in self.requests[user_id]
            if current_time - req_time <= limit_config['window']
        ])
        
        if recent_requests >= limit_config['count']:
            self._apply_penalty(user_id, current_time)
            return True
        
        # Record request
        self.requests[user_id].append(current_time)
        return False
    
    def _cleanup_old_requests(self, user_id: int, current_time: float):
        """Remove old requests"""
        max_window = max(config['window'] for config in self.limits.values())
        cutoff_time = current_time - max_window
        
        while (self.requests[user_id] and 
               self.requests[user_id][0] < cutoff_time):
            self.requests[user_id].popleft()
    
    def _apply_penalty(self, user_id: int, current_time: float):
        """Apply penalty to user"""
        self.penalties[user_id] = current_time + self.penalty_duration
        
        logger.log_user_action(
            user_id,
            "rate_limit_violation",
            {
                "penalty_duration": self.penalty_duration,
                "penalty_expires": self.penalties[user_id]
            }
        )
    
    def get_user_status(self, user_id: int) -> Dict:
        """Get user rate limit status"""
        current_time = time.time()
        
        return {
            "is_penalized": self.penalties[user_id] > current_time,
            "penalty_expires": self.penalties[user_id] if self.penalties[user_id] > current_time else None,
            "recent_requests": {
                action_type: len([
                    req_time for req_time in self.requests[user_id]
                    if current_time - req_time <= config['window']
                ])
                for action_type, config in self.limits.items()
            },
            "limits": self.limits
        }
    
    def reset_user_limits(self, user_id: int):
        """Reset rate limits for user"""
        if user_id in self.requests:
            del self.requests[user_id]
        if user_id in self.penalties:
            del self.penalties[user_id]


# Global enhanced rate limiter instance
enhanced_rate_limiter = RateLimiter()


async def start_performance_monitoring():
    """Start background performance monitoring"""
    async def monitor_loop():
        while True:
            try:
                performance_monitor.record_memory_usage()
                performance_monitor.record_cpu_usage()
                performance_monitor.cleanup_old_metrics()
                cache_manager.cleanup_expired()
                
                await asyncio.sleep(60)  # Monitor every minute
            except Exception as e:
                logger.log_error(e, {"operation": "performance_monitoring"})
                await asyncio.sleep(60)
    
    # Start monitoring task
    asyncio.create_task(monitor_loop())
