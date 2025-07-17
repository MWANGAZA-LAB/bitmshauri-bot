from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

print("✅ BitMshauri app initialized!")


from app.bot import telegram_bot