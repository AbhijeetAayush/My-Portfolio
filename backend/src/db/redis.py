import os
import json
import redis
from typing import Optional, Any
from urllib.parse import urlparse


class RedisClient:
    """Upstash Redis client wrapper"""
    
    def __init__(self):
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable not set")
        
        # Parse Redis URL (Upstash format: redis://default:password@host:port)
        parsed = urlparse(redis_url)
        
        self.client = redis.Redis(
            host=parsed.hostname,
            port=parsed.port or 6379,
            password=parsed.password,
            ssl=True,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Redis set error: {str(e)}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            self.client.delete(key)
        except Exception as e:
            print(f"Redis delete error: {str(e)}")
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception as e:
            print(f"Redis delete_pattern error: {str(e)}")
    
    def invalidate_portfolio_cache(self):
        """Invalidate portfolio cache"""
        self.delete('portfolio_data')
    
    def invalidate_blog_cache(self, blog_id: Optional[str] = None):
        """Invalidate blog cache"""
        if blog_id:
            self.delete(f"blogs:{blog_id}")
        self.delete('blogs:list')
        self.delete_pattern('blogs:*')
    
    def invalidate_comments_cache(self, blog_id: str):
        """Invalidate comments cache for a blog"""
        self.delete(f"comments:{blog_id}")
    
    def invalidate_likes_cache(self, blog_id: str):
        """Invalidate likes cache for a blog"""
        self.delete(f"likes_count:{blog_id}")
