"""
Enhanced BitMshauri Telegram Bot with Professional Features
Comprehensive Bitcoin education bot with multi-language support,
community features, progress tracking, and advanced functionality.
"""

from dotenv import load_dotenv

load_dotenv()

import os
import logging
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    CallbackContext,
    ConversationHandler,
)

# Enhanced imports
from app.enhanced_database import DatabaseManager
from app.utils.logger import logger as app_logger
from app.utils.rate_limiter import rate_limiter, rate_limit
from app.services.price_service import price_monitor
from app.services.calculator import bitcoin_calculator
from app.services.progress_tracker import progress_tracker
from app.services.content_manager import content_manager
from app.services.multi_language import (
    multi_lang_bot,
    get_user_language,
    set_user_language,
)
from app.services.enhanced_audio import enhanced_audio
from app.services.community import community_manager
from app.bot.price_api import get_bitcoin_price  # Legacy support

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Initialize services
db_manager = DatabaseManager()

# Conversation states
(
    WAITING_FOR_GROUP_NAME,
    WAITING_FOR_GROUP_DESCRIPTION,
    WAITING_FOR_FEEDBACK,
    WAITING_FOR_CALCULATION,
) = range(4)

# Global user state tracking
user_quiz_state = {}
user_conversation_state = {}


class EnhancedBitMshauriBot:
    """Enhanced BitMshauri Bot with comprehensive features"""

    def __init__(self):
        self.app = None
        self.setup_logging()

    def setup_logging(self):
        """Configure enhanced logging"""
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger(__name__)

    async def start_command(self, update: Update, context: CallbackContext):
        """Enhanced start command with language detection"""
        try:
            user = update.effective_user
            user_id = user.id
            username = user.username or user.first_name or "BitMshauri User"

            # Add user to database
            db_manager.add_user(user_id, username)

            # Detect language from user's text if available
            user_language = get_user_language(
                user_id, update.message.text if update.message else None
            )

            # Get localized welcome message
            welcome_content = multi_lang_bot.get_lesson(user_id, "intro")
            if welcome_content:
                welcome_text = welcome_content.get("content", "")
            else:
                welcome_text = multi_lang_bot.get_response(user_id, "welcome")

            # Get localized menu
            menu_keyboard = multi_lang_bot.get_menu_keyboard(user_id)
            reply_markup = (
                ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
                if menu_keyboard
                else None
            )

            # Send welcome message with Bitcoin logo
            logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png"

            full_welcome = (
                f"👋 {welcome_text}\n\n🌟 Chagua moja ya chaguo hapa chini:"
            )

            await update.message.reply_photo(
                photo=logo_url, caption=full_welcome, reply_markup=reply_markup
            )

            # Log user start
            app_logger.log_user_action(
                user_id,
                "bot_started",
                {"username": username, "language": user_language},
            )

        except Exception as e:
            app_logger.log_error(
                e,
                {
                    "operation": "start_command",
                    "user_id": update.effective_user.id,
                },
            )
            await update.message.reply_text(
                "Samahani, kuna tatizo. Jaribu tena."
            )

    @rate_limit("message")
    async def handle_message(self, update: Update, context: CallbackContext):
        """Enhanced message handler with rate limiting and multi-language support"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text

            # Detect and update user language
            user_language = get_user_language(user_id, message_text)

            # Handle different message types
            if message_text in self._get_all_menu_options(user_id):
                await self._handle_menu_option(update, context, message_text)
            elif self._is_calculation_request(message_text):
                await self._handle_calculation(update, context, message_text)
            elif message_text.lower().startswith(("bitcoin", "btc", "bei")):
                await self._handle_price_request(update, context)
            else:
                await self._handle_general_message(
                    update, context, message_text
                )

        except Exception as e:
            app_logger.log_error(
                e,
                {
                    "operation": "handle_message",
                    "user_id": update.effective_user.id,
                },
            )
            error_msg = multi_lang_bot.get_response(
                update.effective_user.id, "error_occurred"
            )
            await update.message.reply_text(error_msg)

    def _get_all_menu_options(self, user_id: int) -> List[str]:
        """Get all possible menu options for user's language"""
        try:
            menu_keyboard = multi_lang_bot.get_menu_keyboard(user_id) or []
            secondary_menu = (
                multi_lang_bot.get_secondary_menu_keyboard(user_id) or []
            )

            options = []
            for row in menu_keyboard + secondary_menu:
                options.extend(row)

            return options
        except:
            return []

    def _is_calculation_request(self, text: str) -> bool:
        """Check if message is a calculation request"""
        calc_keywords = [
            "calculate",
            "convert",
            "hesabu",
            "badili",
            "usd",
            "btc",
            "bitcoin",
            "dola",
        ]
        return any(keyword in text.lower() for keyword in calc_keywords)

    async def _handle_menu_option(
        self, update: Update, context: CallbackContext, option: str
    ):
        """Handle menu option selection"""
        user_id = update.effective_user.id

        # Map menu options to handlers
        if "Bitcoin" in option or "bei" in option.lower():
            await self._handle_price_request(update, context)
        elif "Quiz" in option or "jaribio" in option.lower():
            await self._handle_quiz_start(update, context)
        elif "Msaada" in option or "Help" in option:
            await self._handle_help_request(update, context)
        elif "Kidokezo" in option or "Tip" in option:
            await self._handle_daily_tip(update, context)
        elif "Nunua" in option or "Buy" in option:
            await self._handle_purchase_flow(update, context)
        elif "Kundi" in option or "Group" in option:
            await self._handle_community_features(update, context)
        elif "Sauti" in option or "Audio" in option:
            await self._handle_audio_request(update, context)
        else:
            # Try to find matching lesson
            await self._handle_lesson_request(update, context, option)

    async def _handle_price_request(
        self, update: Update, context: CallbackContext
    ):
        """Handle Bitcoin price request with enhanced formatting"""
        try:
            user_id = update.effective_user.id

            # Get current price
            price_data = await price_monitor.get_current_price()

            if price_data:
                # Format price message in user's language
                price_message = multi_lang_bot.format_price_message(
                    user_id, price_data
                )

                # Create price alert button
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🔔 Weka Kumbuka za Bei",
                            callback_data="set_price_alert",
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    price_message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )

                # Log price request
                app_logger.log_user_action(
                    user_id,
                    "price_requested",
                    {"price_usd": price_data.get("usd")},
                )
            else:
                error_msg = "Samahani, bei ya Bitcoin haipatikani kwa sasa. Jaribu tena baadaye."
                await update.message.reply_text(error_msg)

        except Exception as e:
            app_logger.log_error(e, {"operation": "handle_price_request"})
            await update.message.reply_text(
                "Tatizo la kupata bei ya Bitcoin. Jaribu tena."
            )

    async def _handle_calculation(
        self, update: Update, context: CallbackContext, text: str
    ):
        """Handle Bitcoin calculation requests"""
        try:
            user_id = update.effective_user.id

            # Calculate using enhanced calculator
            result = bitcoin_calculator.calculate(text)

            if result:
                # Format result in user's language
                calc_message = multi_lang_bot.format_calculation_result(
                    user_id, result
                )
                await update.message.reply_text(
                    calc_message, parse_mode="Markdown"
                )

                app_logger.log_user_action(
                    user_id,
                    "calculation_performed",
                    {"calculation": text, "result": result},
                )
            else:
                if get_user_language(user_id) == "en":
                    error_msg = "Sorry, I couldn't understand that calculation. Try: '100 USD to BTC' or '0.1 BTC to USD'"
                else:
                    error_msg = "Samahani, sijaweza kuelewa hesabu hiyo. Jaribu: '100 USD to BTC' au '0.1 BTC to USD'"

                await update.message.reply_text(error_msg)

        except Exception as e:
            app_logger.log_error(e, {"operation": "handle_calculation"})
            await update.message.reply_text("Tatizo la kuhesabu. Jaribu tena.")

    async def _handle_quiz_start(
        self, update: Update, context: CallbackContext
    ):
        """Start quiz with enhanced features"""
        try:
            user_id = update.effective_user.id

            # Get quiz in user's language
            quiz_questions = multi_lang_bot.get_quiz(user_id, "msingi")

            if not quiz_questions:
                await update.message.reply_text(
                    "Hakuna maswali ya jaribio kwa sasa."
                )
                return

            # Initialize quiz state
            user_quiz_state[user_id] = {
                "questions": quiz_questions,
                "current_question": 0,
                "score": 0,
                "start_time": datetime.now(),
            }

            # Send first question
            await self._send_quiz_question(update, context, user_id)

        except Exception as e:
            app_logger.log_error(e, {"operation": "handle_quiz_start"})
            await update.message.reply_text("Tatizo la kuanza jaribio.")

    async def _send_quiz_question(
        self, update: Update, context: CallbackContext, user_id: int
    ):
        """Send quiz question with audio option"""
        try:
            quiz_state = user_quiz_state.get(user_id)
            if not quiz_state:
                return

            questions = quiz_state["questions"]
            current_q = quiz_state["current_question"]

            if current_q >= len(questions):
                await self._finish_quiz(update, context, user_id)
                return

            question = questions[current_q]

            # Format question
            question_text = (
                f"❓ **Swali {current_q + 1}/{len(questions)}**\n\n"
            )
            question_text += f"{question['question']}\n\n"

            # Add options
            for i, option in enumerate(question["options"], 1):
                question_text += f"{i}. {option}\n"

            # Create option buttons
            keyboard = []
            for i, option in enumerate(question["options"], 1):
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"{i}. {option}", callback_data=f"quiz_{i-1}"
                        )
                    ]
                )

            # Add audio button
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "🎵 Sikiza Swali", callback_data="quiz_audio"
                    )
                ]
            )

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                question_text, reply_markup=reply_markup, parse_mode="Markdown"
            )

        except Exception as e:
            app_logger.log_error(e, {"operation": "send_quiz_question"})

    async def _handle_audio_request(
        self, update: Update, context: CallbackContext
    ):
        """Handle audio generation requests"""
        try:
            user_id = update.effective_user.id

            # Show voice options
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🎓 Mshauri (Kawaida)", callback_data="voice_mshauri"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⚡ Haraka", callback_data="voice_haraka"
                    )
                ],
                [InlineKeyboardButton("👴 Mzee", callback_data="voice_mzee")],
                [
                    InlineKeyboardButton(
                        "👦 Kijana", callback_data="voice_kijana"
                    )
                ],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            message = "🎵 Chagua aina ya sauti unayotaka kwa masomo ya sauti:"
            await update.message.reply_text(message, reply_markup=reply_markup)

        except Exception as e:
            app_logger.log_error(e, {"operation": "handle_audio_request"})

    async def _handle_community_features(
        self, update: Update, context: CallbackContext
    ):
        """Handle community features"""
        try:
            user_id = update.effective_user.id

            # Show community options
            keyboard = [
                [
                    InlineKeyboardButton(
                        "👥 Orodha ya Makundi", callback_data="list_groups"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "➕ Unda Kundi", callback_data="create_group"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📊 Makundi Yangu", callback_data="my_groups"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏆 Changamoto", callback_data="challenges"
                    )
                ],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            message = (
                "🌟 **Vipengele vya Jamii**\n\n"
                "Jiunga na wengine kujifunza Bitcoin pamoja!"
            )

            await update.message.reply_text(
                message, reply_markup=reply_markup, parse_mode="Markdown"
            )

        except Exception as e:
            app_logger.log_error(e, {"operation": "handle_community_features"})

    async def _handle_lesson_request(
        self, update: Update, context: CallbackContext, lesson_text: str
    ):
        """Handle lesson content request"""
        try:
            user_id = update.effective_user.id

            # Try to match lesson
            lesson_mapping = {
                "Kwa Nini Bitcoin?": "kwa_nini_bitcoin",
                "Why Bitcoin?": "why_bitcoin",
                "Bitcoin ni nini?": "bitcoin_ni_nini",
                "What is Bitcoin?": "what_is_bitcoin",
            }

            lesson_key = lesson_mapping.get(lesson_text)
            if not lesson_key:
                # Fallback to intro lesson
                lesson_key = "intro"

            lesson = multi_lang_bot.get_lesson(user_id, lesson_key)

            if lesson:
                lesson_content = lesson.get("content", "")

                # Add lesson progress tracking
                progress_tracker.complete_lesson(user_id, lesson_key)

                # Create lesson options
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🎵 Sikiza Somo",
                            callback_data=f"audio_lesson_{lesson_key}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "📝 Jaribio", callback_data="start_quiz"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "↩️ Rudi Menyu", callback_data="main_menu"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    lesson_content,
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )

                app_logger.log_user_action(
                    user_id,
                    "lesson_viewed",
                    {
                        "lesson_key": lesson_key,
                        "lesson_title": lesson.get("title", lesson_key),
                    },
                )
            else:
                await update.message.reply_text(
                    "Samahani, somo hilo halipatikani."
                )

        except Exception as e:
            app_logger.log_error(e, {"operation": "handle_lesson_request"})

    async def handle_callback_query(
        self, update: Update, context: CallbackContext
    ):
        """Handle inline keyboard callbacks"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.from_user.id
            data = query.data

            if data.startswith("quiz_"):
                await self._handle_quiz_answer(update, context, data)
            elif data.startswith("voice_"):
                await self._handle_voice_selection(update, context, data)
            elif data.startswith("audio_lesson_"):
                await self._handle_audio_lesson(update, context, data)
            elif data == "set_price_alert":
                await self._handle_price_alert_setup(update, context)
            elif data == "list_groups":
                await self._handle_list_groups(update, context)
            elif data == "create_group":
                await self._handle_create_group_start(update, context)
            elif data == "my_groups":
                await self._handle_my_groups(update, context)
            elif data == "challenges":
                await self._handle_challenges(update, context)
            elif data == "main_menu":
                await self._handle_main_menu(update, context)
            else:
                await query.edit_message_text("Chaguo halipatikani.")

        except Exception as e:
            app_logger.log_error(e, {"operation": "handle_callback_query"})

    async def language_command(self, update: Update, context: CallbackContext):
        """Handle language selection command"""
        try:
            user_id = update.effective_user.id

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🇹🇿 Kiswahili", callback_data="lang_sw"
                    )
                ],
                [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "🌍 Chagua lugha / Choose language:", reply_markup=reply_markup
            )

        except Exception as e:
            app_logger.log_error(e, {"operation": "language_command"})

    async def help_command(self, update: Update, context: CallbackContext):
        """Enhanced help command"""
        try:
            user_id = update.effective_user.id
            language = get_user_language(user_id)

            if language == "en":
                help_text = (
                    "🤖 **BitMshauri Bot Help**\n\n"
                    "**Commands:**\n"
                    "/start - Start the bot\n"
                    "/help - Show this help\n"
                    "/language - Change language\n"
                    "/price - Get Bitcoin price\n"
                    "/calculate - Bitcoin calculator\n"
                    "/quiz - Take a quiz\n"
                    "/progress - View your progress\n"
                    "/groups - Community features\n\n"
                    "**Features:**\n"
                    "• Multi-language support (Swahili/English)\n"
                    "• Bitcoin education lessons\n"
                    "• Interactive quizzes\n"
                    "• Audio lessons\n"
                    "• Price monitoring\n"
                    "• Community groups\n"
                    "• Progress tracking"
                )
            else:
                help_text = (
                    "🤖 **Msaada wa BitMshauri**\n\n"
                    "**Amri:**\n"
                    "/start - Anza bot\n"
                    "/help - Onyesha msaada\n"
                    "/language - Badili lugha\n"
                    "/price - Bei ya Bitcoin\n"
                    "/calculate - Kikokotoo cha Bitcoin\n"
                    "/quiz - Fanya jaribio\n"
                    "/progress - Ona maendeleo yako\n"
                    "/groups - Vipengele vya jamii\n\n"
                    "**Vipengele:**\n"
                    "• Lugha nyingi (Kiswahili/Kiingereza)\n"
                    "• Masomo ya Bitcoin\n"
                    "• Majaribio ya kushirikiana\n"
                    "• Masomo ya sauti\n"
                    "• Ufuatiliaji wa bei\n"
                    "• Makundi ya jamii\n"
                    "• Ufuatiliaji wa maendeleo"
                )

            await update.message.reply_text(help_text, parse_mode="Markdown")

        except Exception as e:
            app_logger.log_error(e, {"operation": "help_command"})

    async def progress_command(self, update: Update, context: CallbackContext):
        """Show user progress"""
        try:
            user_id = update.effective_user.id

            progress = progress_tracker.get_user_progress(user_id)

            if progress:
                language = get_user_language(user_id)

                if language == "en":
                    progress_text = (
                        f"📊 **Your Progress**\n\n"
                        f"🎓 Lessons Completed: {len(progress.get('completed_lessons', []))}\n"
                        f"📝 Quizzes Taken: {len(progress.get('quiz_results', []))}\n"
                        f"🏆 Achievements: {len(progress.get('achievements', []))}\n"
                        f"🔥 Current Streak: {progress.get('streak_days', 0)} days\n"
                        f"💰 Total Score: {progress.get('total_score', 0)}"
                    )
                else:
                    progress_text = (
                        f"📊 **Maendeleo Yako**\n\n"
                        f"🎓 Masomo Yaliyokamilika: {len(progress.get('completed_lessons', []))}\n"
                        f"📝 Majaribio Yaliyofanywa: {len(progress.get('quiz_results', []))}\n"
                        f"🏆 Mafanikio: {len(progress.get('achievements', []))}\n"
                        f"🔥 Mfuatatano wa Sasa: siku {progress.get('streak_days', 0)}\n"
                        f"💰 Jumla ya Alama: {progress.get('total_score', 0)}"
                    )

                await update.message.reply_text(
                    progress_text, parse_mode="Markdown"
                )
            else:
                message = "Haujafanya maendeleo yoyote bado. Anza kujifunza!"
                await update.message.reply_text(message)

        except Exception as e:
            app_logger.log_error(e, {"operation": "progress_command"})

    def setup_handlers(self):
        """Setup all command and message handlers"""
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("language", self.language_command))
        self.app.add_handler(CommandHandler("progress", self.progress_command))

        # Callback query handler
        self.app.add_handler(CallbackQueryHandler(self.handle_callback_query))

        # Message handler
        self.app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.handle_message
            )
        )

    def run(self):
        """Run the bot"""
        try:
            # Create application
            self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

            # Setup handlers
            self.setup_handlers()

            # Start background tasks
            asyncio.create_task(self._start_background_tasks())

            # Run the bot
            self.logger.info("BitMshauri Bot started successfully!")
            self.app.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            app_logger.log_error(e, {"operation": "run_bot"})
            self.logger.error(f"Failed to start bot: {e}")

    async def _start_background_tasks(self):
        """Start background tasks like price monitoring"""
        try:
            # Start price monitoring
            await price_monitor.start_monitoring()

            # Cleanup old audio files daily
            async def daily_cleanup():
                while True:
                    await asyncio.sleep(86400)  # 24 hours
                    enhanced_audio.cleanup_old_audio()

            asyncio.create_task(daily_cleanup())

        except Exception as e:
            app_logger.log_error(e, {"operation": "start_background_tasks"})


# Create and run bot instance
if __name__ == "__main__":
    bot = EnhancedBitMshauriBot()
    bot.run()
