import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


TOKEN = "8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno"


SWAHILI_CONTENT = {
    "welcome": "Habari! Mimi ni BitMshauri, msaidizi wako wa Bitcoin kwa Kiswahili. Chagua moja ya chaguo hapa chini:",
    "bitcoin_explanation": "Bitcoin ni pesa ya kidijitali (cryptocurrency) iliyoundwa mwaka 2009. "
                           "Inatumia teknolojia ya blockchain na idadi yake ni ndogo tu - 21 million pekee zitapatikana.",
    "unknown_command": "Samahani, sijaelewa. Tafadhali chagua moja ya chaguo zilizopo."
}


MENU_KEYBOARD = [
    ["💰 Bei ya Bitcoin", "📚 Bitcoin ni nini?"],
    ["ℹ️ Maelezo zaidi", "❓ Usaidizi"]
]

def create_menu():
    return ReplyKeyboardMarkup(MENU_KEYBOARD, resize_keyboard=True)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        SWAHILI_CONTENT["welcome"],
        reply_markup=create_menu()
    )

async def price_command(update: Update, context: CallbackContext):
    try:
        
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,kes"
        response = requests.get(url, timeout=5)
        data = response.json()
        btc = data['bitcoin']
        
        price_message = (
            f"🏷️ *Bei ya Bitcoin sasa:*\n"
            f"USD: ${btc['usd']:,}\n"
            f"KES: KSh {btc['kes']:,}"
        )
    except Exception as e:
        logger.error(f"Price error: {e}")
        price_message = "Samahani, bei haipatikani kwa sasa. Tafadhali jaribu tena baadaye."
    
    await update.message.reply_text(price_message, parse_mode="Markdown")

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    if text == "💰 Bei ya Bitcoin":
        await price_command(update, context)
    elif text == "📚 Bitcoin ni nini?":
        await update.message.reply_text(SWAHILI_CONTENT["bitcoin_explanation"])
    elif text == "ℹ️ Maelezo zaidi":
        await update.message.reply_text("Hii ni toleo rahisi la BitMshauri. Tunaendelea kuifanya bora!")
    elif text == "❓ Usaidizi":
        await update.message.reply_text("Tuma /start kuanza tena.")
    else:
        await update.message.reply_text(
            SWAHILI_CONTENT["unknown_command"],
            reply_markup=create_menu()
        )

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("bei", price_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Starting BitMshauri bot in minimal mode...")
    application.run_polling()

if __name__ == "__main__":
    main()