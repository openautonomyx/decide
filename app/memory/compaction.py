"""
Compaction Service
Runtime Architecture v2 - Compaction checkpoint and briefing generation

This module provides:
- Context budget monitoring
- Pre-emptive compaction before context fills
- Running summary generation
- Open loop identification
- Checkpoint creation

Status: IMPLEMENTED (interface + basic logic, infra hooks ready)
"""
import json
import logging
from typing import Optional, Any
from datetime import datetime

from app.memory.types import (
    CortexCategory,
    TypedMemory,
    CompactionSummary,
)
from app.core.runtime_config import get_runtime_config

logger = logging.getLogger(__name__)


# Default context budgets from runtime-architecture-v2.md
CONTEXT_BUDGETS = {
    "coding": {
        "input_tokens": 150000,
        "output_tokens": 50000,
    },
    "conversation": {
        "input_tokens": 50000,
        "output_tokens": 10000,
    },
    "autonomous": {
        "input_tokens": 200000,
        "output_tokens": 100000,
    },
    "collaboration": {
        "input_tokens": 100000,
        "output_tokens": 50000,
    },
    "simple": {
        "input_tokens": 30000,
        "output_tokens": 5000,
    },
}

# Compaction thresholds
COMPACTION_THRESHOLD_RATIO = 0.8  # Trigger at 80% of budget
CHECKPOINT_INTERVAL = 50  # Steps between checkpoints


class CompactionService:
    """
    Compaction/briefing service.
    
    Monitors context budget and triggers compaction before limits are reached.
    Generates summaries for human review.
    """
    
    def __init__(self):
        self.config = get_runtime_config()
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (~4 chars per token)"""
        return len(text) // 4
    
    def estimate_messages_tokens(self, messages: list[dict]) -> int:
        """Estimate tokens in message history"""
        total = 0
        for msg in messages:
            total += self.estimate_tokens(msg.get("content", ""))
        return total
    
    def should_compact(
        self,
        task_type: str,
        messages: list[dict],
        current_tokens: int = 0,
    ) -> bool:
        """
        Determine if compaction should trigger.
        
        Args:
            task_type: Type of task
            messages: Current message history
            current_tokens: Current token count
            
        Returns:
            True if compaction should run
        """
        budget = CONTEXT_BUDGETS.get(task_type, CONTEXT_BUDGETS["simple"])
        input_budget = budget["input_tokens"]
        
        # Estimate from messages
        message_tokens = self.estimate_messages_tokens(messages)
        total_tokens = current_tokens + message_tokens
        
        # Trigger at threshold
        threshold = int(input_budget * COMPACTION_THRESHOLD_RATIO)
        
        should = total_tokens >= threshold
        
        if should:
            logger.info(
                f"Compaction triggered for {task_type}: "
                f"{total_tokens}/{input_budget} tokens"
            )
        
        return should
    
    def should_checkpoint(
        self,
        step: int,
        checkpoint_interval: int = None,
    ) -> bool:
        """
        Determine if checkpoint should be created.
        
        Args:
            step: Current step number
            checkpoint_interval: Steps between checkpoints
            
        Returns:
            True if checkpoint should be created
        """
        interval = checkpoint_interval or self.config.checkpoint_interval_steps
        return step > 0 and step % interval == 0
    
    async def generate_summary(
        self,
        thread_id: str,
        tenant_id: str,
        task_type: str,
        messages: list[dict],
        goals: list[str],
        constraints: list[str],
        preferences: list[str],
    ) -> CompactionSummary:
        """
        Generate compaction summary.
        
        Args:
            thread_id: Thread identifier
            tenant_id: Tenant ID
            task_type: Task type
            messages: Message history
            goals: Active goals
            constraints: Active constraints
            preferences: Key preferences
            
        Returns:
            CompactionSummary
        """
        # Build running summary from messages
        running_parts = []
        if messages:
            recent = messages[-5:]  # Last 5 messages
            for msg in recent:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:100]
                running_parts.append(f"{role}: {content}...")
        
        running_summary = " / ".join(running_parts) if running_parts else "No messages yet."
        
        # Identify open loops (goals not yet complete)
        open_loops = list(goals)  # For now, all goals are open
        
        # Current state
        current_state = {
            "task_type": task_type,
            "message_count": len(messages),
            "goals_count": len(goals),
        }
        
        # Estimate token savings
        tokens_before = self.estimate_messages_tokens(messages)
        tokens_after = self.estimate_tokens(running_summary)
        
        summary = CompactionSummary(
            summary_id=f"summary-{datetime.now().timestamp()}",
            thread_id=thread_id,
            tenant_id=tenant_id,
            running_summary=running_summary,
            open_loops=open_loops,
            current_state=current_state,
            key_constraints=constraints[:5],  # Top 5
            key_preferences=preferences[:5],   # Top 5
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            step=len(messages),
        )
        
        logger.info(
            f"Generated summary for thread {thread_id}: "
            f"{tokens_before} -> {tokens_after} tokens"
        )
        
        return summary
    
    async def extract_typed_memories(
        self,
        thread_id: str,
        tenant_id: str,
        messages: list[dict],
    ) -> list[TypedMemory]:
        """
        Extract typed memories from message history.
        
        Args:
            thread_id: Thread identifier
            tenant_id: Tenant ID
            messages: Message history
            
        Returns:
            List of TypedMemory entries
        """
        memories = []
        
        for msg in messages[-20:]:  # Last 20 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Categorize based on content
            if "approved" in content.lower():
                category = CortexCategory.APPROVAL
            elif "prefer" in content.lower():
                category = CortexCategory.PREFERENCE
            elif "constraint" in content.lower() or "must" in content.lower():
                category = CortexCategory.CONSTRAINT
            elif "decision" in content.lower():
                category = CortexCategory.DECISION
            elif "goal" in content.lower():
                category = CortexCategory.GOAL
            elif role == "user":
                category = CortexCategory.EVENT
            else:
                category = CortexCategory.OBSERVATION
            
            memory = TypedMemory(
                memory_id=f"mem-{datetime.now().timestamp()}",
                tenant_id=tenant_id,
                thread_id=thread_id,
                category=category,
                content=content[:500],  # Truncate
                source_type=role,
                importance=5,
            )
            memories.append(memory)
        
        return memories
    
    def get_context_budget(self, task_type: str) -> dict:
        """Get context budget for task type"""
        return CONTEXT_BUDGETS.get(task_type, CONTEXT_BUDGETS["simple"])


# Global instance
_compaction_service: Optional[CompactionService] = None


def get_compaction_service() -> CompactionService:
    """Get compaction service instance"""
    global _compaction_service
    if _compaction_service is None:
        _compaction_service = CompactionService()
    return _compaction_service


__all__ = [
    "CompactionService",
    "get_compaction_service",
    "CONTEXT_BUDGETS",
    "COMPACTION_THRESHOLD_RATIO",
    "CHECKPOINT_INTERVAL",
]