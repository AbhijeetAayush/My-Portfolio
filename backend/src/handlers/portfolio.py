import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.dynamodb import DynamoDBClient
from db.redis import RedisClient
from db.models import Portfolio
from utils.jwt_handler import require_auth
from utils.errors import error_response, UnauthorizedError, NotFoundError


db = DynamoDBClient()
redis_client = RedisClient()


def lambda_handler(event, context):
    """Handle portfolio requests"""
    try:
        method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': ''
            }
        
        if method == 'GET':
            return get_portfolio(event)
        elif method == 'PUT':
            return update_portfolio(event)
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        print(f"Error in portfolio handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }


def get_portfolio(event):
    """Get portfolio data"""
    user_id = 'default'  # Single user portfolio
    
    # Check cache
    cached = redis_client.get('portfolio_data')
    if cached:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'data': cached
            })
        }
    
    # Get from database
    portfolio = db.get_portfolio(user_id)
    
    if not portfolio:
        # Return empty portfolio structure
        portfolio = {
            'userId': user_id,
            'profile_pic_url': '',
            'bio': '',
            'email': '',
            'social_links': {},
            'about_content': '',
            'projects': [],
            'experience': [],
            'updated_at': 0
        }
    
    # Cache for 24 hours
    redis_client.set('portfolio_data', portfolio, ttl=24*60*60)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'data': portfolio
        })
    }


def update_portfolio(event):
    """Update portfolio data"""
    # Require authentication
    try:
        email = require_auth(event)
    except UnauthorizedError as e:
        return error_response(e)
    
    # Parse request body
    body = json.loads(event.get('body', '{}'))
    user_id = 'default'
    
    # Update portfolio
    updated = db.update_portfolio(user_id, body)
    
    # Invalidate cache
    redis_client.invalidate_portfolio_cache()
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps({
            'success': True,
            'data': updated
        })
    }
