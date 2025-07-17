from app import app

@app.route('/')
def home():
    return "👋 Habari! BitMshauri Bitcoin Bot is running"