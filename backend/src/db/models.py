"""Data models for DynamoDB items"""

from datetime import datetime
from typing import List, Dict, Optional
import uuid


def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())


def get_timestamp():
    """Get current timestamp"""
    return int(datetime.utcnow().timestamp())


class Portfolio:
    """Portfolio data model"""
    def __init__(self, data: Dict):
        self.user_id = data.get('userId', 'default')
        self.profile_pic_url = data.get('profile_pic_url', '')
        self.bio = data.get('bio', '')
        self.email = data.get('email', '')
        self.social_links = data.get('social_links', {})
        self.about_content = data.get('about_content', '')
        self.projects = data.get('projects', [])
        self.experience = data.get('experience', [])
        self.updated_at = data.get('updated_at', get_timestamp())
    
    def to_dict(self):
        return {
            'userId': self.user_id,
            'profile_pic_url': self.profile_pic_url,
            'bio': self.bio,
            'email': self.email,
            'social_links': self.social_links,
            'about_content': self.about_content,
            'projects': self.projects,
            'experience': self.experience,
            'updated_at': self.updated_at
        }


class Blog:
    """Blog post data model"""
    def __init__(self, data: Dict):
        self.blog_id = data.get('blogId', generate_id())
        self.created_at = data.get('created_at', get_timestamp())
        self.title = data.get('title', '')
        self.slug = data.get('slug', '')
        self.content = data.get('content', '')
        self.featured_image_url = data.get('featured_image_url', '')
        self.tags = data.get('tags', [])
        self.category = data.get('category', '')
        self.author = data.get('author', '')
        self.reading_time = data.get('reading_time', 0)
        self.likes_count = data.get('likes_count', 0)
        self.seo_description = data.get('seo_description', '')
        self.published_at = data.get('published_at', self.created_at)
    
    def to_dict(self):
        return {
            'blogId': self.blog_id,
            'created_at': self.created_at,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'featured_image_url': self.featured_image_url,
            'tags': self.tags,
            'category': self.category,
            'author': self.author,
            'reading_time': self.reading_time,
            'likes_count': self.likes_count,
            'seo_description': self.seo_description,
            'published_at': self.published_at
        }
    
    def calculate_reading_time(self, content: str):
        """Calculate reading time in minutes"""
        words_per_minute = 200
        word_count = len(content.split())
        return max(1, round(word_count / words_per_minute))


class Comment:
    """Comment data model"""
    def __init__(self, data: Dict):
        self.comment_id = data.get('commentId', generate_id())
        self.created_at = data.get('created_at', get_timestamp())
        self.blog_id = data.get('blogId', '')
        self.author_name = data.get('author_name', '')
        self.author_email = data.get('author_email', '')
        self.content = data.get('content', '')
        self.status = data.get('status', 'approved')
    
    def to_dict(self):
        return {
            'commentId': self.comment_id,
            'created_at': self.created_at,
            'blogId': self.blog_id,
            'author_name': self.author_name,
            'author_email': self.author_email,
            'content': self.content,
            'status': self.status
        }


class Like:
    """Like data model"""
    def __init__(self, data: Dict):
        self.blog_id = data.get('blogId', '')
        self.timestamp_ip = data.get('timestamp_ip', '')
        self.ttl = data.get('ttl', get_timestamp() + 30 * 24 * 60 * 60)  # 30 days
    
    def to_dict(self):
        return {
            'blogId': self.blog_id,
            'timestamp_ip': self.timestamp_ip,
            'ttl': self.ttl
        }
