import re
from typing import Dict, List, Optional, Tuple
from app.utils.logger import logger
from app.services.content_manager import content_manager


class LanguageDetector:
    """Automatic language detection for user messages"""

    def __init__(self):
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
        """Detect language from user text"""
        try:
            if not text or len(text.strip()) < 2:
                return "sw"  # Default to Swahili

            text_clean = text.lower().strip()

            # Count matches for each language
            swahili_matches = len(self.swahili_regex.findall(text_clean))
            english_matches = len(self.english_regex.findall(text_clean))

            # Special cases for common greetings
            if any(
                word in text_clean
                for word in ["habari", "mambo", "hujambo", "niaje"]
            ):
                return "sw"
            elif any(word in text_clean for word in ["hello", "hi", "hey"]):
                return "en"

            # Determine language based on match count
            if swahili_matches > english_matches:
                return "sw"
            elif english_matches > swahili_matches:
                return "en"
            else:
                # Default to Swahili if no clear preference
                return "sw"

        except Exception as e:
            logger.log_error(e, {"operation": "detect_language", "text": text})
            return "sw"  # Default fallback


class MultiLanguageBot:
    """Multi-language bot handler with dynamic content switching"""

    def __init__(self):
        self.language_detector = LanguageDetector()
        self.user_languages = {}  # Store user language preferences
        self.supported_languages = ["sw", "en"]

        # Language-specific response templates
        self.response_templates = {
            "sw": {
                "language_set": "Lugha imebadilishwa kuwa Kiswahili! 🇹🇿",
                "language_detected": "Ninaona unatumia Kiswahili. Nitaendelea kwa Kiswahili!",
                "welcome": "Habari! Mimi ni BitMshauri, msaidizi wako wa Bitcoin.",
                "help_command": "/sw - Badili kwenda Kiswahili\n/en - Switch to English\n/detect - Gundua lugha kiotomatiki",
                "unknown_command": "Samahani, sijui amri hiyo. Andika /help kupata msaada.",
                "error_occurred": "Samahani, kuna tatizo. Jaribu tena.",
                "processing": "Nalinganisha...",
                "done": "Imemaliza!",
            },
            "en": {
                "language_set": "Language changed to English! 🇺🇸",
                "language_detected": "I see you're using English. I'll continue in English!",
                "welcome": "Hello! I'm BitMshauri, your Bitcoin assistant.",
                "help_command": "/sw - Badili kwenda Kiswahili\n/en - Switch to English\n/detect - Auto-detect language",
                "unknown_command": "Sorry, I don't understand that command. Type /help for assistance.",
                "error_occurred": "Sorry, there was an error. Please try again.",
                "processing": "Processing...",
                "done": "Done!",
            },
        }

    def set_user_language(self, user_id: int, language: str) -> bool:
        """Set language preference for user"""
        try:
            if language in self.supported_languages:
                self.user_languages[user_id] = language
                logger.log_user_action(
                    user_id, "language_set", {"language": language}
                )
                return True
            return False
        except Exception as e:
            logger.log_error(e, {"operation": "set_user_language"})
            return False

    def get_user_language(
        self, user_id: int, auto_detect_text: str = None
    ) -> str:
        """Get user's language preference or detect from text"""
        try:
            # Check if user has explicit preference
            if user_id in self.user_languages:
                return self.user_languages[user_id]

            # Auto-detect if text provided
            if auto_detect_text:
                detected_lang = self.language_detector.detect_language(
                    auto_detect_text
                )
                # Store detected language as preference
                self.user_languages[user_id] = detected_lang
                return detected_lang

            # Default to Swahili
            return "sw"

        except Exception as e:
            logger.log_error(e, {"operation": "get_user_language"})
            return "sw"

    def get_response(self, user_id: int, template_key: str, **kwargs) -> str:
        """Get localized response for user"""
        try:
            language = self.get_user_language(user_id)
            template = self.response_templates.get(language, {}).get(
                template_key, ""
            )

            if kwargs:
                return template.format(**kwargs)
            return template

        except Exception as e:
            logger.log_error(e, {"operation": "get_response"})
            return (
                self.response_templates["sw"][template_key]
                if template_key in self.response_templates["sw"]
                else ""
            )

    def get_content(
        self,
        user_id: int,
        content_type: str,
        content_key: str = None,
        auto_detect_text: str = None,
    ):
        """Get localized content for user"""
        try:
            language = self.get_user_language(user_id, auto_detect_text)

            if content_key:
                return content_manager.get_content(
                    content_type, content_key, language
                )
            else:
                return content_manager.get_content(content_type, "", language)

        except Exception as e:
            logger.log_error(e, {"operation": "get_content"})
            return None

    def get_lesson(
        self, user_id: int, lesson_key: str, auto_detect_text: str = None
    ):
        """Get localized lesson"""
        return self.get_content(
            user_id, "lessons", lesson_key, auto_detect_text
        )

    def get_quiz(
        self, user_id: int, quiz_name: str, auto_detect_text: str = None
    ):
        """Get localized quiz"""
        return self.get_content(
            user_id, "quizzes", quiz_name, auto_detect_text
        )

    def get_menu_keyboard(self, user_id: int, auto_detect_text: str = None):
        """Get localized menu keyboard"""
        return self.get_content(
            user_id, "menu_keyboard", None, auto_detect_text
        )

    def get_secondary_menu_keyboard(
        self, user_id: int, auto_detect_text: str = None
    ):
        """Get localized secondary menu keyboard"""
        return self.get_content(
            user_id, "secondary_menu_keyboard", None, auto_detect_text
        )

    def get_daily_tips(self, user_id: int, auto_detect_text: str = None):
        """Get localized daily tips"""
        return self.get_content(user_id, "daily_tips", None, auto_detect_text)

    def format_price_message(self, user_id: int, price_data: Dict) -> str:
        """Format price message in user's language"""
        try:
            language = self.get_user_language(user_id)

            if language == "sw":
                return (
                    f"💰 *Bei ya Bitcoin Sasa:*\n"
                    f"💵 ${price_data.get('usd', 'N/A'):,.2f}\n"
                    f"🏛️ TSh {price_data.get('tzs', 'N/A'):,.0f}\n"
                    f"📊 Mabadiliko ya siku 24: {price_data.get('usd_24h_change', 0):.2f}%\n"
                    f"🕐 Imesasishwa: {price_data.get('last_updated', 'N/A')}"
                )
            else:
                return (
                    f"💰 *Current Bitcoin Price:*\n"
                    f"💵 ${price_data.get('usd', 'N/A'):,.2f}\n"
                    f"🏛️ TSh {price_data.get('tzs', 'N/A'):,.0f}\n"
                    f"📊 24h Change: {price_data.get('usd_24h_change', 0):.2f}%\n"
                    f"🕐 Last Updated: {price_data.get('last_updated', 'N/A')}"
                )

        except Exception as e:
            logger.log_error(e, {"operation": "format_price_message"})
            return "Bei ya Bitcoin haipatikani kwa sasa."

    def format_calculation_result(
        self, user_id: int, calculation_result: Dict
    ) -> str:
        """Format calculation result in user's language"""
        try:
            language = self.get_user_language(user_id)

            if language == "sw":
                return (
                    f"🧮 *Mahesabu ya Bitcoin:*\n"
                    f"📊 {calculation_result.get('original_amount', 0):,.2f} "
                    f"{calculation_result.get('from_currency', '').upper()} = "
                    f"{calculation_result.get('converted_amount', 0):,.8f} "
                    f"{calculation_result.get('to_currency', '').upper()}\n"
                    f"💰 Bei ya sasa: ${calculation_result.get('current_price', 0):,.2f}\n"
                    f"🕐 {calculation_result.get('timestamp', '')}"
                )
            else:
                return (
                    f"🧮 *Bitcoin Calculation:*\n"
                    f"📊 {calculation_result.get('original_amount', 0):,.2f} "
                    f"{calculation_result.get('from_currency', '').upper()} = "
                    f"{calculation_result.get('converted_amount', 0):,.8f} "
                    f"{calculation_result.get('to_currency', '').upper()}\n"
                    f"💰 Current price: ${calculation_result.get('current_price', 0):,.2f}\n"
                    f"🕐 {calculation_result.get('timestamp', '')}"
                )

        except Exception as e:
            logger.log_error(e, {"operation": "format_calculation_result"})
            return "Mahesabu hayawezi kukamilika."

    def get_language_stats(self) -> Dict:
        """Get language usage statistics"""
        try:
            stats = {
                "total_users": len(self.user_languages),
                "language_distribution": {},
                "supported_languages": self.supported_languages,
            }

            for language in self.supported_languages:
                count = sum(
                    1
                    for lang in self.user_languages.values()
                    if lang == language
                )
                stats["language_distribution"][language] = count

            return stats

        except Exception as e:
            logger.log_error(e, {"operation": "get_language_stats"})
            return {}


# Global multi-language bot instance
multi_lang_bot = MultiLanguageBot()


# Helper functions for easy integration
def get_user_language(user_id: int, auto_detect_text: str = None) -> str:
    """Get user's language preference"""
    return multi_lang_bot.get_user_language(user_id, auto_detect_text)


def set_user_language(user_id: int, language: str) -> bool:
    """Set user's language preference"""
    return multi_lang_bot.set_user_language(user_id, language)


def get_localized_response(user_id: int, template_key: str, **kwargs) -> str:
    """Get localized response"""
    return multi_lang_bot.get_response(user_id, template_key, **kwargs)


def get_localized_content(
    user_id: int,
    content_type: str,
    content_key: str = None,
    auto_detect_text: str = None,
):
    """Get localized content"""
    return multi_lang_bot.get_content(
        user_id, content_type, content_key, auto_detect_text
    )
