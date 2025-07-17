import os
import re
from dotenv import load_dotenv

load_dotenv()

def validate_token(token):
    """Check if token matches Telegram bot token format"""
    if not token:
        return False
    
    pattern = r'^\d{8,10}:[a-zA-Z0-9_-]{35}$'
    return re.match(pattern, token) is not None

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '').strip()
    if not validate_token(TELEGRAM_TOKEN):
        raise ValueError("Invalid Telegram token format. Please check your .env file")
    
    GECKO_API_URL = os.getenv('GECKO_API_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bitmshauri.db'