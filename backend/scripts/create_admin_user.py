#!/usr/bin/env python3
"""
Script to create an admin user for the portfolio website.
Run this once after setting up the DynamoDB tables.
"""

import sys
import os
import bcrypt
import boto3
from getpass import getpass

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get table name from environment or use default
USERS_TABLE_NAME = os.environ.get('USERS_TABLE', 'UsersTable')

def create_admin_user():
    """Create an admin user in DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    users_table = dynamodb.Table(USERS_TABLE_NAME)
    
    print("Create Admin User")
    print("=" * 50)
    
    email = input("Enter email: ").strip().lower()
    if not email:
        print("Email is required!")
        return
    
    password = getpass("Enter password: ")
    if len(password) < 8:
        print("Password must be at least 8 characters!")
        return
    
    confirm_password = getpass("Confirm password: ")
    if password != confirm_password:
        print("Passwords do not match!")
        return
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Get current timestamp
    import time
    current_time = int(time.time())
    
    # Create user
    try:
        users_table.put_item(
            Item={
                'email': email,
                'password_hash': password_hash,
                'created_at': current_time,
                'last_login': 0
            }
        )
        print(f"\n✓ Admin user '{email}' created successfully!")
        print("\nYou can now login at /admin/login")
    except Exception as e:
        print(f"\n✗ Error creating user: {str(e)}")
        print("\nMake sure:")
        print("1. DynamoDB table exists")
        print("2. AWS credentials are configured")
        print("3. You have permissions to write to DynamoDB")

if __name__ == '__main__':
    create_admin_user()
