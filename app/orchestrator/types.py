"""
Orchestrator Types
Phase 1 - Core orchestrator type definitions
"""
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class TaskType(str, Enum):
    """Task type categories for runtime selection"""
    CODING = "coding"
    CONVERSATION = "conversation"
    AUTONOMOUS = "autonomous"
    COLLABORATION = "collaboration"
    RESEARCH = "research"
    SIMPLE = "simple"


class OrchestratorStatus(str, Enum):
    """Orchestrator execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPACTING = "compacting"


class ExecutionStage(str, Enum):
    """Orchestrator execution stages"""
    INTAKE = "intake"
    STATE_INIT = "state_init"
    TASK_DETECTION = "task_detection"
    RUNTIME_SELECTION = "runtime_selection"
    CONTEXT_SETUP = "context_setup"
    BUDGET_CHECK = "budget_check"
    TOOL_RESOLUTION = "tool_resolution"
    SKILL_RESOLUTION = "skill_resolution"
    EXECUTION = "execution"
    COMPACTION_CHECK = "compaction_check"
    RESULT_AGGREGATION = "result_aggregation"
    COMPLETE = "complete"


class NextAction(str, Enum):
    """Next action after orchestrator completes"""
    COMPLETE = "complete"
    AWAIT_INPUT = "await_input"
    NEEDS_APPROVAL = "needs_approval"
    NEEDS_COMPACTION = "needs_compaction"
    FALLBACK = "fallback"


class OrchestratorRequest(BaseModel):
    """Incoming orchestrator request"""
    tenant_id: str
    user_id: str
    thread_id: Optional[str] = None
    request_text: str
    request_metadata: Dict[str, Any] = Field(default_factory=dict)
    preferred_runtime: Optional[str] = None
    required_tools: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)


class OrchestratorResult(BaseModel):
    """Normalized orchestrator result"""
    execution_request_id: str
    status: OrchestratorStatus
    selected_runtime: Optional[str] = None
    selected_tools: List[str] = Field(default_factory=list)
    selected_skills: List[str] = Field(default_factory=list)
    branch_id: Optional[str] = None
    output_summary: str = ""
    next_action: NextAction = NextAction.COMPLETE
    audit_refs: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    stages_completed: List[str] = Field(default_factory=list)


class ExecutionState(BaseModel):
    """Execution state container"""
    execution_id: str
    tenant_id: str
    user_id: str
    thread_id: Optional[str] = None
    branch_id: Optional[str] = None
    worker_id: Optional[str] = None
    
    task_type: Optional[TaskType] = None
    runtime_id: Optional[str] = None
    runtime_instance_id: Optional[str] = None
    
    tools: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    
    current_stage: ExecutionStage = ExecutionStage.INTAKE
    status: OrchestratorStatus = OrchestratorStatus.PENDING
    
    context_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StageResult(BaseModel):
    """Result from a single orchestrator stage"""
    stage: ExecutionStage
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    next_stage: Optional[ExecutionStage] = None


__all__ = [
    "TaskType",
    "OrchestratorStatus",
    "ExecutionStage",
    "NextAction",
    "OrchestratorRequest",
    "OrchestratorResult",
    "ExecutionState",
    "StageResult",
]
