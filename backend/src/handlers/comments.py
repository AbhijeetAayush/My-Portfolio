import json
import sys
import os
import hashlib
from urllib.parse import unquote

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.dynamodb import DynamoDBClient
from db.redis import RedisClient
from db.models import Comment
from utils.jwt_handler import require_auth
from utils.validators import validate_email, validate_required
from utils.errors import error_response, UnauthorizedError, NotFoundError, ValidationError


db = DynamoDBClient()
redis_client = RedisClient()

# Rate limiting: track IPs and their comment counts
rate_limit_cache = {}  # In production, use Redis for this


def lambda_handler(event, context):
    """Handle comment requests"""
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
            if not blog_id:
                return error_response(ValidationError("Blog ID is required"))
            return get_comments(event, blog_id)
        elif method == 'POST':
            blog_id = path_params.get('id')
            if not blog_id:
                return error_response(ValidationError("Blog ID is required"))
            return create_comment(event, blog_id)
        elif method == 'DELETE':
            comment_id = path_params.get('id')
            if not comment_id:
                return error_response(ValidationError("Comment ID is required"))
            return delete_comment(event, comment_id)
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
        print(f"Error in comments handler: {str(e)}")
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
    # Try various headers for IP
    ip = (
        headers.get('X-Forwarded-For', '').split(',')[0].strip() or
        headers.get('X-Real-Ip', '') or
        event.get('requestContext', {}).get('identity', {}).get('sourceIp', '') or
        'unknown'
    )
    return ip


def get_comments(event, blog_id):
    """Get all comments for a blog"""
    # Check cache
    cached = redis_client.get(f"comments:{blog_id}")
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
    comments = db.get_comments_by_blog(blog_id)
    
    # Update blog comments count
    blog = db.get_blog_by_id(blog_id)
    if blog:
        db.update_blog(blog_id, {'comments_count': len(comments)})
    
    # Cache for 30 minutes
    redis_client.set(f"comments:{blog_id}", comments, ttl=30*60)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'data': comments
        })
    }


def create_comment(event, blog_id):
    """Create a new comment"""
    # Check if blog exists
    blog = db.get_blog_by_id(blog_id)
    if not blog:
        return error_response(NotFoundError("Blog not found"))
    
    # Parse request body
    body = json.loads(event.get('body', '{}'))
    
    # Validate required fields
    author_name = validate_required(body.get('author_name'), 'author_name')
    author_email = validate_email(body.get('author_email', ''))
    content = validate_required(body.get('content'), 'content')
    
    # Basic rate limiting (check IP)
    client_ip = get_client_ip(event)
    ip_hash = hashlib.md5(client_ip.encode()).hexdigest()
    
    # Simple rate limiting: max 5 comments per hour per IP
    # In production, use Redis for this
    import time
    current_time = int(time.time())
    rate_key = f"comment_rate:{ip_hash}"
    
    # Check rate limit (simplified - in production use Redis)
    # For now, we'll allow comments but log for monitoring
    
    # Create comment
    comment = Comment({
        'blogId': blog_id,
        'author_name': author_name,
        'author_email': author_email,
        'content': content,
        'status': 'approved'  # Auto-approve for now
    })
    
    # Save to database
    comment_data = comment.to_dict()
    created_comment = db.create_comment(comment_data)
    
    # Update blog comments count
    comments = db.get_comments_by_blog(blog_id)
    db.update_blog(blog_id, {'comments_count': len(comments)})
    
    # Invalidate cache
    redis_client.invalidate_comments_cache(blog_id)
    
    return {
        'statusCode': 201,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'data': created_comment
        })
    }


def delete_comment(event, comment_id):
    """Delete a comment (admin only)"""
    # Require authentication
    try:
        email = require_auth(event)
    except UnauthorizedError as e:
        return error_response(e)
    
    # Get comment
    comment = db.get_comment_by_id(comment_id)
    if not comment:
        return error_response(NotFoundError("Comment not found"))
    
    blog_id = comment['blogId']
    
    # Delete comment
    success = db.delete_comment(comment_id)
    
    if not success:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to delete comment'})
        }
    
    # Update blog comments count
    comments = db.get_comments_by_blog(blog_id)
    db.update_blog(blog_id, {'comments_count': len(comments)})
    
    # Invalidate cache
    redis_client.invalidate_comments_cache(blog_id)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps({
            'success': True,
            'message': 'Comment deleted successfully'
        })
    }
