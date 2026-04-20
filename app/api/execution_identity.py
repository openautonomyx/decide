# Execution Identity Binding API Router
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import uuid
import json

from app.db.session import get_db
from app.models.execution_identity import (
    ExecutionIdentityBinding,
    PolicyEvaluationResult,
)
from app.schemas.execution_identity import (
    ExecutionIdentityBindingCreate,
    ExecutionIdentityBindingUpdate,
    ExecutionIdentityBindingResponse,
    ExecutionIdentityBindingDetail,
    ExecutionIdentityBindingList,
    PolicyEvaluationResultCreate,
    PolicyEvaluationResultResponse,
)
from app.integrations.identity.factory import get_adapter, list_providers
from app.integrations.identity.base import NormalizedIdentity

router = APIRouter(prefix="/execution-identities", tags=["execution-identity"])


def _store_policy_eval(
    db: Session,
    provider_name: str,
    workflow_id: Optional[str],
    workflow_version_id: Optional[str],
    run_id: Optional[str],
    external_identity_id: Optional[str],
    evaluation_type: str,
    is_allowed: bool,
    reasons: list,
    metadata: Optional[dict] = None,
) -> PolicyEvaluationResult:
    """Helper to store policy evaluation result."""
    row = PolicyEvaluationResult(
        id=str(uuid.uuid4()),
        provider_name=provider_name,
        workflow_id=workflow_id,
        workflow_version_id=workflow_version_id,
        run_id=run_id,
        external_identity_id=external_identity_id,
        evaluation_type=evaluation_type,
        is_allowed=is_allowed,
        reasons_json=json.dumps(reasons),
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _normalized_to_binding(normalized: NormalizedIdentity, binding_id: str, body: ExecutionIdentityBindingCreate) -> ExecutionIdentityBinding:
    """Convert normalized identity to binding model."""
    return ExecutionIdentityBinding(
        id=binding_id,
        provider_name=normalized.provider,
        workflow_id=body.workflow_id,
        workflow_version_id=body.workflow_version_id,
        template_id=body.template_id,
        external_identity_id=normalized.external_identity_id,
        tenant_id=normalized.tenant_id,
        agent_name=normalized.agent_name,
        agent_type=normalized.agent_type,
        sponsor_id=normalized.sponsor_id,
        owner_ids_json=json.dumps(normalized.owner_ids),
        manager_id=normalized.manager_id,
        blueprint_id=normalized.blueprint_id,
        allowed_models_json=json.dumps(normalized.allowed_models),
        budget_limit=normalized.budget_limit,
        tpm_limit=normalized.tpm_limit,
        expires_at=normalized.expires_at,
        status=normalized.status,
        metadata_json=json.dumps(normalized.provider_metadata),
    )


@router.get("/providers")
async def list_identity_providers():
    """List available identity providers."""
    return {"providers": list_providers()}


@router.post("/bind", response_model=ExecutionIdentityBindingResponse)
async def create_binding(
    body: ExecutionIdentityBindingCreate,
    db: Session = Depends(get_db),
):
    """Bind a workflow/version to an external execution identity."""
    # Get adapter for provider
    adapter = get_adapter(body.provider_name)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {body.provider_name}")
    
    # Verify tenant exists
    from app.models.tenant_employee import Tenant
    tenant = db.query(Tenant).filter(Tenant.id == body.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Fetch and normalize external identity
    normalized = await adapter.sync_identity(body.external_identity_id)
    if not normalized:
        raise HTTPException(status_code=404, detail=f"Execution identity not found in provider: {body.provider_name}")
    
    # Validate tenant matches
    if normalized.tenant_id != body.tenant_id:
        raise HTTPException(status_code=400, detail="Tenant mismatch with external identity")
    
    # Create binding
    binding_id = str(uuid.uuid4())
    binding = _normalized_to_binding(normalized, binding_id, body)
    db.add(binding)
    db.commit()
    db.refresh(binding)
    return binding


@router.get("", response_model=ExecutionIdentityBindingList)
async def list_bindings(
    tenant_id: Optional[str] = None,
    provider_name: Optional[str] = None,
    workflow_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List execution identity bindings."""
    q = db.query(ExecutionIdentityBinding)
    if tenant_id:
        q = q.filter(ExecutionIdentityBinding.tenant_id == tenant_id)
    if provider_name:
        q = q.filter(ExecutionIdentityBinding.provider_name == provider_name)
    if workflow_id:
        q = q.filter(ExecutionIdentityBinding.workflow_id == workflow_id)
    items = q.order_by(ExecutionIdentityBinding.created_at.desc()).all()
    return ExecutionIdentityBindingList(items=items, total=len(items))


@router.get("/{binding_id}", response_model=ExecutionIdentityBindingDetail)
async def get_binding(
    binding_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific binding."""
    binding = db.query(ExecutionIdentityBinding).filter(ExecutionIdentityBinding.id == binding_id).first()
    if not binding:
        raise HTTPException(status_code=404, detail="Binding not found")
    return binding


@router.post("/{binding_id}/sync", response_model=ExecutionIdentityBindingResponse)
async def sync_binding(
    binding_id: str,
    db: Session = Depends(get_db),
):
    """Sync binding from external identity provider."""
    binding = db.query(ExecutionIdentityBinding).filter(ExecutionIdentityBinding.id == binding_id).first()
    if not binding:
        raise HTTPException(status_code=404, detail="Binding not found")
    
    adapter = get_adapter(binding.provider_name)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {binding.provider_name}")
    
    normalized = await adapter.sync_identity(binding.external_identity_id)
    if not normalized:
        raise HTTPException(status_code=404, detail="Execution identity not found in external service")
    
    # Update binding fields
    binding.agent_name = normalized.agent_name
    binding.agent_type = normalized.agent_type
    binding.sponsor_id = normalized.sponsor_id
    binding.owner_ids_json = json.dumps(normalized.owner_ids)
    binding.manager_id = normalized.manager_id
    binding.blueprint_id = normalized.blueprint_id
    binding.allowed_models_json = json.dumps(normalized.allowed_models)
    binding.budget_limit = normalized.budget_limit
    binding.tpm_limit = normalized.tpm_limit
    binding.expires_at = normalized.expires_at
    binding.status = normalized.status
    binding.metadata_json = json.dumps(normalized.provider_metadata)
    binding.last_synced_at = binding.updated_at
    
    db.commit()
    db.refresh(binding)
    return binding




class LoginSponsorMapRequest(BaseModel):
    provider_name: str = "autonomyx_agent_identity"
    tenant_id: str
    sponsor_id: str
    agent_name: Optional[str] = None
    agent_type: Optional[str] = "human_sponsor"
    external_identity_id: Optional[str] = None


@router.post("/login-map", response_model=ExecutionIdentityBindingResponse)
async def login_map_sponsor(
    body: LoginSponsorMapRequest,
    db: Session = Depends(get_db),
):
    """
    Create/update agent_id to human sponsor mapping at login time.

    Idempotent behavior:
    - if mapping exists for (provider_name, tenant_id, sponsor_id): update metadata/timestamp
    - else create a new active mapping
    """
    external_identity_id = body.external_identity_id or f"login::{body.tenant_id}::{body.sponsor_id}"

    binding = (
        db.query(ExecutionIdentityBinding)
        .filter(ExecutionIdentityBinding.provider_name == body.provider_name)
        .filter(ExecutionIdentityBinding.tenant_id == body.tenant_id)
        .filter(ExecutionIdentityBinding.sponsor_id == body.sponsor_id)
        .first()
    )

    metadata = {"auto_created": True, "source": "login_map"}

    if binding:
        binding.status = "active"
        binding.external_identity_id = external_identity_id
        binding.agent_name = body.agent_name or binding.agent_name
        binding.agent_type = body.agent_type or binding.agent_type
        binding.owner_ids_json = binding.owner_ids_json or json.dumps([body.sponsor_id])
        binding.allowed_models_json = binding.allowed_models_json or json.dumps([])
        binding.metadata_json = json.dumps(metadata)
        db.commit()
        db.refresh(binding)
        return binding

    binding = ExecutionIdentityBinding(
        id=str(uuid.uuid4()),
        provider_name=body.provider_name,
        external_identity_id=external_identity_id,
        tenant_id=body.tenant_id,
        agent_name=body.agent_name or f"sponsor-{body.sponsor_id}",
        agent_type=body.agent_type or "human_sponsor",
        sponsor_id=body.sponsor_id,
        owner_ids_json=json.dumps([body.sponsor_id]),
        allowed_models_json=json.dumps([]),
        status="active",
        metadata_json=json.dumps(metadata),
    )
    db.add(binding)
    db.commit()
    db.refresh(binding)
    return binding


@router.get("/policy-results", response_model=list[PolicyEvaluationResultResponse])
async def list_policy_results(
    workflow_id: Optional[str] = None,
    evaluation_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List policy evaluation results."""
    q = db.query(PolicyEvaluationResult)
    if workflow_id:
        q = q.filter(PolicyEvaluationResult.workflow_id == workflow_id)
    if evaluation_type:
        q = q.filter(PolicyEvaluationResult.evaluation_type == evaluation_type)
    return q.order_by(PolicyEvaluationResult.created_at.desc()).limit(limit).all()