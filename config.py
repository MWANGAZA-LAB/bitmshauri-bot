"""Configuration settings for BitMshauri Bot."""

import os
from typing import Optional

# Try to load from bot_config.py first, then fallback to environment variables
try:
    from bot_config import (
        TELEGRAM_BOT_TOKEN as BOT_TOKEN,
        GECKO_API_URL as API_URL,
        SECRET_KEY as SEC_KEY,
        LOG_LEVEL as LOG_LVL,
        DATABASE_PATH as DB_PATH,
    )
    print("✅ Loaded configuration from bot_config.py")
except ImportError:
    print("⚠️ bot_config.py not found, using environment variables")
    BOT_TOKEN = None
    API_URL = None
    SEC_KEY = None
    LOG_LVL = None
    DB_PATH = None

# Fallback to environment variables
from dotenv import load_dotenv
load_dotenv()


class Config:
    """Configuration class for BitMshauri Bot."""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN")

    # API Configuration
    GECKO_API_URL: str = API_URL or os.getenv(
        "GECKO_API_URL", "https://api.coingecko.com/api/v3"
    )

    # Security
    SECRET_KEY: Optional[str] = SEC_KEY or os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is required. Please set it in bot_config.py or .env file")

    # Optional Settings
    LOG_LEVEL: str = LOG_LVL or os.getenv("LOG_LEVEL", "INFO")
    DATABASE_PATH: str = DB_PATH or os.getenv("DATABASE_PATH", "bitmshauri.db")
