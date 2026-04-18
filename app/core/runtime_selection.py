"""
Runtime Selection Module
Runtime Architecture v2 - Runtime selection logic and registry
"""
import logging
from datetime import datetime
from typing import Optional
from app.core.runtime_types import RuntimeType, TaskType, RuntimeCapability
from app.core.runtime_config import get_runtime_config, RuntimeConfig
from app.core.runtime_registry import (
    WorkerRuntime,
    RuntimeSelectionPolicy,
    DEFAULT_RUNTIME_POLICIES,
    WorkerRuntimeRegistry,
    registry as global_registry,
)

logger = logging.getLogger(__name__)


class RuntimeSelector:
    """
    Runtime selection service.
    Selects appropriate runtime based on task type and tenant policy.
    """
    
    def __init__(self, registry: Optional[WorkerRuntimeRegistry] = None):
        self.registry = registry or global_registry
        self.config = get_runtime_config()
    
    def detect_task_type(self, goal: str, capability: Optional[str] = None) -> TaskType:
        """
        Detect task type from goal and capability.
        
        Args:
            goal: The execution goal/description
            capability: Optional explicit capability
            
        Returns:
            TaskType enum value
        """
        # Import here to avoid circular imports
        from app.core.runtime_registry import detect_task_type as _detect
        task_type_str = _detect(goal, capability)
        
        # Map string to enum
        try:
            return TaskType(task_type_str)
        except ValueError:
            return TaskType.SIMPLE
    
    async def select_runtime(
        self,
        task_type: TaskType,
        tenant_id: str,
        policy: Optional[RuntimeSelectionPolicy] = None,
    ) -> WorkerRuntime:
        """
        Select runtime based on task type and tenant policy.
        
        Args:
            task_type: The detected task type
            tenant_id: Tenant identifier
            policy: Optional tenant-specific policy
            
        Returns:
            Selected WorkerRuntime
        """
        # Use registry to select
        runtime = self.registry.select_runtime(
            task_type=task_type.value,
            tenant_id=tenant_id,
            policy=policy,
        )
        
        logger.info(
            f"Selected runtime {runtime.runtime_id} "
            f"(type={runtime.runtime_type.value}) "
            f"for task_type={task_type.value}, tenant={tenant_id}"
        )
        
        return runtime
    
    async def select_for_execution(
        self,
        goal: str,
        capability: Optional[str],
        tenant_id: str,
    ) -> WorkerRuntime:
        """
        Full runtime selection for an execution request.
        
        Combines task type detection and runtime selection.
        
        Args:
            goal: Execution goal
            capability: Optional capability
            tenant_id: Tenant ID
            
        Returns:
            Selected WorkerRuntime
        """
        # Detect task type
        task_type = self.detect_task_type(goal, capability)
        
        # Get tenant policy if available
        policy = self.registry.get_policy(tenant_id)
        
        # Select runtime
        return await self.select_runtime(task_type, tenant_id, policy)
    
    def list_available_runtimes(self) -> list[WorkerRuntime]:
        """List all available runtimes"""
        return self.registry.list_runtimes()
    
    def get_runtime(self, runtime_id: str) -> Optional[WorkerRuntime]:
        """Get specific runtime by ID"""
        return self.registry.get_runtime(runtime_id)


# Global selector instance
_selector: Optional[RuntimeSelector] = None


def get_runtime_selector() -> RuntimeSelector:
    """Get the global runtime selector"""
    global _selector
    if _selector is None:
        _selector = RuntimeSelector()
    return _selector


async def select_runtime_for_task(
    goal: str,
    capability: Optional[str],
    tenant_id: str,
) -> WorkerRuntime:
    """
    Convenience function for runtime selection.
    
    Args:
        goal: Execution goal
        capability: Optional explicit capability
        tenant_id: Tenant ID
        
    Returns:
        Selected WorkerRuntime
    """
    selector = get_runtime_selector()
    return await selector.select_for_execution(goal, capability, tenant_id)


__all__ = [
    "RuntimeSelector",
    "get_runtime_selector",
    "select_runtime_for_task",
]
