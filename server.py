#!/usr/bin/env python3
"""HTTP server for Railway deployment."""

import asyncio
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

from app.clean_telegram_bot import CleanBitMshauriBot
from deployment_config import DeploymentConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global bot instance
bot_instance = None


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
                'bot_username': '@BitMshauriBot'
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
                content_length = int(self.headers['Content-Length'])
                
                # Read request body
                post_data = self.rfile.read(content_length)
                
                # Parse JSON
                update_data = json.loads(post_data.decode('utf-8'))
                
                # Process update asynchronously
                asyncio.create_task(self.process_update(update_data))
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'ok'}
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

    async def process_update(self, update_data):
        """Process Telegram update."""
        try:
            global bot_instance
            if bot_instance is None:
                bot_instance = CleanBitMshauriBot()
                await bot_instance.app.initialize()
            
            # Create Update object and process
            from telegram import Update
            update = Update.de_json(update_data, bot_instance.app.bot)
            await bot_instance.app.process_update(update)
            
        except Exception as e:
            logger.error(f"Update processing error: {e}")

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")


async def start_bot():
    """Start the bot in background."""
    global bot_instance
    try:
        bot_instance = CleanBitMshauriBot()
        await bot_instance.app.initialize()
        logger.info("✅ Bot initialized successfully")
        
        # Start the bot
        await bot_instance.run()
    except Exception as e:
        logger.error(f"Bot startup error: {e}")


def start_server():
    """Start HTTP server."""
    try:
        server = HTTPServer(
            (DeploymentConfig.HOST, DeploymentConfig.PORT), 
            WebhookHandler
        )
        logger.info(f"🚀 Server starting on {DeploymentConfig.HOST}:{DeploymentConfig.PORT}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Server error: {e}")


async def main():
    """Main function."""
    try:
        # Print configuration
        DeploymentConfig.print_config()
        
        # Start bot in background thread
        bot_thread = threading.Thread(target=lambda: asyncio.run(start_bot()))
        bot_thread.daemon = True
        bot_thread.start()
        
        # Start HTTP server
        start_server()
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
    except Exception as e:
        logger.error(f"Main error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
