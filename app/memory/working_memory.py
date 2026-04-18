"""
Working Memory Module
Runtime Architecture v2 - Hot/session/working memory using Redis

This module provides fast in-memory storage for:
- Current conversation state
- Active branch state  
- Temporary context
- Hot coordination cache
- Recent tool outputs

Status: IMPLEMENTED (using Redis)
"""
import json
import logging
from typing import Optional, Any
from datetime import datetime, timedelta

# Try to import redis - if not available, use placeholder
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from app.memory.types import WorkingMemory
from app.core.runtime_config import get_runtime_config

logger = logging.getLogger(__name__)


class WorkingMemoryStore:
    """
    Working memory store using Redis.
    
    Provides fast, TTL-based storage for session state.
    Keys are prefixed with "working:" for isolation.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.config = get_runtime_config()
        self.redis_url = redis_url or self.config.redis_url
        self._client = None
        
        if not self.config.memory_working_enabled:
            logger.warning("Working memory is disabled in config")
            return
            
        if REDIS_AVAILABLE:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                # Test connection
                self._client.ping()
                logger.info(f"Connected to Redis at {self.redis_url}")
            except Exception as e:
                logger.warning(f"Could not connect to Redis: {e}. Using placeholder.")
                self._client = None
    
    def _key(self, thread_id: str) -> str:
        """Generate Redis key for thread"""
        return f"working:{thread_id}"
    
    async def set(
        self,
        thread_id: str,
        state_data: dict,
        ttl_seconds: Optional[int] = None,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """
        Set working memory for a thread.
        
        Args:
            thread_id: Thread/session identifier
            state_data: State to store
            ttl_seconds: Time-to-live (default from config)
            tenant_id: Tenant for isolation (optional)
            
        Returns:
            True if successful
        """
        if not self._client:
            logger.debug(f"[PLACEHOLDER] Would set working memory for thread {thread_id}: {state_data}")
            return True
        
        ttl = ttl_seconds or self.config.runtime_timeout_seconds
        key = self._key(thread_id)
        
        try:
            self._client.setex(
                key,
                ttl,
                json.dumps({
                    "thread_id": thread_id,
                    "tenant_id": tenant_id,
                    "state_data": state_data,
                    "updated_at": datetime.now().isoformat(),
                })
            )
            return True
        except Exception as e:
            logger.error(f"Error setting working memory: {e}")
            return False
    
    async def get(self, thread_id: str) -> Optional[dict]:
        """
        Get working memory for a thread.
        
        Args:
            thread_id: Thread/session identifier
            
        Returns:
            State data or None if not found
        """
        if not self._client:
            logger.debug(f"[PLACEHOLDER] Would get working memory for thread {thread_id}")
            return None
        
        key = self._key(thread_id)
        
        try:
            data = self._client.get(key)
            if data:
                parsed = json.loads(data)
                return parsed.get("state_data")
            return None
        except Exception as e:
            logger.error(f"Error getting working memory: {e}")
            return None
    
    async def delete(self, thread_id: str) -> bool:
        """
        Delete working memory for a thread.
        
        Args:
            thread_id: Thread/session identifier
            
        Returns:
            True if successful
        """
        if not self._client:
            logger.debug(f"[PLACEHOLDER] Would delete working memory for thread {thread_id}")
            return True
        
        key = self._key(thread_id)
        
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting working memory: {e}")
            return False
    
    async def extend_ttl(self, thread_id: str, ttl_seconds: int) -> bool:
        """
        Extend TTL for working memory.
        
        Args:
            thread_id: Thread/session identifier
            ttl_seconds: New TTL in seconds
            
        Returns:
            True if successful
        """
        if not self._client:
            return True
        
        key = self._key(thread_id)
        
        try:
            self._client.expire(key, ttl_seconds)
            return True
        except Exception as e:
            logger.error(f"Error extending TTL: {e}")
            return False
    
    async def exists(self, thread_id: str) -> bool:
        """Check if working memory exists for thread"""
        if not self._client:
            return False
        
        key = self._key(thread_id)
        return bool(self._client.exists(key))
    
    async def health_check(self) -> bool:
        """Check if Redis is available"""
        if not self._client:
            return False
        try:
            return self._client.ping()
        except:
            return False


# Global instance
_working_memory: Optional[WorkingMemoryStore] = None


def get_working_memory() -> WorkingMemoryStore:
    """Get working memory store instance"""
    global _working_memory
    if _working_memory is None:
        _working_memory = WorkingMemoryStore()
    return _working_memory


__all__ = [
    "WorkingMemoryStore",
    "get_working_memory",
    "REDIS_AVAILABLE",
]
