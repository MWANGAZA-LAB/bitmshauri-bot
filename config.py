import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # API Configuration
    GECKO_API_URL = os.getenv(
        "GECKO_API_URL", "https://api.coingecko.com/api/v3"
    )

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "bitmshauri_bot_secret_key_2024")

    # Optional Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "bitmshauri.db")
