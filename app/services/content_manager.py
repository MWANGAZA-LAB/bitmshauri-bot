"""Dynamic content management system with multi-language support."""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.utils.logger import logger


class ContentManager:
    """Dynamic content management system with multi-language support."""

    def __init__(self):
        """Initialize the content manager."""
        self.content_cache = {}
        self.supported_languages = ["sw", "en"]  # Swahili and English
        self.content_version = "1.0"
        self.content_directory = "app/content"

        # Ensure content directory exists
        os.makedirs(self.content_directory, exist_ok=True)

        # Load content on initialization
        self._load_all_content()

    def _load_all_content(self) -> None:
        """Load all content from files and cache."""
        try:
            for language in self.supported_languages:
                self._load_language_content(language)
            logger.logger.info("Content management system initialized")
        except Exception as e:
            logger.log_error(e, {"operation": "load_all_content"})

    def _load_language_content(self, language: str) -> None:
        """Load content for specific language."""
        try:
            content_file = os.path.join(
                self.content_directory, f"content_{language}.json"
            )

            if os.path.exists(content_file):
                with open(content_file, "r", encoding="utf-8") as f:
                    self.content_cache[language] = json.load(f)
            else:
                # Create default content if file doesn't exist
                self.content_cache[language] = self._get_default_content(
                    language
                )
                self._save_language_content(language)

            logger.logger.info(f"Loaded content for language: {language}")

        except Exception as e:
            logger.log_error(e, {"operation": "load_language_content"})
            # Fallback to default content
            self.content_cache[language] = self._get_default_content(language)

    def _save_language_content(self, language: str) -> None:
        """Save content for specific language to file."""
        try:
            content_file = os.path.join(
                self.content_directory, f"content_{language}.json"
            )

            with open(content_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.content_cache[language],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            logger.logger.info(f"Saved content for language: {language}")

        except Exception as e:
            logger.log_error(e, {"operation": "save_language_content"})

    def _get_default_content(self, language: str) -> Dict[str, Any]:
        """Get default content for language."""
        if language == "sw":
            return {
                "welcome": "Karibu kwenye BitMshauri! Mimi ni msaidizi wako wa Bitcoin.",
                "help_command": (
                    "🆘 **Msaada wa BitMshauri**\n\n"
                    "Mimi ni msaidizi wako wa Bitcoin. Ninaweza kukusaidia:\n\n"
                    "📚 **Masomo ya Bitcoin**\n"
                    "• Kujifunza Bitcoin kwa urahisi\n"
                    "• Masomo ya sauti na maandishi\n"
                    "• Jaribio la maarifa\n\n"
                    "💰 **Hesabu za Bei**\n"
                    "• Bei ya Bitcoin ya sasa\n"
                    "• Kubadilisha pesa kuwa Bitcoin\n"
                    "• Hesabu za faida na hasara\n\n"
                    "💡 **Kidokezo cha Leo**\n"
                    "• Vidokezo vya Bitcoin kila siku\n"
                    "• Habari za soko\n\n"
                    "Tumia menu hapa chini au andika swali lako!"
                ),
                "error_occurred": (
                    "Samahani, kuna tatizo kiufundi. "
                    "Tafadhali jaribu tena baadaye."
                ),
                "lessons": {
                    "intro": {
                        "title": "Utangulizi wa Bitcoin",
                        "content": (
                            "🌟 **Karibu kwenye BitMshauri!**\n\n"
                            "Bitcoin ni pesa ya kidijitali ambayo inaweza "
                            "kutumika kwa njia ya P2P (peer-to-peer) bila "
                            "kuhitaji benki au mamlaka ya kati.\n\n"
                            "**Faida za Bitcoin:**\n"
                            "• Usalama na uwazi\n"
                            "• Haraka na rahisi\n"
                            "• Bei ya kimataifa\n"
                            "• Hifadhi ya thamani\n\n"
                            "Anza kujifunza Bitcoin leo!"
                        ),
                    },
                    "kwa_nini_bitcoin": {
                        "title": "Kwa Nini Bitcoin?",
                        "content": (
                            "🤔 **Kwa Nini Bitcoin?**\n\n"
                            "Bitcoin ina faida nyingi zaidi ya pesa za kawaida:\n\n"
                            "**1. Uhuru wa Kifedha**\n"
                            "• Huna mamlaka ya kati\n"
                            "• Unaweza kutumia wakati wowote\n"
                            "• Hakuna mipaka ya nchi\n\n"
                            "**2. Usalama**\n"
                            "• Teknolojia ya blockchain\n"
                            "• Siri ya kibinafsi\n"
                            "• Hakuna uwezo wa kufanywa bandia\n\n"
                            "**3. Bei ya Kimataifa**\n"
                            "• Bei moja duniani kote\n"
                            "• Hakuna malipo ya uhamisho\n"
                            "• Haraka zaidi ya benki\n\n"
                            "Bitcoin ni siku za usoni za pesa!"
                        ),
                    },
                },
                "menu": [
                    ["🌍 Kwa Nini Bitcoin?", "📚 Bitcoin ni nini?"],
                    ["💰 Bei ya Bitcoin", "📝 Jaribio la Bitcoin"],
                    ["🛒 Nunua Bitcoin", "💡 Kidokezo cha Leo"],
                    ["ℹ️ Msaada Zaidi", "📝 Toa Maoni"],
                ],
            }
        else:  # English
            return {
                "welcome": "Welcome to BitMshauri! I'm your Bitcoin assistant.",
                "help_command": (
                    "🆘 **BitMshauri Help**\n\n"
                    "I'm your Bitcoin assistant. I can help you with:\n\n"
                    "📚 **Bitcoin Learning**\n"
                    "• Learn Bitcoin easily\n"
                    "• Audio and text lessons\n"
                    "• Knowledge quizzes\n\n"
                    "💰 **Price Calculations**\n"
                    "• Current Bitcoin price\n"
                    "• Convert money to Bitcoin\n"
                    "• Profit and loss calculations\n\n"
                    "💡 **Daily Tips**\n"
                    "• Daily Bitcoin tips\n"
                    "• Market news\n\n"
                    "Use the menu below or ask me a question!"
                ),
                "error_occurred": (
                    "Sorry, there's a technical issue. "
                    "Please try again later."
                ),
                "lessons": {
                    "intro": {
                        "title": "Bitcoin Introduction",
                        "content": (
                            "🌟 **Welcome to BitMshauri!**\n\n"
                            "Bitcoin is digital money that can be used "
                            "peer-to-peer without needing a bank or "
                            "central authority.\n\n"
                            "**Bitcoin Benefits:**\n"
                            "• Security and transparency\n"
                            "• Fast and easy\n"
                            "• Global price\n"
                            "• Store of value\n\n"
                            "Start learning Bitcoin today!"
                        ),
                    },
                    "why_bitcoin": {
                        "title": "Why Bitcoin?",
                        "content": (
                            "🤔 **Why Bitcoin?**\n\n"
                            "Bitcoin has many advantages over regular money:\n\n"
                            "**1. Financial Freedom**\n"
                            "• No central authority\n"
                            "• Use anytime\n"
                            "• No country borders\n\n"
                            "**2. Security**\n"
                            "• Blockchain technology\n"
                            "• Personal privacy\n"
                            "• Cannot be counterfeited\n\n"
                            "**3. Global Price**\n"
                            "• Same price worldwide\n"
                            "• No transfer fees\n"
                            "• Faster than banks\n\n"
                            "Bitcoin is the future of money!"
                        ),
                    },
                },
                "menu": [
                    ["🌍 Why Bitcoin?", "📚 What is Bitcoin?"],
                    ["💰 Bitcoin Price", "📝 Bitcoin Quiz"],
                    ["🛒 Buy Bitcoin", "💡 Daily Tip"],
                    ["ℹ️ More Help", "📝 Feedback"],
                ],
            }

    def get_content(
        self, language: str, content_type: str, key: str = None
    ) -> Optional[Any]:
        """Get content for specific language and type."""
        try:
            if language not in self.content_cache:
                language = "sw"  # Fallback to Swahili

            content = self.content_cache.get(language, {})

            if content_type == "lesson" and key:
                return content.get("lessons", {}).get(key)
            elif content_type == "response":
                return content.get(key)
            elif content_type == "menu":
                return content.get("menu", [])
            else:
                return content.get(content_type)

        except Exception as e:
            logger.log_error(e, {"operation": "get_content"})
            return None

    def get_lesson(self, language: str, lesson_key: str) -> Optional[Dict[str, Any]]:
        """Get specific lesson content."""
        return self.get_content(language, "lesson", lesson_key)

    def get_response(self, language: str, response_key: str) -> Optional[str]:
        """Get specific response text."""
        return self.get_content(language, "response", response_key)

    def get_menu_keyboard(self, language: str) -> List[List[str]]:
        """Get menu keyboard for language."""
        menu = self.get_content(language, "menu")
        return menu if menu else []

    def update_content(
        self, language: str, content_type: str, key: str, value: Any
    ) -> bool:
        """Update content dynamically."""
        try:
            if language not in self.content_cache:
                self.content_cache[language] = {}

            if content_type == "lesson":
                if "lessons" not in self.content_cache[language]:
                    self.content_cache[language]["lessons"] = {}
                self.content_cache[language]["lessons"][key] = value
            elif content_type == "response":
                self.content_cache[language][key] = value
            elif content_type == "menu":
                self.content_cache[language]["menu"] = value

            # Save to file
            self._save_language_content(language)

            logger.logger.info(
                f"Updated content: {language}/{content_type}/{key}"
            )
            return True

        except Exception as e:
            logger.log_error(e, {"operation": "update_content"})
            return False

    def add_lesson(
        self, language: str, lesson_key: str, title: str, content: str
    ) -> bool:
        """Add new lesson."""
        lesson_data = {
            "title": title,
            "content": content,
            "created_at": datetime.now().isoformat(),
        }
        return self.update_content(language, "lesson", lesson_key, lesson_data)

    def get_all_lessons(self, language: str) -> Dict[str, Any]:
        """Get all lessons for language."""
        return self.get_content(language, "lesson") or {}

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self.supported_languages.copy()

    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported."""
        return language in self.supported_languages

    def get_content_stats(self) -> Dict[str, Any]:
        """Get content statistics."""
        try:
            stats = {
                "supported_languages": len(self.supported_languages),
                "languages": {},
                "total_lessons": 0,
                "content_version": self.content_version,
            }

            for language in self.supported_languages:
                content = self.content_cache.get(language, {})
                lessons = content.get("lessons", {})
                stats["languages"][language] = {
                    "lessons_count": len(lessons),
                    "has_menu": "menu" in content,
                    "has_responses": any(
                        key in content
                        for key in ["welcome", "help_command", "error_occurred"]
                    ),
                }
                stats["total_lessons"] += len(lessons)

            return stats

        except Exception as e:
            logger.log_error(e, {"operation": "get_content_stats"})
            return {}

    def reload_content(self, language: str = None) -> bool:
        """Reload content from files."""
        try:
            if language:
                self._load_language_content(language)
            else:
                self._load_all_content()

            logger.logger.info(f"Reloaded content for {language or 'all languages'}")
            return True

        except Exception as e:
            logger.log_error(e, {"operation": "reload_content"})
            return False

    def backup_content(self, backup_path: str = None) -> bool:
        """Backup all content to file."""
        try:
            if not backup_path:
                backup_path = f"content_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "backup_timestamp": datetime.now().isoformat(),
                        "content_version": self.content_version,
                        "content": self.content_cache,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            logger.logger.info(f"Content backed up to: {backup_path}")
            return True

        except Exception as e:
            logger.log_error(e, {"operation": "backup_content"})
            return False

    def restore_content(self, backup_path: str) -> bool:
        """Restore content from backup file."""
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)

            self.content_cache = backup_data.get("content", {})
            self.content_version = backup_data.get("content_version", "1.0")

            # Save restored content
            for language in self.supported_languages:
                if language in self.content_cache:
                    self._save_language_content(language)

            logger.logger.info(f"Content restored from: {backup_path}")
            return True

        except Exception as e:
            logger.log_error(e, {"operation": "restore_content"})
            return False


# Global content manager instance
content_manager = ContentManager()