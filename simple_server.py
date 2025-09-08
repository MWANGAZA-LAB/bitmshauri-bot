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

# Global bot instance
bot_instance = None
bot_thread = None


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
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'ok', 'message': 'Update received'}
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

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")


def start_bot():
    """Start the bot in a separate thread."""
    global bot_instance
    try:
        logger.info("🤖 Starting bot...")
        
        # Import and start the bot
        from app.clean_telegram_bot import CleanBitMshauriBot
        import asyncio
        
        bot_instance = CleanBitMshauriBot()
        
        # Run the bot
        asyncio.run(bot_instance.run())
        
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
        # Don't exit, just log the error


def start_server():
    """Start HTTP server."""
    try:
        server = HTTPServer((HOST, PORT), WebhookHandler)
        logger.info(f"🚀 Server starting on {HOST}:{PORT}")
        logger.info(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
        
        # Start bot in background thread
        global bot_thread
        bot_thread = Thread(target=start_bot, daemon=True)
        bot_thread.start()
        
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
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN is required")
            sys.exit(1)
        
        # Start server
        start_server()
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
    except Exception as e:
        logger.error(f"Main error: {e}")
        sys.exit(1)
