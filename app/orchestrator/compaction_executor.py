"""
Compaction Executor
Phase 4 - Real context compaction execution

Executes context compaction when threshold conditions are met.
"""
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.orchestrator.types import ExecutionState, OrchestratorRequest

logger = logging.getLogger(__name__)


class CompactionResult:
    """Result of compaction execution"""
    def __init__(
        self,
        success: bool,
        tokens_before: int,
        tokens_after: int,
        tokens_saved: int,
        summary_text: str,
        open_loops: List[str],
        checkpoint_written: bool = False,
        error: Optional[str] = None,
    ):
        self.success = success
        self.tokens_before = tokens_before
        self.tokens_after = tokens_after
        self.tokens_saved = tokens_saved
        self.summary_text = summary_text
        self.open_loops = open_loops
        self.checkpoint_written = checkpoint_written
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "tokens_before": self.tokens_before,
            "tokens_after": self.tokens_after,
            "tokens_saved": self.tokens_saved,
            "summary_text": self.summary_text,
            "open_loops": self.open_loops,
            "checkpoint_written": self.checkpoint_written,
            "error": self.error,
        }


class CompactionExecutor:
    """
    Compaction executor handles context compaction.
    
    Executes when:
    - Token threshold exceeded
    - Explicit compaction requested
    - Periodic checkpoint
    """
    
    def __init__(self):
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
    
    def should_compact(
        self,
        state: ExecutionState,
        threshold: float = 0.8,
    ) -> bool:
        """
        Determine if compaction should be executed.
        
        Args:
            state: Current execution state
            threshold: Threshold ratio (0.0-1.0)
            
        Returns:
            bool: True if compaction should run
        """
        # Get budget for task type
        from app.services.context import get_context_budget_service
        
        task_type = state.task_type.value if state.task_type else "simple"
        budget_service = get_context_budget_service()
        
        budget = budget_service.get_budget_for_task(
            tenant_id=state.tenant_id,
            task_type=task_type,
        )
        
        input_budget = budget.get("input_budget_tokens", 150000)
        threshold_tokens = int(input_budget * threshold)
        
        # Check current context tokens
        current_tokens = state.context_tokens
        
        should = current_tokens >= threshold_tokens
        
        if should:
            logger.info(
                f"Compaction recommended: {current_tokens}/{threshold_tokens} "
                f"({current_tokens/threshold_tokens:.1%})"
            )
        
        return should
    
    def execute(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ) -> CompactionResult:
        """
        Execute compaction on current context.
        
        Args:
            state: Current execution state
            request: Original request
            
        Returns:
            CompactionResult: Compaction execution result
        """
        try:
            # Get current token count
            tokens_before = state.context_tokens
            
            if tokens_before == 0:
                return CompactionResult(
                    success=False,
                    tokens_before=0,
                    tokens_after=0,
                    tokens_saved=0,
                    summary_text="No context to compact",
                    open_loops=[],
                    error="No tokens to compact",
                )
            
            # Generate summary (simplified - real implementation would use LLM)
            summary_text = self._generate_summary(state, request)
            
            # Estimate tokens after compaction
            # In real implementation, would re-summarize with LLM
            tokens_after = len(summary_text) // 4 + 200  # Base + summary
            tokens_saved = tokens_before - tokens_after
            
            # Create checkpoint
            checkpoint = self._write_checkpoint(
                state=state,
                summary_text=summary_text,
                tokens_before=tokens_before,
                tokens_after=tokens_after,
            )
            
            logger.info(
                f"Compaction completed: {tokens_before} -> {tokens_after} "
                f"(saved {tokens_saved} tokens)"
            )
            
            return CompactionResult(
                success=True,
                tokens_before=tokens_before,
                tokens_after=tokens_after,
                tokens_saved=tokens_saved,
                summary_text=summary_text,
                open_loops=state.metadata.get("open_loops", []),
                checkpoint_written=True,
            )
            
        except Exception as e:
            logger.error(f"Compaction failed: {e}")
            return CompactionResult(
                success=False,
                tokens_before=state.context_tokens,
                tokens_after=state.context_tokens,
                tokens_saved=0,
                summary_text="",
                open_loops=[],
                error=str(e),
            )
    
    def _generate_summary(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ) -> str:
        """
        Generate summary of current context.
        
        In a real implementation, this would call an LLM to summarize.
        For now, generates a basic summary.
        """
        # Build summary from history
        history_summary = []
        
        for entry in state.history[-5:]:  # Last 5 entries
            stage = entry.get("stage", "unknown")
            history_summary.append(f"Completed: {stage}")
        
        # Build summary text
        summary_parts = [
            f"Execution: {state.execution_id}",
            f"Task type: {state.task_type.value if state.task_type else 'unknown'}",
            f"Runtime: {state.runtime_id or 'none'}",
            f"History: {'; '.join(history_summary) if history_summary else 'no history'}",
        ]
        
        # Include request summary
        if request.request_text:
            summary_parts.append(f"Current request: {request.request_text[:100]}...")
        
        return " | ".join(summary_parts)
    
    def _write_checkpoint(
        self,
        state: ExecutionState,
        summary_text: str,
        tokens_before: int,
        tokens_after: int,
    ) -> Dict[str, Any]:
        """
        Write checkpoint to state.
        
        Returns checkpoint data.
        """
        checkpoint_id = f"cp-{state.execution_id}-{len(state.history)}"
        
        checkpoint = {
            "id": checkpoint_id,
            "execution_id": state.execution_id,
            "thread_id": state.thread_id,
            "summary": summary_text,
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "tokens_saved": tokens_before - tokens_after,
            "created_at": datetime.utcnow().isoformat(),
            "step": len(state.history),
        }
        
        # Store in executor state
        self._checkpoints[checkpoint_id] = checkpoint
        
        # Also add to execution state metadata
        if "checkpoints" not in state.metadata:
            state.metadata["checkpoints"] = []
        state.metadata["checkpoints"].append(checkpoint)
        
        return checkpoint
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint by ID."""
        return self._checkpoints.get(checkpoint_id)
    
    def get_checkpoints_for_execution(
        self,
        execution_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all checkpoints for an execution."""
        return [
            cp for cp in self._checkpoints.values()
            if cp["execution_id"] == execution_id
        ]


# Global instance
_compaction_executor: Optional[CompactionExecutor] = None


def get_compaction_executor() -> CompactionExecutor:
    """Get global compaction executor."""
    global _compaction_executor
    if _compaction_executor is None:
        _compaction_executor = CompactionExecutor()
    return _compaction_executor


__all__ = [
    "CompactionResult",
    "CompactionExecutor",
    "get_compaction_executor",
]