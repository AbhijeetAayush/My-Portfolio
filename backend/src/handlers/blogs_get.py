"""Handler for getting blogs (list and single)"""
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.dynamodb import DynamoDBClient
from db.redis import RedisClient
from utils.errors import error_response, NotFoundError
from handlers.blogs_utils import cors_headers, cors_preflight_response


db = DynamoDBClient()
redis_client = RedisClient()


def lambda_handler(event, context):
    """Handle GET blog requests"""
    try:
        method = event.get('httpMethod', '')
        path_params = event.get('pathParameters', {}) or {}
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return cors_preflight_response()
        
        if method == 'GET':
            blog_id = path_params.get('id')
            if blog_id:
                return get_blog(event, blog_id)
            else:
                return get_blogs(event)
        else:
            return {
                'statusCode': 405,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        print(f"Error in blogs_get handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Internal server error'})
        }


def get_blogs(event):
    """Get all blogs with pagination"""
    # Check cache
    cached = redis_client.get('blogs:list')
    if cached:
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'success': True,
                'data': cached
            })
        }
    
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    limit = int(query_params.get('limit', 50))
    last_key = query_params.get('last_key')
    
    # Get from database
    result = db.get_all_blogs(limit=limit, last_key=json.loads(last_key) if last_key else None)
    
    # Cache for 1 hour
    redis_client.set('blogs:list', result, ttl=60*60)
    
    return {
        'statusCode': 200,
        'headers': cors_headers(),
        'body': json.dumps({
            'success': True,
            'data': result
        })
    }


def get_blog(event, blog_id):
    """Get single blog by ID or slug"""
    # Check cache
    cached = redis_client.get(f"blogs:{blog_id}")
    if cached:
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'success': True,
                'data': cached
            })
        }
    
    # Try to get by ID first, then by slug
    blog = db.get_blog_by_id(blog_id)
    if not blog:
        blog = db.get_blog_by_slug(blog_id)
    
    if not blog:
        return error_response(NotFoundError("Blog not found"))
    
    # Cache for 1 hour
    redis_client.set(f"blogs:{blog_id}", blog, ttl=60*60)
    
    return {
        'statusCode': 200,
        'headers': cors_headers(),
        'body': json.dumps({
            'success': True,
            'data': blog
        })
    }
