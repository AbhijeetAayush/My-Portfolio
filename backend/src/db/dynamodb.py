import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, List, Optional
from decimal import Decimal
import json
import time


# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Constants for key prefixes
BLOG_ALL_PREFIX = 'BLOG#ALL'
PORTFOLIO_PREFIX = 'PORTFOLIO#'
BLOG_PREFIX = 'BLOG#'
USER_PREFIX = 'USER#'
LIKE_PREFIX = 'LIKE#'
SLUG_PREFIX = 'SLUG#'
METADATA_SK = 'METADATA'


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
    """
    Single-table DynamoDB client with optimized queries (no scans)
    
    Key Structure:
    - PK: Entity identifier (e.g., "PORTFOLIO#default", "BLOG#{blogId}", "USER#{email}", "LIKE#{blogId}#{timestamp}#{ip}")
    - SK: Sort key (e.g., "METADATA", timestamp, slug)
    
    GSI1 (BlogsByDate): GSI1PK="BLOG#ALL", GSI1SK=created_at (for listing blogs)
    GSI2 (BlogBySlug): GSI2PK="SLUG#{slug}", GSI2SK=blogId (for slug lookups)
    GSI3 (LikesByBlog): GSI3PK="LIKE#{blogId}", GSI3SK="{timestamp}#{ip}" (for likes)
    """
    
    def __init__(self):
        self.table = get_table('DATA_TABLE')
    
    # Portfolio operations
    def get_portfolio(self, user_id: str = 'default') -> Optional[Dict]:
        """Get portfolio data - Query operation"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f'{PORTFOLIO_PREFIX}{user_id}',
                    'SK': METADATA_SK
                }
            )
            item = response.get('Item')
            if item:
                # Remove internal keys before returning
                item.pop('PK', None)
                item.pop('SK', None)
                item.pop('GSI1PK', None)
                item.pop('GSI1SK', None)
                item.pop('GSI2PK', None)
                item.pop('GSI2SK', None)
                item.pop('GSI3PK', None)
                item.pop('GSI3SK', None)
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
        expr_attr_values[":updated_at"] = int(time.time())
        
        try:
            self.table.update_item(
                Key={
                    'PK': f'{PORTFOLIO_PREFIX}{user_id}',
                    'SK': METADATA_SK
                },
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
        blog_id = blog_data.get('blogId')
        created_at = blog_data.get('created_at', int(time.time()))
        slug = blog_data.get('slug', '')
        
        # Prepare item with all keys
        item = {
            'PK': f'{BLOG_PREFIX}{blog_id}',
            'SK': METADATA_SK,
            'GSI1PK': BLOG_ALL_PREFIX,
            'GSI1SK': created_at,
            'GSI2PK': f'{SLUG_PREFIX}{slug}',
            'GSI2SK': blog_id,
            **blog_data
        }
        
        try:
            self.table.put_item(Item=item)
            # Return clean data
            return decimal_to_int(blog_data)
        except Exception as e:
            print(f"Error creating blog: {str(e)}")
            raise
    
    def get_blog_by_id(self, blog_id: str) -> Optional[Dict]:
        """Get blog by ID - GetItem operation"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f'{BLOG_PREFIX}{blog_id}',
                    'SK': METADATA_SK
                }
            )
            item = response.get('Item')
            if item:
                # Remove internal keys
                item.pop('PK', None)
                item.pop('SK', None)
                item.pop('GSI1PK', None)
                item.pop('GSI1SK', None)
                item.pop('GSI2PK', None)
                item.pop('GSI2SK', None)
                item.pop('GSI3PK', None)
                item.pop('GSI3SK', None)
                return decimal_to_int(item)
            return None
        except Exception as e:
            print(f"Error getting blog: {str(e)}")
            return None
    
    def get_blog_by_slug(self, slug: str) -> Optional[Dict]:
        """Get blog by slug - Query GSI2 operation"""
        try:
            response = self.table.query(
                IndexName='BlogBySlug',
                KeyConditionExpression=Key('GSI2PK').eq(f'{SLUG_PREFIX}{slug}')
            )
            items = response.get('Items', [])
            if items:
                item = items[0]
                # Get the actual blog using the blogId from GSI2SK
                blog_id = item.get('GSI2SK')
                return self.get_blog_by_id(blog_id)
            return None
        except Exception as e:
            print(f"Error getting blog by slug: {str(e)}")
            return None
    
    def get_all_blogs(self, limit: int = 50, last_key: Optional[Dict] = None) -> Dict:
        """Get all blogs sorted by date - Query GSI1 operation (NO SCAN)"""
        try:
            query_kwargs = {
                'IndexName': 'BlogsByDate',
                'KeyConditionExpression': Key('GSI1PK').eq(BLOG_ALL_PREFIX),
                'ScanIndexForward': False,  # Descending order (newest first)
                'Limit': limit
            }
            
            if last_key:
                # Convert last_key to proper format for GSI
                query_kwargs['ExclusiveStartKey'] = {
                    'PK': last_key.get('PK'),
                    'SK': last_key.get('SK'),
                    'GSI1PK': last_key.get('GSI1PK'),
                    'GSI1SK': last_key.get('GSI1SK')
                }
            
            response = self.table.query(**query_kwargs)
            items = response.get('Items', [])
            
            # Clean items and extract blog data
            cleaned_items = []
            for item in items:
                # Get full blog data
                blog_id = item.get('blogId')
                if blog_id:
                    blog = self.get_blog_by_id(blog_id)
                    if blog:
                        cleaned_items.append(blog)
            
            # Prepare last_key for pagination
            last_eval_key = response.get('LastEvaluatedKey')
            pagination_key = None
            if last_eval_key:
                pagination_key = {
                    'PK': last_eval_key.get('PK'),
                    'SK': last_eval_key.get('SK'),
                    'GSI1PK': last_eval_key.get('GSI1PK'),
                    'GSI1SK': last_eval_key.get('GSI1SK')
                }
            
            return {
                'items': cleaned_items,
                'last_key': pagination_key
            }
        except Exception as e:
            print(f"Error getting blogs: {str(e)}")
            raise
    
    def update_blog(self, blog_id: str, data: Dict) -> Optional[Dict]:
        """Update blog post"""
        # Get existing blog to preserve GSI keys
        blog = self.get_blog_by_id(blog_id)
        if not blog:
            return None
        
        # Merge updates
        blog.update(data)
        
        # Reconstruct item with GSI keys
        created_at = blog.get('created_at', int(time.time()))
        slug = blog.get('slug', '')
        
        item = {
            'PK': f'{BLOG_PREFIX}{blog_id}',
            'SK': METADATA_SK,
            'GSI1PK': BLOG_ALL_PREFIX,
            'GSI1SK': created_at,
            'GSI2PK': f'{SLUG_PREFIX}{slug}',
            'GSI2SK': blog_id,
            **blog
        }
        
        try:
            self.table.put_item(Item=item)
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
            
            self.table.delete_item(
                Key={
                    'PK': f'{BLOG_PREFIX}{blog_id}',
                    'SK': METADATA_SK
                }
            )
            return True
        except Exception as e:
            print(f"Error deleting blog: {str(e)}")
            raise
    
    # Like operations
    def add_like(self, blog_id: str, timestamp_ip: str) -> bool:
        """Add a like to a blog"""
        try:
            ttl = int(time.time()) + 30 * 24 * 60 * 60  # 30 days
            
            self.table.put_item(
                Item={
                    'PK': f'{LIKE_PREFIX}{blog_id}#{timestamp_ip}',
                    'SK': timestamp_ip,
                    'GSI3PK': f'{LIKE_PREFIX}{blog_id}',
                    'GSI3SK': timestamp_ip,
                    'TTL': ttl
                }
            )
            return True
        except Exception as e:
            print(f"Error adding like: {str(e)}")
            raise
    
    def get_likes_count(self, blog_id: str) -> int:
        """Get likes count for a blog - Query GSI3 operation"""
        try:
            response = self.table.query(
                IndexName='LikesByBlog',
                KeyConditionExpression=Key('GSI3PK').eq(f'{LIKE_PREFIX}{blog_id}'),
                Select='COUNT'  # Only count, don't return items
            )
            return response.get('Count', 0)
        except Exception as e:
            print(f"Error getting likes count: {str(e)}")
            return 0
    
    def has_liked(self, blog_id: str, timestamp_ip: str) -> bool:
        """Check if IP has already liked - Query GSI3 operation"""
        try:
            response = self.table.query(
                IndexName='LikesByBlog',
                KeyConditionExpression=Key('GSI3PK').eq(f'{LIKE_PREFIX}{blog_id}') & Key('GSI3SK').eq(timestamp_ip),
                Limit=1
            )
            return len(response.get('Items', [])) > 0
        except Exception as e:
            print(f"Error checking like: {str(e)}")
            return False
    
    # User operations
    def get_user(self, email: str) -> Optional[Dict]:
        """Get user by email - GetItem operation"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f'{USER_PREFIX}{email}',
                    'SK': METADATA_SK
                }
            )
            item = response.get('Item')
            if item:
                # Remove internal keys
                item.pop('PK', None)
                item.pop('SK', None)
                return decimal_to_int(item)
            return None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def update_user_login(self, email: str):
        """Update user last login time"""
        try:
            self.table.update_item(
                Key={
                    'PK': f'{USER_PREFIX}{email}',
                    'SK': METADATA_SK
                },
                UpdateExpression="SET last_login = :login",
                ExpressionAttributeValues={
                    ':login': int(time.time())
                }
            )
        except Exception as e:
            print(f"Error updating user login: {str(e)}")
            # Don't raise, this is not critical
