from app import app
from app.bot.telegram_bot import bot_app
from app.database import init_db

if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_db()
    print("🚀 Starting BitMshauri Telegram bot...")
    bot_app.run_polling()
