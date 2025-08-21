import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.enhanced_telegram_bot import EnhancedBitMshauriBot


# Initialize the bot
bot = EnhancedBitMshauriBot()


class TelegramWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle Telegram webhook POST requests"""
        try:
            # Get the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse the JSON data
            update_data = json.loads(post_data.decode('utf-8'))
            
            # Process the update with the bot
            response = bot.handle_webhook(update_data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error handling webhook: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_GET(self):
        """Handle health check requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "message": "BitMshauri Bot is running",
            "version": "1.0.0"
        }).encode())


def handler(request, context):
    """Vercel serverless function handler"""
    if request.method == 'POST':
        return TelegramWebhookHandler().do_POST()
    elif request.method == 'GET':
        return TelegramWebhookHandler().do_GET()
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
