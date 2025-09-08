#!/usr/bin/env python3
"""BitMshauri Bot - Main Entry Point."""

import asyncio

from app.clean_telegram_bot import CleanBitMshauriBot


def main() -> None:
    """Main entry point for the bot."""
    bot = CleanBitMshauriBot()
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
