#!/usr/bin/env python3
"""Webhook handler for Railway deployment."""

import asyncio
import json
import logging
from typing import Dict, Any

from telegram import Update
from telegram.ext import Application

from app.clean_telegram_bot import CleanBitMshauriBot
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global bot instance
bot_instance = None


async def get_bot_instance() -> CleanBitMshauriBot:
    """Get or create bot instance."""
    global bot_instance
    if bot_instance is None:
        bot_instance = CleanBitMshauriBot()
        await bot_instance.app.initialize()
    return bot_instance


async def webhook_handler(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming webhook requests."""
    try:
        # Get bot instance
        bot = await get_bot_instance()
        
        # Parse update from request
        update_data = request_data.get('body', {})
        if isinstance(update_data, str):
            update_data = json.loads(update_data)
        
        # Create Update object
        update = Update.de_json(update_data, bot.app.bot)
        
        # Process update
        await bot.app.process_update(update)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'ok'})
        }
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        bot = await get_bot_instance()
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'ok',
                'message': 'BitMshauri Bot is running',
                'version': '1.0.0',
                'bot_username': '@BitMshauriBot'
            })
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def handle_request(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """Main request handler for Railway."""
    try:
        # Get request path
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        # Route requests
        if path == '/webhook' and method == 'POST':
            return asyncio.run(webhook_handler(event))
        elif path == '/health' and method == 'GET':
            return asyncio.run(health_check())
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Not found'})
            }
            
    except Exception as e:
        logger.error(f"Request handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


if __name__ == "__main__":
    # For local testing
    test_event = {
        'path': '/health',
        'httpMethod': 'GET'
    }
    
    result = handle_request(test_event)
    print(json.dumps(result, indent=2))
