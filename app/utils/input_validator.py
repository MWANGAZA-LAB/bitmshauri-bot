"""Input validation utilities for BitMshauri Bot.

Provides secure input validation and sanitization.
"""

import html
import re
from typing import Any, Dict

from app.utils.logger import logger


class InputValidator:
    """Secure input validation and sanitization."""

    # Regex patterns for validation
    PATTERNS = {
        "username": re.compile(r"^[a-zA-Z0-9_]{3,20}$"),
        "telegram_username": re.compile(r"^@?[a-zA-Z0-9_]{5,32}$"),
        "numeric": re.compile(r"^\d+(\.\d+)?$"),
        "currency_code": re.compile(r"^[A-Z]{3}$"),
        "lesson_key": re.compile(r"^[a-z_]+$"),
        "quiz_name": re.compile(r"^[a-z_]+$"),
        "group_name": re.compile(r"^[a-zA-Z0-9\s\-_]{3,50}$"),
        "message_text": re.compile(
            r"^[\w\s\.,!?\-_@#$%&*()+=:;\"'<>/\\[\]{}|`~]{1,4000}$"
        ),
    }

    # Allowed HTML tags for content (if any)
    ALLOWED_TAGS = {"b", "i", "u", "code", "pre"}

    @classmethod
    def validate_username(cls, username: str) -> bool:
        """Validate username format."""
        if not username or not isinstance(username, str):
            return False
        return bool(cls.PATTERNS["username"].match(username.strip()))

    @classmethod
    def validate_telegram_username(cls, username: str) -> bool:
        """Validate Telegram username format."""
        if not username or not isinstance(username, str):
            return False
        return bool(
            cls.PATTERNS["telegram_username"].match(username.strip())
        )

    @classmethod
    def validate_numeric(cls, value: str) -> bool:
        """Validate numeric input."""
        if not value or not isinstance(value, str):
            return False
        return bool(cls.PATTERNS["numeric"].match(value.strip()))

    @classmethod
    def validate_currency_code(cls, code: str) -> bool:
        """Validate currency code format."""
        if not code or not isinstance(code, str):
            return False
        return bool(cls.PATTERNS["currency_code"].match(code.strip()))

    @classmethod
    def validate_lesson_key(cls, key: str) -> bool:
        """Validate lesson key format."""
        if not key or not isinstance(key, str):
            return False
        return bool(cls.PATTERNS["lesson_key"].match(key.strip()))

    @classmethod
    def validate_quiz_name(cls, name: str) -> bool:
        """Validate quiz name format."""
        if not name or not isinstance(name, str):
            return False
        return bool(cls.PATTERNS["quiz_name"].match(name.strip()))

    @classmethod
    def validate_group_name(cls, name: str) -> bool:
        """Validate group name format."""
        if not name or not isinstance(name, str):
            return False
        return bool(cls.PATTERNS["group_name"].match(name.strip()))

    @classmethod
    def validate_message_text(cls, text: str) -> bool:
        """Validate message text format."""
        if not text or not isinstance(text, str):
            return False
        return bool(cls.PATTERNS["message_text"].match(text.strip()))

    @classmethod
    def validate_user_id(cls, user_id: Any) -> bool:
        """Validate user ID format."""
        try:
            uid = int(user_id)
            return 1 <= uid <= 2**63 - 1  # Valid Telegram user ID range
        except (ValueError, TypeError):
            return False

    @classmethod
    def validate_calculation_input(cls, text: str) -> Dict[str, Any]:
        """Validate calculation input and extract components."""
        if not text or not isinstance(text, str):
            return {"valid": False, "error": "Invalid input format"}

        text = text.strip().lower()

        # Common calculation patterns
        patterns = [
            r"(\d+(?:\.\d+)?)\s*(usd|dollar|dollars)\s*(?:to|in)\s*(btc|bitcoin)",
            r"(\d+(?:\.\d+)?)\s*(btc|bitcoin)\s*(?:to|in)\s*(usd|dollar|dollars)",
            r"(\d+(?:\.\d+)?)\s*(?:usd|dollar|dollars)",
            r"(\d+(?:\.\d+)?)\s*(?:btc|bitcoin)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                amount = float(match.group(1))
                if amount <= 0:
                    return {"valid": False, "error": "Amount must be positive"}
                return {
                    "valid": True,
                    "amount": amount,
                    "text": text,
                    "pattern": pattern,
                }

        return {"valid": False, "error": "Invalid calculation format"}

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Sanitize HTML content."""
        if not text or not isinstance(text, str):
            return ""

        # Escape HTML entities
        sanitized = html.escape(text)

        # Remove any remaining potentially dangerous content
        sanitized = re.sub(
            r"<script[^>]*>.*?</script>", "", sanitized,
            flags=re.IGNORECASE | re.DOTALL
        )
        sanitized = re.sub(
            r"<iframe[^>]*>.*?</iframe>", "", sanitized,
            flags=re.IGNORECASE | re.DOTALL
        )
        sanitized = re.sub(
            r"javascript:", "", sanitized, flags=re.IGNORECASE
        )

        return sanitized.strip()

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for safe storage."""
        if not filename or not isinstance(filename, str):
            return ""

        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
        sanitized = re.sub(r'[^\w\-_\.]', "_", sanitized)
        sanitized = sanitized.strip("._")

        # Limit length
        if len(sanitized) > 100:
            if "." in sanitized:
                name, ext = sanitized.rsplit(".", 1)
                sanitized = name[:95] + f".{ext}"
            else:
                sanitized = sanitized[:100]

        return sanitized or "file"

    @classmethod
    def validate_file_upload(
        cls, filename: str, content_type: str, size: int
    ) -> Dict[str, Any]:
        """Validate file upload parameters."""
        # Allowed file types
        allowed_types = {
            "image/jpeg", "image/png", "image/gif", "image/webp",
            "audio/mpeg", "audio/wav", "audio/ogg",
            "text/plain", "application/pdf"
        }

        # Maximum file size (10MB)
        max_size = 10 * 1024 * 1024

        if not filename:
            return {"valid": False, "error": "No filename provided"}

        if content_type not in allowed_types:
            return {"valid": False, "error": "File type not allowed"}

        if size > max_size:
            return {"valid": False, "error": "File too large"}

        if size <= 0:
            return {"valid": False, "error": "Invalid file size"}

        return {"valid": True, "filename": cls.sanitize_filename(filename)}

    @classmethod
    def validate_api_key(cls, api_key: str) -> bool:
        """Validate API key format."""
        if not api_key or not isinstance(api_key, str):
            return False

        # Basic API key validation (adjust based on your requirements)
        api_key = api_key.strip()
        return (
            10 <= len(api_key) <= 200 and
            re.match(r"^[a-zA-Z0-9_\-]+$", api_key) is not None
        )

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate URL format."""
        if not url or not isinstance(url, str):
            return False

        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE
        )
        return bool(url_pattern.match(url.strip()))

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False

        email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        return bool(email_pattern.match(email.strip()))

    @classmethod
    def validate_phone_number(cls, phone: str) -> bool:
        """Validate phone number format."""
        if not phone or not isinstance(phone, str):
            return False

        # Remove all non-digit characters
        digits = re.sub(r"\D", "", phone)
        return 7 <= len(digits) <= 15

    @classmethod
    def validate_password_strength(cls, password: str) -> Dict[str, Any]:
        """Validate password strength."""
        if not password or not isinstance(password, str):
            return {"valid": False, "error": "Password required"}

        if len(password) < 8:
            return {"valid": False, "error": "Password too short"}

        if len(password) > 128:
            return {"valid": False, "error": "Password too long"}

        # Check for required character types
        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

        strength_score = sum([has_lower, has_upper, has_digit, has_special])

        if strength_score < 3:
            return {
                "valid": False,
                "error": (
                    "Password must contain at least 3 of: lowercase, "
                    "uppercase, digits, special characters"
                )
            }

        return {"valid": True, "strength": strength_score}

    @classmethod
    def validate_json_input(cls, json_str: str) -> Dict[str, Any]:
        """Validate JSON input."""
        if not json_str or not isinstance(json_str, str):
            return {"valid": False, "error": "Invalid JSON input"}

        try:
            import json
            parsed = json.loads(json_str)
            return {"valid": True, "data": parsed}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": f"Invalid JSON: {str(e)}"}

    @classmethod
    def validate_sql_injection(cls, text: str) -> bool:
        """Basic SQL injection detection."""
        if not text or not isinstance(text, str):
            return True

        # Common SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|\#|\/\*|\*\/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"].*['\"]\s*=\s*['\"].*['\"])",
            r"(\bUNION\s+SELECT\b)",
            r"(\bDROP\s+TABLE\b)",
            r"(\bDELETE\s+FROM\b)",
        ]

        text_upper = text.upper()
        for pattern in sql_patterns:
            if re.search(pattern, text_upper, re.IGNORECASE):
                logger.logger.warning(f"Potential SQL injection detected: {text[:100]}")
                return False

        return True

    @classmethod
    def validate_xss(cls, text: str) -> bool:
        """Basic XSS detection."""
        if not text or not isinstance(text, str):
            return True

        # Common XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                logger.logger.warning(f"Potential XSS detected: {text[:100]}")
                return False

        return True

    @classmethod
    def comprehensive_validation(cls, text: str, validation_type: str = "general") -> Dict[str, Any]:
        """Comprehensive validation based on type."""
        if not text or not isinstance(text, str):
            return {"valid": False, "error": "Invalid input"}

        # Basic security checks
        if not cls.validate_sql_injection(text):
            return {"valid": False, "error": "Potential security risk detected"}

        if not cls.validate_xss(text):
            return {"valid": False, "error": "Potential security risk detected"}

        # Type-specific validation
        if validation_type == "username":
            is_valid = cls.validate_username(text)
            return {
                "valid": is_valid,
                "error": "Invalid username format" if not is_valid else None
            }
        elif validation_type == "email":
            is_valid = cls.validate_email(text)
            return {
                "valid": is_valid,
                "error": "Invalid email format" if not is_valid else None
            }
        elif validation_type == "url":
            is_valid = cls.validate_url(text)
            return {
                "valid": is_valid,
                "error": "Invalid URL format" if not is_valid else None
            }
        elif validation_type == "message":
            is_valid = cls.validate_message_text(text)
            return {
                "valid": is_valid,
                "error": "Invalid message format" if not is_valid else None
            }
        else:
            return {"valid": True, "error": None}


# Convenience functions for backward compatibility
def validate_input(text: str, validation_type: str = "general") -> Dict[str, Any]:
    """Validate input using the InputValidator class."""
    return InputValidator.comprehensive_validation(text, validation_type)