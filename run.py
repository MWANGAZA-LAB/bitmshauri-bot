from app import app
from app.bot.telegram_bot import bot_app

if __name__ == '__main__':
    print("🚀 Starting BitMshauri Telegram bot...")
    bot_app.run_polling()