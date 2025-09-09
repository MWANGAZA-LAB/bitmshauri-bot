#!/usr/bin/env python3
"""Enhanced BitMshauri Bot with comprehensive content integration."""

import logging
import requests
import asyncio
import random
import os
import tempfile
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from telegram.error import Conflict, NetworkError, TimedOut

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Try to import text-to-speech libraries
try:
    from gtts import gTTS
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ gTTS not available. Audio features disabled.")

# Import comprehensive content
from app.bot.content_swahili import LESSONS as SWAHILI_LESSONS
from app.bot.content_english import LESSONS as ENGLISH_LESSONS

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is required. Please set it in .env file")

# User language preferences (in-memory storage)
user_languages = {}


def generate_audio(text, lang="en"):
    """Generate audio from text using gTTS."""
    if not AUDIO_AVAILABLE:
        return None
    
    try:
        # Clean text for better audio
        clean_text = re.sub(r'[^\w\s.,!?]', '', text)
        clean_text = clean_text.replace('*', '').replace('_', '')
        
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        return None


def get_bitcoin_price():
    """Get current Bitcoin price in USD and KES."""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        data = response.json()
        usd_price = data["bitcoin"]["usd"]
        
        # Convert to KES (approximate rate: 1 USD = 130 KES)
        kes_price = usd_price * 130
        
        return f"💰 *Bitcoin Price*\n🇺🇸 USD: ${usd_price:,.2f}\n🇰🇪 KES: KSh {kes_price:,.2f}\n📊 Current prices from CoinGecko"
    except Exception as e:
        logger.error(f"Error fetching Bitcoin price: {e}")
        return "💰 *Bitcoin Price*\n❌ Unable to fetch current price. Please try again later."


def detect_language(text):
    """Detect if text is in Swahili or English."""
    swahili_words = ['habari', 'asante', 'karibu', 'bitcoin', 'nini', 'jinsi', 'kwa', 'na', 'ya', 'wa', 'ni']
    swahili_count = sum(1 for word in swahili_words if word.lower() in text.lower())
    return swahili_count >= 2


def get_main_menu_keyboard(lang="en", collapsed=False):
    """Get main menu keyboard based on language with collapsible option."""
    if lang == "sw":
        if collapsed:
            # Collapsed menu - only essential options
            keyboard = [
                [
                    InlineKeyboardButton("📚 Bitcoin ni nini?", callback_data="bitcoin_ni_nini"),
                    InlineKeyboardButton("📱 Nunua kwa M-Pesa", callback_data="mpesa_guide")
                ],
                [
                    InlineKeyboardButton("📝 Jaribio", callback_data="quiz"),
                    InlineKeyboardButton("💡 Kidokezo cha Leo", callback_data="daily_tip")
                ],
                [
                    InlineKeyboardButton("🔍 Menyu Kamili", callback_data="expand_menu"),
                    InlineKeyboardButton("🌍 Lugha", callback_data="language")
                ]
            ]
        else:
            # Full menu
            keyboard = [
                [
                    InlineKeyboardButton("📚 Bitcoin ni nini?", callback_data="bitcoin_ni_nini"),
                    InlineKeyboardButton("🔗 P2P Inafanyaje", callback_data="p2p_inafanyaje")
                ],
                [
                    InlineKeyboardButton("👛 Aina za Pochi", callback_data="kufungua_pochi"),
                    InlineKeyboardButton("🔒 Usalama wa Pochi", callback_data="usalama_pochi")
                ],
                [
                    InlineKeyboardButton("📱 Nunua kwa M-Pesa", callback_data="mpesa_guide"),
                    InlineKeyboardButton("⚖️ Faida na Hatari", callback_data="faida_na_hatari")
                ],
                [
                    InlineKeyboardButton("❓ Maswali Mengine", callback_data="maswali_mengine"),
                    InlineKeyboardButton("🔐 Teknolojia ya Blockchain", callback_data="blockchain_usalama")
                ],
                [
                    InlineKeyboardButton("📝 Jaribio la Bitcoin", callback_data="quiz"),
                    InlineKeyboardButton("💡 Kidokezo cha Leo", callback_data="daily_tip")
                ],
                [
                    InlineKeyboardButton("ℹ️ Kuhusu BitMshauri", callback_data="kuhusu_bitmshauri"),
                    InlineKeyboardButton("🔍 Menyu Fupi", callback_data="collapse_menu")
                ],
                [
                    InlineKeyboardButton("🌍 Badilisha Lugha", callback_data="language")
                ]
            ]
    else:
        if collapsed:
            # Collapsed English menu
            keyboard = [
                [
                    InlineKeyboardButton("📚 What is Bitcoin?", callback_data="what_is_bitcoin"),
                    InlineKeyboardButton("📱 Buy with M-Pesa", callback_data="buying_guide")
                ],
                [
                    InlineKeyboardButton("📝 Quiz", callback_data="quiz"),
                    InlineKeyboardButton("💡 Daily Tip", callback_data="daily_tip")
                ],
                [
                    InlineKeyboardButton("🔍 Full Menu", callback_data="expand_menu"),
                    InlineKeyboardButton("🌍 Language", callback_data="language")
                ]
            ]
        else:
            # Full English menu
            keyboard = [
                [
                    InlineKeyboardButton("📚 What is Bitcoin?", callback_data="what_is_bitcoin"),
                    InlineKeyboardButton("🔗 How P2P Works", callback_data="how_p2p_works")
                ],
                [
                    InlineKeyboardButton("👛 Wallet Types", callback_data="wallet_types"),
                    InlineKeyboardButton("🔒 Wallet Security", callback_data="wallet_security")
                ],
                [
                    InlineKeyboardButton("📱 Buy with M-Pesa", callback_data="buying_guide"),
                    InlineKeyboardButton("⚖️ Pros and Cons", callback_data="pros_and_cons")
                ],
                [
                    InlineKeyboardButton("❓ FAQ", callback_data="frequently_asked"),
                    InlineKeyboardButton("🔐 Blockchain Technology", callback_data="blockchain_technology")
                ],
                [
                    InlineKeyboardButton("📝 Bitcoin Quiz", callback_data="quiz"),
                    InlineKeyboardButton("💡 Daily Tip", callback_data="daily_tip")
                ],
                [
                    InlineKeyboardButton("ℹ️ About BitMshauri", callback_data="about_bitmshauri"),
                    InlineKeyboardButton("🔍 Compact Menu", callback_data="collapse_menu")
                ],
                [
                    InlineKeyboardButton("🌍 Change Language", callback_data="language")
                ]
            ]
    
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    if not update.message or not update.message.from_user:
        return
    
    user = update.message.from_user
    user_id = user.id
    
    # Detect language preference
    lang = "sw" if detect_language(user.first_name or "") else "en"
    user_languages[user_id] = lang
    
    # Get Bitcoin price
    price_info = get_bitcoin_price()
    
    # Welcome message
    if lang == "sw":
        welcome_text = f"""🎉 Karibu kwenye BitMshauri Bot!

Habari {user.first_name}! Mimi ni msaidizi wako wa Bitcoin! 🇹🇿

{price_info}

Chagua moja ya chaguo hapa chini:

🎶 Unaweza pia kupata matoleo ya sauti kwa kubonyeza 🎵"""
    else:
        welcome_text = f"""🎉 Welcome to BitMshauri Bot!

Hello {user.first_name}! I'm your Bitcoin education assistant! 🇺🇸

{price_info}

Choose one of the options below:

🎶 You can also get audio versions by clicking 🎵"""
    
    reply_markup = get_main_menu_keyboard(lang, collapsed=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    if not update.callback_query or not update.callback_query.from_user:
        return
    
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    # Get user language preference
    lang = user_languages.get(user_id, "en")
    
    # Handle menu collapse/expand
    if callback_data == "collapse_menu":
        if lang == "sw":
            response_text = "🔍 <b>Menyu Fupi</b>\n\nChagua moja ya chaguo hapa chini:"
        else:
            response_text = "🔍 <b>Compact Menu</b>\n\nChoose one of the options below:"
        reply_markup = get_main_menu_keyboard(lang, collapsed=True)
        await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='HTML')
        return
    
    elif callback_data == "expand_menu":
        if lang == "sw":
            response_text = "🔍 <b>Menyu Kamili</b>\n\nChagua moja ya chaguo hapa chini:"
        else:
            response_text = "🔍 <b>Full Menu</b>\n\nChoose one of the options below:"
        reply_markup = get_main_menu_keyboard(lang, collapsed=False)
        await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='HTML')
        return
    
    # Handle different callback types
    if callback_data == "price":
        # Price is now shown automatically in welcome message, redirect to main menu
        if lang == "sw":
            response_text = "💰 Bei ya Bitcoin imeonyeshwa tayari katika ujumbe wa karibu. Chagua chaguo jingine:"
        else:
            response_text = "💰 Bitcoin price is already shown in the welcome message. Choose another option:"
        reply_markup = get_main_menu_keyboard(lang, collapsed=True)
        
    elif callback_data in SWAHILI_LESSONS:
        # Handle Swahili lessons
        lesson = SWAHILI_LESSONS[callback_data]
        response_text = lesson["content"]
        
        # Add audio button
        audio_keyboard = [
            [InlineKeyboardButton("🎵 Sauti", callback_data=f"audio_{callback_data}")],
            [InlineKeyboardButton("⬅️ Rudi", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(audio_keyboard)
        
    elif callback_data in ENGLISH_LESSONS:
        # Handle English lessons
        lesson = ENGLISH_LESSONS[callback_data]
        response_text = lesson["content"]
        
        # Add audio button
        audio_keyboard = [
            [InlineKeyboardButton("🎵 Audio", callback_data=f"audio_{callback_data}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(audio_keyboard)
        
    elif callback_data.startswith("audio_"):
        # Handle audio generation
        lesson_key = callback_data.replace("audio_", "")
        
        if lang == "sw" and lesson_key in SWAHILI_LESSONS:
            lesson = SWAHILI_LESSONS[lesson_key]
            audio_lang = "sw"
        elif lang == "en" and lesson_key in ENGLISH_LESSONS:
            lesson = ENGLISH_LESSONS[lesson_key]
            audio_lang = "en"
        else:
            response_text = "❌ Audio not available for this lesson."
            reply_markup = get_main_menu_keyboard(lang, collapsed=True)
            await query.edit_message_text(text=response_text, reply_markup=reply_markup)
            return
        
        # Generate audio
        audio_file = generate_audio(lesson["content"], audio_lang)
        
        if audio_file:
            try:
                with open(audio_file, 'rb') as audio:
                    await query.message.reply_voice(voice=InputFile(audio))
                os.unlink(audio_file)  # Clean up
                
                if lang == "sw":
                    response_text = "🎵 Sauti imetolewa! Chagua chaguo jingine:"
                else:
                    response_text = "🎵 Audio generated! Choose another option:"
                reply_markup = get_main_menu_keyboard(lang, collapsed=True)
                await query.edit_message_text(text=response_text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error sending audio: {e}")
                response_text = "❌ Error generating audio. Please try again."
                reply_markup = get_main_menu_keyboard(lang, collapsed=True)
                await query.edit_message_text(text=response_text, reply_markup=reply_markup)
        else:
            response_text = "❌ Audio generation failed. Please try again."
            reply_markup = get_main_menu_keyboard(lang, collapsed=True)
            await query.edit_message_text(text=response_text, reply_markup=reply_markup)
        return
        
    elif callback_data == "back_to_menu":
        if lang == "sw":
            response_text = "🏠 <b>Menyu Kuu</b>\n\nChagua moja ya chaguo hapa chini:"
        else:
            response_text = "🏠 <b>Main Menu</b>\n\nChoose one of the options below:"
        reply_markup = get_main_menu_keyboard(lang, collapsed=True)
        
    elif callback_data == "language":
        # Toggle language
        new_lang = "en" if lang == "sw" else "sw"
        user_languages[user_id] = new_lang
        
        if new_lang == "sw":
            response_text = "🌍 Lugha imebadilishwa kwenda Kiswahili! 🇹🇿"
        else:
            response_text = "🌍 Language changed to English! 🇺🇸"
        
        reply_markup = get_main_menu_keyboard(new_lang, collapsed=True)
        
    elif callback_data == "quiz":
        if lang == "sw":
            response_text = "📝 <b>Jaribio la Bitcoin</b>\n\nHili ni jaribio la kujifunza kuhusu Bitcoin. Chagua chaguo jingine:"
        else:
            response_text = "📝 <b>Bitcoin Quiz</b>\n\nThis is a learning quiz about Bitcoin. Choose another option:"
        reply_markup = get_main_menu_keyboard(lang, collapsed=True)
        
    elif callback_data == "daily_tip":
        if lang == "sw":
            response_text = "💡 <b>Kidokezo cha Leo</b>\n\nBitcoin ni sarafu ya kidijitali huru. Chagua chaguo jingine:"
        else:
            response_text = "💡 <b>Daily Tip</b>\n\nBitcoin is a decentralized digital currency. Choose another option:"
        reply_markup = get_main_menu_keyboard(lang, collapsed=True)
        
    else:
        # Default response
        if lang == "sw":
            response_text = "❓ Chaguo hili halijafafanuliwa. Chagua chaguo jingine:"
        else:
            response_text = "❓ This option is not defined. Choose another option:"
        reply_markup = get_main_menu_keyboard(lang, collapsed=True)
    
    await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='HTML')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    if not update.message or not update.message.text:
        return
    
    user_id = update.message.from_user.id
    text = update.message.text.lower()
    
    # Get user language preference
    lang = user_languages.get(user_id, "en")
    
    # Simple text responses
    if any(word in text for word in ['hello', 'hi', 'habari', 'hujambo']):
        if lang == "sw":
            response = "Habari! Ninaweza kukusaidia kujifunza kuhusu Bitcoin. Tumia menyu hapa chini:"
        else:
            response = "Hello! I can help you learn about Bitcoin. Use the menu below:"
    else:
        if lang == "sw":
            response = "Sielewi. Tumia menyu hapa chini:"
        else:
            response = "I don't understand. Use the menu below:"
    
    reply_markup = get_main_menu_keyboard(lang, collapsed=True)
    await update.message.reply_text(response, reply_markup=reply_markup)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if isinstance(context.error, Conflict):
        logger.error("🚨 CONFLICT ERROR: Another bot instance is running!")
        logger.error("💡 SOLUTION: Stop all other bot instances and try again.")
    elif isinstance(context.error, (NetworkError, TimedOut)):
        logger.warning("🌐 Network error: Retrying connection...")
    else:
        logger.error(f"❌ Unexpected error: {context.error}")


def main():
    """Main function to run the bot."""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("🚀 Starting BitMshauri Bot...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )


if __name__ == "__main__":
    main()
