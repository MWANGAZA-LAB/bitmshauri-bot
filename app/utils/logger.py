"""Enhanced logging system with structured logging and error tracking."""

import json
import logging
import os
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional


class StructuredLogger:
    """Enhanced logging system with structured logging and error tracking."""

    def __init__(self, name: str = "bitmshauri"):
        """Initialize the structured logger."""
        self.logger = logging.getLogger(name)
        self.setup_logging()

    def setup_logging(self) -> None:
        """Setup structured logging with multiple handlers."""
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
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
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

        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)

        # Prevent duplicate logs
        self.logger.propagate = False

    def _format_structured_message(
        self, level: str, message: str, metadata: Dict[str, Any] = None
    ) -> str:
        """Format message with structured data."""
        structured_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "metadata": metadata or {},
        }
        return json.dumps(structured_data, ensure_ascii=False)

    def info(self, message: str, metadata: Dict[str, Any] = None) -> None:
        """Log info message with metadata."""
        formatted_message = self._format_structured_message(
            "INFO", message, metadata
        )
        self.logger.info(formatted_message)

    def warning(self, message: str, metadata: Dict[str, Any] = None) -> None:
        """Log warning message with metadata."""
        formatted_message = self._format_structured_message(
            "WARNING", message, metadata
        )
        self.logger.warning(formatted_message)

    def error(self, message: str, metadata: Dict[str, Any] = None) -> None:
        """Log error message with metadata."""
        formatted_message = self._format_structured_message(
            "ERROR", message, metadata
        )
        self.logger.error(formatted_message)

    def critical(self, message: str, metadata: Dict[str, Any] = None) -> None:
        """Log critical message with metadata."""
        formatted_message = self._format_structured_message(
            "CRITICAL", message, metadata
        )
        self.logger.critical(formatted_message)

    def debug(self, message: str, metadata: Dict[str, Any] = None) -> None:
        """Log debug message with metadata."""
        formatted_message = self._format_structured_message(
            "DEBUG", message, metadata
        )
        self.logger.debug(formatted_message)

    def log_user_action(
        self, user_id: int, action: str, metadata: Dict[str, Any] = None
    ) -> None:
        """Log user action with structured data."""
        action_metadata = {
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }
        self.info(f"User action: {action}", action_metadata)

    def log_error(
        self, exception: Exception, metadata: Dict[str, Any] = None
    ) -> None:
        """Log error with full traceback and metadata."""
        error_metadata = {
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }
        self.error(f"Exception occurred: {str(exception)}", error_metadata)

    def log_performance(
        self, operation: str, duration: float, metadata: Dict[str, Any] = None
    ) -> None:
        """Log performance metrics."""
        perf_metadata = {
            "operation": operation,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }
        self.info(f"Performance: {operation} took {duration:.3f}s", perf_metadata)

    def log_api_call(
        self, endpoint: str, method: str, status_code: int,
        response_time: float, metadata: Dict[str, Any] = None
    ) -> None:
        """Log API call details."""
        api_metadata = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_seconds": response_time,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }
        self.info(
            f"API call: {method} {endpoint} - {status_code} "
            f"({response_time:.3f}s)",
            api_metadata
        )

    def log_database_operation(
        self, operation: str, table: str, duration: float,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log database operation."""
        db_metadata = {
            "operation": operation,
            "table": table,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }
        self.info(
            f"Database: {operation} on {table} took {duration:.3f}s",
            db_metadata
        )

    def log_security_event(
        self, event_type: str, severity: str, metadata: Dict[str, Any] = None
    ) -> None:
        """Log security-related events."""
        security_metadata = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }
        if severity == "HIGH":
            self.critical(f"Security event: {event_type}", security_metadata)
        else:
            self.warning(f"Security event: {event_type}", security_metadata)

    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        try:
            log_files = [
                "logs/bitmshauri.log",
                "logs/bitmshauri_errors.log",
            ]

            stats = {
                "log_files": {},
                "total_size": 0,
                "last_modified": None,
            }

            for log_file in log_files:
                if os.path.exists(log_file):
                    file_stat = os.stat(log_file)
                    stats["log_files"][log_file] = {
                        "size": file_stat.st_size,
                        "modified": datetime.fromtimestamp(
                            file_stat.st_mtime
                        ).isoformat(),
                    }
                    stats["total_size"] += file_stat.st_size

                    if not stats["last_modified"] or \
                            file_stat.st_mtime > stats["last_modified"]:
                        stats["last_modified"] = datetime.fromtimestamp(
                            file_stat.st_mtime
                        ).isoformat()

            return stats

        except Exception as e:
            self.error(f"Failed to get log stats: {str(e)}")
            return {}

    def cleanup_old_logs(self, days_to_keep: int = 30) -> None:
        """Clean up old log files."""
        try:
            import glob
            from datetime import timedelta

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            log_patterns = [
                "logs/bitmshauri.log.*",
                "logs/bitmshauri_errors.log.*",
            ]

            for pattern in log_patterns:
                for log_file in glob.glob(pattern):
                    try:
                        file_time = datetime.fromtimestamp(
                            os.path.getmtime(log_file)
                        )
                        if file_time < cutoff_date:
                            os.remove(log_file)
                            self.info(f"Removed old log file: {log_file}")
                    except Exception as e:
                        self.error(f"Failed to remove {log_file}: {str(e)}")

        except Exception as e:
            self.error(f"Failed to cleanup old logs: {str(e)}")

    def set_log_level(self, level: str) -> None:
        """Set logging level."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            self.info(f"Log level changed to {level.upper()}")
        else:
            self.warning(f"Invalid log level: {level}")


# Global logger instance
logger = StructuredLogger("bitmshauri")