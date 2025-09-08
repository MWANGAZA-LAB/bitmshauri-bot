"""
Input validation utilities for BitMshauri Bot
Provides secure input validation and sanitization
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from app.utils.logger import logger


class InputValidator:
    """Secure input validation and sanitization"""
    
    # Regex patterns for validation
    PATTERNS = {
        'username': re.compile(r'^[a-zA-Z0-9_]{3,20}$'),
        'telegram_username': re.compile(r'^@?[a-zA-Z0-9_]{5,32}$'),
        'numeric': re.compile(r'^\d+(\.\d+)?$'),
        'currency_code': re.compile(r'^[A-Z]{3}$'),
        'lesson_key': re.compile(r'^[a-z_]+$'),
        'quiz_name': re.compile(r'^[a-z_]+$'),
        'group_name': re.compile(r'^[a-zA-Z0-9\s\-_]{3,50}$'),
        'message_text': re.compile(r'^[\w\s\.,!?\-_@#$%&*()+=:;"\'<>/\\[\]{}|`~]{1,4000}$'),
    }
    
    # Allowed HTML tags for content (if any)
    ALLOWED_TAGS = {'b', 'i', 'u', 'code', 'pre'}
    
    @classmethod
    def validate_username(cls, username: str) -> bool:
        """Validate username format"""
        if not username or not isinstance(username, str):
            return False
        return bool(cls.PATTERNS['username'].match(username.strip()))
    
    @classmethod
    def validate_telegram_username(cls, username: str) -> bool:
        """Validate Telegram username format"""
        if not username or not isinstance(username, str):
            return False
        return bool(cls.PATTERNS['telegram_username'].match(username.strip()))
    
    @classmethod
    def validate_numeric(cls, value: str) -> bool:
        """Validate numeric input"""
        if not value or not isinstance(value, str):
            return False
        return bool(cls.PATTERNS['numeric'].match(value.strip()))
    
    @classmethod
    def validate_currency_code(cls, currency: str) -> bool:
        """Validate currency code"""
        if not currency or not isinstance(currency, str):
            return False
        return bool(cls.PATTERNS['currency_code'].match(currency.strip().upper()))
    
    @classmethod
    def validate_lesson_key(cls, key: str) -> bool:
        """Validate lesson key format"""
        if not key or not isinstance(key, str):
            return False
        return bool(cls.PATTERNS['lesson_key'].match(key.strip()))
    
    @classmethod
    def validate_quiz_name(cls, name: str) -> bool:
        """Validate quiz name format"""
        if not name or not isinstance(name, str):
            return False
        return bool(cls.PATTERNS['quiz_name'].match(name.strip()))
    
    @classmethod
    def validate_group_name(cls, name: str) -> bool:
        """Validate group name format"""
        if not name or not isinstance(name, str):
            return False
        return bool(cls.PATTERNS['group_name'].match(name.strip()))
    
    @classmethod
    def validate_message_text(cls, text: str) -> bool:
        """Validate message text content"""
        if not text or not isinstance(text, str):
            return False
        return bool(cls.PATTERNS['message_text'].match(text.strip()))
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 4000) -> str:
        """Sanitize text input by escaping HTML and limiting length"""
        if not text or not isinstance(text, str):
            return ""
        
        # HTML escape
        sanitized = html.escape(text.strip())
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.log_user_action(
                None, 
                "text_truncated", 
                {"original_length": len(text), "truncated_length": max_length}
            )
        
        return sanitized
    
    @classmethod
    def sanitize_html_content(cls, content: str) -> str:
        """Sanitize HTML content by removing dangerous tags"""
        if not content or not isinstance(content, str):
            return ""
        
        # Remove script tags and dangerous attributes
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'on\w+\s*=', '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    @classmethod
    def validate_user_id(cls, user_id: Any) -> bool:
        """Validate user ID format"""
        if isinstance(user_id, int):
            return 1 <= user_id <= 2**63 - 1
        elif isinstance(user_id, str):
            try:
                uid = int(user_id)
                return 1 <= uid <= 2**63 - 1
            except ValueError:
                return False
        return False
    
    @classmethod
    def validate_calculation_input(cls, text: str) -> Dict[str, Any]:
        """Validate and parse calculation input"""
        if not text or not isinstance(text, str):
            return {"valid": False, "error": "Invalid input"}
        
        text = text.strip().lower()
        
        # Check for malicious patterns
        dangerous_patterns = [
            r'<script', r'javascript:', r'data:', r'vbscript:',
            r'onload=', r'onerror=', r'onclick=', r'eval\(',
            r'exec\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.log_user_action(
                    None,
                    "malicious_input_detected",
                    {"pattern": pattern, "input": text[:100]}
                )
                return {"valid": False, "error": "Invalid input detected"}
        
        # Validate calculation format
        calc_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:usd|dollars?)\s*(?:to|into|=|in)\s*(?:btc|bitcoin)',
            r'(\d+(?:\.\d+)?)\s*(?:kes|ksh|shillings?)\s*(?:to|into|=|in)\s*(?:btc|bitcoin)',
            r'(\d+(?:\.\d+)?)\s*(?:btc|bitcoin)\s*(?:to|into|=|in)\s*(?:usd|dollars?)',
            r'(\d+(?:\.\d+)?)\s*(?:btc|bitcoin)\s*(?:to|into|=|in)\s*(?:kes|ksh|shillings?)',
        ]
        
        for pattern in calc_patterns:
            match = re.search(pattern, text)
            if match:
                amount = float(match.group(1))
                if 0 < amount <= 1000000:  # Reasonable limits
                    return {"valid": True, "amount": amount, "pattern": pattern}
        
        return {"valid": False, "error": "Invalid calculation format"}
    
    @classmethod
    def validate_language_code(cls, lang_code: str) -> bool:
        """Validate language code"""
        if not lang_code or not isinstance(lang_code, str):
            return False
        return lang_code.strip().lower() in ['sw', 'en']
    
    @classmethod
    def validate_price_alert_input(cls, price: Any, currency: str, condition: str) -> Dict[str, Any]:
        """Validate price alert input"""
        result = {"valid": True, "errors": []}
        
        # Validate price
        try:
            price_float = float(price)
            if not (0 < price_float <= 1000000):  # Reasonable price limits
                result["errors"].append("Price must be between 0 and 1,000,000")
                result["valid"] = False
        except (ValueError, TypeError):
            result["errors"].append("Invalid price format")
            result["valid"] = False
        
        # Validate currency
        if not cls.validate_currency_code(currency):
            result["errors"].append("Invalid currency code")
            result["valid"] = False
        
        # Validate condition
        if condition not in ['above', 'below']:
            result["errors"].append("Condition must be 'above' or 'below'")
            result["valid"] = False
        
        return result


def validate_and_sanitize_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize input data dictionary"""
    validator = InputValidator()
    sanitized_data = {}
    
    for key, value in input_data.items():
        if key == 'username':
            if validator.validate_username(str(value)):
                sanitized_data[key] = validator.sanitize_text(str(value), 20)
            else:
                raise ValueError(f"Invalid username: {value}")
        
        elif key == 'message_text':
            if validator.validate_message_text(str(value)):
                sanitized_data[key] = validator.sanitize_text(str(value))
            else:
                raise ValueError(f"Invalid message text: {value}")
        
        elif key == 'user_id':
            if validator.validate_user_id(value):
                sanitized_data[key] = int(value)
            else:
                raise ValueError(f"Invalid user ID: {value}")
        
        elif key == 'language':
            if validator.validate_language_code(str(value)):
                sanitized_data[key] = str(value).strip().lower()
            else:
                raise ValueError(f"Invalid language code: {value}")
        
        else:
            # Default sanitization for other fields
            if isinstance(value, str):
                sanitized_data[key] = validator.sanitize_text(str(value))
            else:
                sanitized_data[key] = value
    
    return sanitized_data


# Decorator for input validation
def validate_input(**validation_rules):
    """Decorator to validate function inputs"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract validation rules for this function
            validated_kwargs = {}
            
            for key, value in kwargs.items():
                if key in validation_rules:
                    rule = validation_rules[key]
                    validator = InputValidator()
                    
                    if rule == 'username' and not validator.validate_username(str(value)):
                        raise ValueError(f"Invalid username: {value}")
                    elif rule == 'user_id' and not validator.validate_user_id(value):
                        raise ValueError(f"Invalid user ID: {value}")
                    elif rule == 'message_text' and not validator.validate_message_text(str(value)):
                        raise ValueError(f"Invalid message text: {value}")
                    elif rule == 'language' and not validator.validate_language_code(str(value)):
                        raise ValueError(f"Invalid language: {value}")
                    
                    validated_kwargs[key] = value
                else:
                    validated_kwargs[key] = value
            
            return func(*args, **validated_kwargs)
        return wrapper
    return decorator
