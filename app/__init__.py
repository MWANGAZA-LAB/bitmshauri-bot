#from flask import Flask
from config import Config
import os

#app = Flask(__name__)
#app.config.from_object(Config)

print("✅ BitMshauri app initialized!")

# Import bot components after app initialization
from app.bot import telegram_bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")