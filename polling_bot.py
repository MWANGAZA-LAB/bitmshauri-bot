#!/usr/bin/env python3
"""Simple polling-based Telegram bot as backup."""

import requests
import time
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno"
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None):
    """Get updates from Telegram."""
    try:
        url = f"{BOT_URL}/getUpdates"
        params = {'timeout': 30}
        if offset:
            params['offset'] = offset
        
        response = requests.get(url, params=params, timeout=35)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get updates: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return None

def send_message(chat_id, text):
    """Send message to Telegram."""
    try:
        url = f"{BOT_URL}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Message sent to chat {chat_id}")
            return True
        else:
            logger.error(f"Failed to send message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def process_message(message):
    """Process incoming message."""
    try:
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        logger.info(f"Processing message: {text} from chat {chat_id}")
        
        # Simple response logic
        if text == '/start':
            response_text = """🎉 Karibu! Welcome to BitMshauri Bot!

I'm here to help you learn about Bitcoin in Swahili and English.

📚 Available Commands:
/start - Start the bot
/help - Show help message
/price - Get Bitcoin price
/language - Change language

Ask me anything about Bitcoin!"""
            
        elif text == '/help':
            response_text = """📚 Available Commands:

/start - Start the bot
/help - Show this help message
/price - Get Bitcoin price
/language - Change language

💡 You can also ask me questions about Bitcoin in Swahili or English!"""
            
        elif text == '/price':
            response_text = """💰 Bitcoin Price

I'm working on getting live Bitcoin prices for you!

For now, you can check current prices at:
• CoinGecko: https://coingecko.com
• CoinMarketCap: https://coinmarketcap.com

This feature will be available soon! 🚀"""
            
        elif text == '/language':
            response_text = """🌍 Language Settings

I support both Swahili and English!

Current language: English
To switch to Swahili, just send me a message in Swahili!

Lugha ya sasa: Kiingereza
Kubadilisha kwa Kiswahili, tuma ujumbe wa Kiswahili!"""
            
        elif text and text.startswith('/'):
            response_text = f"❓ Command '{text}' not recognized.\n\nUse /help to see available commands."
            
        else:
            response_text = f"""👋 Hello! You said: "{text}"

I'm BitMshauri Bot, your Bitcoin education assistant!

💡 Try these commands:
/help - See all commands
/price - Get Bitcoin price
/language - Language settings

Ask me anything about Bitcoin! 🪙"""
        
        # Send response
        send_message(chat_id, response_text)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def main():
    """Main polling loop."""
    logger.info("🤖 Starting BitMshauri Bot (Polling Mode)")
    logger.info("=" * 50)
    
    offset = None
    
    while True:
        try:
            # Get updates
            updates = get_updates(offset)
            
            if updates and updates.get('ok'):
                for update in updates['result']:
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        process_message(update['message'])
            
            # Wait before next poll
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main()
