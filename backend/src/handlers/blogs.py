import json
import sys
import os
import re
from urllib.parse import unquote

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.dynamodb import DynamoDBClient
from db.redis import RedisClient
from db.models import Blog
from utils.jwt_handler import require_auth
from utils.validators import validate_required, validate_slug
from utils.errors import error_response, UnauthorizedError, NotFoundError, ValidationError


db = DynamoDBClient()
redis_client = RedisClient()


def lambda_handler(event, context):
    """Handle blog requests"""
    try:
        method = event.get('httpMethod', '')
        path = event.get('path', '')
        path_params = event.get('pathParameters', {}) or {}
        
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
            blog_id = path_params.get('id')
            if blog_id:
                return get_blog(event, blog_id)
            else:
                return get_blogs(event)
        elif method == 'POST':
            return create_blog(event)
        elif method == 'PUT':
            blog_id = path_params.get('id')
            if not blog_id:
                return error_response(ValidationError("Blog ID is required"))
            return update_blog(event, blog_id)
        elif method == 'DELETE':
            blog_id = path_params.get('id')
            if not blog_id:
                return error_response(ValidationError("Blog ID is required"))
            return delete_blog(event, blog_id)
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
        print(f"Error in blogs handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }


def get_blogs(event):
    """Get all blogs with pagination"""
    # Check cache
    cached = redis_client.get('blogs:list')
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
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
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
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
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
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'data': blog
        })
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
        raise ValidationError("A blog with this slug already exists")
    
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
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps({
            'success': True,
            'data': created_blog
        })
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
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps({
            'success': True,
            'data': updated_blog
        })
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
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to delete blog'})
        }
    
    # Invalidate cache
    redis_client.invalidate_blog_cache(blog_id)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps({
            'success': True,
            'message': 'Blog deleted successfully'
        })
    }


def generate_slug(title):
    """Generate URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug
