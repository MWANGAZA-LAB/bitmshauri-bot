import os
import tempfile
import asyncio
from typing import Dict, List, Optional, Tuple
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import normalize, speedup
import io
from app.utils.logger import logger
from app.services.content_manager import content_manager
from app.services.multi_language import multi_lang_bot

class EnhancedAudioService:
    """Enhanced audio generation with multiple voices, speeds, and effects"""
    
    def __init__(self):
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'bitmshauri_audio')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Audio settings
        self.default_settings = {
            'language': 'sw',
            'tld': 'co.za',  # For South African accent
            'speed': 1.0,
            'pitch': 1.0,
            'volume': 1.0,
            'add_intro': True,
            'add_outro': True
        }
        
        # Voice profiles
        self.voice_profiles = {
            'mshauri': {
                'language': 'sw',
                'tld': 'co.za',
                'speed': 0.9,
                'pitch': 1.0,
                'description': 'Sauti ya BitMshauri - pole pole na wazi'
            },
            'haraka': {
                'language': 'sw',
                'tld': 'co.ke',
                'speed': 1.2,
                'pitch': 1.1,
                'description': 'Sauti ya haraka - kwa wale wanaoelewa'
            },
            'mzee': {
                'language': 'sw',
                'tld': 'co.tz',
                'speed': 0.8,
                'pitch': 0.9,
                'description': 'Sauti ya mzee - kwa heshima na busara'
            },
            'kijana': {
                'language': 'sw',
                'tld': 'co.ke',
                'speed': 1.1,
                'pitch': 1.2,
                'description': 'Sauti ya kijana - machangamano na furaha'
            },
            'teacher': {
                'language': 'en',
                'tld': 'co.uk',
                'speed': 0.9,
                'pitch': 1.0,
                'description': 'Clear teaching voice - educational content'
            }
        }
        
        # Intro/outro sounds
        self.intro_texts = {
            'sw': "Habari, mimi ni BitMshauri.",
            'en': "Hello, I'm BitMshauri."
        }
        
        self.outro_texts = {
            'sw': "Asante kwa kusikiliza!",
            'en': "Thank you for listening!"
        }
    
    async def generate_audio(self, 
                           text: str, 
                           user_id: int = None,
                           voice_profile: str = 'mshauri',
                           custom_settings: Dict = None) -> Optional[str]:
        """Generate enhanced audio with voice effects"""
        try:
            # Get user language
            language = multi_lang_bot.get_user_language(user_id) if user_id else 'sw'
            
            # Merge settings
            settings = self.default_settings.copy()
            if voice_profile in self.voice_profiles:
                settings.update(self.voice_profiles[voice_profile])
            if custom_settings:
                settings.update(custom_settings)
            
            # Override language if specified
            if language:
                settings['language'] = language
            
            # Clean and prepare text
            clean_text = self._clean_text_for_audio(text)
            
            # Add intro/outro if enabled
            full_text = self._add_intro_outro(clean_text, settings)
            
            # Generate base audio
            audio_file = await self._generate_base_audio(full_text, settings)
            
            # Apply audio effects
            enhanced_audio_file = await self._apply_audio_effects(audio_file, settings)
            
            # Log audio generation
            if user_id:
                logger.log_user_action(user_id, 'audio_generated', {
                    'voice_profile': voice_profile,
                    'language': settings['language'],
                    'text_length': len(text)
                })
            
            return enhanced_audio_file
            
        except Exception as e:
            logger.log_error(e, {
                "operation": "generate_audio",
                "voice_profile": voice_profile,
                "user_id": user_id
            })
            return None
    
    def _clean_text_for_audio(self, text: str) -> str:
        """Clean text for better audio generation"""
        try:
            # Remove markdown formatting
            import re
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
            clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)  # Italic
            clean_text = re.sub(r'`(.*?)`', r'\1', clean_text)  # Code
            clean_text = re.sub(r'#{1,6}\s*', '', clean_text)  # Headers
            
            # Remove emojis (optional, can be converted to words)
            clean_text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', clean_text)
            
            # Fix spacing
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            # Convert common symbols to words
            replacements = {
                'Bitcoin': 'Bitcoin',
                'BTC': 'Bitcoin',
                '$': 'dola',
                '%': 'asilimia',
                '&': 'na',
                '@': 'at'
            }
            
            for symbol, word in replacements.items():
                clean_text = clean_text.replace(symbol, word)
            
            return clean_text
            
        except Exception as e:
            logger.log_error(e, {"operation": "clean_text_for_audio"})
            return text
    
    def _add_intro_outro(self, text: str, settings: Dict) -> str:
        """Add intro and outro to text"""
        try:
            full_text = text
            
            if settings.get('add_intro', True):
                intro = self.intro_texts.get(settings['language'], '')
                if intro:
                    full_text = f"{intro} {full_text}"
            
            if settings.get('add_outro', True):
                outro = self.outro_texts.get(settings['language'], '')
                if outro:
                    full_text = f"{full_text} {outro}"
            
            return full_text
            
        except Exception as e:
            logger.log_error(e, {"operation": "add_intro_outro"})
            return text
    
    async def _generate_base_audio(self, text: str, settings: Dict) -> Optional[str]:
        """Generate base audio using gTTS"""
        try:
            tts = gTTS(
                text=text,
                lang=settings['language'],
                tld=settings.get('tld', 'com'),
                slow=False
            )
            
            # Save to temporary file
            temp_file = os.path.join(self.temp_dir, f"audio_{hash(text)}.mp3")
            tts.save(temp_file)
            
            return temp_file
            
        except Exception as e:
            logger.log_error(e, {"operation": "generate_base_audio"})
            return None
    
    async def _apply_audio_effects(self, audio_file: str, settings: Dict) -> Optional[str]:
        """Apply audio effects using pydub"""
        try:
            if not audio_file or not os.path.exists(audio_file):
                return None
            
            # Load audio
            audio = AudioSegment.from_mp3(audio_file)
            
            # Apply speed change
            speed = settings.get('speed', 1.0)
            if speed != 1.0:
                audio = speedup(audio, playback_speed=speed)
            
            # Apply pitch change (approximate using sample rate manipulation)
            pitch = settings.get('pitch', 1.0)
            if pitch != 1.0:
                # Change sample rate for pitch effect
                new_sample_rate = int(audio.frame_rate * pitch)
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                audio = audio.set_frame_rate(audio.frame_rate)
            
            # Apply volume change
            volume = settings.get('volume', 1.0)
            if volume != 1.0:
                # Convert to dB change
                db_change = 20 * (volume - 1)  # Rough conversion
                audio = audio + db_change
            
            # Normalize audio
            audio = normalize(audio)
            
            # Save enhanced audio
            enhanced_file = audio_file.replace('.mp3', '_enhanced.mp3')
            audio.export(enhanced_file, format="mp3", bitrate="128k")
            
            # Clean up original file
            try:
                os.remove(audio_file)
            except:
                pass
            
            return enhanced_file
            
        except Exception as e:
            logger.log_error(e, {"operation": "apply_audio_effects"})
            return audio_file  # Return original if effects fail
    
    async def generate_lesson_audio(self, 
                                  lesson_key: str, 
                                  user_id: int,
                                  voice_profile: str = 'mshauri') -> Optional[str]:
        """Generate audio for a specific lesson"""
        try:
            # Get lesson content in user's language
            lesson = multi_lang_bot.get_lesson(user_id, lesson_key)
            
            if not lesson or not isinstance(lesson, dict):
                return None
            
            lesson_text = lesson.get('content', '')
            if not lesson_text:
                return None
            
            # Add lesson-specific intro
            language = multi_lang_bot.get_user_language(user_id)
            if language == 'sw':
                intro = f"Somo: {lesson.get('title', lesson_key)}"
            else:
                intro = f"Lesson: {lesson.get('title', lesson_key)}"
            
            full_text = f"{intro}. {lesson_text}"
            
            # Generate audio with teaching voice
            audio_file = await self.generate_audio(
                full_text,
                user_id,
                voice_profile,
                {'add_intro': False, 'add_outro': True}
            )
            
            return audio_file
            
        except Exception as e:
            logger.log_error(e, {"operation": "generate_lesson_audio"})
            return None
    
    async def generate_quiz_audio(self, 
                                quiz_question: Dict, 
                                user_id: int,
                                voice_profile: str = 'kijana') -> Optional[str]:
        """Generate audio for quiz question"""
        try:
            language = multi_lang_bot.get_user_language(user_id)
            
            # Format quiz question for audio
            question_text = quiz_question.get('question', '')
            options = quiz_question.get('options', [])
            
            if language == 'sw':
                audio_text = f"Swali: {question_text}. "
                audio_text += "Chaguo zako ni: "
                for i, option in enumerate(options, 1):
                    audio_text += f"Chaguo {i}: {option}. "
            else:
                audio_text = f"Question: {question_text}. "
                audio_text += "Your options are: "
                for i, option in enumerate(options, 1):
                    audio_text += f"Option {i}: {option}. "
            
            # Generate audio
            audio_file = await self.generate_audio(
                audio_text,
                user_id,
                voice_profile,
                {'add_intro': False, 'add_outro': False}
            )
            
            return audio_file
            
        except Exception as e:
            logger.log_error(e, {"operation": "generate_quiz_audio"})
            return None
    
    async def generate_price_alert_audio(self, 
                                       price_data: Dict, 
                                       user_id: int,
                                       voice_profile: str = 'haraka') -> Optional[str]:
        """Generate audio for price alerts"""
        try:
            language = multi_lang_bot.get_user_language(user_id)
            
            if language == 'sw':
                audio_text = (
                    f"Kumbuka ya bei! Bitcoin sasa ni dola "
                    f"{price_data.get('usd', 0):,.0f}. "
                    f"Mabadiliko ya siku ishirini na nne ni "
                    f"{price_data.get('usd_24h_change', 0):.1f} asilimia."
                )
            else:
                audio_text = (
                    f"Price alert! Bitcoin is now "
                    f"{price_data.get('usd', 0):,.0f} dollars. "
                    f"Twenty-four hour change is "
                    f"{price_data.get('usd_24h_change', 0):.1f} percent."
                )
            
            # Generate audio
            audio_file = await self.generate_audio(
                audio_text,
                user_id,
                voice_profile,
                {'add_intro': True, 'add_outro': False}
            )
            
            return audio_file
            
        except Exception as e:
            logger.log_error(e, {"operation": "generate_price_alert_audio"})
            return None
    
    def get_voice_profiles(self, language: str = None) -> Dict:
        """Get available voice profiles"""
        try:
            if language:
                return {
                    name: profile for name, profile in self.voice_profiles.items()
                    if profile['language'] == language
                }
            return self.voice_profiles.copy()
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_voice_profiles"})
            return {}
    
    def cleanup_old_audio(self, max_age_hours: int = 24):
        """Clean up old audio files"""
        try:
            import time
            current_time = time.time()
            
            for filename in os.listdir(self.temp_dir):
                if filename.endswith('.mp3'):
                    file_path = os.path.join(self.temp_dir, filename)
                    file_age = current_time - os.path.getctime(file_path)
                    
                    if file_age > (max_age_hours * 3600):  # Convert hours to seconds
                        try:
                            os.remove(file_path)
                        except:
                            pass
            
        except Exception as e:
            logger.log_error(e, {"operation": "cleanup_old_audio"})
    
    def get_audio_stats(self) -> Dict:
        """Get audio generation statistics"""
        try:
            stats = {
                'temp_directory': self.temp_dir,
                'available_voices': len(self.voice_profiles),
                'supported_languages': list(set(p['language'] for p in self.voice_profiles.values())),
                'total_audio_files': 0,
                'total_size_mb': 0
            }
            
            if os.path.exists(self.temp_dir):
                total_size = 0
                file_count = 0
                
                for filename in os.listdir(self.temp_dir):
                    if filename.endswith('.mp3'):
                        file_path = os.path.join(self.temp_dir, filename)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                
                stats['total_audio_files'] = file_count
                stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_audio_stats"})
            return {}

# Global enhanced audio service instance
enhanced_audio = EnhancedAudioService()

# Helper functions for easy integration
async def generate_audio_message(text: str, user_id: int = None, voice_profile: str = 'mshauri') -> Optional[str]:
    """Generate audio for any text message"""
    return await enhanced_audio.generate_audio(text, user_id, voice_profile)

async def generate_lesson_audio_file(lesson_key: str, user_id: int) -> Optional[str]:
    """Generate audio for lesson"""
    return await enhanced_audio.generate_lesson_audio(lesson_key, user_id)

async def generate_quiz_audio_file(quiz_question: Dict, user_id: int) -> Optional[str]:
    """Generate audio for quiz question"""
    return await enhanced_audio.generate_quiz_audio(quiz_question, user_id)

def get_available_voices(language: str = None) -> Dict:
    """Get available voice profiles"""
    return enhanced_audio.get_voice_profiles(language)
