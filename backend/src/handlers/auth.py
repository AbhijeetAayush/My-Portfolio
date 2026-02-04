import json
import bcrypt
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.dynamodb import DynamoDBClient
from utils.jwt_handler import generate_tokens
from utils.validators import validate_email, validate_password
from utils.errors import error_response, ValidationError, UnauthorizedError


db = DynamoDBClient()


def lambda_handler(event, context):
    """Handle authentication requests"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')
        
        # Validate input
        email = validate_email(email)
        password = validate_password(password)
        
        # Get user from database
        user = db.get_user(email)
        if not user:
            raise UnauthorizedError("Invalid email or password")
        
        # Verify password
        password_hash = user.get('password_hash', '')
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            raise UnauthorizedError("Invalid email or password")
        
        # Update last login
        db.update_user_login(email)
        
        # Generate tokens
        tokens = generate_tokens(email)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'data': tokens
            })
        }
    
    except (ValidationError, UnauthorizedError) as e:
        return error_response(e)
    except Exception as e:
        print(f"Unexpected error in auth handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }
