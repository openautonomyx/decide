# Execution Identity Schemas
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class ExecutionIdentityBindingBase(BaseModel):
    workflow_id: Optional[str] = None
    workflow_version_id: Optional[str] = None
    template_id: Optional[str] = None
    execution_identity_id: str
    tenant_id: str
    agent_name: Optional[str] = None
    agent_type: Optional[str] = None
    sponsor_id: Optional[str] = None
    owner_ids_json: Optional[str] = None
    manager_id: Optional[str] = None
    blueprint_id: Optional[str] = None
    allowed_models_json: Optional[str] = None
    budget_limit: Optional[float] = None
    tpm_limit: Optional[int] = None
    expires_at: Optional[datetime] = None
    status: str = "active"
    source_system: str = "autonomyx-agent-identity"


class ExecutionIdentityBindingCreate(ExecutionIdentityBindingBase):
    pass


class ExecutionIdentityBindingUpdate(BaseModel):
    workflow_id: Optional[str] = None
    workflow_version_id: Optional[str] = None
    template_id: Optional[str] = None
    status: Optional[str] = None
    metadata_json: Optional[str] = None


class ExecutionIdentityBindingResponse(ExecutionIdentityBindingBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    last_synced_at: Optional[datetime] = None
    metadata_json: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ExecutionIdentityBindingDetail(ExecutionIdentityBindingResponse):
    pass


class PolicyEvaluationResultBase(BaseModel):
    workflow_id: Optional[str] = None
    workflow_version_id: Optional[str] = None
    run_id: Optional[str] = None
    execution_identity_id: Optional[str] = None
    evaluation_type: str
    is_allowed: bool
    reasons_json: Optional[str] = None
    metadata_json: Optional[str] = None


class PolicyEvaluationResultCreate(PolicyEvaluationResultBase):
    pass


class PolicyEvaluationResultResponse(PolicyEvaluationResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class ExecutionIdentityBindingList(BaseModel):
    items: List[ExecutionIdentityBindingResponse] = []
    total: int = 0