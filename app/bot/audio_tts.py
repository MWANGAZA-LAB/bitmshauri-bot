import os
import logging
from gtts import gTTS
import tempfile
from io import BytesIO
import asyncio
import aiofiles
import re

logger = logging.getLogger(__name__)


class SwahiliTTS:
    def __init__(self):
        self.language = "sw"  # Swahili language code
        self.slow = False

    async def text_to_speech(self, text: str) -> BytesIO:
        """Convert text to speech and return audio file"""
        try:
            # Clean text for better TTS
            clean_text = self._clean_text_for_tts(text)

            # Create TTS object
            tts = gTTS(text=clean_text, lang=self.language, slow=self.slow)

            # Save to BytesIO buffer
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            logger.info(f"Generated TTS audio for text length: {len(text)}")
            return audio_buffer

        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise

    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS pronunciation"""
        # Remove markdown formatting
        clean_text = text.replace("*", "").replace("_", "").replace("`", "")

        # Remove emojis and special chars for better pronunciation
        clean_text = re.sub(r"[^\w\s\.\,\!\?\-]", " ", clean_text)

        # Replace common abbreviations with full words
        replacements = {
            "Bitcoin": "Bitkoyini",
            "P2P": "Pii tu Pii",
            "FAQ": "Maswali ya kawaida",
            "AI": "Akili ya bandia",
            "URL": "anwani ya tovuti",
            "M-Pesa": "Em Pesa",
            "BTC": "Bitkoyini",
            "USD": "dola za marekani",
        }

        for old, new in replacements.items():
            clean_text = clean_text.replace(old, new)

        # Limit length for TTS (max 500 chars for better performance)
        if len(clean_text) > 500:
            clean_text = clean_text[:497] + "..."

        return clean_text


# Global TTS instance
tts_engine = SwahiliTTS()
