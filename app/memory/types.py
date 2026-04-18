"""
Memory Types Module
Runtime Architecture v2 - Type definitions for memory layers
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Memory type categories"""
    WORKING = "working"       # Short-lived, hot, mutable
    EPISODIC = "episodic"     # Event/history oriented
    SEMANTIC = "semantic"     # Stable facts/preferences
    CORTEX = "cortex"         # Cross-thread synthesized
    CHECKPOINT = "checkpoint" # State snapshots


class MemoryStatus(str, Enum):
    """Memory operation status"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class WorkingMemory(BaseModel):
    """Working memory entry"""
    memory_id: str
    thread_id: str
    tenant_id: str
    
    # Content
    state_data: dict = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # TTL in seconds
    ttl_seconds: int = 1800  # 30 minutes default


class EpisodicMemory(BaseModel):
    """Episodic memory entry (event/history)"""
    memory_id: str
    thread_id: str
    tenant_id: str
    execution_request_id: Optional[str] = None
    
    # Content
    event_type: str  # tool_call, agent_turn, decision, user_input
    event_data: dict = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)


class SemanticMemory(BaseModel):
    """Semantic memory entry (facts/preferences)"""
    memory_id: str
    tenant_id: str
    memory_type: str  # preference, fact, snippet, knowledge
    
    # Content
    content_text: str
    content_embedding: Optional[list[float]] = None
    
    # Source
    source_type: Optional[str] = None  # user, org, profile
    source_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class CortexMemory(BaseModel):
    """Cortex/briefing memory entry"""
    memory_id: str
    thread_id: str
    tenant_id: str
    execution_request_id: Optional[str] = None
    
    # Content
    briefing_data: dict = Field(default_factory=dict)
    summary: Optional[str] = None
    pending_actions: list[dict] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class CheckpointMemory(BaseModel):
    """Checkpoint/state snapshot entry"""
    memory_id: str
    thread_id: str
    tenant_id: str
    execution_request_id: Optional[str] = None
    
    # Content
    step_number: int
    state_data: dict = Field(default_factory=dict)
    state_hash: Optional[str] = None
    
    # Type
    checkpoint_type: str = "thread"  # thread, branch, worker
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    compressed: bool = False
    size_bytes: Optional[int] = None


# =============================================================================
# Cortex Typed Memory Categories
# =============================================================================
# From runtime-architecture-v2.md - Typed memory taxonomy

class CortexCategory(str, Enum):
    """Cortex typed memory categories"""
    FACT = "fact"                   # Verified facts
    PREFERENCE = "preference"        # User/org preferences
    DECISION = "decision"            # Decisions made
    IDENTITY = "identity"           # Identity information
    EVENT = "event"                # Important events
    OBSERVATION = "observation"       # Observations made
    GOAL = "goal"                 # Goals/milestones
    TODO = "todo"                 # Todos/action items
    CONSTRAINT = "constraint"        # Constraints/rules
    APPROVAL = "approval"          # Approval records
    OVERRIDE = "override"          # Override records
    DELEGATION = "delegation"       # Delegation records
    MILESTONE = "milestone"        # Milestone progress


class TypedMemory(BaseModel):
    """Typed memory entry for Cortex"""
    memory_id: str
    tenant_id: str
    thread_id: str
    execution_request_id: Optional[str] = None
    
    # Typed category
    category: CortexCategory
    
    # Content
    content: str
    confidence: float = Field(default=1.0, description="Confidence 0-1")
    
    # Source
    source_type: Optional[str] = None  # user, agent, system, workflow
    source_id: Optional[str] = None
    
    # Metadata
    importance: int = Field(default=5, description="Importance 1-10")
    metadata: dict = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class CompactionSummary(BaseModel):
    """Compaction/briefing summary"""
    summary_id: str
    thread_id: str
    tenant_id: str
    execution_request_id: Optional[str] = None
    
    # Compaction outputs
    running_summary: str                         # Summary of execution so far
    open_loops: list[str]                      # Open items to track
    current_state: dict = Field(default_factory=dict)  # Current state snapshot
    key_constraints: list[str] = Field(default_factory=list)  # Important constraints
    key_preferences: list[str] = Field(default_factory=list)  # Key preferences
    
    # Metadata
    tokens_before: int = 0
    tokens_after: int = 0
    step: int = 0
    
    created_at: datetime = Field(default_factory=datetime.now)


__all__ = [
    # Base types
    "MemoryType",
    "MemoryStatus",
    # Memory entries
    "WorkingMemory",
    "EpisodicMemory", 
    "SemanticMemory",
    "CortexMemory",
    "CheckpointMemory",
    # Cortex types
    "CortexCategory",
    "TypedMemory",
    "CompactionSummary",
]
