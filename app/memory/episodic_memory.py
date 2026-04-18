"""
Episodic Memory Module
Runtime Architecture v2 - Event/history-oriented memory

This module provides storage for:
- Important interactions
- Decisions made
- Approvals
- Overrides
- Delegation events
- Notable outcomes

Status: PARTIAL (Redis cache layer implemented, Postgres backing via existing tables)
"""
import json
import logging
from typing import Optional, Any
from datetime import datetime, timedelta

# Try to import redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from app.memory.types import EpisodicMemory
from app.core.runtime_config import get_runtime_config

logger = logging.getLogger(__name__)


class EpisodicMemoryStore:
    """
    Episodic memory store.
    
    Uses Redis as LRU cache layer for recent events,
    with Postgres as backing store (via existing execution_history table).
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.config = get_runtime_config()
        self.redis_url = redis_url or self.config.redis_url
        self._client = None
        
        if not self.config.memory_episodic_enabled:
            logger.warning("Episodic memory is disabled in config")
            return
        
        if REDIS_AVAILABLE:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                )
                self._client.ping()
                logger.info("Episodic memory Redis cache connected")
            except Exception as e:
                logger.warning(f"Could not connect to Redis for episodic: {e}")
                self._client = None
    
    def _cache_key(self, thread_id: str, event_type: str) -> str:
        """Generate cache key for episodic event"""
        return f"episodic:{thread_id}:{event_type}"
    
    async def store_event(
        self,
        thread_id: str,
        tenant_id: str,
        event_type: str,
        event_data: dict,
        execution_request_id: Optional[str] = None,
    ) -> bool:
        """
        Store an episodic event.
        
        Args:
            thread_id: Thread identifier
            tenant_id: Tenant ID
            event_type: Type of event (tool_call, decision, approval, etc.)
            event_data: Event content
            execution_request_id: Associated execution request
            
        Returns:
            True if successful
        """
        # Store in Redis cache for fast access
        if self._client:
            try:
                key = f"episodic:{thread_id}"
                event = {
                    "memory_id": f"ep-{datetime.now().timestamp()}",
                    "thread_id": thread_id,
                    "tenant_id": tenant_id,
                    "event_type": event_type,
                    "event_data": event_data,
                    "execution_request_id": execution_request_id,
                    "created_at": datetime.now().isoformat(),
                }
                # Add to list, keep last 100
                self._client.lpush(key, json.dumps(event))
                self._client.ltrim(key, 0, 99)
                self._client.expire(key, 86400)  # 24 hour TTL
                logger.debug(f"Stored episodic event {event_type} for thread {thread_id}")
            except Exception as e:
                logger.error(f"Error storing episodic event: {e}")
        
        # NOTE: Long-term storage via existing execution_history table
        # This is handled by the existing control-plane service layer
        
        return True
    
    async def get_events(
        self,
        thread_id: str,
        limit: int = 50,
        event_type: Optional[str] = None,
    ) -> list[dict]:
        """
        Get episodic events for a thread.
        
        Args:
            thread_id: Thread identifier
            limit: Maximum events to return
            event_type: Optional filter by event type
            
        Returns:
            List of events
        """
        if not self._client:
            logger.debug(f"[PLACEHOLDER] Would get episodic events for thread {thread_id}")
            return []
        
        try:
            key = f"episodic:{thread_id}"
            events_raw = self._client.lrange(key, 0, limit - 1)
            
            events = []
            for event_str in events_raw:
                event = json.loads(event_str)
                if event_type is None or event.get("event_type") == event_type:
                    events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error getting episodic events: {e}")
            return []
    
    async def get_recent_events(
        self,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        Get recent events across all threads.
        
        Args:
            tenant_id: Optional tenant filter
            limit: Maximum events to return
            
        Returns:
            List of recent events
        """
        # NOTE: This would query Postgres via execution_history
        # For now, placeholder
        logger.debug(f"[PLACEHOLDER] Would get recent events for tenant {tenant_id}")
        return []


# Global instance
_episodic_memory: Optional[EpisodicMemoryStore] = None


def get_episodic_memory() -> EpisodicMemoryStore:
    """Get episodic memory store instance"""
    global _episodic_memory
    if _episodic_memory is None:
        _episodic_memory = EpisodicMemoryStore()
    return _episodic_memory


__all__ = [
    "EpisodicMemoryStore",
    "get_episodic_memory",
]
