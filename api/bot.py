import json
import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Simple bot handler without complex imports
def handler(request, context):
    """Vercel serverless function handler for Telegram bot"""
    try:
        # Handle CORS
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'application/json'
        }
        
        # Handle OPTIONS request (CORS preflight)
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # Handle GET request (health check)
        if request.method == 'GET':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'ok',
                    'message': 'BitMshauri Bot is running',
                    'version': '1.0.0',
                    'endpoint': '/api/bot'
                })
            }
        
        # Handle POST request (Telegram webhook)
        if request.method == 'POST':
            try:
                # Get the request body
                body = request.body
                if isinstance(body, bytes):
                    body = body.decode('utf-8')
                
                # Parse the JSON data
                update_data = json.loads(body)
                
                # Simple response for now (we'll enhance this later)
                response = {
                    'status': 'received',
                    'message': 'Webhook received successfully',
                    'update_id': update_data.get('update_id', 'unknown')
                }
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(response)
                }
                
            except Exception as e:
                print(f"Error handling webhook: {e}")
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({'error': str(e)})
                }
        
        # Handle unsupported methods
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
        
    except Exception as e:
        print(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
