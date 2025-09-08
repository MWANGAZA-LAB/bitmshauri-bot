#!/usr/bin/env python3
"""BitMshauri Bot Startup Script.

This script provides an easy way to start the bot with proper error handling.
"""

import asyncio
import sys
import signal
from app.clean_telegram_bot import CleanBitMshauriBot
from config import Config


class BotManager:
    """Bot manager with graceful shutdown handling."""
    
    def __init__(self):
        self.bot = None
        self.running = False
    
    async def start(self):
        """Start the bot."""
        try:
            print("🚀 Starting BitMshauri Bot...")
            print("=" * 50)
            
            # Create bot instance
            self.bot = CleanBitMshauriBot()
            self.running = True
            
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            print("✅ Bot initialized successfully!")
            print(f"🤖 Bot Token: {Config.TELEGRAM_BOT_TOKEN[:10]}...")
            print(f"📊 Log Level: {Config.LOG_LEVEL}")
            print(f"💾 Database: {Config.DATABASE_PATH}")
            print("\n🎯 Bot is now running...")
            print("Press Ctrl+C to stop the bot gracefully.")
            print("=" * 50)
            
            # Start the bot
            await self.bot.run()
            
        except KeyboardInterrupt:
            print("\n⏹️ Received shutdown signal...")
            await self.shutdown()
        except Exception as e:
            print(f"\n❌ Bot startup failed: {e}")
            await self.shutdown()
            sys.exit(1)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n⏹️ Received signal {signum}, shutting down...")
        self.running = False
    
    async def shutdown(self):
        """Gracefully shutdown the bot."""
        try:
            if self.bot:
                print("🔄 Shutting down bot...")
                await self.bot.shutdown()
                print("✅ Bot shutdown completed!")
        except Exception as e:
            print(f"⚠️ Error during shutdown: {e}")


async def main():
    """Main entry point."""
    bot_manager = BotManager()
    await bot_manager.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
