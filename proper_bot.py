#!/usr/bin/env python3
"""Enhanced BitMshauri Bot with comprehensive Swahili content integration."""

import logging
import requests
import time
import asyncio
import random
import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from telegram.error import Conflict, NetworkError, TimedOut

# Try to import text-to-speech libraries
try:
    from gtts import gTTS
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ gTTS not available. Audio features disabled.")

# Import comprehensive content
from app.bot.content_swahili import LESSONS as SWAHILI_LESSONS, QUIZZES as SWAHILI_QUIZZES, DAILY_TIPS as SWAHILI_TIPS, MENU_KEYBOARD as SWAHILI_MENU
from app.bot.content_english import LESSONS as ENGLISH_LESSONS, QUIZZES as ENGLISH_QUIZZES, DAILY_TIPS as ENGLISH_TIPS, MENU_KEYBOARD as ENGLISH_MENU

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno"

# User language preferences (in-memory storage)
user_languages = {}

def generate_audio(text, lang="en"):
    """Generate audio from text using gTTS."""
    if not AUDIO_AVAILABLE:
        return None
    
    try:
        # Clean text for TTS
        clean_text = text.replace("*", "").replace("_", "").replace("`", "")
        clean_text = clean_text.replace("💰", "").replace("🔗", "").replace("👛", "")
        clean_text = clean_text.replace("🔒", "").replace("⚠️", "").replace("📱", "")
        clean_text = clean_text.replace("⚖️", "").replace("❓", "").replace("ℹ️", "")
        clean_text = clean_text.replace("💡", "").replace("📝", "").replace("🌍", "")
        clean_text = clean_text.replace("🇺🇸", "").replace("🇰🇪", "").replace("📊", "")
        
        # Set language for TTS
        tts_lang = "sw" if lang == "sw" else "en"
        
        # Generate audio
        tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
            
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        return None

def get_bitcoin_price():
    """Get Bitcoin price in USD and KES with fallback."""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,kes",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            usd_price = data['bitcoin']['usd']
            kes_price = data['bitcoin']['kes']
            
            usd_formatted = f"{usd_price:,.2f}"
            kes_formatted = f"{kes_price:,.2f}"
            
            return f"""💰 <b>Bei ya Bitcoin</b>

🇺🇸 <b>USD:</b> ${usd_formatted}
🇰🇪 <b>KES:</b> KSh {kes_formatted}

📊 <i>Bei za sasa kutoka CoinGecko</i>"""
            
        else:
            return """💰 <b>Bei ya Bitcoin</b>

❌ Haiwezi kupata bei za sasa. Tafadhali jaribu tena baadaye.

📊 Angalia bei hapa:
• <a href="https://coingecko.com">CoinGecko</a>
• <a href="https://coinmarketcap.com">CoinMarketCap</a>"""
            
    except Exception as e:
        logger.error(f"Error fetching Bitcoin price: {e}")
        return """💰 <b>Bei ya Bitcoin</b>

❌ Huduma haipatikani kwa sasa. Tafadhali jaribu tena baadaye.

📊 Angalia bei hapa:
• <a href="https://coingecko.com">CoinGecko</a>
• <a href="https://coinmarketcap.com">CoinMarketCap</a>"""

def detect_language(text):
    """Detect if text is in Swahili."""
    swahili_keywords = [
        'bitcoin', 'pesa', 'fedha', 'nini', 'jinsi', 'vipi', 'wapi', 'lini', 'kwa nini',
        'ni', 'na', 'ya', 'wa', 'za', 'kwa', 'katika', 'hapa', 'huko', 'hivyo',
        'kama', 'lakini', 'au', 'pia', 'bado', 'tena', 'sana', 'pia', 'hata',
        'habari', 'hujambo', 'karibu', 'asante', 'pole', 'samahani'
    ]
    text_lower = text.lower()
    swahili_count = sum(1 for keyword in swahili_keywords if keyword in text_lower)
    return swahili_count >= 2

def get_main_menu_keyboard(lang="en", collapsed=False):
    """Get main menu keyboard based on language with collapsible option."""
    if lang == "sw":
        if collapsed:
            # Collapsed menu - only essential options
            keyboard = [
                [
                    InlineKeyboardButton("💰 Bei ya Bitcoin", callback_data="price"),
                    InlineKeyboardButton("📚 Bitcoin ni nini?", callback_data="bitcoin_ni_nini")
                ],
                [
                    InlineKeyboardButton("📱 Nunua kwa M-Pesa", callback_data="mpesa_guide"),
                    InlineKeyboardButton("📝 Jaribio", callback_data="quiz")
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
                    InlineKeyboardButton("💰 Bei ya Bitcoin", callback_data="price"),
                    InlineKeyboardButton("📚 Bitcoin ni nini?", callback_data="bitcoin_ni_nini")
                ],
                [
                    InlineKeyboardButton("🔗 P2P Inafanyaje", callback_data="p2p_inafanyaje"),
                    InlineKeyboardButton("👛 Aina za Pochi", callback_data="kufungua_pochi")
                ],
                [
                    InlineKeyboardButton("🔒 Usalama wa Pochi", callback_data="usalama_pochi"),
                    InlineKeyboardButton("📱 Nunua kwa M-Pesa", callback_data="mpesa_guide")
                ],
                [
                    InlineKeyboardButton("⚖️ Faida na Hatari", callback_data="faida_na_hatari"),
                    InlineKeyboardButton("❓ Maswali Mengine", callback_data="maswali_mengine")
                ],
                [
                    InlineKeyboardButton("🔐 Teknolojia ya Blockchain", callback_data="blockchain_usalama"),
                    InlineKeyboardButton("📝 Jaribio la Bitcoin", callback_data="quiz")
                ],
                [
                    InlineKeyboardButton("💡 Kidokezo cha Leo", callback_data="daily_tip"),
                    InlineKeyboardButton("ℹ️ Kuhusu BitMshauri", callback_data="kuhusu_bitmshauri")
                ],
                [
                    InlineKeyboardButton("🔍 Menyu Fupi", callback_data="collapse_menu"),
                    InlineKeyboardButton("🌍 Badilisha Lugha", callback_data="language")
                ]
            ]
    else:
        if collapsed:
            # Collapsed English menu
            keyboard = [
                [
                    InlineKeyboardButton("💰 Bitcoin Price", callback_data="price"),
                    InlineKeyboardButton("📚 What is Bitcoin?", callback_data="what_is_bitcoin")
                ],
                [
                    InlineKeyboardButton("📱 Buy with M-Pesa", callback_data="buying_guide"),
                    InlineKeyboardButton("📝 Quiz", callback_data="quiz")
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
                    InlineKeyboardButton("💰 Bitcoin Price", callback_data="price"),
                    InlineKeyboardButton("📚 What is Bitcoin?", callback_data="what_is_bitcoin")
                ],
                [
                    InlineKeyboardButton("🔗 How P2P Works", callback_data="how_p2p_works"),
                    InlineKeyboardButton("👛 Wallet Types", callback_data="wallet_types")
                ],
                [
                    InlineKeyboardButton("🔒 Wallet Security", callback_data="wallet_security"),
                    InlineKeyboardButton("📱 Buy with M-Pesa", callback_data="buying_guide")
                ],
                [
                    InlineKeyboardButton("⚖️ Pros and Cons", callback_data="pros_and_cons"),
                    InlineKeyboardButton("❓ FAQ", callback_data="frequently_asked")
                ],
                [
                    InlineKeyboardButton("🔐 Blockchain Technology", callback_data="blockchain_technology"),
                    InlineKeyboardButton("📝 Bitcoin Quiz", callback_data="quiz")
                ],
                [
                    InlineKeyboardButton("💡 Daily Tip", callback_data="daily_tip"),
                    InlineKeyboardButton("ℹ️ About BitMshauri", callback_data="about_bitmshauri")
                ],
                [
                    InlineKeyboardButton("🔍 Compact Menu", callback_data="collapse_menu"),
                    InlineKeyboardButton("🌍 Change Language", callback_data="language")
                ]
            ]
    
    return InlineKeyboardMarkup(keyboard)

def get_quiz_keyboard(lang="sw"):
    """Get quiz keyboard."""
    if lang == "sw":
        keyboard = [
            [
                InlineKeyboardButton("📝 Jaribio la Msingi", callback_data="quiz_msingi"),
                InlineKeyboardButton("🔒 Jaribio la Usalama", callback_data="quiz_usalama")
            ],
            [
                InlineKeyboardButton("⬅️ Rudi Menu", callback_data="back_to_menu")
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("📝 Basic Quiz", callback_data="quiz_basic"),
                InlineKeyboardButton("🔒 Security Quiz", callback_data="quiz_security")
            ],
            [
                InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")
            ]
        ]
    
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with comprehensive content and audio."""
    user = update.effective_user
    user_id = user.id
    
    # Detect language and store preference
    is_swahili = detect_language(update.message.text if update.message else "")
    lang = "sw" if is_swahili else "en"
    user_languages[user_id] = lang
    
    # Get Bitcoin price
    price_info = get_bitcoin_price()
    
    if lang == "sw":
        welcome_text = f"""🎉 <b>Karibu BitMshauri Bot!</b>

Hujambo {user.first_name}! Mimi ni msaidizi wako wa elimu ya Bitcoin! 🇰🇪

{price_info}

📚 <b>Chagua moja ya chaguzi hapa chini:</b>

🎵 <i>Unaweza pia kupata sauti ya maudhui kwa kubonyeza 🎵</i>"""
    else:
        welcome_text = f"""🎉 <b>Welcome to BitMshauri Bot!</b>

Hello {user.first_name}! I'm your Bitcoin education assistant! 🇺🇸

{price_info}

📚 <b>Choose one of the options below:</b>

🎵 <i>You can also get audio versions by clicking 🎵</i>"""
    
    reply_markup = get_main_menu_keyboard(lang, collapsed=True)  # Start with collapsed menu
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    is_swahili = detect_language(update.message.text if update.message else "")
    lang = "sw" if is_swahili else "en"
    
    price_info = get_bitcoin_price()
    
    if lang == "sw":
        help_text = f"""📚 <b>BitMshauri Bot - Msaada</b>

{price_info}

<b>Amri Zinazopatikana:</b>
/start - Anza boti na bei ya Bitcoin
/help - Onyesha msaada huu
/price - Pata bei ya Bitcoin (USD & KES)

<b>Mifano ya Maswali:</b>
• "Bitcoin ni nini?"
• "Jinsi ya kununua Bitcoin?"
• "Vidokezo vya usalama"
• "Bitcoin Kenya"

🌍 <b>Lugha:</b> Ninaongea Kiswahili na Kiingereza!"""
    else:
        help_text = f"""📚 <b>BitMshauri Bot - Help</b>

{price_info}

<b>Available Commands:</b>
/start - Start bot with Bitcoin price
/help - Show this help
/price - Get Bitcoin price (USD & KES)

<b>Example Questions:</b>
• "What is Bitcoin?"
• "How to buy Bitcoin?"
• "Security tips"
• "Bitcoin in Kenya"

🌍 <b>Languages:</b> I speak Swahili and English!"""
    
    reply_markup = get_main_menu_keyboard(lang)
    
    await update.message.reply_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command."""
    price_info = get_bitcoin_price()
    is_swahili = detect_language(update.message.text if update.message else "")
    lang = "sw" if is_swahili else "en"
    
    reply_markup = get_main_menu_keyboard(lang)
    
    await update.message.reply_text(
        price_info,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks with comprehensive content, collapsible menus, and audio."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = query.from_user.id
    
    # Get user's language preference
    lang = user_languages.get(user_id, "en")
    
    # Handle menu collapse/expand
    if callback_data == "collapse_menu":
        if lang == "sw":
            response_text = "🔍 <b>Menyu Imefupishwa</b>\n\nChagua moja ya chaguzi hapa chini:"
        else:
            response_text = "🔍 <b>Menu Collapsed</b>\n\nChoose one of the options below:"
        reply_markup = get_main_menu_keyboard(lang, collapsed=True)
        await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='HTML')
        return
        
    elif callback_data == "expand_menu":
        if lang == "sw":
            response_text = "🔍 <b>Menyu Kamili</b>\n\nChagua moja ya chaguzi hapa chini:"
        else:
            response_text = "🔍 <b>Full Menu</b>\n\nChoose one of the options below:"
        reply_markup = get_main_menu_keyboard(lang, collapsed=False)
        await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='HTML')
        return
    
    # Handle different callback types
    if callback_data == "price":
        response_text = get_bitcoin_price()
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
        
    elif callback_data == "quiz":
        if lang == "sw":
            response_text = """📝 <b>Jaribio la Bitcoin</b>

Chagua aina ya jaribio unalotaka kufanya:

📝 <b>Jaribio la Msingi</b> - Maswali ya kimsingi kuhusu Bitcoin
🔒 <b>Jaribio la Usalama</b> - Maswali kuhusu usalama wa Bitcoin

Jaribio hili litakusaidia kujifunza zaidi kuhusu Bitcoin!"""
        else:
            response_text = """📝 <b>Bitcoin Quiz</b>

Choose the type of quiz you want to take:

📝 <b>Basic Quiz</b> - Basic questions about Bitcoin
🔒 <b>Security Quiz</b> - Questions about Bitcoin security

This quiz will help you learn more about Bitcoin!"""
        
        reply_markup = get_quiz_keyboard(lang)
        
    elif callback_data.startswith("quiz_"):
        # Handle quiz questions
        quiz_type = callback_data.split("_")[1]
        if quiz_type in QUIZZES and QUIZZES[quiz_type]:
            quiz = QUIZZES[quiz_type][0]  # Get first question
            
            if lang == "sw":
                response_text = f"""📝 <b>Swali la {quiz_type.title()}</b>

{quiz['question']}

Chagua jibu sahihi:"""
                
                # Create options keyboard
                options_keyboard = []
                for i, option in enumerate(quiz['options']):
                    options_keyboard.append([InlineKeyboardButton(
                        f"{chr(65+i)}. {option}", 
                        callback_data=f"answer_{quiz_type}_{i}"
                    )])
                
                options_keyboard.append([InlineKeyboardButton("⬅️ Rudi", callback_data="quiz")])
                reply_markup = InlineKeyboardMarkup(options_keyboard)
            else:
                response_text = f"""📝 <b>{quiz_type.title()} Question</b>

{quiz['question']}

Choose the correct answer:"""
                
                # Create options keyboard
                options_keyboard = []
                for i, option in enumerate(quiz['options']):
                    options_keyboard.append([InlineKeyboardButton(
                        f"{chr(65+i)}. {option}", 
                        callback_data=f"answer_{quiz_type}_{i}"
                    )])
                
                options_keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="quiz")])
                reply_markup = InlineKeyboardMarkup(options_keyboard)
        else:
            response_text = "❓ No quiz available."
            reply_markup = get_main_menu_keyboard(lang)
            
    elif callback_data.startswith("answer_"):
        # Handle quiz answers
        parts = callback_data.split("_")
        quiz_type = parts[1]
        answer_index = int(parts[2])
        
        if quiz_type in QUIZZES and QUIZZES[quiz_type]:
            quiz = QUIZZES[quiz_type][0]
            correct_answer = quiz['answer']
            
            if answer_index == correct_answer:
                if lang == "sw":
                    response_text = f"""✅ <b>Jibu Sahihi!</b>

{quiz['explanation']}

Hongera! Umejibu swali hili kwa usahihi."""
                else:
                    response_text = f"""✅ <b>Correct Answer!</b>

{quiz['explanation']}

Congratulations! You answered this question correctly."""
            else:
                if lang == "sw":
                    response_text = f"""❌ <b>Jibu si sahihi.</b>

Jibu sahihi ni: {quiz['options'][correct_answer]}

{quiz['explanation']}

Usiwe na hofu, ujifunze zaidi na ujaribu tena!"""
                else:
                    response_text = f"""❌ <b>Incorrect Answer.</b>

The correct answer is: {quiz['options'][correct_answer]}

{quiz['explanation']}

Don't worry, keep learning and try again!"""
            
            reply_markup = get_quiz_keyboard(lang)
            
    elif callback_data == "daily_tip":
        tip = random.choice(DAILY_TIPS)
        if lang == "sw":
            response_text = f"""💡 <b>Kidokezo cha Leo</b>

{tip}

<b>Kidokezo cha kesho:</b> Jaribu kujifunza kitu kipya kuhusu Bitcoin kila siku!"""
        else:
            response_text = f"""💡 <b>Daily Tip</b>

{tip}

<b>Tomorrow's tip:</b> Try to learn something new about Bitcoin every day!"""
        
        reply_markup = get_main_menu_keyboard(lang)
        
    elif callback_data.startswith("audio_"):
        # Handle audio generation
        lesson_key = callback_data.replace("audio_", "")
        
        if lesson_key in SWAHILI_LESSONS:
            lesson_content = SWAHILI_LESSONS[lesson_key]["content"]
            audio_lang = "sw"
        elif lesson_key in ENGLISH_LESSONS:
            lesson_content = ENGLISH_LESSONS[lesson_key]["content"]
            audio_lang = "en"
        else:
            response_text = "❌ Audio not available for this content."
            reply_markup = get_main_menu_keyboard(lang, collapsed=True)
            await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='HTML')
            return
        
        # Generate audio
        audio_file = generate_audio(lesson_content, audio_lang)
        
        if audio_file and os.path.exists(audio_file):
            try:
                with open(audio_file, 'rb') as audio:
                    await query.message.reply_voice(
                        voice=InputFile(audio),
                        caption="🎵 Audio version of the content"
                    )
                os.unlink(audio_file)  # Clean up temp file
            except Exception as e:
                logger.error(f"Error sending audio: {e}")
                response_text = "❌ Error generating audio. Please try again."
                reply_markup = get_main_menu_keyboard(lang, collapsed=True)
                await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            response_text = "❌ Audio generation failed. Please try again."
            reply_markup = get_main_menu_keyboard(lang, collapsed=True)
            await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='HTML')
        return
        
    elif callback_data == "back_to_menu":
        if lang == "sw":
            response_text = """🏠 <b>Rudi Menu Kuu</b>

Chagua moja ya chaguzi hapa chini:"""
        else:
            response_text = """🏠 <b>Back to Main Menu</b>

Choose one of the options below:"""
        
        reply_markup = get_main_menu_keyboard(lang, collapsed=True)
        
    elif callback_data == "language":
        # Toggle language
        new_lang = "en" if lang == "sw" else "sw"
        user_languages[user_id] = new_lang
        
        if new_lang == "sw":
            response_text = """🌍 <b>Lugha Imebadilishwa - Kiswahili</b>

Karibu! Sasa nitajibu kwa Kiswahili.

🇰🇪 <b>Kiswahili:</b> Nina elimu kamili ya Bitcoin
🇺🇸 <b>English:</b> I also support English

💡 <b>Mifano ya maswali:</b>
• "Bitcoin ni nini?"
• "Jinsi ya kununua Bitcoin?"
• "Vidokezo vya usalama"

Nitajibu kwa Kiswahili! 🗣️"""
        else:
            response_text = """🌍 <b>Language Changed - English</b>

Welcome! I'll now respond in English.

🇺🇸 <b>English:</b> I have comprehensive Bitcoin education
🇰🇪 <b>Kiswahili:</b> Ninaunga mkono Kiswahili pia

💡 <b>Example questions:</b>
• "What is Bitcoin?"
• "How to buy Bitcoin?"
• "Security tips"

I'll respond in English! 🗣️"""
        
        reply_markup = get_main_menu_keyboard(new_lang, collapsed=True)
        
    elif callback_data == "help":
        if lang == "sw":
            response_text = """📚 <b>BitMshauri Bot - Msaada</b>

<b>Amri Zinazopatikana:</b>
/start - Anza boti na bei ya Bitcoin
/help - Onyesha msaada huu
/price - Pata bei ya Bitcoin (USD & KES)

<b>Mifano ya Maswali:</b>
• "Bitcoin ni nini?"
• "Jinsi ya kununua Bitcoin?"
• "Vidokezo vya usalama"
• "Bitcoin Kenya"

🌍 <b>Lugha:</b> Ninaongea Kiswahili na Kiingereza!"""
        else:
            response_text = """📚 <b>BitMshauri Bot - Help</b>

<b>Available Commands:</b>
/start - Start bot with Bitcoin price
/help - Show this help
/price - Get Bitcoin price (USD & KES)

<b>Example Questions:</b>
• "What is Bitcoin?"
• "How to buy Bitcoin?"
• "Security tips"
• "Bitcoin in Kenya"

🌍 <b>Languages:</b> I speak Swahili and English!"""
        
        reply_markup = get_main_menu_keyboard(lang)
        
    else:
        response_text = "❓ Chaguo lisilojulikana. Tafadhali jaribu tena."
        reply_markup = get_main_menu_keyboard(lang)
    
    # Edit the message with new content
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages."""
    message_text = update.message.text.lower()
    is_swahili = detect_language(message_text)
    lang = "sw" if is_swahili else "en"
    
    # Get Bitcoin price for most responses
    price_info = get_bitcoin_price()
    
    # Check for specific Swahili content
    if any(keyword in message_text for keyword in ['bitcoin ni nini', 'nini bitcoin']):
        response_text = f"{LESSONS['bitcoin_ni_nini']['content']}\n\n{price_info}"
        
    elif any(keyword in message_text for keyword in ['jinsi ya kununua', 'kununua bitcoin', 'nunua']):
        response_text = f"{LESSONS['mpesa_guide']['content']}\n\n{price_info}"
        
    elif any(keyword in message_text for keyword in ['usalama', 'security', 'hifadhi']):
        response_text = f"{LESSONS['usalama_pochi']['content']}\n\n{price_info}"
        
    elif any(keyword in message_text for keyword in ['p2p', 'peer to peer']):
        response_text = f"{LESSONS['p2p_inafanyaje']['content']}\n\n{price_info}"
        
    elif any(keyword in message_text for keyword in ['pochi', 'wallet']):
        response_text = f"{LESSONS['kufungua_pochi']['content']}\n\n{price_info}"
        
    else:
        # General response
        if lang == "sw":
            response_text = f"""👋 <b>Hujambo!</b> Umesema: "{update.message.text}"

Mimi ni BitMshauri Bot, msaidizi wako wa elimu ya Bitcoin! 🪙

{price_info}

💡 <b>Jaribu chaguzi hizi:</b>
• "Bitcoin ni nini?"
• "Jinsi ya kununua Bitcoin?"
• "Vidokezo vya usalama"
• "P2P inafanyaje"

Niulize chochote kuhusu Bitcoin! 🇰🇪"""
        else:
            response_text = f"""👋 <b>Hello!</b> You said: "{update.message.text}"

I'm BitMshauri Bot, your Bitcoin education assistant! 🪙

{price_info}

💡 <b>Try these options:</b>
• "What is Bitcoin?"
• "How to buy Bitcoin?"
• "Security tips"
• "How does P2P work?"

Ask me anything about Bitcoin! 🇺🇸"""
    
    reply_markup = get_main_menu_keyboard(lang)
    
    await update.message.reply_text(
        response_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors with better conflict resolution."""
    error = context.error
    
    if isinstance(error, Conflict):
        logger.warning("🔄 Conflict detected - another bot instance may be running")
        logger.info("💡 Attempting to resolve conflict...")
        
        # Wait and retry
        await asyncio.sleep(5)
        return
        
    elif isinstance(error, (NetworkError, TimedOut)):
        logger.warning(f"🌐 Network error: {error}")
        logger.info("💡 Retrying connection...")
        await asyncio.sleep(3)
        return
        
    else:
        logger.error(f"❌ Unexpected error: {error}")

def clear_webhook():
    """Clear any existing webhook to prevent conflicts."""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        if response.status_code == 200:
            logger.info("✅ Webhook cleared successfully")
        else:
            logger.warning(f"⚠️ Failed to clear webhook: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error clearing webhook: {e}")

def main():
    """Start the enhanced bot with comprehensive Swahili content."""
    logger.info("🤖 Starting Enhanced BitMshauri Bot with comprehensive Swahili content...")
    
    # Clear any existing webhook first
    clear_webhook()
    
    # Create application with better error handling
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("price", price_command))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for regular text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot with enhanced conflict resolution
    logger.info("🚀 Starting enhanced bot with comprehensive Swahili content...")
    
    try:
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            read_timeout=30,
            write_timeout=30,
            connect_timeout=30,
            pool_timeout=30
        )
    except Conflict as e:
        logger.error(f"❌ Persistent conflict: {e}")
        logger.info("💡 Please ensure only one bot instance is running")
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    main()
