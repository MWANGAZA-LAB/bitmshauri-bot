#!/usr/bin/env python3
"""Simple HTTP server for Railway deployment."""

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN", 
    "8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno"
)

# Set environment variable for the bot
os.environ["TELEGRAM_BOT_TOKEN"] = TELEGRAM_BOT_TOKEN

# Global variables


class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for webhooks."""

    def do_GET(self):
        """Handle GET requests (health check)."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'ok',
                'message': 'BitMshauri Bot is running',
                'version': '1.0.0',
                'bot_username': '@BitMshauriBot',
                'timestamp': time.time()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

    def do_POST(self):
        """Handle POST requests (webhooks)."""
        if self.path == '/webhook':
            try:
                # Get content length
                content_length = int(self.headers.get('Content-Length', 0))
                
                if content_length == 0:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'No content')
                    return
                
                # Read request body
                post_data = self.rfile.read(content_length)
                
                # Parse JSON
                update_data = json.loads(post_data.decode('utf-8'))
                
                # Log the update
                logger.info(f"Received update: {update_data.get('update_id', 'unknown')}")
                
                # Process the update
                self.process_update(update_data)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'ok', 'message': 'Update processed'}
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

    def process_update(self, update_data):
        """Process Telegram update."""
        try:
            # Import here to avoid circular imports
            from telegram import Update
            import asyncio
            
            # Create Update object
            update = Update.de_json(update_data, None)
            
            # Process the update
            if update and update.message:
                message = update.message
                chat_id = message.chat_id
                text = message.text
                
                logger.info(f"Processing message: {text} from chat {chat_id}")
                
                # Simple response logic
                if text == '/start':
                    response_text = "🎉 Karibu! Welcome to BitMshauri Bot!\n\nI'm here to help you learn about Bitcoin in Swahili and English.\n\nUse /help to see all available commands."
                elif text == '/help':
                    response_text = "📚 Available Commands:\n\n/start - Start the bot\n/help - Show this help message\n/price - Get Bitcoin price\n/language - Change language\n\nAsk me anything about Bitcoin!"
                elif text and text.startswith('/'):
                    response_text = f"❓ Command '{text}' not recognized. Use /help to see available commands."
                else:
                    response_text = f"👋 Hello! You said: {text}\n\nI'm BitMshauri Bot, your Bitcoin education assistant. Use /help to see what I can do!"
                
                # Send response
                self.send_telegram_message(chat_id, response_text)
                
        except Exception as e:
            logger.error(f"Error processing update: {e}")

    def send_telegram_message(self, chat_id, text):
        """Send message to Telegram."""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"Message sent to chat {chat_id}")
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")


def setup_webhook():
    """Setup Telegram webhook."""
    try:
        import requests
        
        # Get Railway URL from environment
        railway_url = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if not railway_url:
            logger.warning("RAILWAY_PUBLIC_DOMAIN not set, webhook setup skipped")
            return
        
        webhook_url = f"https://{railway_url}/webhook"
        
        # Set webhook
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
        data = {'url': webhook_url}
        
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Webhook set to: {webhook_url}")
        else:
            logger.error(f"❌ Failed to set webhook: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")


def start_server():
    """Start HTTP server."""
    try:
        server = HTTPServer((HOST, PORT), WebhookHandler)
        logger.info(f"🚀 Server starting on {HOST}:{PORT}")
        logger.info(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
        
        # Setup webhook
        setup_webhook()
        
        # Start HTTP server
        server.serve_forever()
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        logger.info("🚀 Starting BitMshauri Bot Server")
        logger.info("=" * 50)
        
        # Validate configuration
        if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
            logger.error("❌ TELEGRAM_BOT_TOKEN is required")
            sys.exit(1)
        
        # Start server
        start_server()
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
    except Exception as e:
        logger.error(f"Main error: {e}")
        sys.exit(1)
