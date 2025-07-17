import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, CallbackContext
)
from .. import app
from app.bot.price_api import get_bitcoin_price
from app.bot.content_swahili import LESSONS, MENU_KEYBOARD, QUIZZES, DAILY_TIPS, SECONDARY_MENU_KEYBOARD
from app.database import update_user, get_all_users, update_last_tip
from apscheduler.schedulers.background import BackgroundScheduler
import random
import os
import requests
from datetime import datetime, timedelta

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

# --- Core Command Handlers ---
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

# --- Menu Navigation Handlers ---
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

# --- Purchase Flow Handlers ---
async def purchase_bitcoin(update: Update, context: CallbackContext):
    keyboard = [["Bitika", "Bitsacco"], ["⬅️ Rudi Mwanzo"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Unaweza kununua Bitcoin kupitia Bitika au Bitsacco. Chagua jukwaa unalopendelea:",
        reply_markup=reply_markup
    )

async def handle_purchase_platform(update: Update, context: CallbackContext, platform: str):
    url = "bitika.xyz" if platform == "Bitika" else "bitsacco.com"
    message = (
        f"Asante kwa kuchagua {platform}! Tafadhali tembelea [{url}](https://{url}) "
        "kukamilisha ununuzi wako. \n\nBonyeza hapa chini ukimaliza."
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

# --- Quiz Handlers ---

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Set this in your environment

async def ai_answer_handler(update: Update, context: CallbackContext):
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
        "max_tokens": 200
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip()
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("Samahani, kuna tatizo na huduma ya AI. Tafadhali jaribu tena baadaye.")

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
            f"Alama: {score}/{total} ({percentage}%)\n{message}\n\n"
            "Unaweza kujaribu tena wakati wowote!"
        )
        await update.message.reply_text(result, reply_markup=create_menu(), parse_mode="Markdown")
        del user_quiz_state[user_id]

# --- Daily Tip Scheduler ---
async def send_daily_tip(bot, user_id, chat_id):
    # This is a helper for the main scheduler to avoid code duplication
    try:
        tip = random.choice(DAILY_TIPS)
        await bot.send_message(chat_id=chat_id, text=tip, parse_mode="Markdown")
        update_last_tip(user_id)
        logger.info(f"Sent tip to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send tip to user {user_id}: {e}")

async def scheduled_tip_job(context: CallbackContext):
    logger.info("Running scheduled daily tips job...")
    users = get_all_users() # Assuming this returns (user_id, chat_id, last_tip_timestamp)
    if not users:
        logger.info("No users found to send tips to.")
        return

    for user_id, chat_id, last_tip_str in users:
        # Add logic to check if a tip should be sent (e.g., not in the last 23 hours)
        # For now, we will send to all for simplicity of testing.
        await send_daily_tip(context.bot, user_id, chat_id)

# --- Main Message Handler ---
async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text
    update_user(user, update.effective_chat.id)

    if user.id in user_quiz_state:
        await handle_quiz_answer(update, context)
        return

    # Static lesson content and main menu actions
    responses = {
        "📚 Bitcoin ni nini?": lambda u, c: u.message.reply_text(LESSONS['bitcoin_ni_nini']['content'], parse_mode="Markdown"),
        "🔗 P2P Inafanyaje": lambda u, c: u.message.reply_text(LESSONS['p2p_inafanyaje']['content'], parse_mode="Markdown"),
        "👛 Aina za Pochi": lambda u, c: u.message.reply_text(LESSONS['kufungua_pochi']['content'], parse_mode="Markdown"),
        "🔒 Usalama wa Pochi": lambda u, c: u.message.reply_text(LESSONS['usalama_pochi']['content'], parse_mode="Markdown"),
        "⚠️ Kupoteza Ufunguo": lambda u, c: u.message.reply_text(LESSONS['kupoteza_ufunguo']['content'], parse_mode="Markdown"),
        "📱 Matumizi ya Pochi": lambda u, c: u.message.reply_text(LESSONS['mfano_matumizi']['content'], parse_mode="Markdown"),
        "⚖️ Faida na Hatari": lambda u, c: u.message.reply_text(LESSONS['faida_na_hatari']['content'], parse_mode="Markdown"),
        "🔐 Teknolojia ya Blockchain": lambda u, c: u.message.reply_text(LESSONS['blockchain_usalama']['content'], parse_mode="Markdown"),
        "❓ Maswali Mengine": lambda u, c: u.message.reply_text(LESSONS['maswali_mengine']['content'], parse_mode="Markdown"),
        "💰 Bei ya Bitcoin": price_command,
        "📝 Jaribio la Bitcoin": start_quiz,
        "💡 Kidokezo cha Leo": lambda u, c: send_daily_tip(c.bot, u.effective_user.id, u.effective_chat.id),
        "ℹ️ Msaada Zaidi": show_more_help,
        "⬅️ Rudi Mwanzo": back_to_main_menu,
        "🛒 Nunua Bitcoin": purchase_bitcoin,
        "Bitika": lambda u, c: handle_purchase_platform(u, c, "Bitika"),
        "Bitsacco": lambda u, c: handle_purchase_platform(u, c, "Bitsacco"),
        "✅ Nimemaliza Muamala": transaction_complete,
    }

    if text in responses:
        await responses[text](update, context)
    else:
        await update.message.reply_text(
            "Samahani, sijaelewa. Tafadhali chagua moja ya chaguo zilizopo kwenye menyu.",
            reply_markup=create_menu()
        )

    if text == "❓ Maswali Mengine":
        await update.message.reply_text(
            "Andika swali lako kuhusu Bitcoin hapa chini, na nitakujibu moja kwa moja!"
        )
        context.user_data["awaiting_ai_question"] = True
        return

    if context.user_data.get("awaiting_ai_question"):
        context.user_data["awaiting_ai_question"] = False
        await ai_answer_handler(update, context)
        return

# --- Bot Initialization ---
def init_bot():
    try:
        application = Application.builder().token(app.config['TELEGRAM_TOKEN']).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Schedule daily tips
        job_queue = application.job_queue
        job_queue.run_daily(scheduled_tip_job, time=datetime.strptime('09:00', '%H:%M').time())
        
        logger.info("Telegram bot initialized successfully")
        return application
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        raise

bot_app = init_bot()
