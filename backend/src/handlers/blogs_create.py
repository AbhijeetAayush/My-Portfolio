"""Handler for creating blogs"""
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.dynamodb import DynamoDBClient
from db.redis import RedisClient
from db.models import Blog
from utils.jwt_handler import require_auth
from utils.validators import validate_required, validate_slug
from utils.errors import error_response, UnauthorizedError, ValidationError
from handlers.blogs_utils import cors_headers, cors_preflight_response, generate_slug


db = DynamoDBClient()
redis_client = RedisClient()


def lambda_handler(event, context):
    """Handle POST blog requests"""
    try:
        method = event.get('httpMethod', '')
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return cors_preflight_response()
        
        if method == 'POST':
            return create_blog(event)
        else:
            return {
                'statusCode': 405,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        print(f"Error in blogs_create handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Internal server error'})
        }


def create_blog(event):
    """Create a new blog post"""
    # Require authentication
    try:
        email = require_auth(event)
    except UnauthorizedError as e:
        return error_response(e)
    
    # Parse request body
    body = json.loads(event.get('body', '{}'))
    
    # Validate required fields
    title = validate_required(body.get('title'), 'title')
    content = validate_required(body.get('content'), 'content')
    slug = body.get('slug') or generate_slug(title)
    slug = validate_slug(slug)
    
    # Check if slug already exists
    existing = db.get_blog_by_slug(slug)
    if existing:
        return error_response(ValidationError("A blog with this slug already exists"))
    
    # Create blog model
    blog = Blog({
        'title': title,
        'slug': slug,
        'content': body.get('content', ''),
        'featured_image_url': body.get('featured_image_url', ''),
        'tags': body.get('tags', []),
        'category': body.get('category', ''),
        'author': email,
        'seo_description': body.get('seo_description', ''),
    })
    
    # Calculate reading time
    blog.reading_time = blog.calculate_reading_time(content)
    
    # Save to database
    blog_data = blog.to_dict()
    created_blog = db.create_blog(blog_data)
    
    # Invalidate cache
    redis_client.invalidate_blog_cache()
    
    return {
        'statusCode': 201,
        'headers': cors_headers(),
        'body': json.dumps({
            'success': True,
            'data': created_blog
        })
    }
