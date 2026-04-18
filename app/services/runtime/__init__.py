"""
Runtime Registry Service
Phase 0 - Runtime registry and selection for orchestrator

This service provides:
- Runtime registration and management
- Runtime health monitoring
- Runtime selection for task execution

Status: IMPLEMENTED (internal + admin APIs)
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.runtime_types import RuntimeType, RuntimeCapability

logger = logging.getLogger(__name__)


class RuntimeRegistryService:
    """
    Central runtime registry service.
    
    Manages runtime registration, health, and selection.
    """
    
    def __init__(self):
        self._runtimes: Dict[str, Dict[str, Any]] = {}
        self._instances: Dict[str, Dict[str, Any]] = {}
    
    # ========== Registry Management ==========
    
    def register_runtime(self, runtime_id: str, runtime_data: Dict[str, Any]) -> None:
        """Register a new runtime."""
        self._runtimes[runtime_id] = {
            "id": runtime_id,
            "name": runtime_data.get("name", runtime_id),
            "type": runtime_data.get("type", RuntimeType.LANGGRAPH_ORCHESTRATOR.value),
            "description": runtime_data.get("description", ""),
            "max_context_tokens": runtime_data.get("max_context_tokens", 200000),
            "supports_streaming": runtime_data.get("supports_streaming", False),
            "supports_tools": runtime_data.get("supports_tools", True),
            "supports_checkpoint": runtime_data.get("supports_checkpoint", False),
            "enabled": runtime_data.get("enabled", True),
            "created_at": datetime.utcnow(),
        }
        logger.info(f"Registered runtime: {runtime_id}")
    
    def get_runtime(self, runtime_id: str) -> Optional[Dict[str, Any]]:
        """Get runtime by ID."""
        return self._runtimes.get(runtime_id)
    
    def list_runtimes(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """List all runtimes."""
        runtimes = list(self._runtimes.values())
        if enabled_only:
            runtimes = [r for r in runtimes if r.get("enabled", True)]
        return runtimes
    
    def update_runtime(self, runtime_id: str, updates: Dict[str, Any]) -> bool:
        """Update runtime configuration."""
        if runtime_id not in self._runtimes:
            return False
        self._runtimes[runtime_id].update(updates)
        self._runtimes[runtime_id]["updated_at"] = datetime.utcnow()
        return True
    
    # ========== Instance Management ==========
    
    def register_instance(
        self,
        runtime_id: str,
        instance_id: str,
        instance_data: Dict[str, Any],
    ) -> bool:
        """Register a runtime instance."""
        if runtime_id not in self._runtimes:
            return False
        
        self._instances[instance_id] = {
            "id": instance_id,
            "runtime_id": runtime_id,
            "instance_type": instance_data.get("instance_type", "local"),
            "endpoint": instance_data.get("endpoint", ""),
            "status": "healthy",
            "health_score": 100.0,
            "last_heartbeat": datetime.utcnow(),
            "created_at": datetime.utcnow(),
        }
        logger.info(f"Registered instance: {instance_id} for runtime: {runtime_id}")
        return True
    
    def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get instance by ID."""
        return self._instances.get(instance_id)
    
    def list_instances(self, runtime_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List runtime instances."""
        instances = list(self._instances.values())
        if runtime_id:
            instances = [i for i in instances if i["runtime_id"] == runtime_id]
        return instances
    
    def update_instance_health(
        self,
        instance_id: str,
        status: str,
        health_score: float,
    ) -> bool:
        """Update instance health status."""
        if instance_id not in self._instances:
            return False
        self._instances[instance_id]["status"] = status
        self._instances[instance_id]["health_score"] = health_score
        self._instances[instance_id]["last_heartbeat"] = datetime.utcnow()
        return True
    
    # ========== Selection ==========
    
    def select_runtime(
        self,
        task_type: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Select best runtime for task type.
        
        Args:
            task_type: Type of task (coding, conversation, etc.)
            tenant_id: Optional tenant ID for policy lookup
            
        Returns:
            Runtime ID or None if no suitable runtime found
        """
        # Find enabled runtimes that support the task type
        candidates = []
        for runtime in self._runtimes.values():
            if not runtime.get("enabled", True):
                continue
            
            # Check if runtime supports this task type (by tags/capabilities)
            capabilities = runtime.get("capabilities", [])
            if task_type in capabilities or "all" in capabilities:
                candidates.append(runtime)
        
        if not candidates:
            # Fallback to any enabled runtime
            candidates = [r for r in self._runtimes.values() if r.get("enabled", True)]
        
        if not candidates:
            return None
        
        # Select first candidate (could enhance with health scoring)
        return candidates[0]["id"]
    
    def get_healthy_instances(self, runtime_id: str) -> List[Dict[str, Any]]:
        """Get healthy instances for a runtime."""
        instances = self.list_instances(runtime_id)
        return [i for i in instances if i.get("status") == "healthy"]
    
    # ========== Health Check ==========
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary."""
        total_instances = len(self._instances)
        healthy = len([i for i in self._instances.values() if i.get("status") == "healthy"])
        
        return {
            "total_runtimes": len(self._runtimes),
            "total_instances": total_instances,
            "healthy_instances": healthy,
            "unhealthy_instances": total_instances - healthy,
            "status": "healthy" if healthy == total_instances else "degraded",
        }


# Global instance
_registry_service: Optional[RuntimeRegistryService] = None


def get_runtime_registry_service() -> RuntimeRegistryService:
    """Get global runtime registry service."""
    global _registry_service
    if _registry_service is None:
        _registry_service = RuntimeRegistryService()
        _initialize_default_runtimes(_registry_service)
    return _registry_service


def _initialize_default_runtimes(service: RuntimeRegistryService):
    """Initialize default runtimes."""
    defaults = [
        {
            "id": "langgraph",
            "name": "LangGraph Orchestrator",
            "type": "langgraph",
            "description": "LangGraph-based workflow orchestration",
            "capabilities": ["coding", "autonomous", "collaboration"],
            "max_context_tokens": 200000,
            "supports_tools": True,
            "supports_checkpoint": True,
        },
        {
            "id": "openai_agents",
            "name": "OpenAI Agents SDK",
            "type": "openai_agents",
            "description": "OpenAI Agents SDK runtime",
            "capabilities": ["conversation", "general"],
            "max_context_tokens": 128000,
            "supports_streaming": True,
            "supports_tools": True,
        },
        {
            "id": "claude_agent",
            "name": "Claude Agent SDK",
            "type": "claude_agent",
            "description": "Claude Agent SDK runtime",
            "capabilities": ["coding", "conversation"],
            "max_context_tokens": 200000,
            "supports_tools": True,
        },
    ]
    
    for runtime in defaults:
        service.register_runtime(runtime["id"], runtime)


__all__ = [
    "RuntimeRegistryService",
    "get_runtime_registry_service",
]