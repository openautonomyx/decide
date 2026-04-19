# Execution Identity Binding API Router
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import uuid

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
from app.integrations.agent_identity import (
    get_agent_identity_client,
    normalize_identity_response,
)

router = APIRouter(prefix="/execution-identities", tags=["execution-identity"])


def _eval_result_row(
    db: Session,
    workflow_id: Optional[str],
    workflow_version_id: Optional[str],
    run_id: Optional[str],
    execution_identity_id: Optional[str],
    evaluation_type: str,
    is_allowed: bool,
    reasons: list,
    metadata: Optional[dict] = None,
) -> PolicyEvaluationResult:
    """Helper to store policy evaluation result."""
    import json
    row = PolicyEvaluationResult(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        workflow_version_id=workflow_version_id,
        run_id=run_id,
        execution_identity_id=execution_identity_id,
        evaluation_type=evaluation_type,
        is_allowed=is_allowed,
        reasons_json=json.dumps(reasons),
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/bind", response_model=ExecutionIdentityBindingResponse)
async def create_binding(
    body: ExecutionIdentityBindingCreate,
    db: Session = Depends(get_db),
):
    """Bind a workflow/version to an external execution identity."""
    client = get_agent_identity_client()
    
    # Verify tenant exists
    from app.models.tenant_employee import Tenant
    tenant = db.query(Tenant).filter(Tenant.id == body.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Fetch external identity to validate it exists
    identity_data = await client.get_execution_identity(body.execution_identity_id)
    if not identity_data:
        raise HTTPException(status_code=404, detail="Execution identity not found in external service")
    
    # Validate tenant matches
    if identity_data.get("tenant_id") != body.tenant_id:
        raise HTTPException(status_code=400, detail="Tenant mismatch with external identity")
    
    # Create binding
    binding_id = str(uuid.uuid4())
    normalized = normalize_identity_response(identity_data)
    
    binding = ExecutionIdentityBinding(
        id=binding_id,
        workflow_id=body.workflow_id,
        workflow_version_id=body.workflow_version_id,
        template_id=body.template_id,
        execution_identity_id=body.execution_identity_id,
        tenant_id=body.tenant_id,
        agent_name=normalized.get("agent_name"),
        agent_type=normalized.get("agent_type"),
        sponsor_id=normalized.get("sponsor_id"),
        owner_ids_json=normalized.get("owner_ids_json"),
        manager_id=normalized.get("manager_id"),
        blueprint_id=normalized.get("blueprint_id"),
        allowed_models_json=normalized.get("allowed_models_json"),
        budget_limit=normalized.get("budget_limit"),
        tpm_limit=normalized.get("tpm_limit"),
        expires_at=normalized.get("expires_at"),
        status=body.status,
        source_system="autonomyx-agent-identity",
        last_synced_at=normalized.get("metadata_json"),
        metadata_json=normalized.get("metadata_json"),
    )
    db.add(binding)
    db.commit()
    db.refresh(binding)
    return binding


@router.get("", response_model=ExecutionIdentityBindingList)
async def list_bindings(
    tenant_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List execution identity bindings."""
    q = db.query(ExecutionIdentityBinding)
    if tenant_id:
        q = q.filter(ExecutionIdentityBinding.tenant_id == tenant_id)
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
    """Sync binding from external identity service."""
    binding = db.query(ExecutionIdentityBinding).filter(ExecutionIdentityBinding.id == binding_id).first()
    if not binding:
        raise HTTPException(status_code=404, detail="Binding not found")
    
    client = get_agent_identity_client()
    identity_data = await client.get_execution_identity(binding.execution_identity_id)
    
    if not identity_data:
        raise HTTPException(status_code=404, detail="Execution identity not found in external service")
    
    normalized = normalize_identity_response(identity_data)
    
    # Update binding fields
    binding.agent_name = normalized.get("agent_name")
    binding.agent_type = normalized.get("agent_type")
    binding.sponsor_id = normalized.get("sponsor_id")
    binding.owner_ids_json = normalized.get("owner_ids_json")
    binding.manager_id = normalized.get("manager_id")
    binding.blueprint_id = normalized.get("blueprint_id")
    binding.allowed_models_json = normalized.get("allowed_models_json")
    binding.budget_limit = normalized.get("budget_limit")
    binding.tpm_limit = normalized.get("tpm_limit")
    binding.expires_at = normalized.get("expires_at")
    binding.status = normalized.get("status", "active")
    binding.metadata_json = normalized.get("metadata_json")
    binding.last_synced_at = binding.updated_at
    
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