import json


def handler(request, context):
    """Handle root URL requests"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'OK'})
        }
    
    if request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'ok',
                'message': 'BitMshauri Bot API',
                'version': '1.0.0',
                'endpoints': {
                    'root': '/',
                    'bot_webhook': '/api/bot',
                    'health_check': '/api/bot (GET)'
                },
                'description': 'Bitcoin Education Bot for East Africa',
                'features': [
                    'Multi-language support (Swahili/English)',
                    'Real-time Bitcoin price monitoring',
                    'Interactive lessons and quizzes',
                    'Currency conversion calculator',
                    'Community features',
                    'Progress tracking'
                ]
            })
        }
    
    return {
        'statusCode': 405,
        'headers': headers,
        'body': json.dumps({'error': 'Method not allowed'})
    }
