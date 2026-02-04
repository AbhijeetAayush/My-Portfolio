"""Handler for updating blogs"""
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.dynamodb import DynamoDBClient
from db.redis import RedisClient
from db.models import Blog
from utils.jwt_handler import require_auth
from utils.validators import validate_slug
from utils.errors import error_response, UnauthorizedError, NotFoundError, ValidationError
from handlers.blogs_utils import cors_headers, cors_preflight_response


db = DynamoDBClient()
redis_client = RedisClient()


def lambda_handler(event, context):
    """Handle PUT blog requests"""
    try:
        method = event.get('httpMethod', '')
        path_params = event.get('pathParameters', {}) or {}
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return cors_preflight_response()
        
        if method == 'PUT':
            blog_id = path_params.get('id')
            if not blog_id:
                return error_response(ValidationError("Blog ID is required"))
            return update_blog(event, blog_id)
        else:
            return {
                'statusCode': 405,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        print(f"Error in blogs_update handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Internal server error'})
        }


def update_blog(event, blog_id):
    """Update a blog post"""
    # Require authentication
    try:
        email = require_auth(event)
    except UnauthorizedError as e:
        return error_response(e)
    
    # Get existing blog
    blog = db.get_blog_by_id(blog_id)
    if not blog:
        return error_response(NotFoundError("Blog not found"))
    
    # Parse request body
    body = json.loads(event.get('body', '{}'))
    
    # Update fields
    update_data = {}
    if 'title' in body:
        update_data['title'] = body['title']
    if 'content' in body:
        update_data['content'] = body['content']
        # Recalculate reading time
        update_data['reading_time'] = Blog({}).calculate_reading_time(body['content'])
    if 'slug' in body:
        slug = validate_slug(body['slug'])
        # Check if slug is taken by another blog
        existing = db.get_blog_by_slug(slug)
        if existing and existing['blogId'] != blog_id:
            return error_response(ValidationError("A blog with this slug already exists"))
        update_data['slug'] = slug
    if 'featured_image_url' in body:
        update_data['featured_image_url'] = body['featured_image_url']
    if 'tags' in body:
        update_data['tags'] = body['tags']
    if 'category' in body:
        update_data['category'] = body['category']
    if 'seo_description' in body:
        update_data['seo_description'] = body['seo_description']
    
    # Update in database
    updated_blog = db.update_blog(blog_id, update_data)
    
    # Invalidate cache
    redis_client.invalidate_blog_cache(blog_id)
    
    return {
        'statusCode': 200,
        'headers': cors_headers(),
        'body': json.dumps({
            'success': True,
            'data': updated_blog
        })
    }
