"""Handler for deleting blogs"""
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.dynamodb import DynamoDBClient
from db.redis import RedisClient
from utils.jwt_handler import require_auth
from utils.errors import error_response, UnauthorizedError, NotFoundError, ValidationError
from handlers.blogs_utils import cors_headers, cors_preflight_response


db = DynamoDBClient()
redis_client = RedisClient()


def lambda_handler(event, context):
    """Handle DELETE blog requests"""
    try:
        method = event.get('httpMethod', '')
        path_params = event.get('pathParameters', {}) or {}
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return cors_preflight_response()
        
        if method == 'DELETE':
            blog_id = path_params.get('id')
            if not blog_id:
                return error_response(ValidationError("Blog ID is required"))
            return delete_blog(event, blog_id)
        else:
            return {
                'statusCode': 405,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        print(f"Error in blogs_delete handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Internal server error'})
        }


def delete_blog(event, blog_id):
    """Delete a blog post"""
    # Require authentication
    try:
        email = require_auth(event)
    except UnauthorizedError as e:
        return error_response(e)
    
    # Check if blog exists
    blog = db.get_blog_by_id(blog_id)
    if not blog:
        return error_response(NotFoundError("Blog not found"))
    
    # Delete blog
    success = db.delete_blog(blog_id)
    
    if not success:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to delete blog'})
        }
    
    # Invalidate cache
    redis_client.invalidate_blog_cache(blog_id)
    
    return {
        'statusCode': 200,
        'headers': cors_headers(),
        'body': json.dumps({
            'success': True,
            'message': 'Blog deleted successfully'
        })
    }
