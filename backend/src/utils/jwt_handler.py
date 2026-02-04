import os
import jwt
import time
from datetime import datetime, timedelta
from .errors import UnauthorizedError


JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRY = 15 * 60  # 15 minutes
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 * 60  # 7 days


def generate_tokens(email):
    """Generate access and refresh tokens"""
    now = datetime.utcnow()
    
    access_token_payload = {
        'email': email,
        'type': 'access',
        'exp': now + timedelta(seconds=ACCESS_TOKEN_EXPIRY),
        'iat': now
    }
    
    refresh_token_payload = {
        'email': email,
        'type': 'refresh',
        'exp': now + timedelta(seconds=REFRESH_TOKEN_EXPIRY),
        'iat': now
    }
    
    access_token = jwt.encode(access_token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': ACCESS_TOKEN_EXPIRY
    }


def verify_token(token, token_type='access'):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        if payload.get('type') != token_type:
            raise UnauthorizedError("Invalid token type")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")


def get_token_from_event(event):
    """Extract token from API Gateway event"""
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization') or headers.get('authorization')
    
    if not auth_header:
        raise UnauthorizedError("Authorization header missing")
    
    if not auth_header.startswith('Bearer '):
        raise UnauthorizedError("Invalid authorization format")
    
    return auth_header.split('Bearer ')[1]


def require_auth(event):
    """Decorator helper to require authentication"""
    token = get_token_from_event(event)
    payload = verify_token(token, 'access')
    return payload['email']
