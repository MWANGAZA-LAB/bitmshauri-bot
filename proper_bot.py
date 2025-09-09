#!/usr/bin/env python3
"""Proper BitMshauri Bot using python-telegram-bot library with handlers and callbacks."""

import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno"

# Educational content
BITCOIN_EDUCATION = {
    "what_is_bitcoin": {
        "en": """🪙 <b>What is Bitcoin?</b>

Bitcoin is a digital currency that operates without a central bank or single administrator. It was created in 2009 by an anonymous person or group using the name Satoshi Nakamoto.

<b>Key Features:</b>
• Decentralized - No single authority controls it
• Digital - Exists only in digital form
• Limited Supply - Only 21 million will ever exist
• Secure - Protected by cryptography
• Global - Can be sent anywhere in the world

<b>How it works:</b>
Bitcoin uses blockchain technology - a public ledger that records all transactions. This makes it transparent and secure.""",
        
        "sw": """🪙 <b>Bitcoin ni nini?</b>

Bitcoin ni pesa za kidijitali zinazofanya kazi bila benki kuu au msimamizi mmoja. Ilitengenezwa mwaka 2009 na mtu asiyejulikana au kikundi kinachotumia jina Satoshi Nakamoto.

<b>Sifa Muhimu:</b>
• Haijasimamiwa na mamlaka moja
• Ni kidijitali - ipo tu kwa umbo la kidijitali
• Idadi ndogo - Milioni 21 tu zitakuwepo milele
• Salama - Inalindwa na mfumo wa siri
• Kimataifa - Inaweza kutumwa popote ulimwenguni

<b>Inafanyaje kazi:</b>
Bitcoin hutumia teknolojia ya blockchain - daftari la umma linalorekodi shughuli zote. Hii inafanya iwe wazi na salama."""
    },
    
    "how_to_buy": {
        "en": """💳 <b>How to Buy Bitcoin in Kenya</b>

<b>Popular Platforms:</b>
• <b>BitPesa</b> - Local Kenyan platform
• <b>LocalBitcoins</b> - Peer-to-peer trading
• <b>Binance</b> - Global exchange
• <b>Paxful</b> - Multiple payment methods

<b>Steps to Buy:</b>
1. Choose a platform
2. Create an account
3. Verify your identity
4. Add payment method (M-Pesa, bank transfer)
5. Place your order
6. Store Bitcoin securely

<b>Payment Methods:</b>
• M-Pesa
• Bank Transfer
• Credit/Debit Card
• Mobile Money

⚠️ <b>Always do your research before investing!</b>""",
        
        "sw": """💳 <b>Jinsi ya Kununua Bitcoin Kenya</b>

<b>Mifumo Maarufu:</b>
• <b>BitPesa</b> - Mfumo wa Kenya
• <b>LocalBitcoins</b> - Biashara ya moja kwa moja
• <b>Binance</b> - Ubadilishaji wa kimataifa
• <b>Paxful</b> - Njia nyingi za malipo

<b>Hatua za Kununua:</b>
1. Chagua mfumo
2. Unda akaunti
3. Thibitisha utambulisho wako
4. Ongeza njia ya malipo (M-Pesa, uhamisho wa benki)
5. Weka agizo lako
6. Hifadhi Bitcoin kwa usalama

<b>Njia za Malipo:</b>
• M-Pesa
• Uhamisho wa Benki
• Kadi ya Mkopo/Debiti
• Pesa za Simu

⚠️ <b>Daima fanya utafiti kabla ya kuwekeza!</b>"""
    },
    
    "security_tips": {
        "en": """🔒 <b>Bitcoin Security Tips</b>

<b>Wallet Security:</b>
• Use hardware wallets for large amounts
• Enable two-factor authentication
• Keep private keys offline
• Use strong passwords
• Backup your wallet

<b>Transaction Security:</b>
• Double-check addresses before sending
• Start with small amounts
• Use reputable exchanges
• Don't share private keys
• Be wary of phishing scams

<b>Storage Options:</b>
• <b>Hot Wallets</b> - Online, convenient but less secure
• <b>Cold Wallets</b> - Offline, more secure
• <b>Hardware Wallets</b> - Most secure option

<b>Red Flags:</b>
• Promises of guaranteed returns
• Requests for private keys
• Unverified platforms
• Pressure to invest quickly

💡 <b>Remember: If it sounds too good to be true, it probably is!</b>""",
        
        "sw": """🔒 <b>Vidokezo vya Usalama wa Bitcoin</b>

<b>Usalama wa Pochi:</b>
• Tumia pochi za vifaa kwa kiasi kikubwa
• Wezesha uthibitishaji wa hatua mbili
• Weka funguo za siri nje ya mtandao
• Tumia nenosiri kali
• Rudisha pochi yako

<b>Usalama wa Shughuli:</b>
• Hakiki anwani kabla ya kutuma
• Anza na kiasi kidogo
• Tumia mifumo ya kujulikana
• Usishiriki funguo za siri
• Kuwa mwangalifu na ulaghai

<b>Chaguzi za Kuhifadhi:</b>
• <b>Pochi za Moto</b> - Mtandaoni, rahisi lakini si salama sana
• <b>Pochi za Baridi</b> - Nje ya mtandao, salama zaidi
• <b>Pochi za Vifaa</b> - Chaguo salama zaidi

<b>Alama za Hatari:</b>
• Ahadi za faida za uhakika
• Maombi ya funguo za siri
• Mifumo isiyothibitishwa
• Shinikizo la kuwekeza haraka

💡 <b>Kumbuka: Ikiwa inaonekana nzuri sana kuwa ni kweli, labda si kweli!</b>"""
    }
}

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
            
            return f"""💰 <b>Bitcoin Price</b>

🇺🇸 <b>USD:</b> ${usd_formatted}
🇰🇪 <b>KES:</b> KSh {kes_formatted}

📊 <i>Live prices from CoinGecko</i>"""
            
        else:
            return """💰 <b>Bitcoin Price</b>

❌ Unable to fetch current prices. Please try again later.

📊 Check prices at:
• <a href="https://coingecko.com">CoinGecko</a>
• <a href="https://coinmarketcap.com">CoinMarketCap</a>"""
            
    except Exception as e:
        logger.error(f"Error fetching Bitcoin price: {e}")
        return """💰 <b>Bitcoin Price</b>

❌ Service temporarily unavailable. Please try again later.

📊 Check prices at:
• <a href="https://coingecko.com">CoinGecko</a>
• <a href="https://coinmarketcap.com">CoinMarketCap</a>"""

def detect_language(text):
    """Detect if text is in Swahili."""
    swahili_keywords = [
        'bitcoin', 'pesa', 'fedha', 'nini', 'jinsi', 'vipi', 'wapi', 'lini', 'kwa nini',
        'ni', 'na', 'ya', 'wa', 'za', 'kwa', 'katika', 'hapa', 'huko', 'hivyo',
        'kama', 'lakini', 'au', 'pia', 'bado', 'tena', 'sana', 'pia', 'hata'
    ]
    text_lower = text.lower()
    swahili_count = sum(1 for keyword in swahili_keywords if keyword in text_lower)
    return swahili_count >= 2

def get_main_menu_keyboard(lang="en"):
    """Get main menu keyboard."""
    if lang == "sw":
        keyboard = [
            [
                InlineKeyboardButton("💰 Bei ya Bitcoin", callback_data="price"),
                InlineKeyboardButton("📚 Jifunze Bitcoin", callback_data="learn")
            ],
            [
                InlineKeyboardButton("💳 Nunua Bitcoin", callback_data="buy"),
                InlineKeyboardButton("🔒 Usalama", callback_data="security")
            ],
            [
                InlineKeyboardButton("🌍 Badilisha Lugha", callback_data="language"),
                InlineKeyboardButton("❓ Msaada", callback_data="help")
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("💰 Bitcoin Price", callback_data="price"),
                InlineKeyboardButton("📚 Learn Bitcoin", callback_data="learn")
            ],
            [
                InlineKeyboardButton("💳 Buy Bitcoin", callback_data="buy"),
                InlineKeyboardButton("🔒 Security", callback_data="security")
            ],
            [
                InlineKeyboardButton("🌍 Change Language", callback_data="language"),
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
    
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    is_swahili = detect_language(update.message.text if update.message else "")
    lang = "sw" if is_swahili else "en"
    
    # Get Bitcoin price
    price_info = get_bitcoin_price()
    
    if lang == "sw":
        welcome_text = f"""🎉 <b>Karibu BitMshauri Bot!</b>

Hujambo {user.first_name}! Mimi ni msaidizi wako wa elimu ya Bitcoin! 🇰🇪

{price_info}

📚 <b>Chagua moja ya chaguzi hapa chini:</b>"""
    else:
        welcome_text = f"""🎉 <b>Welcome to BitMshauri Bot!</b>

Hello {user.first_name}! I'm your Bitcoin education assistant! 🇺🇸

{price_info}

📚 <b>Choose one of the options below:</b>"""
    
    reply_markup = get_main_menu_keyboard(lang)
    
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
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()  # Important: answer the callback query
    
    callback_data = query.data
    is_swahili = detect_language(query.message.text if query.message else "")
    lang = "sw" if is_swahili else "en"
    
    if callback_data == "price":
        response_text = get_bitcoin_price()
        
    elif callback_data == "learn":
        response_text = BITCOIN_EDUCATION["what_is_bitcoin"][lang]
        
    elif callback_data == "buy":
        response_text = BITCOIN_EDUCATION["how_to_buy"][lang]
        
    elif callback_data == "security":
        response_text = BITCOIN_EDUCATION["security_tips"][lang]
        
    elif callback_data == "language":
        if lang == "sw":
            response_text = """🌍 <b>Language Settings / Mipangilio ya Lugha</b>

I support both Swahili and English! / Ninaunga mkono Kiswahili na Kiingereza!

🇺🇸 <b>English:</b> Send me messages in English
🇰🇪 <b>Kiswahili:</b> Tuma ujumbe wa Kiswahili

💡 <b>Examples / Mifano:</b>
• "What is Bitcoin?" (English)
• "Bitcoin ni nini?" (Kiswahili)

I'll respond in the same language you use! 🗣️"""
        else:
            response_text = """🌍 <b>Language Settings / Mipangilio ya Lugha</b>

I support both Swahili and English! / Ninaunga mkono Kiswahili na Kiingereza!

🇺🇸 <b>English:</b> Send me messages in English
🇰🇪 <b>Kiswahili:</b> Tuma ujumbe wa Kiswahili

💡 <b>Examples / Mifano:</b>
• "What is Bitcoin?" (English)
• "Bitcoin ni nini?" (Kiswahili)

I'll respond in the same language you use! 🗣️"""
        
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
    
    else:
        response_text = "❓ Unknown option. Please try again."
    
    # Edit the message with new content
    await query.edit_message_text(
        text=response_text,
        reply_markup=get_main_menu_keyboard(lang),
        parse_mode='HTML'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages."""
    message_text = update.message.text.lower()
    is_swahili = detect_language(message_text)
    lang = "sw" if is_swahili else "en"
    
    # Get Bitcoin price for most responses
    price_info = get_bitcoin_price()
    
    if 'what is bitcoin' in message_text or 'bitcoin ni nini' in message_text:
        response_text = f"{BITCOIN_EDUCATION['what_is_bitcoin'][lang]}\n\n{price_info}"
        
    elif 'how to buy' in message_text or 'jinsi ya kununua' in message_text:
        response_text = f"{BITCOIN_EDUCATION['how_to_buy'][lang]}\n\n{price_info}"
        
    elif 'security' in message_text or 'usalama' in message_text:
        response_text = f"{BITCOIN_EDUCATION['security_tips'][lang]}\n\n{price_info}"
        
    else:
        # General response
        if lang == "sw":
            response_text = f"""👋 <b>Hujambo!</b> Umesema: "{update.message.text}"

Mimi ni BitMshauri Bot, msaidizi wako wa elimu ya Bitcoin! 🪙

{price_info}

💡 <b>Jaribu amri hizi:</b>
/learn - Jifunze kuhusu Bitcoin
/buy - Jinsi ya kununua Bitcoin
/security - Vidokezo vya usalama
/help - Ona amri zote

Niulize chochote kuhusu Bitcoin! 🇰🇪"""
        else:
            response_text = f"""👋 <b>Hello!</b> You said: "{update.message.text}"

I'm BitMshauri Bot, your Bitcoin education assistant! 🪙

{price_info}

💡 <b>Try these commands:</b>
/learn - Learn about Bitcoin
/buy - How to buy Bitcoin
/security - Security tips
/help - See all commands

Ask me anything about Bitcoin! 🇺🇸"""
    
    reply_markup = get_main_menu_keyboard(lang)
    
    await update.message.reply_text(
        response_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Handle specific errors
    if "Conflict" in str(context.error):
        logger.error("❌ Bot conflict detected. Another instance may be running.")
        logger.info("💡 Solution: Stop all other bot instances and try again.")
    elif "Forbidden" in str(context.error):
        logger.error("❌ Bot is blocked by user or doesn't have permission.")
    elif "BadRequest" in str(context.error):
        logger.error("❌ Bad request - check bot configuration.")

def main():
    """Start the bot."""
    # Create application with error handling
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
    
    # Start the bot with conflict resolution
    logger.info("🤖 Starting BitMshauri Bot with proper handlers...")
    logger.info("🔄 If you see conflicts, make sure only one instance is running.")
    
    try:
        application.run_polling(
            drop_pending_updates=True,  # Clear any pending updates
            allowed_updates=["message", "callback_query"]  # Only handle these update types
        )
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        if "Conflict" in str(e):
            logger.info("💡 Solution: Stop all other bot instances and try again.")

if __name__ == "__main__":
    main()
