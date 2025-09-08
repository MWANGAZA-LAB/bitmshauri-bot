"""
Clean BitMshauri Telegram Bot - Unified Version
Consolidates all features with proper menu integration and command routing
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

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
)

# Enhanced imports with proper error handling
from app.utils.database_manager import async_db_manager
from app.utils.logger import logger
from app.utils.input_validator import InputValidator
from app.utils.performance_monitor import (
    monitor_performance,
    enhanced_rate_limiter,
    start_performance_monitoring
)
from app.services.price_service import price_monitor
from app.services.calculator import bitcoin_calculator
from app.services.multi_language import multi_lang_bot
from app.services.enhanced_audio import enhanced_audio
from config import Config


class CleanBitMshauriBot:
    """Clean BitMshauri Bot with proper menu integration"""

    def __init__(self):
        self.app: Optional[Application] = None
        self.config = Config()
        self.validator = InputValidator()
        self.setup_logging()

        # Menu mapping for proper command routing
        self.menu_handlers = {
            # Primary menu items
            "🌍 Kwa Nini Bitcoin?": self._handle_lesson_request,
            "📚 Bitcoin ni nini?": self._handle_lesson_request,
            "💰 Bei ya Bitcoin": self._handle_price_request,
            "📝 Jaribio la Bitcoin": self._handle_quiz_start,
            "🛒 Nunua Bitcoin": self._handle_purchase_flow,
            "💡 Kidokezo cha Leo": self._handle_daily_tip,
            "ℹ️ Msaada Zaidi": self._handle_help_request,
            "📝 Toa Maoni": self._handle_feedback_request,

            # Secondary menu items
            "🔗 P2P Inafanyaje": self._handle_lesson_request,
            "👛 Aina za Pochi": self._handle_lesson_request,
            "🔒 Usalama wa Pochi": self._handle_lesson_request,
            "⚠️ Kupoteza Ufunguo": self._handle_lesson_request,
            "📱 Matumizi ya Pochi": self._handle_lesson_request,
            "⚖️ Faida na Hatari": self._handle_lesson_request,
            "🔐 Teknolojia ya Blockchain": self._handle_lesson_request,
            "❓ Maswali Mengine": self._handle_ai_questions,
            "🎵 Masomo ya Sauti": self._handle_audio_request,
            "⬅️ Rudi Mwanzo": self._handle_main_menu,

            # English menu items
            "🌍 Why Bitcoin?": self._handle_lesson_request,
            "📚 What is Bitcoin?": self._handle_lesson_request,
            "💰 Bitcoin Price": self._handle_price_request,
            "📝 Bitcoin Quiz": self._handle_quiz_start,
            "🛒 Buy Bitcoin": self._handle_purchase_flow,
            "💡 Daily Tip": self._handle_daily_tip,
            "ℹ️ More Help": self._handle_help_request,
            "📝 Feedback": self._handle_feedback_request,
        }

        # Lesson key mapping
        self.lesson_mapping = {
            "🌍 Kwa Nini Bitcoin?": "kwa_nini_bitcoin",
            "📚 Bitcoin ni nini?": "bitcoin_ni_nini",
            "🔗 P2P Inafanyaje": "p2p_inafanyaje",
            "👛 Aina za Pochi": "kufungua_pochi",
            "🔒 Usalama wa Pochi": "usalama_pochi",
            "⚠️ Kupoteza Ufunguo": "kupoteza_ufunguo",
            "📱 Matumizi ya Pochi": "mfano_matumizi",
            "⚖️ Faida na Hatari": "faida_na_hatari",
            "🔐 Teknolojia ya Blockchain": "blockchain_usalama",
            "🌍 Why Bitcoin?": "why_bitcoin",
            "📚 What is Bitcoin?": "what_is_bitcoin",
        }

    def setup_logging(self):
        """Configure enhanced logging"""
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=getattr(logging, self.config.LOG_LEVEL),
        )
        self.logger = logging.getLogger(__name__)

    @monitor_performance("start_command")
    async def start_command(self, update: Update, context: CallbackContext):
        """Enhanced start command with proper validation and error handling"""
        try:
            # Validate input
            user = update.effective_user
            if not self.validator.validate_user_id(user.id):
                await update.message.reply_text("Invalid user ID")
                return

            user_id = user.id
            username = user.username or user.first_name or "BitMshauri User"

            # Add user to database with validation
            sanitized_data = {
                'user_id': user_id,
                'username': username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'chat_id': update.effective_chat.id
            }

            await async_db_manager.add_user(**sanitized_data)

            # Detect language and get localized content
            user_language = multi_lang_bot.get_user_language(
                user_id, update.message.text if update.message else None
            )

            welcome_content = multi_lang_bot.get_lesson(user_id, "intro")
            welcome_text = (
                welcome_content.get("content", "")
                if welcome_content
                else multi_lang_bot.get_response(user_id, "welcome")
            )

            # Get localized menu
            menu_keyboard = multi_lang_bot.get_menu_keyboard(user_id)
            reply_markup = (
                ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
                if menu_keyboard
                else None
            )

            # Send welcome message
            full_welcome = (
                f"👋 {welcome_text}\n\n"
                f"🌟 Chagua moja ya chaguo hapa chini:"
            )

            await update.message.reply_photo(
                photo=("https://upload.wikimedia.org/wikipedia/commons/"
                       "thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png"),
                caption=full_welcome,
                reply_markup=reply_markup
            )

            # Log user start
            logger.log_user_action(
                user_id,
                "bot_started",
                {"username": username, "language": user_language},
            )

        except Exception as e:
            logger.log_error(
                e,
                {
                    "operation": "start_command",
                    "user_id": update.effective_user.id,
                },
            )
            await self._send_error_message(update, "start_error")

    @monitor_performance("handle_message")
    async def handle_message(self, update: Update, context: CallbackContext):
        """Enhanced message handler with rate limiting and validation"""
        try:
            user_id = update.effective_user.id

            # Rate limiting check
            if enhanced_rate_limiter.is_rate_limited(user_id, "message"):
                await update.message.reply_text(
                    "⏰ Subiri kidogo! Umetuma maombi mengi sana. "
                    "Tafadhali jaribu tena baada ya dakika chache."
                )
                return

            # Validate message text
            message_text = update.message.text
            if not self.validator.validate_message_text(message_text):
                await update.message.reply_text("Invalid message format")
                return

            # Detect and update user language
            multi_lang_bot.get_user_language(user_id, message_text)

            # Route message to appropriate handler
            await self._route_message(update, context, message_text)

        except Exception as e:
            logger.log_error(
                e,
                {
                    "operation": "handle_message",
                    "user_id": update.effective_user.id,
                },
            )
            await self._send_error_message(update, "message_error")

    async def _route_message(self, update: Update, context: CallbackContext,
                           text: str):
        """Route message to appropriate handler with proper menu integration"""
        # Check if it's a menu option
        if text in self.menu_handlers:
            handler = self.menu_handlers[text]
            await handler(update, context, text)
        # Check if it's a calculation request
        elif self._is_calculation_request(text):
            await self._handle_calculation(update, context, text)
        # Check if it's a price request
        elif text.lower().startswith(("bitcoin", "btc", "bei")):
            await self._handle_price_request(update, context)
        # Check if it's feedback
        elif context.user_data.get("awaiting_feedback"):
            await self._handle_feedback_submission(update, context, text)
        # Check if it's AI question
        elif context.user_data.get("awaiting_ai_question"):
            await self._handle_ai_answer(update, context, text)
        else:
            await self._handle_general_message(update, context, text)

    def _is_calculation_request(self, text: str) -> bool:
        """Check if message is a calculation request"""
        validation_result = self.validator.validate_calculation_input(text)
        return validation_result.get("valid", False)

    @monitor_performance("handle_price_request")
    async def _handle_price_request(self, update: Update,
                                  context: CallbackContext,
                                  menu_text: str = None):
        """Handle Bitcoin price request with enhanced formatting"""
        try:
            user_id = update.effective_user.id

            # Get current price with caching
            price_data = await price_monitor.get_current_price()

            if price_data:
                # Format price message in user's language
                price_message = multi_lang_bot.format_price_message(
                    user_id, price_data
                )

                # Create price alert button
                keyboard = [[
                    InlineKeyboardButton(
                        "🔔 Weka Kumbuka za Bei",
                        callback_data="set_price_alert",
                    )
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    price_message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )

                # Log price request
                logger.log_user_action(
                    user_id,
                    "price_requested",
                    {"price_usd": price_data.get("usd")},
                )
            else:
                await self._send_error_message(update, "price_unavailable")

        except Exception as e:
            logger.log_error(e, {"operation": "handle_price_request"})
            await self._send_error_message(update, "price_error")

    @monitor_performance("handle_calculation")
    async def _handle_calculation(self, update: Update, context: CallbackContext,
                                text: str):
        """Handle Bitcoin calculation requests with validation"""
        try:
            user_id = update.effective_user.id

            # Validate calculation input
            validation_result = self.validator.validate_calculation_input(text)
            if not validation_result["valid"]:
                await update.message.reply_text(validation_result["error"])
                return

            # Calculate using enhanced calculator
            result = await bitcoin_calculator.calculate(text)

            if result:
                # Format result in user's language
                calc_message = multi_lang_bot.format_calculation_result(
                    user_id, result
                )
                await update.message.reply_text(
                    calc_message, parse_mode="Markdown"
                )

                logger.log_user_action(
                    user_id,
                    "calculation_performed",
                    {"calculation": text, "result": result},
                )
            else:
                await self._send_error_message(update, "calculation_error")

        except Exception as e:
            logger.log_error(e, {"operation": "handle_calculation"})
            await self._send_error_message(update, "calculation_error")

    async def _handle_lesson_request(self, update: Update,
                                   context: CallbackContext, menu_text: str):
        """Handle lesson content request with proper menu integration"""
        try:
            user_id = update.effective_user.id

            # Get lesson key from menu mapping
            lesson_key = self.lesson_mapping.get(menu_text, "intro")
            lesson = multi_lang_bot.get_lesson(user_id, lesson_key)

            if lesson:
                lesson_content = lesson.get("content", "")

                # Track lesson completion
                await async_db_manager.save_lesson_progress(user_id, lesson_key)

                # Create lesson options
                keyboard = [
                    [InlineKeyboardButton(
                        "🎵 Sikiza Somo",
                        callback_data=f"audio_lesson_{lesson_key}"
                    )],
                    [InlineKeyboardButton(
                        "📝 Jaribio", callback_data="start_quiz"
                    )],
                    [InlineKeyboardButton(
                        "↩️ Rudi Menyu", callback_data="main_menu"
                    )],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    lesson_content,
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )

                logger.log_user_action(
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
            logger.log_error(e, {"operation": "handle_lesson_request"})
            await self._send_error_message(update, "lesson_error")

    @monitor_performance("handle_quiz_start")
    async def _handle_quiz_start(self, update: Update, context: CallbackContext,
                               menu_text: str = None):
        """Start quiz with enhanced features"""
        try:
            user_id = update.effective_user.id

            # Rate limiting for quiz
            if enhanced_rate_limiter.is_rate_limited(user_id, "quiz"):
                await update.message.reply_text(
                    "⏰ Subiri kidogo! Umetumia majaribio mengi. "
                    "Tafadhali jaribu tena baadaye."
                )
                return

            # Get quiz in user's language
            quiz_questions = multi_lang_bot.get_quiz(user_id, "msingi")

            if not quiz_questions:
                await update.message.reply_text(
                    "Hakuna maswali ya jaribio kwa sasa."
                )
                return

            # Initialize quiz state
            context.user_data['quiz_state'] = {
                "questions": quiz_questions,
                "current_question": 0,
                "score": 0,
                "start_time": datetime.now(),
            }

            # Send first question
            await self._send_quiz_question(update, context, user_id)

        except Exception as e:
            logger.log_error(e, {"operation": "handle_quiz_start"})
            await self._send_error_message(update, "quiz_error")

    async def _send_quiz_question(self, update: Update, context: CallbackContext,
                                user_id: int):
        """Send quiz question with audio option"""
        try:
            quiz_state = context.user_data.get('quiz_state')
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
                keyboard.append([
                    InlineKeyboardButton(
                        f"{i}. {option}", callback_data=f"quiz_{i-1}"
                    )
                ])

            # Add audio button
            keyboard.append([
                InlineKeyboardButton(
                    "🎵 Sikiza Swali", callback_data="quiz_audio"
                )
            ])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                question_text, reply_markup=reply_markup,
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.log_error(e, {"operation": "send_quiz_question"})

    async def _finish_quiz(self, update: Update, context: CallbackContext,
                         user_id: int):
        """Finish quiz and show results"""
        try:
            quiz_state = context.user_data.get('quiz_state', {})
            questions = quiz_state.get("questions", [])
            score = quiz_state.get("score", 0)
            start_time = quiz_state.get("start_time", datetime.now())

            time_taken = (datetime.now() - start_time).total_seconds()
            percentage = (score / len(questions)) * 100 if questions else 0

            # Save quiz result
            await async_db_manager.save_quiz_result(
                user_id, "msingi", score, len(questions),
                quiz_state.get("answers", []), int(time_taken)
            )

            # Format results message
            if percentage >= 80:
                result_emoji = "🏆"
                result_text = "Hongera! Umefanya vizuri sana!"
            elif percentage >= 60:
                result_emoji = "👍"
                result_text = "Vizuri! Unaendelea vizuri."
            else:
                result_emoji = "📚"
                result_text = "Endelea kujifunza zaidi."

            message = (
                f"{result_emoji} **Matokeo ya Jaribio**\n\n"
                f"📊 Alama: {score}/{len(questions)} ({percentage:.1f}%)\n"
                f"⏱️ Muda: {int(time_taken)} sekunde\n\n"
                f"{result_text}"
            )

            await update.message.reply_text(message, parse_mode="Markdown")

            # Clear quiz state
            context.user_data.pop('quiz_state', None)

            logger.log_user_action(
                user_id,
                "quiz_completed",
                {
                    "score": score,
                    "total_questions": len(questions),
                    "percentage": percentage,
                    "time_taken": time_taken
                }
            )

        except Exception as e:
            logger.log_error(e, {"operation": "finish_quiz"})

    async def _handle_help_request(self, update: Update, context: CallbackContext,
                                 menu_text: str = None):
        """Enhanced help command"""
        try:
            user_id = update.effective_user.id

            help_text = multi_lang_bot.get_response(user_id, "help_command")
            await update.message.reply_text(help_text, parse_mode="Markdown")

        except Exception as e:
            logger.log_error(e, {"operation": "handle_help_request"})
            await self._send_error_message(update, "help_error")

    async def _handle_daily_tip(self, update: Update, context: CallbackContext,
                              menu_text: str = None):
        """Handle daily tip request"""
        try:
            user_id = update.effective_user.id
            tips = multi_lang_bot.get_daily_tips(user_id)

            if tips:
                import random
                tip = random.choice(tips)
                await update.message.reply_text(tip)
            else:
                await update.message.reply_text("Hakuna kidokezo kwa sasa.")

        except Exception as e:
            logger.log_error(e, {"operation": "handle_daily_tip"})
            await self._send_error_message(update, "tip_error")

    async def _handle_purchase_flow(self, update: Update,
                                  context: CallbackContext,
                                  menu_text: str = None):
        """Handle Bitcoin purchase flow"""
        try:
            message = (
                "🛒 **Kununua Bitcoin**\n\n"
                "Kwa sasa tunafanya kazi kwenye mfumo wa kununua Bitcoin. "
                "Tafadhali rudi baadaye au tumia msaada wa mtaalamu wa Bitcoin."
            )

            await update.message.reply_text(message, parse_mode="Markdown")

        except Exception as e:
            logger.log_error(e, {"operation": "handle_purchase_flow"})
            await self._send_error_message(update, "purchase_error")

    async def _handle_audio_request(self, update: Update,
                                  context: CallbackContext,
                                  menu_text: str = None):
        """Handle audio generation requests"""
        try:
            user_id = update.effective_user.id

            # Rate limiting for audio
            if enhanced_rate_limiter.is_rate_limited(user_id, "audio"):
                await update.message.reply_text(
                    "⏰ Subiri kidogo! Umetumia maombi mengi ya sauti. "
                    "Tafadhali jaribu tena baadaye."
                )
                return

            # Show voice options
            keyboard = [
                [InlineKeyboardButton(
                    "🎓 Mshauri (Kawaida)", callback_data="voice_mshauri"
                )],
                [InlineKeyboardButton(
                    "⚡ Haraka", callback_data="voice_haraka"
                )],
                [InlineKeyboardButton(
                    "👴 Mzee", callback_data="voice_mzee"
                )],
                [InlineKeyboardButton(
                    "👦 Kijana", callback_data="voice_kijana"
                )],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            message = (
                "🎵 Chagua aina ya sauti unayotaka kwa masomo ya sauti:"
            )
            await update.message.reply_text(message, reply_markup=reply_markup)

        except Exception as e:
            logger.log_error(e, {"operation": "handle_audio_request"})
            await self._send_error_message(update, "audio_error")

    async def _handle_ai_questions(self, update: Update,
                                 context: CallbackContext,
                                 menu_text: str = None):
        """Handle AI questions request"""
        try:
            message = (
                "🤖 **Maswali ya AI**\n\n"
                "Andika swali lako kuhusu Bitcoin na nitakujibu kwa haraka!"
            )

            await update.message.reply_text(message, parse_mode="Markdown")
            context.user_data["awaiting_ai_question"] = True

        except Exception as e:
            logger.log_error(e, {"operation": "handle_ai_questions"})
            await self._send_error_message(update, "ai_error")

    async def _handle_ai_answer(self, update: Update, context: CallbackContext,
                              text: str):
        """Handle AI answer generation"""
        try:
            context.user_data["awaiting_ai_question"] = False

            # Simple AI response (placeholder - integrate with actual AI service)
            ai_response = (
                f"🤖 Jibu la AI kwa swali lako: '{text}'\n\n"
                f"Hii ni mfano wa jibu la AI. "
                f"Huduma kamili itafanywa hivi karibuni."
            )

            await update.message.reply_text(ai_response, parse_mode="Markdown")

        except Exception as e:
            logger.log_error(e, {"operation": "handle_ai_answer"})
            await self._send_error_message(update, "ai_error")

    async def _handle_feedback_request(self, update: Update,
                                     context: CallbackContext,
                                     menu_text: str = None):
        """Handle feedback request"""
        try:
            message = (
                "📝 **Toa Maoni**\n\n"
                "Tafadhali andika maoni au ushauri wako hapa chini. "
                "Tunathamini mchango wako!"
            )

            await update.message.reply_text(message, parse_mode="Markdown")
            context.user_data["awaiting_feedback"] = True

        except Exception as e:
            logger.log_error(e, {"operation": "handle_feedback_request"})
            await self._send_error_message(update, "feedback_error")

    async def _handle_feedback_submission(self, update: Update,
                                        context: CallbackContext, text: str):
        """Handle feedback submission"""
        try:
            user_id = update.effective_user.id
            context.user_data["awaiting_feedback"] = False

            # Save feedback
            await async_db_manager.save_feedback(user_id, text)

            message = "✅ Asante kwa maoni yako! Tunathamini mchango wako."
            await update.message.reply_text(message)

        except Exception as e:
            logger.log_error(e, {"operation": "handle_feedback_submission"})
            await self._send_error_message(update, "feedback_error")

    async def _handle_main_menu(self, update: Update, context: CallbackContext,
                              menu_text: str = None):
        """Handle main menu return"""
        try:
            user_id = update.effective_user.id

            # Get localized menu
            menu_keyboard = multi_lang_bot.get_menu_keyboard(user_id)
            reply_markup = (
                ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
                if menu_keyboard
                else None
            )

            await update.message.reply_text(
                "🏠 Menyu kuu:",
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.log_error(e, {"operation": "handle_main_menu"})
            await self._send_error_message(update, "menu_error")

    async def _handle_general_message(self, update: Update,
                                    context: CallbackContext, text: str):
        """Handle general messages"""
        try:
            # Provide helpful response
            message = (
                "Samahani, sijui unachomaanisha. "
                "Tafadhali tumia menu au andika /help kupata msaada."
            )

            await update.message.reply_text(message)

        except Exception as e:
            logger.log_error(e, {"operation": "handle_general_message"})
            await self._send_error_message(update, "general_error")

    async def _send_error_message(self, update: Update, error_type: str):
        """Send localized error message"""
        try:
            user_id = update.effective_user.id
            error_message = multi_lang_bot.get_response(user_id, "error_occurred")
            await update.message.reply_text(error_message)
        except Exception:
            # Fallback error message
            await update.message.reply_text("Samahani, kuna tatizo. Jaribu tena.")

    @monitor_performance("handle_callback_query")
    async def handle_callback_query(self, update: Update,
                                  context: CallbackContext):
        """Handle inline keyboard callbacks with validation"""
        try:
            query = update.callback_query
            await query.answer()

            data = query.data

            # Validate callback data
            if not data or len(data) > 100:  # Reasonable limit
                await query.edit_message_text("Invalid callback data")
                return

            # Route callback to appropriate handler
            if data.startswith("quiz_"):
                await self._handle_quiz_callback(update, context, data)
            elif data.startswith("voice_"):
                await self._handle_voice_callback(update, context, data)
            elif data.startswith("audio_lesson_"):
                await self._handle_audio_lesson_callback(update, context, data)
            elif data == "set_price_alert":
                await self._handle_price_alert_callback(update, context)
            elif data == "start_quiz":
                await self._handle_quiz_start(update, context)
            elif data == "main_menu":
                await self._handle_main_menu(update, context)
            else:
                await query.edit_message_text("Chaguo halipatikani.")

        except Exception as e:
            logger.log_error(e, {"operation": "handle_callback_query"})
            await self._send_error_message(update, "callback_error")

    async def _handle_quiz_callback(self, update: Update, context: CallbackContext,
                                  data: str):
        """Handle quiz-related callbacks"""
        try:
            query = update.callback_query

            if data == "quiz_audio":
                # Handle audio request for quiz
                await query.edit_message_text("🎵 Sauti inatengenezwa...")
                return

            # Handle quiz answer
            answer_index = int(data.split("_")[1])
            quiz_state = context.user_data.get('quiz_state')

            if not quiz_state:
                await query.edit_message_text("Quiz state not found")
                return

            questions = quiz_state["questions"]
            current_q = quiz_state["current_question"]

            if current_q >= len(questions):
                await query.edit_message_text("Quiz already completed")
                return

            question = questions[current_q]
            correct_answer = question["answer"]

            # Check answer
            if answer_index == correct_answer:
                quiz_state["score"] += 1
                feedback = "✅ Sahihi!"
            else:
                feedback = (
                    f"❌ Sio sahihi. "
                    f"Jibu sahihi ni: {question['options'][correct_answer]}"
                )

            # Show feedback
            await query.edit_message_text(feedback)

            # Move to next question
            quiz_state["current_question"] += 1
            await asyncio.sleep(2)  # Brief pause

            # Send next question
            await self._send_quiz_question(update, context, query.from_user.id)

        except Exception as e:
            logger.log_error(e, {"operation": "handle_quiz_callback"})

    async def _handle_voice_callback(self, update: Update,
                                   context: CallbackContext, data: str):
        """Handle voice selection callbacks"""
        try:
            query = update.callback_query

            voice_type = data.split("_")[1]
            await query.edit_message_text(
                f"🎵 Sauti ya {voice_type} inatengenezwa..."
            )

            # Here you would implement actual voice generation
            # For now, just show a placeholder message
            await asyncio.sleep(2)
            await query.edit_message_text("🎵 Sauti imetengenezwa! (Placeholder)")

        except Exception as e:
            logger.log_error(e, {"operation": "handle_voice_callback"})

    async def _handle_audio_lesson_callback(self, update: Update,
                                          context: CallbackContext, data: str):
        """Handle audio lesson callbacks"""
        try:
            query = update.callback_query

            await query.edit_message_text("🎵 Somo la sauti linatengenezwa...")

            # Here you would implement actual audio lesson generation
            await asyncio.sleep(2)
            await query.edit_message_text(
                "🎵 Somo la sauti limetengenezwa! (Placeholder)"
            )

        except Exception as e:
            logger.log_error(e, {"operation": "handle_audio_lesson_callback"})

    async def _handle_price_alert_callback(self, update: Update,
                                         context: CallbackContext):
        """Handle price alert setup callbacks"""
        try:
            query = update.callback_query

            await query.edit_message_text(
                "🔔 Kumbuka za bei zitafanywa hivi karibuni. "
                "Tafadhali rudi baadaye."
            )

        except Exception as e:
            logger.log_error(e, {"operation": "handle_price_alert_callback"})

    def setup_handlers(self):
        """Setup all command and message handlers"""
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self._handle_help_request))

        # Callback query handler
        self.app.add_handler(CallbackQueryHandler(self.handle_callback_query))

        # Message handler
        self.app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.handle_message
            )
        )

    async def run(self):
        """Run the bot with proper initialization"""
        try:
            # Initialize database
            await async_db_manager.initialize()

            # Start performance monitoring
            await start_performance_monitoring()

            # Create application
            self.app = Application.builder().token(
                self.config.TELEGRAM_BOT_TOKEN
            ).build()

            # Setup handlers
            self.setup_handlers()

            # Start background tasks
            asyncio.create_task(self._start_background_tasks())

            # Run the bot
            self.logger.info("Clean BitMshauri Bot started successfully!")
            await self.app.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.log_error(e, {"operation": "run_bot"})
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
            logger.log_error(e, {"operation": "start_background_tasks"})

    async def shutdown(self):
        """Graceful shutdown"""
        try:
            if self.app:
                await self.app.stop()
            await async_db_manager.close()
            self.logger.info("Bot shutdown completed")
        except Exception as e:
            logger.log_error(e, {"operation": "shutdown"})


# Create and run bot instance
async def main():
    """Main entry point"""
    bot = CleanBitMshauriBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        await bot.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
