import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, CallbackContext
)
from app import app
from app.bot.price_api import get_bitcoin_price
from app.bot.content_swahili import LESSONS, MENU_KEYBOARD, QUIZZES, DAILY_TIPS
from app.database import update_user
from apscheduler.schedulers.background import BackgroundScheduler
import random
from datetime import datetime, timedelta


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


user_quiz_state = {}
user_last_tip = {}

def create_menu():
    return ReplyKeyboardMarkup(MENU_KEYBOARD, resize_keyboard=True)

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update_user(user)
    
    welcome_msg = (
        f"Habari {user.first_name}! 👋\n\n"
        f"{LESSONS['intro']['content']}"
    )
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=create_menu()
    )

async def price_command(update: Update, context: CallbackContext):
    price = get_bitcoin_price()
    await update.message.reply_text(price, parse_mode="Markdown")

async def send_daily_tip(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    
    
    last_tip_time = user_last_tip.get(user_id, datetime.min)
    if datetime.now() - last_tip_time < timedelta(hours=24):
        await update.message.reply_text(
            "Umepokea kidokezo cha leo tayari. Rudi kesho kwa kidokezo kingine!",
            reply_markup=create_menu()
        )
        return
    
    
    tip = random.choice(DAILY_TIPS)
    await update.message.reply_text(tip, parse_mode="Markdown")
    
    
    user_last_tip[user_id] = datetime.now()

async def start_quiz(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    
    
    user_quiz_state[user_id] = {
        'quiz_name': 'msingi',
        'current_question': 0,
        'score': 0
    }
    
    await ask_quiz_question(update, context, user_id)

async def ask_quiz_question(update: Update, context: CallbackContext, user_id: int):
    state = user_quiz_state.get(user_id)
    if not state:
        await update.message.reply_text(
            "Samahani, jaribio limeisha. Tafadhali anza tena.",
            reply_markup=create_menu()
        )
        return
    
    quiz = QUIZZES[state['quiz_name']]
    question = quiz[state['current_question']]
    
    
    question_text = f"❓ *Swali {state['current_question']+1}/{len(quiz)}:*\n{question['question']}\n\n"
    options = []
    for i, option in enumerate(question['options']):
        question_text += f"{i+1}. {option}\n"
        options.append(str(i+1))
    
    
    keyboard = [options[i:i+2] for i in range(0, len(options), 2)]
    keyboard.append(['❌ Acha Jaribio'])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        question_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_quiz_answer(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    text = update.message.text
    
    state = user_quiz_state.get(user_id)
    if not state:
        await update.message.reply_text(
            "Samahani, jaribio limeisha. Tafadhali anza tena.",
            reply_markup=create_menu()
        )
        return
    
    quiz = QUIZZES[state['quiz_name']]
    question = quiz[state['current_question']]
    
    
    if text == '❌ Acha Jaribio':
        del user_quiz_state[user_id]
        await update.message.reply_text(
            "Umeacha jaribio. Unaweza kuanza tena wakati wowote!",
            reply_markup=create_menu()
        )
        return
    
    
    if not text.isdigit() or int(text) < 1 or int(text) > len(question['options']):
        await update.message.reply_text(
            "Tafadhali chagua namba moja kati ya chaguo zilizopendekezwa."
        )
        return
    
    
    selected_index = int(text) - 1
    if selected_index == question['answer']:
        state['score'] += 1
        response = f"✅ Sahihi! {question['explanation']}"
    else:
        correct_answer = question['options'][question['answer']]
        response = f"❌ Si sahihi. Jibu sahihi ni: {correct_answer}\n{question['explanation']}"
    
    await update.message.reply_text(response, parse_mode="Markdown")
    
    
    state['current_question'] += 1
    if state['current_question'] < len(quiz):
        await ask_quiz_question(update, context, user_id)
    else:
        
        score = state['score']
        total = len(quiz)
        percentage = int(score / total * 100)
        
        if percentage >= 80:
            emoji = "🎉"
            message = "Hongera! Umefanya kazi nzuri sana!"
        elif percentage >= 50:
            emoji = "👍"
            message = "Vizuri! Unaendelea vizuri!"
        else:
            emoji = "💪"
            message = "Endelea kujifunza, utafanikiwa!"
        
        result = (
            f"{emoji} *Umeshinda Jaribio!*\n\n"
            f"Alama: {score}/{total} ({percentage}%)\n"
            f"{message}\n\n"
            "Unaweza kujaribu tena wakati wowote kwa kubonyeza '📝 Jaribio la Bitcoin'"
        )
        
        await update.message.reply_text(
            result,
            reply_markup=create_menu(),
            parse_mode="Markdown"
        )
        del user_quiz_state[user_id]

async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text
    update_user(user)
    
    
    if user.id in user_quiz_state:
        await handle_quiz_answer(update, context)
        return
    
    responses = {
        "💰 Bei ya Bitcoin": price_command,
        "📚 Bitcoin ni nini?": lambda u, c: u.message.reply_text(LESSONS['bitcoin_ni_nini']['content'], parse_mode="Markdown"),
        "🔗 P2P Inafanyaje": lambda u, c: u.message.reply_text(LESSONS['p2p_inafanyaje']['content'], parse_mode="Markdown"),
        "👛 Aina za Pochi": lambda u, c: u.message.reply_text(LESSONS['kufungua_pochi']['content'], parse_mode="Markdown"),
        "🔒 Usalama wa Pochi": lambda u, c: u.message.reply_text(LESSONS['usalama_pochi']['content'], parse_mode="Markdown"),
        "⚠️ Kupoteza Ufunguo": lambda u, c: u.message.reply_text(LESSONS['kupoteza_ufunguo']['content'], parse_mode="Markdown"),
        "📱 Matumizi ya Pochi": lambda u, c: u.message.reply_text(LESSONS['mfano_matumizi']['content'], parse_mode="Markdown"),
        "📱 Nunua kwa M-Pesa": lambda u, c: u.message.reply_text(LESSONS['mpesa_guide']['content'], parse_mode="Markdown"),
        "⚖️ Faida na Hatari": lambda u, c: u.message.reply_text(LESSONS['faida_na_hatari']['content'], parse_mode="Markdown"),
        "🔐 Teknolojia ya Blockchain": lambda u, c: u.message.reply_text(LESSONS['blockchain_usalama']['content'], parse_mode="Markdown"),
        "❓ Maswali Mengine": lambda u, c: u.message.reply_text(LESSONS['maswali_mengine']['content'], parse_mode="Markdown"),
        "ℹ️ Kuhusu BitMshauri": lambda u, c: u.message.reply_text(LESSONS['kuhusu_bitmshauri']['content'], parse_mode="Markdown"),
        "📝 Jaribio la Bitcoin": start_quiz,
        "💡 Kidokezo cha Leo": send_daily_tip,
    }
    
    if text in responses:
        await responses[text](update, context)
    else:
        await update.message.reply_text(
            "Samahani, sijaelewa. Tafadhali chagua moja ya chaguo zilizopo.",
            reply_markup=create_menu()
        )

def init_bot():
    try:
        application = Application.builder().token(app.config['TELEGRAM_TOKEN']).build()
        
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("price", price_command))
        application.add_handler(CommandHandler("bei", price_command))
        application.add_handler(CommandHandler("jaribio", start_quiz))
        application.add_handler(CommandHandler("kidokezo", send_daily_tip))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("Telegram bot initialized successfully")
        
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_scheduled_tips, 'cron', hour=9, minute=0, args=[application])  # 9 AM EAT
        scheduler.start()
        logger.info("Daily tip scheduler started")
        
        return application
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        raise


async def send_scheduled_tips(application):
    logger.info("Sending scheduled daily tips")
    
    
    tip = random.choice(DAILY_TIPS)
    logger.info(f"Today's tip: {tip}")
    
    
    


def create_bot_app():
  return init_bot()

bot_app = create_bot_app()