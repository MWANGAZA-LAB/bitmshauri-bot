from dotenv import load_dotenv
load_dotenv()
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, CallbackContext, CallbackQueryHandler
)
from app.bot.price_api import get_bitcoin_price
from app.bot.content_swahili import LESSONS, MENU_KEYBOARD, QUIZZES, DAILY_TIPS, SECONDARY_MENU_KEYBOARD
from app.database import update_user, get_all_users, update_last_tip, save_feedback
from app.bot.audio_tts import tts_engine
import random
import requests
from datetime import datetime, timedelta
from app.database import get_user_by_id
import io

# Add missing OPENAI_API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- State & Keyboard Management ---
user_quiz_state = {}

def create_menu():
    return ReplyKeyboardMarkup(MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False)

def create_secondary_menu():
    return ReplyKeyboardMarkup(SECONDARY_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update_user(user, update.effective_chat.id)
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png"
    welcome_msg = (
        f"Habari {user.first_name}! 👋\n\n"
        f"{LESSONS['intro']['content']}"
    )
    await update.message.reply_photo(
        photo=logo_url,
        caption=welcome_msg,
        reply_markup=create_menu()
    )

async def price_command(update: Update, context: CallbackContext):
    price = get_bitcoin_price()
    await update.message.reply_text(price, parse_mode="Markdown")
    
async def show_more_help(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Chagua mada unayotaka kujifunza zaidi:",
        reply_markup=create_secondary_menu()
    )

async def back_to_main_menu(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Unakaribishwa tena kwenye menyu kuu.",
        reply_markup=create_menu()
    )
    
async def health(update: Update, context: CallbackContext):
    await update.message.reply_text("✅ Bot is running!")

# --- Audio Functions ---
async def send_lesson_with_audio(update: Update, context: CallbackContext, lesson_key: str):
    """Send lesson text with audio option"""
    lesson_content = safe_get_lesson(lesson_key)
    
    # Create inline keyboard with audio option
    keyboard = [
        [InlineKeyboardButton("🔊 Sikiliza Audio", callback_data=f"audio_{lesson_key}")],
        [InlineKeyboardButton("📖 Soma tu", callback_data="text_only")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📚 *Somo: {lesson_key.replace('_', ' ').title()}*\n\n"
        f"{lesson_content}\n\n"
        f"💡 *Chagua jinsi unavyotaka kupokea maudhui:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_audio_callback(update: Update, context: CallbackContext):
    """Handle audio generation callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("audio_"):
        lesson_key = query.data.replace("audio_", "")
        await generate_and_send_audio(query, context, lesson_key)
    elif query.data == "text_only":
        await query.edit_message_text("✅ Umechagua kusoma tu. Endelea na mafunzo!")
    elif query.data == "back_to_menu":
        await query.edit_message_text("⬅️ Umerudi kwenye menyu kuu.")

async def generate_and_send_audio(query, context: CallbackContext, lesson_key: str):
    """Generate and send audio for lesson"""
    try:
        # Show loading message
        await query.edit_message_text("🎵 Inaandaa sauti... Subiri kidogo...")
        
        # Get lesson content
        lesson_content = safe_get_lesson(lesson_key)
        
        # Generate audio
        audio_buffer = await tts_engine.text_to_speech(lesson_content)
        
        # Send audio file
        await context.bot.send_voice(
            chat_id=query.message.chat.id,
            voice=audio_buffer,
            caption=f"🎵 Audio ya somo: *{lesson_key.replace('_', ' ').title()}*",
            parse_mode="Markdown"
        )
        
        # Update message
        await query.edit_message_text(
            "✅ Audio imetumwa! 🎵\n\n"
            "💡 Sikiliza audio ukifuata maandishi juu."
        )
        
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        await query.edit_message_text(
            "❌ Samahani, imeshindwa kutengeneza audio. "
            "Tafadhali jaribu tena au soma maandishi."
        )

async def show_audio_menu(update: Update, context: CallbackContext):
    """Show audio lessons menu"""
    keyboard = [
        [InlineKeyboardButton("🔊 Kwa Nini Bitcoin?", callback_data="audio_kwa_nini_bitcoin")],
        [InlineKeyboardButton("🔊 Bitcoin ni nini?", callback_data="audio_bitcoin_ni_nini")],
        [InlineKeyboardButton("🔊 P2P Inafanyaje", callback_data="audio_p2p_inafanyaje")],
        [InlineKeyboardButton("🔊 Aina za Pochi", callback_data="audio_kufungua_pochi")],
        [InlineKeyboardButton("🔊 Usalama wa Pochi", callback_data="audio_usalama_pochi")],
        [InlineKeyboardButton("🔊 Blockchain", callback_data="audio_blockchain_usalama")],
        [InlineKeyboardButton("⬅️ Rudi Mwanzo", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎵 *Masomo ya Sauti*\n\n"
        "Chagua somo unalotaka kusikiliza kwa sauti:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def create_audio_lesson_response(lesson_key):
    """Create lesson response with audio option"""
    async def lesson_with_audio(update: Update, context: CallbackContext):
        await send_lesson_with_audio(update, context, lesson_key)
    return lesson_with_audio

# --- Purchase Flow Handlers ---
async def purchase_bitcoin(update: Update, context: CallbackContext):
    message = (
        "💰 *Chagua njia ya kupata Bitcoin:*\n\n"
        "🛒 **KUNUNUA BITCOIN:**\n"
        "• *Bitika* - Nunua kwa M-Pesa\n"
        "• *Bitsacco* - P2P marketplace\n\n"
        "👛 **POCHI ZA BITCOIN:**\n"
        "• *Blink* - Pochi rahisi\n"
        "• *Fedi* - Pochi ya jamii\n"
        "• *Phoenix* - Lightning wallet\n"
        "• *Wallet of Satoshi* - Custodial wallet\n\n"
        "💳 **KUTUMIA BITCOIN:**\n"
        "• *Tando* - Tumia Bitcoin kwa M-Pesa\n\n"
        "Chagua kategoria unayotaka:"
    )
    keyboard = [
        ["🛒 Nunua Bitcoin", "👛 Pochi za Bitcoin"], 
        ["💳 Tumia Bitcoin", "⬅️ Rudi Mwanzo"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)
    
async def show_purchase_platforms(update: Update, context: CallbackContext):
    keyboard = [["Bitika", "Bitsacco"], ["⬅️ Rudi Mwanzo"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🛒 *Majukwaa ya kununua Bitcoin:*\n\nChagua jukwaa unalopendelea:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_wallet_platforms(update: Update, context: CallbackContext):
    keyboard = [
        ["Blink", "Fedi"], 
        ["Phoenix", "Wallet of Satoshi"], 
        ["⬅️ Rudi Mwanzo"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👛 *Pochi za Bitcoin:*\n\nChagua pochi unayopendelea:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_spending_platforms(update: Update, context: CallbackContext):
    keyboard = [["Tando"], ["⬅️ Rudi Mwanzo"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "💳 *Njia za kutumia Bitcoin:*\n\nChagua huduma unayotaka:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
async def handle_purchase_platform(update: Update, context: CallbackContext, platform: str):
    platform_info = {
        # Purchase platforms
        "Bitika": {"url": "bitika.xyz", "desc": "Jukwaa la kununua na kuuza Bitcoin kwa M-Pesa", "type": "purchase"},
        "Bitsacco": {"url": "bitsacco.com", "desc": "Jukwaa la P2P la Bitcoin kwa wafanya biashara", "type": "purchase"},
        
        # Wallet platforms
        "Blink": {"url": "play.google.com/store/apps/details?id=com.galoyapp&pli=1", "desc": "Pochi ya Bitcoin ya haraka na rahisi", "type": "wallet"},
        "Fedi": {"url": "fedi.xyz", "desc": "Pochi ya jamii ya Bitcoin", "type": "wallet"},
        "Phoenix": {"url": "phoenix.acinq.co", "desc": "Pochi ya Lightning ya Bitcoin", "type": "wallet"},
        "Wallet of Satoshi": {"url": "walletofsatoshi.com", "desc": "Pochi rahisi ya Lightning", "type": "wallet"},
        
        # Spending platforms
        "Tando": {"url": "tando.africa", "desc": "Tumia Bitcoin kwa M-Pesa - kubadilisha Bitcoin kuwa pesa taslimu", "type": "spending"}
    }
    
    info = platform_info.get(platform, {"url": "unknown-platform.com", "desc": "Jukwaa la Bitcoin", "type": "unknown"})
    
    # Different instructions based on platform type
    if info["type"] == "purchase":
        instructions = (
            "📋 *Hatua za kununua Bitcoin:*\n"
            f"1. Nenda {info['url']}\n"
            f"2. Jisajili au ingia\n"
            f"3. Chagua 'Nunua Bitcoin'\n"
            f"4. Fuata maelekezo ya kulipa\n"
            f"5. Pokea Bitcoin kwenye pochi yako\n\n"
        )
    elif info["type"] == "wallet":
        instructions = (
            "📋 *Hatua za kupata pochi:*\n"
            f"1. Nenda {info['url']}\n"
            f"2. Pakua programu au fungua mtandaoni\n"
            f"3. Tengeneza akaunti mpya\n"
            f"4. Hifadhi seed phrase kwa usalama\n"
            f"5. Anza kutuma na kupokea Bitcoin\n\n"
        )
    elif info["type"] == "spending":
        instructions = (
            "📋 *Hatua za kutumia Bitcoin:*\n"
            f"1. Nenda {info['url']}\n"
            f"2. Jisajili na akaunti yako\n"
            f"3. Unganisha pochi yako ya Bitcoin\n"
            f"4. Badilisha Bitcoin kuwa M-Pesa\n"
            f"5. Tumia kama pesa za kawaida\n\n"
        )
    else:
        instructions = (
            "📋 *Hatua za haraka:*\n"
            f"1. Nenda {info['url']}\n"
            f"2. Jisajili au ingia\n"
            f"3. Fuata maelekezo\n\n"
        )
    
    message = (
        f"✅ *Umechagua {platform}*\n\n"
        f"📝 {info['desc']}\n\n"
        f"🔗 Tembelea: [{info['url']}](https://{info['url']})\n\n"
        f"{instructions}"
        f"Bonyeza hapa chini ukimaliza."
    )
    keyboard = [["✅ Nimemaliza Muamala"], ["⬅️ Rudi Mwanzo"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)

async def transaction_complete(update: Update, context: CallbackContext):
    user = update.effective_user
    message = (
        f"🎉 Hongera {user.first_name} kwa ununuzi wako! \n\n"
        "Asante kwa kutumia BitMshauri. Tunatumai umepata huduma bora."
    )
    await update.message.reply_text(message, reply_markup=create_menu())

# --- AI Handler ---
async def ai_answer_handler(update: Update, context: CallbackContext):
    if not OPENAI_API_KEY:
        await update.message.reply_text(
            "Samahani, huduma ya AI haijaanzishwa. Tafadhali wasiliana na msimamizi."
        )
        return
        
    user_question = update.message.text
    prompt = f"Jibu swali lifuatalo kuhusu Bitcoin kwa Kiswahili: {user_question}"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "Jibu maswali kuhusu Bitcoin kwa Kiswahili, kwa ufupi na urafiki."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 400
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=10)
        result = response.json()
        logger.info(f"OpenAI response: {result}")

        if "choices" in result and result["choices"]:
            answer = result["choices"][0]["message"]["content"].strip()
            
            # Create audio option for AI response
            keyboard = [
                [InlineKeyboardButton("🔊 Sikiliza Audio", callback_data=f"ai_audio_{hash(answer)}")],
                [InlineKeyboardButton("📖 Soma tu", callback_data="text_only")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🤖 *Jibu la AI:*\n\n{answer}\n\n💡 *Je, unataka kusikiliza kwa sauti?*",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
            # Store AI response for audio generation
            context.user_data["last_ai_response"] = answer
        else:
            error_msg = result.get("error", {}).get("message", "Hakuna jibu lililopatikana kutoka AI.")
            await update.message.reply_text(f"Samahani, AI haikuweza kujibu: {error_msg}")

    except Exception as e:
        logger.error(f"AI handler error: {e}")
        await update.message.reply_text("Samahani, kuna tatizo na huduma ya AI. Tafadhali jaribu tena baadaye.")

# --- Quiz Functions ---
async def start_quiz(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_quiz_state[user_id] = {'quiz_name': 'msingi', 'current_question': 0, 'score': 0}
    await ask_quiz_question(update, context, user_id)
    
async def ask_quiz_question(update: Update, context: CallbackContext, user_id: int):
    state = user_quiz_state.get(user_id)
    if not state:
        await update.message.reply_text("Samahani, jaribio limeisha. Tafadhali anza tena.", reply_markup=create_menu())
        return

    quiz = QUIZZES[state['quiz_name']]
    q_data = quiz[state['current_question']]
    q_text = f"❓ *Swali {state['current_question']+1}/{len(quiz)}:*\n{q_data['question']}\n\n"
    options = [f"{i+1}. {opt}" for i, opt in enumerate(q_data['options'])]
    q_text += "\n".join(options)

    keyboard = [[str(i+1) for i in range(len(q_data['options']))], ['❌ Acha Jaribio']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(q_text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_quiz_answer(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text
    state = user_quiz_state.get(user_id)
    
    if not state:
        await update.message.reply_text("Samahani, jaribio limeisha. Tafadhali anza tena.", reply_markup=create_menu())
        return

    if text == '❌ Acha Jaribio':
        del user_quiz_state[user_id]
        await update.message.reply_text("Umeacha jaribio. Unaweza kuanza tena wakati wowote!", reply_markup=create_menu())
        return

    quiz = QUIZZES[state['quiz_name']]
    q_data = quiz[state['current_question']]
    try:
        selected_index = int(text) - 1
        if not 0 <= selected_index < len(q_data['options']):
            raise ValueError()
    except (ValueError, IndexError):
        await update.message.reply_text("Tafadhali chagua namba moja kati ya chaguo zilizopendekezwa.")
        return

    if selected_index == q_data['answer']:
        state['score'] += 1
        response = f"✅ Sahihi! {q_data['explanation']}"
    else:
        correct_answer = q_data['options'][q_data['answer']]
        response = f"❌ Si sahihi. Jibu sahihi ni: {correct_answer}\n{q_data['explanation']}"
    await update.message.reply_text(response, parse_mode="Markdown")

    state['current_question'] += 1
    if state['current_question'] < len(quiz):
        await ask_quiz_question(update, context, user_id)
    else:
        score, total = state['score'], len(quiz)
        percentage = int(score / total * 100)
        emoji, message = ("🎉", "Hongera! Umefanya kazi nzuri sana!") if percentage >= 80 else \
                         ("👍", "Vizuri! Unaendelea vizuri!") if percentage >= 50 else \
                         ("💪", "Endelea kujifunza, utafanikiwa!")
        result = (
            f"{emoji} *Umeshinda Jaribio!*\n\n"
            f"Alama zako: {score}/{total} ({percentage}%)\n{message}"
        )
        await update.message.reply_text(result, reply_markup=create_menu(), parse_mode="Markdown")
        del user_quiz_state[user_id]

# --- Daily Tips ---
async def send_daily_tip(bot, user_id, chat_id):
    try:
        tip = random.choice(DAILY_TIPS)
        await bot.send_message(chat_id=chat_id, text=tip, parse_mode="Markdown")
        update_last_tip(user_id)
        logger.info(f"Sent tip to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send tip to user {user_id}: {e}")

async def scheduled_tip_job(context: CallbackContext):
    logger.info("Running scheduled daily tips job...")
    users = get_all_users()
    if not users:
        logger.info("No users found to send tips to.")
        return

    for user_id, chat_id, last_tip_str in users:
        await send_daily_tip(context.bot, user_id, chat_id)
    
    logger.info(f"Sent tips to {len(users)} users.")

async def ask_for_feedback(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Tafadhali andika maoni au ushauri wako hapa chini. Tunathamini mchango wako!"
    )
    context.user_data["awaiting_feedback"] = True

def safe_get_lesson(lesson_key):
    """Safely get lesson content with fallback"""
    return LESSONS.get(lesson_key, {}).get('content', f"Samahani, somo '{lesson_key}' halipatikani.")

# --- Enhanced Callback Handler ---
async def handle_audio_callback_enhanced(update: Update, context: CallbackContext):
    """Enhanced callback handler for all audio functions"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("audio_"):
        lesson_key = query.data.replace("audio_", "")
        await generate_and_send_audio(query, context, lesson_key)
    elif query.data.startswith("ai_audio_"):
        # Handle AI response audio
        ai_response = context.user_data.get("last_ai_response")
        if ai_response:
            try:
                await query.edit_message_text("🎵 Inaandaa sauti ya AI... Subiri kidogo...")
                audio_buffer = await tts_engine.text_to_speech(ai_response)
                await context.bot.send_voice(
                    chat_id=query.message.chat.id,
                    voice=audio_buffer,
                    caption="🤖🎵 Sauti ya jibu la AI",
                    parse_mode="Markdown"
                )
                await query.edit_message_text("✅ Sauti ya AI imetumwa! 🎵")
            except Exception as e:
                logger.error(f"AI audio generation failed: {e}")
                await query.edit_message_text("❌ Imeshindwa kutengeneza sauti ya AI.")
    elif query.data == "text_only":
        await query.edit_message_text("✅ Umechagua kusoma tu. Endelea na mafunzo!")
    elif query.data == "back_to_menu":
        await query.edit_message_text("⬅️ Umerudi kwenye menyu kuu.")

# --- Main Message Handler ---
async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text
    update_user(user, update.effective_chat.id)

    if user.id in user_quiz_state:
        await handle_quiz_answer(update, context)
        return

    if context.user_data.get("awaiting_feedback"):
        context.user_data["awaiting_feedback"] = False
        feedback = update.message.text
        user = update.effective_user
        save_feedback(user.id, user.username, feedback)
        await update.message.reply_text("Asante kwa maoni yako!")
        return

    # Enhanced responses with audio support
    responses = {
        # Audio-enabled lessons
        "🌍 Kwa Nini Bitcoin?": create_audio_lesson_response('kwa_nini_bitcoin'),
        "📚 Bitcoin ni nini?": create_audio_lesson_response('bitcoin_ni_nini'),
        "🔗 P2P Inafanyaje": create_audio_lesson_response('p2p_inafanyaje'),
        "👛 Aina za Pochi": create_audio_lesson_response('kufungua_pochi'),
        "🔒 Usalama wa Pochi": create_audio_lesson_response('usalama_pochi'),
        "⚠️ Kupoteza Ufunguo": create_audio_lesson_response('kupoteza_ufunguo'),
        "📱 Matumizi ya Pochi": create_audio_lesson_response('mfano_matumizi'),
        "⚖️ Faida na Hatari": create_audio_lesson_response('faida_na_hatari'),
        "🔐 Teknolojia ya Blockchain": create_audio_lesson_response('blockchain_usalama'),
        
        # New audio menu
        "🎵 Masomo ya Sauti": show_audio_menu,
        
        # Regular functions
        "💰 Bei ya Bitcoin": price_command,
        "📝 Jaribio la Bitcoin": start_quiz,
        "💡 Kidokezo cha Leo": lambda u, c: send_daily_tip(c.bot, u.effective_user.id, u.effective_chat.id),
        "ℹ️ Msaada Zaidi": show_more_help,
        "⬅️ Rudi Mwanzo": back_to_main_menu,
        
        # Category handlers
        "🛒 Nunua Bitcoin": show_purchase_platforms,
        "👛 Pochi za Bitcoin": show_wallet_platforms,
        "💳 Tumia Bitcoin": show_spending_platforms,
        
        # Purchase platforms
        "Bitika": lambda u, c: handle_purchase_platform(u, c, "Bitika"),
        "Bitsacco": lambda u, c: handle_purchase_platform(u, c, "Bitsacco"),
        
        # Wallet platforms
        "Blink": lambda u, c: handle_purchase_platform(u, c, "Blink"),
        "Fedi": lambda u, c: handle_purchase_platform(u, c, "Fedi"),
        "Phoenix": lambda u, c: handle_purchase_platform(u, c, "Phoenix"),
        "Wallet of Satoshi": lambda u, c: handle_purchase_platform(u, c, "Wallet of Satoshi"),
        
        # Spending platforms
        "Tando": lambda u, c: handle_purchase_platform(u, c, "Tando"),
        
        "✅ Nimemaliza Muamala": transaction_complete,
        "📝 Toa Maoni": lambda u, c: ask_for_feedback(u, c),
    }

    # Handle special AI questions
    if text == "❓ Maswali Mengine":
        if update.message:
            await update.message.reply_text(
                safe_get_lesson('maswali_mengine'),
                parse_mode="Markdown"
            )
        context.user_data["awaiting_ai_question"] = True
        return

    if context.user_data.get("awaiting_ai_question"):
        context.user_data["awaiting_ai_question"] = False
        await ai_answer_handler(update, context)
        return
    
    # Handle static responses or commands
    if text in responses:
        await responses[text](update, context)
    else:
        if update.message:
            await update.message.reply_text(
                "Samahani, sijakuelewa. Tafadhali chagua moja ya chaguo kwenye menyu."
            )

# --- Bot Initialization ---
def init_bot():
    try:
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        if not telegram_token:
            raise ValueError("TELEGRAM_TOKEN environment variable is not set")
            
        application = Application.builder().token(telegram_token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("health", health))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add callback query handler for audio buttons
        application.add_handler(CallbackQueryHandler(handle_audio_callback_enhanced))

        # Added timezone for better scheduling
        from datetime import timezone, timedelta
        east_africa_tz = timezone(timedelta(hours=3))
        
        application.job_queue.run_daily(
            scheduled_tip_job,
            time=datetime.strptime('09:00', '%H:%M').time(),
            days=(0, 1, 2, 3, 4, 5, 6),
            name="daily_tips"
        )

        logger.info("Telegram bot initialized successfully with audio support")
        return application

    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        raise

bot_app = init_bot()
