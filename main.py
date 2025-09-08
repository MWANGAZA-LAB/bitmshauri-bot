#!/usr/bin/env python3
"""BitMshauri Bot - Main Entry Point"""

from app.clean_telegram_bot import CleanBitMshauriBot
import asyncio

if __name__ == "__main__":
    bot = CleanBitMshauriBot()
    asyncio.run(bot.run())
