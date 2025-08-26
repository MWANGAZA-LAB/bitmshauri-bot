import time
from collections import defaultdict, deque
from typing import Dict, Optional
from app.utils.logger import logger


class RateLimiter:
    """Advanced rate limiting system with multiple strategies"""

    def __init__(self):
        # User request tracking
        self.user_requests = defaultdict(deque)
        self.user_penalties = defaultdict(float)

        # Global rate limiting
        self.global_requests = deque()

        # Rate limits configuration
        self.LIMITS = {
            "messages_per_minute": 20,
            "quizzes_per_hour": 5,
            "api_calls_per_minute": 10,
            "audio_requests_per_hour": 15,
            "global_requests_per_second": 100,
        }

        # Penalty system
        self.PENALTY_DURATION = 300  # 5 minutes
        self.MAX_VIOLATIONS = 3

    def is_rate_limited(
        self, user_id: int, action_type: str = "message"
    ) -> bool:
        """Check if user is rate limited for specific action"""
        current_time = time.time()

        # Check if user is under penalty
        if self.user_penalties[user_id] > current_time:
            logger.log_user_action(
                user_id,
                "rate_limit_blocked",
                {
                    "action_type": action_type,
                    "penalty_expires": self.user_penalties[user_id],
                },
            )
            return True

        # Clean old requests
        self._cleanup_old_requests(user_id, current_time)

        # Check specific action limits
        if action_type == "message":
            limit = self.LIMITS["messages_per_minute"]
            window = 60
        elif action_type == "quiz":
            limit = self.LIMITS["quizzes_per_hour"]
            window = 3600
        elif action_type == "api_call":
            limit = self.LIMITS["api_calls_per_minute"]
            window = 60
        elif action_type == "audio":
            limit = self.LIMITS["audio_requests_per_hour"]
            window = 3600
        else:
            limit = self.LIMITS["messages_per_minute"]
            window = 60

        # Count recent requests
        recent_requests = len(
            [
                req_time
                for req_time in self.user_requests[user_id]
                if current_time - req_time <= window
            ]
        )

        if recent_requests >= limit:
            self._apply_penalty(user_id, action_type)
            return True

        # Check global rate limit
        if self._is_global_rate_limited():
            return True

        # Record the request
        self.user_requests[user_id].append(current_time)
        self.global_requests.append(current_time)

        return False

    def _cleanup_old_requests(self, user_id: int, current_time: float):
        """Remove old requests outside the tracking window"""
        # Keep requests from last hour (longest window we track)
        cutoff_time = current_time - 3600

        # Clean user requests
        while (
            self.user_requests[user_id]
            and self.user_requests[user_id][0] < cutoff_time
        ):
            self.user_requests[user_id].popleft()

        # Clean global requests (keep last minute)
        global_cutoff = current_time - 60
        while self.global_requests and self.global_requests[0] < global_cutoff:
            self.global_requests.popleft()

    def _apply_penalty(self, user_id: int, action_type: str):
        """Apply penalty to user for rate limit violation"""
        current_time = time.time()
        penalty_end = current_time + self.PENALTY_DURATION

        self.user_penalties[user_id] = penalty_end

        logger.log_user_action(
            user_id,
            "rate_limit_violation",
            {
                "action_type": action_type,
                "penalty_duration": self.PENALTY_DURATION,
                "penalty_expires": penalty_end,
            },
        )

    def _is_global_rate_limited(self) -> bool:
        """Check global rate limiting"""
        current_time = time.time()
        recent_global = len(
            [
                req_time
                for req_time in self.global_requests
                if current_time - req_time <= 1  # Last second
            ]
        )

        return recent_global >= self.LIMITS["global_requests_per_second"]

    def get_user_status(self, user_id: int) -> Dict:
        """Get current rate limit status for user"""
        current_time = time.time()

        # Check penalty status
        penalty_time = self.user_penalties.get(user_id, 0)
        is_penalized = penalty_time > current_time

        # Count recent requests by type
        user_requests = self.user_requests[user_id]

        recent_messages = len(
            [req for req in user_requests if current_time - req <= 60]
        )

        recent_hourly = len(
            [req for req in user_requests if current_time - req <= 3600]
        )

        return {
            "is_penalized": is_penalized,
            "penalty_expires": penalty_time if is_penalized else None,
            "recent_messages_per_minute": recent_messages,
            "recent_requests_per_hour": recent_hourly,
            "limits": {
                "messages_per_minute": self.LIMITS["messages_per_minute"],
                "quizzes_per_hour": self.LIMITS["quizzes_per_hour"],
                "audio_requests_per_hour": self.LIMITS[
                    "audio_requests_per_hour"
                ],
            },
        }

    def reset_user_limits(self, user_id: int):
        """Reset rate limits for a user (admin function)"""
        if user_id in self.user_requests:
            del self.user_requests[user_id]
        if user_id in self.user_penalties:
            del self.user_penalties[user_id]

        logger.log_user_action(user_id, "rate_limits_reset")


# Global rate limiter instance
rate_limiter = RateLimiter()


# Decorator for rate limiting
def rate_limit(action_type: str = "message"):
    """Decorator to apply rate limiting to functions"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id from update object
            user_id = None
            if args and hasattr(args[0], "effective_user"):
                user_id = args[0].effective_user.id
            elif (
                args
                and hasattr(args[0], "message")
                and hasattr(args[0].message, "from_user")
            ):
                user_id = args[0].message.from_user.id

            if user_id and rate_limiter.is_rate_limited(user_id, action_type):
                # Send rate limit message
                try:
                    if args and hasattr(args[0], "message"):
                        await args[0].message.reply_text(
                            "⏰ Subiri kidogo! Umetuma maombi mengi sana. "
                            "Tafadhali jaribu tena baada ya dakika chache."
                        )
                    elif args and hasattr(args[0], "callback_query"):
                        await args[0].callback_query.answer(
                            "⏰ Subiri kidogo! Umetuma maombi mengi sana.",
                            show_alert=True,
                        )
                except:
                    pass
                return None

            return await func(*args, **kwargs)

        return wrapper

    return decorator
