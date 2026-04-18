"""
LangGraph Orchestration State
Runtime Architecture v2 - State model for LangGraph orchestration
"""
from typing import Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Orchestration execution status"""
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    AWAITING_HUMAN = "awaiting_human"
    COMPLETED = "completed"
    FAILED = "failed"


class OrchestrationState(BaseModel):
    """
    LangGraph orchestration state.
    
    This is the working state passed between graph nodes.
    It is separate from the persistent execution_request in the control plane.
    """
    # Identification
    execution_id: str = Field(description="Unique execution ID")
    thread_id: str = Field(description="LangGraph thread ID")
    tenant_id: str = Field(description="Tenant ID")
    
    # Input
    goal: str = Field(description="User goal/request")
    capability: Optional[str] = Field(default=None, description="Requested capability")
    
    # Runtime selection
    task_type: str = Field(default="conversation", description="Detected task type")
    selected_runtime_id: Optional[str] = Field(default=None, description="Selected runtime ID")
    selected_runtime_type: Optional[str] = Field(default=None, description="Runtime type")
    
    # Execution
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING)
    current_step: int = Field(default=0, description="Current step in orchestration")
    max_steps: int = Field(default=50, description="Max steps before checkpoint")
    
    # Branching
    branch_id: Optional[str] = Field(default=None, description="Current branch ID")
    branch_depth: int = Field(default=0, description="Current branch depth")
    
    # Checkpointing
    last_checkpoint_step: int = Field(default=0, description="Last checkpoint step")
    checkpoint_required: bool = Field(default=False, description="Checkpoint needed")
    
    # Approval workflow
    approval_required: bool = Field(default=False, description="Requires human approval")
    approval_status: Optional[str] = Field(default=None, description="approval_request status")
    
    # Results
    result: Optional[dict] = Field(default=None, description="Final result")
    error: Optional[str] = Field(default=None, description="Error if failed")
    
    # Context (accumulated)
    context: dict = Field(default_factory=dict, description="Execution context")
    messages: list[dict] = Field(default_factory=list, description="Message history")
    tool_calls: list[dict] = Field(default_factory=list, description="Tool calls made")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class BranchContext(BaseModel):
    """Context for a single branch in the graph"""
    branch_id: str
    parent_branch_id: Optional[str] = None
    status: str = "pending"
    result: Optional[dict] = None
    children: list[str] = Field(default_factory=list)


class GraphCheckpoint(BaseModel):
    """Checkpoint for graph state recovery"""
    checkpoint_id: str
    thread_id: str
    execution_id: str
    
    step: int
    state_snapshot: dict
    
    created_at: datetime = Field(default_factory=datetime.now)


__all__ = [
    "ExecutionStatus",
    "OrchestrationState",
    "BranchContext",
    "GraphCheckpoint",
]
