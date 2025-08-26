#!/usr/bin/env python3
"""BitMshauri Bot - Main Entry Point"""

from app.enhanced_telegram_bot import EnhancedBitMshauriBot

if __name__ == "__main__":
    bot = EnhancedBitMshauriBot()
    bot.run()
