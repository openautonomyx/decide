"""
Task and Workflow Schemas
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
# from uuid import UUID (DB uses VARCHAR(36))


# Task
class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: str = "pending"  # pending/in_progress/completed/blocked/cancelled
    priority: str = "medium"  # low/medium/high/urgent


class TaskCreate(TaskBase):
    tenant_id: str
    project_id: str | None = None
    assigned_to_employee_id: str | None = None
    assigned_to_agent_id: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None


class Task(TaskBase):
    id: str
    tenant_id: str
    project_id: str | None = None
    assigned_to_employee_id: str | None = None
    assigned_to_agent_id: str | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    total: int
    items: list[Task]


# Task Comment
class TaskCommentBase(BaseModel):
    content: str


class TaskCommentCreate(TaskCommentBase):
    task_id: str
    author_type: str
    author_id: str


class TaskComment(TaskCommentBase):
    id: str
    task_id: str
    author_type: str
    author_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Execution Request
class ExecutionRequestBase(BaseModel):
    goal: str
    capability: str | None = None
    quality: str | None = None


class ExecutionRequestCreate(ExecutionRequestBase):
    tenant_id: str


class ExecutionRequestUpdate(BaseModel):
    status: str | None = None


class ExecutionRequest(ExecutionRequestBase):
    id: str
    tenant_id: str
    status: str
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class ExecutionRequestWithHistory(ExecutionRequest):
    history: list["ExecutionHistory"] = []


# Execution History
class ExecutionHistoryBase(BaseModel):
    event_type: str
    event_data: dict | None = None


class ExecutionHistoryCreate(ExecutionHistoryBase):
    execution_request_id: str
    thread_id: str | None = None


class ExecutionHistory(ExecutionHistoryBase):
    id: str
    execution_request_id: str
    thread_id: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Approval Request
class ApprovalRequestBase(BaseModel):
    pass


class ApprovalRequestCreate(ApprovalRequestBase):
    execution_request_id: str
    requested_by_type: str
    requested_by_id: str


class ApprovalRequestUpdate(BaseModel):
    status: str | None = None  # approved/denied
    approver_notes: str | None = None


class ApprovalRequest(ApprovalRequestBase):
    id: str
    execution_request_id: str
    status: str
    requested_by_type: str
    requested_by_id: str
    approver: str | None = None
    approver_notes: str | None = None
    requested_at: datetime
    decided_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class ExecutionRequestList(BaseModel):
    total: int
    items: list[ExecutionRequest]


