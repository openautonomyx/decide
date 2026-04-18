"""
Orchestrator State Management
Phase 1 - Execution state persistence and retrieval
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.orchestrator.types import (
    ExecutionState,
    OrchestratorStatus,
    ExecutionStage,
    TaskType,
)

logger = logging.getLogger(__name__)


class ExecutionStateStore:
    """
    In-memory execution state store.
    
    Note: In production, this would persist to Redis/DB.
    """
    
    def __init__(self):
        self._states: Dict[str, ExecutionState] = {}
    
    def create(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        thread_id: Optional[str] = None,
    ) -> ExecutionState:
        """Create new execution state."""
        state = ExecutionState(
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            thread_id=thread_id,
        )
        self._states[execution_id] = state
        logger.info(f"Created execution state: {execution_id}")
        return state
    
    def get(self, execution_id: str) -> Optional[ExecutionState]:
        """Get execution state by ID."""
        return self._states.get(execution_id)
    
    def get_by_thread(self, thread_id: str) -> List[ExecutionState]:
        """Get all execution states for a thread."""
        return [s for s in self._states.values() if s.thread_id == thread_id]
    
    def update(self, execution_id: str, **updates) -> bool:
        """Update execution state."""
        if execution_id not in self._states:
            return False
        
        state = self._states[execution_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        state.updated_at = datetime.utcnow()
        return True
    
    def add_history(
        self,
        execution_id: str,
        stage: str,
        data: Dict[str, Any],
    ) -> bool:
        """Add to execution history."""
        if execution_id not in self._states:
            return False
        
        entry = {
            "stage": stage,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._states[execution_id].history.append(entry)
        return True
    
    def advance_stage(
        self,
        execution_id: str,
        new_stage: ExecutionStage,
    ) -> bool:
        """Advance execution to next stage."""
        if execution_id not in self._states:
            return False
        
        state = self._states[execution_id]
        state.current_stage = new_stage
        state.updated_at = datetime.utcnow()
        
        # Add to history
        self.add_history(execution_id, new_stage.value, {})
        
        logger.info(f"Execution {execution_id} advanced to {new_stage.value}")
        return True
    
    def set_status(
        self,
        execution_id: str,
        status: OrchestratorStatus,
    ) -> bool:
        """Set execution status."""
        if execution_id not in self._states:
            return False
        
        self._states[execution_id].status = status
        self._states[execution_id].updated_at = datetime.utcnow()
        return True
    
    def set_runtime(
        self,
        execution_id: str,
        runtime_id: str,
        instance_id: Optional[str] = None,
    ) -> bool:
        """Set selected runtime."""
        if execution_id not in self._states:
            return False
        
        state = self._states[execution_id]
        state.runtime_id = runtime_id
        state.runtime_instance_id = instance_id
        state.updated_at = datetime.utcnow()
        return True
    
    def set_task_type(
        self,
        execution_id: str,
        task_type: TaskType,
    ) -> bool:
        """Set detected task type."""
        if execution_id not in self._states:
            return False
        
        self._states[execution_id].task_type = task_type
        self._states[execution_id].updated_at = datetime.utcnow()
        return True
    
    def set_branch(
        self,
        execution_id: str,
        branch_id: str,
    ) -> bool:
        """Set branch ID."""
        if execution_id not in self._states:
            return False
        
        self._states[execution_id].branch_id = branch_id
        self._states[execution_id].updated_at = datetime.utcnow()
        return True
    
    def set_worker(
        self,
        execution_id: str,
        worker_id: str,
    ) -> bool:
        """Set worker ID."""
        if execution_id not in self._states:
            return False
        
        self._states[execution_id].worker_id = worker_id
        self._states[execution_id].updated_at = datetime.utcnow()
        return True
    
    def add_tool(self, execution_id: str, tool_id: str) -> bool:
        """Add tool to execution."""
        if execution_id not in self._states:
            return False
        
        if tool_id not in self._states[execution_id].tools:
            self._states[execution_id].tools.append(tool_id)
        return True
    
    def add_skill(self, execution_id: str, skill_id: str) -> bool:
        """Add skill to execution."""
        if execution_id not in self._states:
            return False
        
        if skill_id not in self._states[execution_id].skills:
            self._states[execution_id].skills.append(skill_id)
        return True
    
    def update_tokens(
        self,
        execution_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> bool:
        """Update token counts."""
        if execution_id not in self._states:
            return False
        
        state = self._states[execution_id]
        state.input_tokens += input_tokens
        state.output_tokens += output_tokens
        state.context_tokens = state.input_tokens + state.output_tokens
        state.updated_at = datetime.utcnow()
        return True
    
    def list_active(self) -> List[ExecutionState]:
        """List all active executions."""
        return [
            s for s in self._states.values()
            if s.status in [OrchestratorStatus.PENDING, OrchestratorStatus.RUNNING]
        ]
    
    def delete(self, execution_id: str) -> bool:
        """Delete execution state."""
        if execution_id in self._states:
            del self._states[execution_id]
            return True
        return False


# Global instance
_state_store: Optional[ExecutionStateStore] = None


def get_state_store() -> ExecutionStateStore:
    """Get global state store."""
    global _state_store
    if _state_store is None:
        _state_store = ExecutionStateStore()
    return _state_store


__all__ = [
    "ExecutionStateStore",
    "get_state_store",
]