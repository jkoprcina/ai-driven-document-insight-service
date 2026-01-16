"""
Caching layer service for storing embeddings and model outputs.
Supports Redis and in-memory fallback.
"""
import redis
import json
import pickle
import logging
from typing import Optional, Any, Dict
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """Manage caching of embeddings and model outputs."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL
            ttl: Time to live for cached items (seconds)
        """
        self.ttl = ttl
        self.redis_url = redis_url
        self.redis_client = None
        self.in_memory_cache = {}  # Fallback to in-memory
        
        # Try to connect to Redis
        try:
            import redis
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis")
            self.use_redis = True
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
            self.use_redis = False
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        combined = f"{prefix}:" + ":".join(str(arg) for arg in args)
        return combined
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL
            
        Returns:
            Success status
        """
        try:
            ttl = ttl or self.ttl
            
            if self.use_redis and self.redis_client:
                # Serialize value
                serialized = pickle.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
            else:
                # In-memory fallback - store with timestamp
                self.in_memory_cache[key] = {
                    "value": value,
                    "ttl": ttl,
                    "timestamp": datetime.now()
                }
            
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cache value with TTL validation for in-memory cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            if self.use_redis and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
            else:
                # In-memory fallback - validate TTL
                if key in self.in_memory_cache:
                    entry = self.in_memory_cache[key]
                    # Check if TTL has expired
                    if "timestamp" in entry:
                        set_time = entry["timestamp"]
                        ttl = entry.get("ttl", self.ttl)
                        if datetime.now() > set_time + timedelta(seconds=ttl):
                            # Expired, remove and return None
                            del self.in_memory_cache[key]
                            return None
                    return entry["value"]
            
            return None
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None
    
    def cache_embeddings(self, session_id: str, embeddings: Dict) -> bool:
        """
        Cache document embeddings.
        
        Args:
            session_id: Session ID
            embeddings: Embeddings dictionary
            
        Returns:
            Success status
        """
        key = self._generate_key("embeddings", session_id)
        return self.set(key, embeddings, ttl=86400)  # 24h TTL
    
    def get_embeddings(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve cached embeddings.
        
        Args:
            session_id: Session ID
            
        Returns:
            Embeddings or None
        """
        key = self._generate_key("embeddings", session_id)
        return self.get(key)
    
    def cache_qa_result(self, session_id: str, question: str, result: Dict) -> bool:
        """
        Cache QA result.
        
        Args:
            session_id: Session ID
            question: Question text
            result: QA result dictionary
            
        Returns:
            Success status
        """
        # Create hash of question for key
        question_hash = hashlib.md5(question.encode()).hexdigest()
        key = self._generate_key("qa_result", session_id, question_hash)
        return self.set(key, result, ttl=3600)  # 1h TTL
    
    def get_qa_result(self, session_id: str, question: str) -> Optional[Dict]:
        """
        Retrieve cached QA result.
        
        Args:
            session_id: Session ID
            question: Question text
            
        Returns:
            QA result or None
        """
        question_hash = hashlib.md5(question.encode()).hexdigest()
        key = self._generate_key("qa_result", session_id, question_hash)
        return self.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
            else:
                if key in self.in_memory_cache:
                    del self.in_memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"Error deleting cache: {e}")
            return False
    
    def clear_session(self, session_id: str) -> int:
        """Clear all cache entries for a session."""
        try:
            count = 0
            if self.use_redis and self.redis_client:
                # Get all keys matching pattern (both formats: "key:session_id" and "key:session_id:subkey")
                pattern = f"*{session_id}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
            else:
                # In-memory fallback
                keys_to_delete = [k for k in self.in_memory_cache.keys() if session_id in k]
                for k in keys_to_delete:
                    del self.in_memory_cache[k]
                count = len(keys_to_delete)
            
            logger.info(f"Cleared {count} cache entries for session {session_id}")
            return count
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        try:
            if self.use_redis and self.redis_client:
                info = self.redis_client.info('memory')
                return {
                    "type": "redis",
                    "memory_used": info.get('used_memory', 0),
                    "memory_human": info.get('used_memory_human', 'N/A'),
                    "connected": True
                }
            else:
                return {
                    "type": "in-memory",
                    "num_entries": len(self.in_memory_cache),
                    "connected": True
                }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
