import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.utils.logger import logger

class ContentManager:
    """Dynamic content management system with multi-language support"""
    
    def __init__(self):
        self.content_cache = {}
        self.supported_languages = ['sw', 'en']  # Swahili and English
        self.content_version = "1.0"
        self.content_directory = "app/content"
        
        # Ensure content directory exists
        os.makedirs(self.content_directory, exist_ok=True)
        
        # Load content on initialization
        self._load_all_content()
    
    def _load_all_content(self):
        """Load all content from files and cache"""
        try:
            for language in self.supported_languages:
                self._load_language_content(language)
            logger.logger.info("Content management system initialized")
        except Exception as e:
            logger.log_error(e, {"operation": "load_all_content"})
    
    def _load_language_content(self, language: str):
        """Load content for specific language"""
        try:
            content_file = os.path.join(self.content_directory, f"content_{language}.json")
            
            if os.path.exists(content_file):
                with open(content_file, 'r', encoding='utf-8') as f:
                    self.content_cache[language] = json.load(f)
            else:
                # Create default content if file doesn't exist
                self.content_cache[language] = self._get_default_content(language)
                self._save_language_content(language)
            
            logger.logger.info(f"Loaded content for language: {language}")
            
        except Exception as e:
            logger.log_error(e, {"operation": "load_language_content", "language": language})
            # Fallback to default content
            self.content_cache[language] = self._get_default_content(language)
    
    def _save_language_content(self, language: str):
        """Save content for specific language"""
        try:
            content_file = os.path.join(self.content_directory, f"content_{language}.json")
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(self.content_cache[language], f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.log_error(e, {"operation": "save_language_content", "language": language})
    
    def _get_default_content(self, language: str) -> Dict:
        """Get default content for language"""
        if language == 'sw':
            return self._get_swahili_content()
        elif language == 'en':
            return self._get_english_content()
        else:
            return {}
    
    def _get_swahili_content(self) -> Dict:
        """Default Swahili content"""
        return {
            "lessons": {
                "intro": {
                    "title": "Utangulizi wa BitMshauri",
                    "content": "Habari! Mimi ni BitMshauri, msaidizi wako wa Bitcoin kwa Kiswahili. Chagua moja ya chaguo hapa chini:",
                    "category": "basic",
                    "duration_minutes": 2,
                    "difficulty": "beginner"
                },
                "kwa_nini_bitcoin": {
                    "title": "Kwa Nini Bitcoin?",
                    "content": (
                        "🌍 *Kwa Nini Utumie Bitcoin?*\n\n"
                        "Watu wengi hawajui kwanini Bitcoin ni muhimu. Hapa kuna sababu kuu:\n\n"
                        "🔐 *Uhuru wa Fedha:*\n"
                        "- Bitcoin haidhibitiwi na benki au serikali\n"
                        "- Wewe pekee unadhibiti pesa zako\n\n"
                        "💸 *Malipo ya Haraka na Nafuu:*\n"
                        "- Tuma pesa kwa mtu yeyote duniani papo hapo\n"
                        "- Gharama ni ndogo sana ukilinganisha na benki au M-Pesa\n\n"
                        "📉 *Ulinzi dhidi ya mfumuko wa bei:*\n"
                        "- Bitcoin haitolewi kiholela kama sarafu za kawaida\n"
                        "- Ni 21 milioni tu zitawahi kuwepo\n\n"
                        "📱 *Ufikiaji kwa Wote:*\n"
                        "- Hata ukiwa kijijini, unaweza kutumia Bitcoin na simu ya mkononi\n\n"
                        "_Bitcoin ni njia mpya ya kifedha, inayokupa uhuru, usalama, na uwezo wa kushiriki katika uchumi wa kidijitali._"
                    ),
                    "category": "basic",
                    "duration_minutes": 5,
                    "difficulty": "beginner"
                }
            },
            "quizzes": {
                "msingi": [
                    {
                        "question": "Bitcoin inasimamiwa na nani?",
                        "options": ["Benki Kuu", "Serikali", "Hakuna mtu", "Kampuni ya Bitcoin"],
                        "answer": 2,
                        "explanation": "Bitcoin ni mtandao wa peer-to-peer usiosimamiwa na mtu au taasisi yoyote."
                    }
                ]
            },
            "daily_tips": [
                "💡 Bitcoin ni sarafu ya kidijitali ya kwanza ulimwenguni",
                "🔐 Hifadhi seed phrase yako kwa usalama mkubwa",
                "📚 Soma na ujifunze kabla ya kuwekeza"
            ],
            "menu_keyboard": [
                ["🌍 Kwa Nini Bitcoin?", "📚 Bitcoin ni nini?"],
                ["💰 Bei ya Bitcoin", "📝 Jaribio la Bitcoin"],
                ["🛒 Nunua Bitcoin", "💡 Kidokezo cha Leo"],
                ["ℹ️ Msaada Zaidi", "📝 Toa Maoni"]
            ],
            "secondary_menu_keyboard": [
                ["🔗 P2P Inafanyaje", "👛 Aina za Pochi"],
                ["🔒 Usalama wa Pochi", "⚠️ Kupoteza Ufunguo"],
                ["📱 Matumizi ya Pochi", "⚖️ Faida na Hatari"],
                ["🔐 Teknolojia ya Blockchain", "❓ Maswali Mengine"],
                ["🎵 Masomo ya Sauti", "⬅️ Rudi Mwanzo"]
            ]
        }
    
    def _get_english_content(self) -> Dict:
        """Default English content"""
        return {
            "lessons": {
                "intro": {
                    "title": "Welcome to BitMshauri",
                    "content": "Hello! I'm BitMshauri, your Bitcoin assistant in multiple languages. Choose an option below:",
                    "category": "basic",
                    "duration_minutes": 2,
                    "difficulty": "beginner"
                },
                "why_bitcoin": {
                    "title": "Why Bitcoin?",
                    "content": (
                        "🌍 *Why Use Bitcoin?*\n\n"
                        "Many people don't understand why Bitcoin is important. Here are the key reasons:\n\n"
                        "🔐 *Financial Freedom:*\n"
                        "- Bitcoin is not controlled by banks or governments\n"
                        "- You alone control your money\n\n"
                        "💸 *Fast and Cheap Payments:*\n"
                        "- Send money to anyone worldwide instantly\n"
                        "- Very low fees compared to banks or traditional services\n\n"
                        "📉 *Protection Against Inflation:*\n"
                        "- Bitcoin cannot be printed endlessly like traditional currencies\n"
                        "- Only 21 million will ever exist\n\n"
                        "📱 *Accessible to Everyone:*\n"
                        "- Even in rural areas, you can use Bitcoin with a mobile phone\n\n"
                        "_Bitcoin is a new form of money that gives you freedom, security, and the ability to participate in the digital economy._"
                    ),
                    "category": "basic",
                    "duration_minutes": 5,
                    "difficulty": "beginner"
                }
            },
            "quizzes": {
                "basic": [
                    {
                        "question": "Who controls Bitcoin?",
                        "options": ["Central Bank", "Government", "No one", "Bitcoin Company"],
                        "answer": 2,
                        "explanation": "Bitcoin is a peer-to-peer network not controlled by any person or institution."
                    }
                ]
            },
            "daily_tips": [
                "💡 Bitcoin is the world's first digital currency",
                "🔐 Keep your seed phrase extremely secure",
                "📚 Learn before you invest"
            ],
            "menu_keyboard": [
                ["🌍 Why Bitcoin?", "📚 What is Bitcoin?"],
                ["💰 Bitcoin Price", "📝 Bitcoin Quiz"],
                ["🛒 Buy Bitcoin", "💡 Daily Tip"],
                ["ℹ️ More Help", "📝 Feedback"]
            ],
            "secondary_menu_keyboard": [
                ["🔗 How P2P Works", "👛 Wallet Types"],
                ["🔒 Wallet Security", "⚠️ Lost Keys"],
                ["📱 Using Wallets", "⚖️ Risks & Benefits"],
                ["🔐 Blockchain Tech", "❓ More Questions"],
                ["🎵 Audio Lessons", "⬅️ Back to Main"]
            ]
        }
    
    def get_content(self, content_type: str, content_key: str, language: str = 'sw') -> Optional[Any]:
        """Get specific content item"""
        try:
            if language not in self.content_cache:
                return None
            
            content = self.content_cache[language].get(content_type, {})
            return content.get(content_key)
            
        except Exception as e:
            logger.log_error(e, {
                "operation": "get_content",
                "content_type": content_type,
                "content_key": content_key,
                "language": language
            })
            return None
    
    def get_lesson(self, lesson_key: str, language: str = 'sw') -> Optional[Dict]:
        """Get lesson content"""
        return self.get_content('lessons', lesson_key, language)
    
    def get_quiz(self, quiz_name: str, language: str = 'sw') -> Optional[List]:
        """Get quiz questions"""
        return self.get_content('quizzes', quiz_name, language)
    
    def get_menu_keyboard(self, language: str = 'sw') -> Optional[List]:
        """Get menu keyboard layout"""
        return self.get_content('menu_keyboard', '', language)
    
    def get_secondary_menu_keyboard(self, language: str = 'sw') -> Optional[List]:
        """Get secondary menu keyboard layout"""
        return self.get_content('secondary_menu_keyboard', '', language)
    
    def get_daily_tips(self, language: str = 'sw') -> Optional[List]:
        """Get daily tips"""
        return self.get_content('daily_tips', '', language)
    
    def update_content(self, content_type: str, content_key: str, content_data: Any, language: str = 'sw') -> bool:
        """Update content item"""
        try:
            if language not in self.content_cache:
                self.content_cache[language] = {}
            
            if content_type not in self.content_cache[language]:
                self.content_cache[language][content_type] = {}
            
            if content_key:
                self.content_cache[language][content_type][content_key] = content_data
            else:
                self.content_cache[language][content_type] = content_data
            
            # Save to file
            self._save_language_content(language)
            
            logger.log_user_action(None, 'content_updated', {
                'content_type': content_type,
                'content_key': content_key,
                'language': language
            })
            
            return True
            
        except Exception as e:
            logger.log_error(e, {
                "operation": "update_content",
                "content_type": content_type,
                "content_key": content_key,
                "language": language
            })
            return False
    
    def add_lesson(self, lesson_key: str, lesson_data: Dict, language: str = 'sw') -> bool:
        """Add new lesson"""
        lesson_data['created_at'] = datetime.now().isoformat()
        lesson_data['version'] = self.content_version
        return self.update_content('lessons', lesson_key, lesson_data, language)
    
    def add_quiz_question(self, quiz_name: str, question_data: Dict, language: str = 'sw') -> bool:
        """Add question to quiz"""
        try:
            quiz = self.get_quiz(quiz_name, language) or []
            quiz.append(question_data)
            return self.update_content('quizzes', quiz_name, quiz, language)
        except Exception as e:
            logger.log_error(e, {"operation": "add_quiz_question"})
            return False
    
    def get_content_analytics(self) -> Dict:
        """Get content analytics and statistics"""
        try:
            analytics = {
                'languages': list(self.content_cache.keys()),
                'content_summary': {}
            }
            
            for language, content in self.content_cache.items():
                analytics['content_summary'][language] = {
                    'lessons': len(content.get('lessons', {})),
                    'quizzes': len(content.get('quizzes', {})),
                    'daily_tips': len(content.get('daily_tips', [])),
                    'last_updated': datetime.now().isoformat()
                }
            
            return analytics
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_content_analytics"})
            return {}
    
    def validate_content(self, language: str = None) -> Dict:
        """Validate content for completeness and consistency"""
        try:
            languages_to_check = [language] if language else self.supported_languages
            validation_results = {}
            
            for lang in languages_to_check:
                if lang not in self.content_cache:
                    validation_results[lang] = {'status': 'missing', 'issues': ['Content not loaded']}
                    continue
                
                content = self.content_cache[lang]
                issues = []
                
                # Check required sections
                required_sections = ['lessons', 'quizzes', 'daily_tips', 'menu_keyboard']
                for section in required_sections:
                    if section not in content:
                        issues.append(f"Missing section: {section}")
                
                # Check lesson completeness
                lessons = content.get('lessons', {})
                for lesson_key, lesson_data in lessons.items():
                    if not isinstance(lesson_data, dict):
                        issues.append(f"Lesson {lesson_key}: Invalid format")
                    elif 'content' not in lesson_data:
                        issues.append(f"Lesson {lesson_key}: Missing content")
                
                # Check quiz validity
                quizzes = content.get('quizzes', {})
                for quiz_name, quiz_data in quizzes.items():
                    if not isinstance(quiz_data, list):
                        issues.append(f"Quiz {quiz_name}: Should be a list")
                    else:
                        for i, question in enumerate(quiz_data):
                            if not all(key in question for key in ['question', 'options', 'answer']):
                                issues.append(f"Quiz {quiz_name}, Question {i+1}: Missing required fields")
                
                validation_results[lang] = {
                    'status': 'valid' if not issues else 'invalid',
                    'issues': issues,
                    'total_lessons': len(lessons),
                    'total_quizzes': len(quizzes)
                }
            
            return validation_results
            
        except Exception as e:
            logger.log_error(e, {"operation": "validate_content"})
            return {'error': str(e)}

# Global content manager instance
content_manager = ContentManager()

# Helper functions for backward compatibility
def safe_get_lesson(lesson_key: str, language: str = 'sw') -> str:
    """Get lesson content with fallback"""
    lesson = content_manager.get_lesson(lesson_key, language)
    if lesson and isinstance(lesson, dict):
        return lesson.get('content', f"Samahani, somo '{lesson_key}' halipatikani.")
    return f"Samahani, somo '{lesson_key}' halipatikani."

def get_lessons_dict(language: str = 'sw') -> Dict:
    """Get all lessons as dictionary for backward compatibility"""
    lessons = content_manager.get_content('lessons', '', language) or {}
    return {key: {'content': lesson.get('content', '')} for key, lesson in lessons.items()}

def get_menu_keyboard(language: str = 'sw') -> List:
    """Get menu keyboard for backward compatibility"""
    return content_manager.get_menu_keyboard(language) or []

def get_secondary_menu_keyboard(language: str = 'sw') -> List:
    """Get secondary menu keyboard for backward compatibility"""
    return content_manager.get_secondary_menu_keyboard(language) or []

def get_quizzes_dict(language: str = 'sw') -> Dict:
    """Get all quizzes as dictionary for backward compatibility"""
    return content_manager.get_content('quizzes', '', language) or {}

def get_daily_tips_list(language: str = 'sw') -> List:
    """Get daily tips as list for backward compatibility"""
    return content_manager.get_daily_tips(language) or []
