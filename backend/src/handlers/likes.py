import json
import sys
import os
import hashlib
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.dynamodb import DynamoDBClient
from db.redis import RedisClient
from utils.errors import error_response, NotFoundError, ValidationError


db = DynamoDBClient()
redis_client = RedisClient()


def lambda_handler(event, context):
    """Handle like requests"""
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
        
        blog_id = path_params.get('id')
        if not blog_id:
            return error_response(ValidationError("Blog ID is required"))
        
        if method == 'GET':
            return get_likes(event, blog_id)
        elif method == 'POST':
            return add_like(event, blog_id)
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
        print(f"Error in likes handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }


def get_client_ip(event):
    """Extract client IP from event"""
    headers = event.get('headers', {})
    ip = (
        headers.get('X-Forwarded-For', '').split(',')[0].strip() or
        headers.get('X-Real-Ip', '') or
        event.get('requestContext', {}).get('identity', {}).get('sourceIp', '') or
        'unknown'
    )
    return ip


def get_likes(event, blog_id):
    """Get likes count for a blog"""
    # Check cache
    cached = redis_client.get(f"likes_count:{blog_id}")
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
    likes_count = db.get_likes_count(blog_id)
    
    # Update blog likes count
    blog = db.get_blog_by_id(blog_id)
    if blog:
        db.update_blog(blog_id, {'likes_count': likes_count})
    
    result = {
        'likes_count': likes_count,
        'has_liked': False
    }
    
    # Check if current IP has liked
    client_ip = get_client_ip(event)
    ip_hash = hashlib.md5(client_ip.encode()).hexdigest()
    timestamp = int(time.time())
    timestamp_ip = f"{timestamp}:{ip_hash}"
    
    if db.has_liked(blog_id, timestamp_ip):
        result['has_liked'] = True
    
    # Cache for 15 minutes
    redis_client.set(f"likes_count:{blog_id}", result, ttl=15*60)
    
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


def add_like(event, blog_id):
    """Add a like to a blog"""
    # Check if blog exists
    blog = db.get_blog_by_id(blog_id)
    if not blog:
        return error_response(NotFoundError("Blog not found"))
    
    # Get client IP
    client_ip = get_client_ip(event)
    ip_hash = hashlib.md5(client_ip.encode()).hexdigest()
    timestamp = int(time.time())
    timestamp_ip = f"{timestamp}:{ip_hash}"
    
    # Check if already liked (basic check - in production, use better rate limiting)
    if db.has_liked(blog_id, timestamp_ip):
        # Still return success but don't increment
        likes_count = db.get_likes_count(blog_id)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Already liked',
                'data': {'likes_count': likes_count}
            })
        }
    
    # Add like
    db.add_like(blog_id, timestamp_ip)
    
    # Get updated count
    likes_count = db.get_likes_count(blog_id)
    
    # Update blog likes count
    db.update_blog(blog_id, {'likes_count': likes_count})
    
    # Invalidate cache
    redis_client.invalidate_likes_cache(blog_id)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'data': {'likes_count': likes_count}
        })
    }
