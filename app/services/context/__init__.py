"""
Context Service
Phase 0 - Context window and compaction governance

This service provides:
- Context budget management
- Token accounting
- Compaction triggers and summaries

Status: IMPLEMENTED (internal + runtime APIs)
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


# Default context budgets from architecture docs
DEFAULT_BUDGETS = {
    "coding": {"input_tokens": 150000, "output_tokens": 50000},
    "conversation": {"input_tokens": 50000, "output_tokens": 10000},
    "autonomous": {"input_tokens": 200000, "output_tokens": 100000},
    "collaboration": {"input_tokens": 100000, "output_tokens": 50000},
    "research": {"input_tokens": 150000, "output_tokens": 30000},
    "simple": {"input_tokens": 30000, "output_tokens": 5000},
}

COMPACTION_THRESHOLD_RATIO = 0.8  # Trigger at 80%


class ContextBudgetService:
    """
    Context budget management service.
    
    Manages token budgets per task type and tenant.
    """
    
    def __init__(self):
        self._budgets: Dict[str, Dict[str, Any]] = {}
    
    def create_budget(
        self,
        tenant_id: str,
        task_type: str,
        input_budget: int = None,
        output_budget: int = None,
        threshold: float = COMPACTION_THRESHOLD_RATIO,
    ) -> Dict[str, Any]:
        """Create a context budget."""
        import uuid
        budget_id = f"budget-{uuid.uuid4().hex[:12]}"
        
        defaults = DEFAULT_BUDGETS.get(task_type, DEFAULT_BUDGETS["simple"])
        
        budget = {
            "id": budget_id,
            "tenant_id": tenant_id,
            "task_type": task_type,
            "input_budget_tokens": input_budget or defaults["input_tokens"],
            "output_budget_tokens": output_budget or defaults["output_tokens"],
            "compaction_threshold": threshold,
            "created_at": datetime.utcnow(),
        }
        
        self._budgets[budget_id] = budget
        logger.info(f"Created budget for tenant {tenant_id}, task type {task_type}")
        return budget
    
    def get_budget(self, budget_id: str) -> Optional[Dict[str, Any]]:
        """Get budget by ID."""
        return self._budgets.get(budget_id)
    
    def get_budget_for_task(
        self,
        tenant_id: str,
        task_type: str,
    ) -> Dict[str, Any]:
        """Get or create budget for task type."""
        # Look for existing
        for budget in self._budgets.values():
            if budget["tenant_id"] == tenant_id and budget["task_type"] == task_type:
                return budget
        
        # Create default
        return self.create_budget(tenant_id, task_type)
    
    def list_budgets(self, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List budgets."""
        budgets = list(self._budgets.values())
        if tenant_id:
            budgets = [b for b in budgets if b["tenant_id"] == tenant_id]
        return budgets
    
    def update_budget(self, budget_id: str, updates: Dict[str, Any]) -> bool:
        """Update budget configuration."""
        if budget_id not in self._budgets:
            return False
        self._budgets[budget_id].update(updates)
        return True
    
    def check_budget(
        self,
        tenant_id: str,
        task_type: str,
        current_tokens: int,
    ) -> Dict[str, Any]:
        """
        Check if current tokens exceed budget threshold.
        
        Returns:
            {
                "should_compact": bool,
                "budget": budget info,
                "threshold": threshold tokens,
                "headroom": remaining tokens
            }
        """
        budget = self.get_budget_for_task(tenant_id, task_type)
        threshold = int(budget["input_budget_tokens"] * budget["compaction_threshold"])
        
        return {
            "should_compact": current_tokens >= threshold,
            "budget": budget,
            "threshold": threshold,
            "headroom": threshold - current_tokens,
        }


class TokenAccountingService:
    """
    Token usage accounting service.
    
    Tracks token usage per thread/tenant.
    """
    
    def __init__(self):
        self._usage: Dict[str, Dict[str, Any]] = {}
    
    def record_usage(
        self,
        thread_id: str,
        tenant_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        runtime_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record token usage for a request."""
        import uuid
        record_id = f"usage-{uuid.uuid4().hex[:12]}"
        
        # Get or create usage record for thread
        if thread_id not in self._usage:
            self._usage[thread_id] = {
                "thread_id": thread_id,
                "tenant_id": tenant_id,
                "total_input": 0,
                "total_output": 0,
                "request_count": 0,
                "records": [],
            }
        
        record = {
            "id": record_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "runtime_id": runtime_id,
            "recorded_at": datetime.utcnow(),
        }
        
        self._usage[thread_id]["total_input"] += input_tokens
        self._usage[thread_id]["total_output"] += output_tokens
        self._usage[thread_id]["request_count"] += 1
        self._usage[thread_id]["records"].append(record)
        
        return record
    
    def get_usage(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get usage record for a thread."""
        return self._usage.get(thread_id)
    
    def get_total_usage(self, tenant_id: str) -> Dict[str, int]:
        """Get total usage for a tenant across all threads."""
        total_input = 0
        total_output = 0
        request_count = 0
        
        for usage in self._usage.values():
            if usage["tenant_id"] == tenant_id:
                total_input += usage["total_input"]
                total_output += usage["total_output"]
                request_count += usage["request_count"]
        
        return {
            "total_input": total_input,
            "total_output": total_output,
            "total_tokens": total_input + total_output,
            "request_count": request_count,
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (~4 chars per token)."""
        return len(text) // 4
    
    def estimate_messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Estimate tokens in message history."""
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            total += self.estimate_tokens(content)
        return total


class CompactionService:
    """
    Compaction service.
    
    Manages context summarization and compaction.
    """
    
    def __init__(self):
        self._summaries: Dict[str, Dict[str, Any]] = {}
    
    def create_summary(
        self,
        thread_id: str,
        tenant_id: str,
        running_summary: str,
        open_loops: List[str],
        tokens_before: int,
        tokens_after: int,
        step: int,
    ) -> Dict[str, Any]:
        """Create a compaction summary."""
        import uuid
        summary_id = f"summary-{uuid.uuid4().hex[:12]}"
        
        summary = {
            "id": summary_id,
            "thread_id": thread_id,
            "tenant_id": tenant_id,
            "running_summary": running_summary,
            "open_loops": open_loops,
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "tokens_saved": tokens_before - tokens_after,
            "step": step,
            "created_at": datetime.utcnow(),
        }
        
        self._summaries[summary_id] = summary
        return summary
    
    def get_summary(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """Get summary by ID."""
        return self._summaries.get(summary_id)
    
    def get_latest_summary(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get latest summary for a thread."""
        thread_summaries = [
            s for s in self._summaries.values() if s["thread_id"] == thread_id
        ]
        if not thread_summaries:
            return None
        return max(thread_summaries, key=lambda s: s["created_at"])
    
    def list_summaries(
        self,
        thread_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """List summaries."""
        summaries = list(self._summaries.values())
        if thread_id:
            summaries = [s for s in summaries if s["thread_id"] == thread_id]
        return sorted(summaries, key=lambda s: s["created_at"], reverse=True)[:limit]


# Global instances
_budget_service: Optional[ContextBudgetService] = None
_token_service: Optional[TokenAccountingService] = None
_compaction_service: Optional[CompactionService] = None


def get_context_budget_service() -> ContextBudgetService:
    """Get global context budget service."""
    global _budget_service
    if _budget_service is None:
        _budget_service = ContextBudgetService()
    return _budget_service


def get_token_accounting_service() -> TokenAccountingService:
    """Get global token accounting service."""
    global _token_service
    if _token_service is None:
        _token_service = TokenAccountingService()
    return _token_service


def get_compaction_service() -> CompactionService:
    """Get global compaction service."""
    global _compaction_service
    if _compaction_service is None:
        _compaction_service = CompactionService()
    return _compaction_service


__all__ = [
    "ContextBudgetService",
    "TokenAccountingService",
    "CompactionService",
    "get_context_budget_service",
    "get_token_accounting_service",
    "get_compaction_service",
    "DEFAULT_BUDGETS",
    "COMPACTION_THRESHOLD_RATIO",
]