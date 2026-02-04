import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict, List, Optional
from decimal import Decimal
import json


# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')


def get_table(table_name_env_var):
    """Get DynamoDB table by environment variable name"""
    table_name = os.environ.get(table_name_env_var)
    if not table_name:
        raise ValueError(f"Environment variable {table_name_env_var} not set")
    return dynamodb.Table(table_name)


def decimal_to_int(obj):
    """Convert Decimal to int for JSON serialization"""
    if isinstance(obj, Decimal):
        return int(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_int(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_int(item) for item in obj]
    return obj


class DynamoDBClient:
    """DynamoDB client wrapper"""
    
    def __init__(self):
        self.portfolio_table = get_table('PORTFOLIO_TABLE')
        self.blogs_table = get_table('BLOGS_TABLE')
        self.comments_table = get_table('COMMENTS_TABLE')
        self.likes_table = get_table('LIKES_TABLE')
        self.users_table = get_table('USERS_TABLE')
    
    # Portfolio operations
    def get_portfolio(self, user_id: str = 'default') -> Optional[Dict]:
        """Get portfolio data"""
        try:
            response = self.portfolio_table.get_item(Key={'userId': user_id})
            item = response.get('Item')
            if item:
                return decimal_to_int(item)
            return None
        except Exception as e:
            print(f"Error getting portfolio: {str(e)}")
            return None
    
    def update_portfolio(self, user_id: str, data: Dict) -> Dict:
        """Update portfolio data"""
        # Remove None values
        update_data = {k: v for k, v in data.items() if v is not None}
        
        # Build update expression
        update_expr = "SET "
        expr_attr_names = {}
        expr_attr_values = {}
        
        for i, (key, value) in enumerate(update_data.items(), 1):
            update_expr += f"#{key} = :val{i}, "
            expr_attr_names[f"#{key}"] = key
            expr_attr_values[f":val{i}"] = value
        
        update_expr += "#updated_at = :updated_at"
        expr_attr_names["#updated_at"] = "updated_at"
        expr_attr_values[":updated_at"] = int(__import__('time').time())
        
        try:
            self.portfolio_table.update_item(
                Key={'userId': user_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
            return self.get_portfolio(user_id)
        except Exception as e:
            print(f"Error updating portfolio: {str(e)}")
            raise
    
    # Blog operations
    def create_blog(self, blog_data: Dict) -> Dict:
        """Create a new blog post"""
        try:
            self.blogs_table.put_item(Item=blog_data)
            return decimal_to_int(blog_data)
        except Exception as e:
            print(f"Error creating blog: {str(e)}")
            raise
    
    def get_blog_by_id(self, blog_id: str) -> Optional[Dict]:
        """Get blog by ID"""
        try:
            response = self.blogs_table.query(
                KeyConditionExpression=Key('blogId').eq(blog_id)
            )
            items = response.get('Items', [])
            if items:
                return decimal_to_int(items[0])
            return None
        except Exception as e:
            print(f"Error getting blog: {str(e)}")
            return None
    
    def get_blog_by_slug(self, slug: str) -> Optional[Dict]:
        """Get blog by slug"""
        try:
            response = self.blogs_table.query(
                IndexName='slugIndex',
                KeyConditionExpression=Key('slug').eq(slug)
            )
            items = response.get('Items', [])
            if items:
                return decimal_to_int(items[0])
            return None
        except Exception as e:
            print(f"Error getting blog by slug: {str(e)}")
            return None
    
    def get_all_blogs(self, limit: int = 50, last_key: Optional[Dict] = None) -> Dict:
        """Get all blogs with pagination"""
        try:
            scan_kwargs = {
                'Limit': limit
            }
            if last_key:
                scan_kwargs['ExclusiveStartKey'] = last_key
            
            response = self.blogs_table.scan(**scan_kwargs)
            items = response.get('Items', [])
            
            # Sort by created_at descending
            items.sort(key=lambda x: x.get('created_at', 0), reverse=True)
            
            return {
                'items': decimal_to_int(items),
                'last_key': response.get('LastEvaluatedKey')
            }
        except Exception as e:
            print(f"Error getting blogs: {str(e)}")
            raise
    
    def update_blog(self, blog_id: str, data: Dict) -> Dict:
        """Update blog post"""
        # Get existing blog
        blog = self.get_blog_by_id(blog_id)
        if not blog:
            return None
        
        # Merge updates
        blog.update(data)
        
        try:
            self.blogs_table.put_item(Item=blog)
            return decimal_to_int(blog)
        except Exception as e:
            print(f"Error updating blog: {str(e)}")
            raise
    
    def delete_blog(self, blog_id: str) -> bool:
        """Delete blog post"""
        try:
            blog = self.get_blog_by_id(blog_id)
            if not blog:
                return False
            
            self.blogs_table.delete_item(
                Key={
                    'blogId': blog_id,
                    'created_at': blog['created_at']
                }
            )
            return True
        except Exception as e:
            print(f"Error deleting blog: {str(e)}")
            raise
    
    # Comment operations
    def create_comment(self, comment_data: Dict) -> Dict:
        """Create a new comment"""
        try:
            self.comments_table.put_item(Item=comment_data)
            return decimal_to_int(comment_data)
        except Exception as e:
            print(f"Error creating comment: {str(e)}")
            raise
    
    def get_comments_by_blog(self, blog_id: str) -> List[Dict]:
        """Get all comments for a blog"""
        try:
            response = self.comments_table.query(
                IndexName='blogIdIndex',
                KeyConditionExpression=Key('blogId').eq(blog_id)
            )
            items = response.get('Items', [])
            # Filter approved comments
            approved = [item for item in items if item.get('status') == 'approved']
            # Sort by created_at ascending
            approved.sort(key=lambda x: x.get('created_at', 0))
            return decimal_to_int(approved)
        except Exception as e:
            print(f"Error getting comments: {str(e)}")
            return []
    
    def get_comment_by_id(self, comment_id: str) -> Optional[Dict]:
        """Get comment by ID"""
        try:
            response = self.comments_table.query(
                KeyConditionExpression=Key('commentId').eq(comment_id)
            )
            items = response.get('Items', [])
            if items:
                return decimal_to_int(items[0])
            return None
        except Exception as e:
            print(f"Error getting comment: {str(e)}")
            return None
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete comment"""
        try:
            comment = self.get_comment_by_id(comment_id)
            if not comment:
                return False
            
            self.comments_table.delete_item(
                Key={
                    'commentId': comment_id,
                    'created_at': comment['created_at']
                }
            )
            return True
        except Exception as e:
            print(f"Error deleting comment: {str(e)}")
            raise
    
    # Like operations
    def add_like(self, blog_id: str, timestamp_ip: str) -> bool:
        """Add a like to a blog"""
        try:
            self.likes_table.put_item(
                Item={
                    'blogId': blog_id,
                    'timestamp_ip': timestamp_ip,
                    'ttl': int(__import__('time').time()) + 30 * 24 * 60 * 60
                }
            )
            return True
        except Exception as e:
            print(f"Error adding like: {str(e)}")
            raise
    
    def get_likes_count(self, blog_id: str) -> int:
        """Get likes count for a blog"""
        try:
            response = self.likes_table.query(
                KeyConditionExpression=Key('blogId').eq(blog_id)
            )
            return len(response.get('Items', []))
        except Exception as e:
            print(f"Error getting likes count: {str(e)}")
            return 0
    
    def has_liked(self, blog_id: str, timestamp_ip: str) -> bool:
        """Check if IP has already liked"""
        try:
            response = self.likes_table.get_item(
                Key={
                    'blogId': blog_id,
                    'timestamp_ip': timestamp_ip
                }
            )
            return 'Item' in response
        except Exception as e:
            print(f"Error checking like: {str(e)}")
            return False
    
    # User operations
    def get_user(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            response = self.users_table.get_item(Key={'email': email})
            item = response.get('Item')
            if item:
                return decimal_to_int(item)
            return None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def update_user_login(self, email: str):
        """Update user last login time"""
        try:
            self.users_table.update_item(
                Key={'email': email},
                UpdateExpression="SET last_login = :login",
                ExpressionAttributeValues={
                    ':login': int(__import__('time').time())
                }
            )
        except Exception as e:
            print(f"Error updating user login: {str(e)}")
            # Don't raise, this is not critical
