"""
Cortex Module
Runtime Architecture v2 - Cross-thread synthesized summaries/briefings

This module provides:
- Briefing snapshots
- Compacted thread summaries
- Pending action synthesis
- Cross-project/state summaries

Status: PARTIAL (Redis cache + Postgres adapter interface)
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

from app.memory.types import CortexMemory
from app.core.runtime_config import get_runtime_config

logger = logging.getLogger(__name__)


class CortexStore:
    """
    Cortex/briefing store.
    
    Uses Redis for hot/cached briefs,
    with Postgres backing for durable archives.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.config = get_runtime_config()
        self.redis_url = redis_url or self.config.redis_url
        self._client = None
        
        if not self.config.memory_cortex_enabled:
            logger.warning("Cortex memory is disabled in config")
            return
        
        if REDIS_AVAILABLE:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                )
                self._client.ping()
                logger.info("Cortex Redis cache connected")
            except Exception as e:
                logger.warning(f"Could not connect to Redis for cortex: {e}")
                self._client = None
    
    def _key(self, thread_id: str) -> str:
        """Generate Redis key for cortex brief"""
        return f"cortex:brief:{thread_id}"
    
    async def create_briefing(
        self,
        thread_id: str,
        tenant_id: str,
        summary: str,
        pending_actions: list[dict],
        recommendations: Optional[list[dict]] = None,
        execution_request_id: Optional[str] = None,
    ) -> str:
        """
        Create a new briefing.
        
        Args:
            thread_id: Thread identifier
            tenant_id: Tenant ID
            summary: Brief summary
            pending_actions: List of pending actions
            recommendations: Optional recommendations
            execution_request_id: Associated execution
            
        Returns:
            briefing_id
        """
        briefing_id = f"brief-{datetime.now().timestamp()}"
        
        briefing_data = {
            "briefing_id": briefing_id,
            "thread_id": thread_id,
            "tenant_id": tenant_id,
            "summary": summary,
            "pending_actions": pending_actions,
            "recommendations": recommendations or [],
            "execution_request_id": execution_request_id,
            "created_at": datetime.now().isoformat(),
        }
        
        # Store in Redis cache (hot)
        if self._client:
            try:
                key = self._key(thread_id)
                self._client.setex(
                    key,
                    604800,  # 7 days TTL
                    json.dumps(briefing_data)
                )
                logger.debug(f"Created briefing {briefing_id} for thread {thread_id}")
            except Exception as e:
                logger.error(f"Error caching briefing: {e}")
        
        # Archive to Postgres (durable) - would use SQLAlchemy
        # This is a placeholder
        logger.debug(f"[ADAPTER] Would archive briefing {briefing_id} to Postgres")
        
        return briefing_id
    
    async def get_briefing(
        self,
        thread_id: str,
    ) -> Optional[dict]:
        """
        Get current briefing for a thread.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            Briefing data or None
        """
        if not self._client:
            logger.debug(f"[PLACEHOLDER] Would get briefing for thread {thread_id}")
            return None
        
        try:
            key = self._key(thread_id)
            data = self._client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting briefing: {e}")
            return None
    
    async def update_briefing(
        self,
        thread_id: str,
        summary: Optional[str] = None,
        pending_actions: Optional[list[dict]] = None,
        recommendations: Optional[list[dict]] = None,
    ) -> bool:
        """
        Update existing briefing.
        
        Args:
            thread_id: Thread identifier
            summary: New summary
            pending_actions: Updated pending actions
            recommendations: Updated recommendations
            
        Returns:
            True if successful
        """
        existing = await self.get_briefing(thread_id)
        if not existing:
            return False
        
        if summary:
            existing["summary"] = summary
        if pending_actions:
            existing["pending_actions"] = pending_actions
        if recommendations:
            existing["recommendations"] = recommendations
        
        existing["updated_at"] = datetime.now().isoformat()
        
        if self._client:
            try:
                key = self._key(thread_id)
                self._client.setex(
                    key,
                    604800,
                    json.dumps(existing)
                )
                return True
            except Exception as e:
                logger.error(f"Error updating briefing: {e}")
                return False
        
        return True
    
    async def delete_briefing(
        self,
        thread_id: str,
    ) -> bool:
        """Delete briefing for a thread"""
        if self._client:
            try:
                key = self._key(thread_id)
                self._client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Error deleting briefing: {e}")
                return False
        return True
    
    async def list_briefings(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """
        List recent briefings for a tenant.
        
        Args:
            tenant_id: Tenant ID
            limit: Maximum to return
            
        Returns:
            List of briefings
        """
        # Would query Postgres - placeholder
        logger.debug(f"[ADAPTER] Would list briefings for tenant {tenant_id}")
        return []


# Global instance
_cortex_store: Optional[CortexStore] = None


def get_cortex_store() -> CortexStore:
    """Get cortex store instance"""
    global _cortex_store
    if _cortex_store is None:
        _cortex_store = CortexStore()
    return _cortex_store


__all__ = [
    "CortexStore",
    "get_cortex_store",
]
