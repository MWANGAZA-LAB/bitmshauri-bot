"""Multi-language support system for BitMshauri Bot."""

import re
from typing import Dict, List, Optional, Tuple

from app.services.content_manager import content_manager
from app.utils.logger import logger


class LanguageDetector:
    """Automatic language detection for user messages."""

    def __init__(self):
        """Initialize the language detector."""
        # Swahili keywords and patterns
        self.swahili_patterns = [
            # Common Swahili words
            r"\b(habari|mambo|poa|sawa|hujambo|sijambo|niaje|vipi)\b",
            r"\b(asante|karibu|pole|hongera|baadaye|tutaonana)\b",
            r"\b(nina|una|ana|tuna|mna|wana|si|ndio|hapana)\b",
            r"\b(nini|nani|lini|wapi|gani|namna|jinsi)\b",
            r"\b(bitcoin|pesa|fedha|dola|shilingi)\b",
            # Swahili phrases
            r"\b(kwa nini|vipi|iko wapi|ni nini|si nini)\b",
            r"\b(naomba|nataka|nahitaji|naweza|siwezi)\b",
        ]

        # English keywords and patterns
        self.english_patterns = [
            r"\b(hello|hi|hey|good|morning|afternoon|evening|night)\b",
            r"\b(please|thank|sorry|excuse|welcome|goodbye)\b",
            r"\b(what|when|where|who|how|why|which)\b",
            r"\b(bitcoin|money|price|buy|sell|wallet|crypto)\b",
            r"\b(help|need|want|can|could|would|should)\b",
        ]

        self.swahili_regex = re.compile(
            "|".join(self.swahili_patterns), re.IGNORECASE
        )
        self.english_regex = re.compile(
            "|".join(self.english_patterns), re.IGNORECASE
        )

    def detect_language(self, text: str) -> str:
        """Detect language from user text."""
        try:
            if not text or len(text.strip()) < 2:
                return "sw"  # Default to Swahili

            text_clean = text.lower().strip()

            # Count matches for each language
            swahili_matches = len(self.swahili_regex.findall(text_clean))
            english_matches = len(self.english_regex.findall(text_clean))

            # Determine language based on matches
            if swahili_matches > english_matches:
                return "sw"
            elif english_matches > swahili_matches:
                return "en"
            else:
                # If equal or no matches, check for specific indicators
                if any(word in text_clean for word in ["bitcoin", "btc", "crypto"]):
                    return "en"  # Default to English for crypto terms
                return "sw"  # Default to Swahili

        except Exception as e:
            logger.log_error(e, {"operation": "detect_language"})
            return "sw"  # Fallback to Swahili


class MultiLanguageBot:
    """Multi-language bot with dynamic content switching."""

    def __init__(self):
        """Initialize the multi-language bot."""
        self.language_detector = LanguageDetector()
        self.user_languages = {}  # Cache user language preferences
        self.content_manager = content_manager

    def get_user_language(self, user_id: int, message_text: str = None) -> str:
        """Get user's preferred language with auto-detection."""
        try:
            # Check if user has cached language preference
            if user_id in self.user_languages:
                return self.user_languages[user_id]

            # Auto-detect from message if provided
            if message_text:
                detected_language = self.language_detector.detect_language(
                    message_text
                )
                self.user_languages[user_id] = detected_language
                return detected_language

            # Default to Swahili
            self.user_languages[user_id] = "sw"
            return "sw"

        except Exception as e:
            logger.log_error(e, {"operation": "get_user_language"})
            return "sw"

    def set_user_language(self, user_id: int, language: str) -> bool:
        """Set user's preferred language."""
        try:
            if language in ["sw", "en"]:
                self.user_languages[user_id] = language
                logger.log_user_action(
                    user_id, "language_changed", {"language": language}
                )
                return True
            return False

        except Exception as e:
            logger.log_error(e, {"operation": "set_user_language"})
            return False

    def get_response(self, user_id: int, response_key: str) -> str:
        """Get localized response for user."""
        try:
            language = self.get_user_language(user_id)
            response = self.content_manager.get_response(language, response_key)

            if response:
                return response

            # Fallback to Swahili if not found
            if language != "sw":
                response = self.content_manager.get_response("sw", response_key)
                if response:
                    return response

            # Final fallback
            return "Samahani, kuna tatizo kiufundi. Jaribu tena."

        except Exception as e:
            logger.log_error(e, {"operation": "get_response"})
            return "Samahani, kuna tatizo kiufundi. Jaribu tena."

    def get_lesson(self, user_id: int, lesson_key: str) -> Optional[Dict]:
        """Get localized lesson for user."""
        try:
            language = self.get_user_language(user_id)
            lesson = self.content_manager.get_lesson(language, lesson_key)

            if lesson:
                return lesson

            # Fallback to Swahili if not found
            if language != "sw":
                lesson = self.content_manager.get_lesson("sw", lesson_key)
                if lesson:
                    return lesson

            return None

        except Exception as e:
            logger.log_error(e, {"operation": "get_lesson"})
            return None

    def get_menu_keyboard(self, user_id: int) -> List[List[str]]:
        """Get localized menu keyboard for user."""
        try:
            language = self.get_user_language(user_id)
            menu = self.content_manager.get_menu_keyboard(language)

            if menu:
                return menu

            # Fallback to Swahili if not found
            if language != "sw":
                menu = self.content_manager.get_menu_keyboard("sw")
                if menu:
                    return menu

            # Final fallback
            return [
                ["🌍 Kwa Nini Bitcoin?", "📚 Bitcoin ni nini?"],
                ["💰 Bei ya Bitcoin", "📝 Jaribio la Bitcoin"],
                ["ℹ️ Msaada Zaidi"],
            ]

        except Exception as e:
            logger.log_error(e, {"operation": "get_menu_keyboard"})
            return []

    def format_price_message(self, user_id: int, price_data: Dict) -> str:
        """Format price message in user's language."""
        try:
            language = self.get_user_language(user_id)

            if language == "sw":
                return (
                    f"💰 **Bei ya Bitcoin**\n\n"
                    f"🇺🇸 USD: ${price_data.get('usd', 0):,.2f}\n"
                    f"🇰🇪 KES: KSh {price_data.get('kes', 0):,.2f}\n\n"
                    f"📈 Mabadiliko (24h): {price_data.get('price_change_24h', 0):+.2f}%\n"
                    f"📊 Soko: ${price_data.get('market_cap', 0):,.0f}\n\n"
                    f"⏰ Muda: {price_data.get('timestamp', 'N/A')}"
                )
            else:  # English
                return (
                    f"💰 **Bitcoin Price**\n\n"
                    f"🇺🇸 USD: ${price_data.get('usd', 0):,.2f}\n"
                    f"🇰🇪 KES: KSh {price_data.get('kes', 0):,.2f}\n\n"
                    f"📈 Change (24h): {price_data.get('price_change_24h', 0):+.2f}%\n"
                    f"📊 Market Cap: ${price_data.get('market_cap', 0):,.0f}\n\n"
                    f"⏰ Time: {price_data.get('timestamp', 'N/A')}"
                )

        except Exception as e:
            logger.log_error(e, {"operation": "format_price_message"})
            return "Samahani, bei haipatikani kwa sasa."

    def format_calculation_result(
        self, user_id: int, result: Dict
    ) -> str:
        """Format calculation result in user's language."""
        try:
            language = self.get_user_language(user_id)

            if language == "sw":
                return (
                    f"💰 **Hesabu ya Bitcoin**\n\n"
                    f"{result.get('formatted', '')}\n\n"
                    f"📊 Bei ya Bitcoin: ${result.get('btc_price_usd', 0):,.2f}\n"
                    f"📈 Mabadiliko (24h): {result.get('price_change_24h', 0):+.2f}%\n"
                    f"💡 *Kidokezo: Bei ya Bitcoin inabadilika kila wakati*"
                )
            else:  # English
                return (
                    f"💰 **Bitcoin Calculation**\n\n"
                    f"{result.get('formatted', '')}\n\n"
                    f"📊 Bitcoin Price: ${result.get('btc_price_usd', 0):,.2f}\n"
                    f"📈 Change (24h): {result.get('price_change_24h', 0):+.2f}%\n"
                    f"💡 *Tip: Bitcoin price changes constantly*"
                )

        except Exception as e:
            logger.log_error(e, {"operation": "format_calculation_result"})
            return "Samahani, sijaweza kufanya hesabu hiyo."

    def get_quiz(self, user_id: int, quiz_name: str) -> List[Dict]:
        """Get localized quiz for user."""
        try:
            language = self.get_user_language(user_id)

            # Sample quiz questions (in real implementation, load from content manager)
            if language == "sw":
                return [
                    {
                        "question": "Bitcoin ni nini?",
                        "options": [
                            "Pesa ya kidijitali",
                            "Benki ya kimataifa",
                            "Kampuni ya teknolojia",
                            "Mfumo wa malipo ya benki",
                        ],
                        "answer": 0,
                        "explanation": "Bitcoin ni pesa ya kidijitali ambayo inatumia teknolojia ya blockchain.",
                    },
                    {
                        "question": "Blockchain ni nini?",
                        "options": [
                            "Aina ya benki",
                            "Teknolojia ya kuhifadhi taarifa",
                            "Mfumo wa malipo",
                            "Kampuni ya teknolojia",
                        ],
                        "answer": 1,
                        "explanation": "Blockchain ni teknolojia ya kuhifadhi taarifa kwa njia ya usalama na uwazi.",
                    },
                ]
            else:  # English
                return [
                    {
                        "question": "What is Bitcoin?",
                        "options": [
                            "Digital currency",
                            "International bank",
                            "Technology company",
                            "Bank payment system",
                        ],
                        "answer": 0,
                        "explanation": "Bitcoin is a digital currency that uses blockchain technology.",
                    },
                    {
                        "question": "What is blockchain?",
                        "options": [
                            "Type of bank",
                            "Data storage technology",
                            "Payment system",
                            "Technology company",
                        ],
                        "answer": 1,
                        "explanation": "Blockchain is a secure and transparent data storage technology.",
                    },
                ]

        except Exception as e:
            logger.log_error(e, {"operation": "get_quiz"})
            return []

    def get_daily_tips(self, user_id: int) -> List[str]:
        """Get localized daily tips for user."""
        try:
            language = self.get_user_language(user_id)

            if language == "sw":
                return [
                    "💡 Bitcoin ni hifadhi ya thamani ya muda mrefu.",
                    "💡 Usiweke pesa zote katika Bitcoin - tofautisha uwekezaji wako.",
                    "💡 Jifunze kuhusu usalama wa pochi kabla ya kununua Bitcoin.",
                    "💡 Bei ya Bitcoin inabadilika kila wakati - usiogope mabadiliko.",
                    "💡 Bitcoin ni teknolojia ya usoni - jifunze zaidi kuhusu blockchain.",
                ]
            else:  # English
                return [
                    "💡 Bitcoin is a long-term store of value.",
                    "💡 Don't put all your money in Bitcoin - diversify your investments.",
                    "💡 Learn about wallet security before buying Bitcoin.",
                    "💡 Bitcoin price changes constantly - don't fear the volatility.",
                    "💡 Bitcoin is future technology - learn more about blockchain.",
                ]

        except Exception as e:
            logger.log_error(e, {"operation": "get_daily_tips"})
            return []

    def get_language_switcher_message(self, user_id: int) -> str:
        """Get language switcher message."""
        try:
            current_language = self.get_user_language(user_id)

            if current_language == "sw":
                return (
                    "🌍 **Badilisha Lugha**\n\n"
                    "Lugha yako ya sasa: Kiswahili\n\n"
                    "Chagua lugha unayotaka kutumia:\n"
                    "• 🇹🇿 Kiswahili (sasa)\n"
                    "• 🇺🇸 English\n\n"
                    "Andika 'English' au 'Kiswahili' kubadilisha lugha."
                )
            else:
                return (
                    "🌍 **Change Language**\n\n"
                    "Your current language: English\n\n"
                    "Choose the language you want to use:\n"
                    "• 🇹🇿 Kiswahili\n"
                    "• 🇺🇸 English (current)\n\n"
                    "Type 'English' or 'Kiswahili' to change language."
                )

        except Exception as e:
            logger.log_error(e, {"operation": "get_language_switcher_message"})
            return "Samahani, kuna tatizo kiufundi. Jaribu tena."

    def handle_language_switch(self, user_id: int, text: str) -> Tuple[bool, str]:
        """Handle language switching request."""
        try:
            text_lower = text.lower().strip()

            if text_lower in ["english", "en", "inglés"]:
                if self.set_user_language(user_id, "en"):
                    return True, "Language changed to English! 🇺🇸"
                else:
                    return False, "Failed to change language."

            elif text_lower in ["kiswahili", "swahili", "sw", "kiswahili"]:
                if self.set_user_language(user_id, "sw"):
                    return True, "Lugha imebadilishwa kuwa Kiswahili! 🇹🇿"
                else:
                    return False, "Imeshindwa kubadilisha lugha."

            return False, "Invalid language option."

        except Exception as e:
            logger.log_error(e, {"operation": "handle_language_switch"})
            return False, "Samahani, kuna tatizo kiufundi. Jaribu tena."

    def get_user_stats(self) -> Dict[str, int]:
        """Get user language statistics."""
        try:
            stats = {"sw": 0, "en": 0, "total": 0}

            for language in self.user_languages.values():
                if language in stats:
                    stats[language] += 1
                stats["total"] += 1

            return stats

        except Exception as e:
            logger.log_error(e, {"operation": "get_user_stats"})
            return {"sw": 0, "en": 0, "total": 0}


# Global multi-language bot instance
multi_lang_bot = MultiLanguageBot()