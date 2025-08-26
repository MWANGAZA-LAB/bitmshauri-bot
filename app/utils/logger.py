import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import json
import traceback
from typing import Optional, Dict, Any


class StructuredLogger:
    """Enhanced logging system with structured logging and error tracking"""

    def __init__(self, name: str = "bitmshauri"):
        self.logger = logging.getLogger(name)
        self.setup_logging()

    def setup_logging(self):
        """Setup structured logging with multiple handlers"""
        self.logger.setLevel(logging.INFO)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create logs directory
        os.makedirs("logs", exist_ok=True)

        # Console handler with colored output
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)

        # File handler with rotation
        file_handler = RotatingFileHandler(
            "logs/bitmshauri.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # Error file handler
        error_handler = RotatingFileHandler(
            "logs/bitmshauri_errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)

    def log_user_action(
        self, user_id: int, action: str, details: Optional[Dict] = None
    ):
        """Log user actions with structured data"""
        log_data = {
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.logger.info(f"USER_ACTION: {json.dumps(log_data)}")

    def log_error(
        self,
        error: Exception,
        context: Optional[Dict] = None,
        user_id: Optional[int] = None,
    ):
        """Log errors with full context"""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
        }
        self.logger.error(f"ERROR: {json.dumps(error_data)}")

    def log_performance(
        self,
        function_name: str,
        duration: float,
        user_id: Optional[int] = None,
    ):
        """Log performance metrics"""
        perf_data = {
            "function": function_name,
            "duration_seconds": duration,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
        }
        self.logger.info(f"PERFORMANCE: {json.dumps(perf_data)}")


# Global logger instance
logger = StructuredLogger()


# Decorator for automatic error handling
def handle_errors(func):
    """Decorator to automatically handle and log errors"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            user_id = None
            # Try to extract user_id from update object
            if args and hasattr(args[0], "effective_user"):
                user_id = args[0].effective_user.id

            logger.log_error(e, {"function": func.__name__}, user_id)

            # Send user-friendly error message
            if args and hasattr(args[0], "message"):
                try:
                    await args[0].message.reply_text(
                        "Samahani, kuna tatizo la kiufundi. Tafadhali jaribu tena baadaye."
                    )
                except:
                    pass

            return None

    return wrapper


# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor function performance"""

    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = await func(*args, **kwargs)
        duration = (datetime.now() - start_time).total_seconds()

        user_id = None
        if args and hasattr(args[0], "effective_user"):
            user_id = args[0].effective_user.id

        logger.log_performance(func.__name__, duration, user_id)
        return result

    return wrapper
