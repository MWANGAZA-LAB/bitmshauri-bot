"""Configuration settings for BitMshauri Bot."""

import os
from typing import Optional

# Try to load from bot_config.py first, then fallback to deployment config
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
    print("⚠️ bot_config.py not found, using deployment configuration")
    try:
        from deployment_config import DeploymentConfig
        BOT_TOKEN = DeploymentConfig.TELEGRAM_BOT_TOKEN
        API_URL = DeploymentConfig.GECKO_API_URL
        SEC_KEY = DeploymentConfig.SECRET_KEY
        LOG_LVL = DeploymentConfig.LOG_LEVEL
        DB_PATH = DeploymentConfig.DATABASE_PATH
        print("✅ Loaded configuration from deployment_config.py")
    except ImportError:
        print("⚠️ Using environment variables only")
        BOT_TOKEN: Optional[str] = None
        API_URL: Optional[str] = None
        SEC_KEY: Optional[str] = None
        LOG_LVL: Optional[str] = None
        DB_PATH: Optional[str] = None

# Fallback to environment variables
from dotenv import load_dotenv
load_dotenv()


class Config:
    """Configuration class for BitMshauri Bot."""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = (
        BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN")
    )
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is required. Please set it in environment variables"
        )

    # API Configuration
    GECKO_API_URL: str = API_URL or os.getenv(
        "GECKO_API_URL", "https://api.coingecko.com/api/v3"
    )

    # Security
    SECRET_KEY: Optional[str] = SEC_KEY or os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        # Fallback for deployment environments
        SECRET_KEY = "bitmshauri_secure_key_2024_production"
        print("⚠️ Using fallback SECRET_KEY for deployment")

    # Optional Settings
    LOG_LEVEL: str = LOG_LVL or os.getenv("LOG_LEVEL", "INFO")
    DATABASE_PATH: str = DB_PATH or os.getenv("DATABASE_PATH", "bitmshauri.db")
