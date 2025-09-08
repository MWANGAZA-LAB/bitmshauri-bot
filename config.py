"""Configuration settings for BitMshauri Bot."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for BitMshauri Bot."""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")

    # API Configuration
    GECKO_API_URL: str = os.getenv(
        "GECKO_API_URL", "https://api.coingecko.com/api/v3"
    )

    # Security
    SECRET_KEY: Optional[str] = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")

    # Optional Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "bitmshauri.db")
