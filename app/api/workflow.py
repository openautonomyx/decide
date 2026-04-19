"""
Workflow API Router
Import, validate, publish, and run workflows.
"""
import json
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.models.workflow_definition import (
    WorkflowDefinition,
    WorkflowVersion,
    WorkflowNode,
    WorkflowEdge,
    WorkflowValidationResult,
    WorkflowPublishArtifact,
    WorkflowRun,
    WorkflowRunStep,
)
from app.models.execution_identity import ExecutionIdentityBinding, PolicyEvaluationResult
from app.models.skill import SkillDefinition, SkillVersion, SkillBinding
from app.integrations.identity.factory import get_adapter
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Supported node types for MVP
SUPPORTED_NODE_TYPES = {"start", "llm", "tool", "condition", "human_approval", "end"}


def _evaluate_identity_for_workflow(
    db: Session,
    workflow_id: str,
    workflow_tenant_id: str,
    evaluation_type: str,
) -> tuple[bool, list, dict]:
    """
    Evaluate identity constraints for a workflow.
    Returns (is_allowed, reasons, metadata).
    """
    # Find binding for this workflow
    binding = db.query(ExecutionIdentityBinding).filter(
        ExecutionIdentityBinding.workflow_id == workflow_id
    ).first()
    
    if not binding:
        # No binding = no identity constraints to check
        return True, [], {"has_binding": False}
    
    # Get adapter for provider
    adapter = get_adapter(binding.provider_name)
    if not adapter:
        return False, [f"Unknown provider: {binding.provider_name}"], {"provider": binding.provider_name}
    
    # Fetch latest identity data using asyncio.run for sync context
    normalized = None
    try:
        import asyncio
        normalized = asyncio.run(adapter.sync_identity(binding.external_identity_id))
    except Exception:
        # Fall back to cached binding data
        pass
    
    if not normalized:
        # Try cached binding
        from app.integrations.identity.base import NormalizedIdentity
        import json
        normalized = NormalizedIdentity(
            external_identity_id=binding.external_identity_id,
            provider=binding.provider_name,
            tenant_id=binding.tenant_id,
            agent_name=binding.agent_name,
            agent_type=binding.agent_type,
            owner_ids=json.loads(binding.owner_ids_json) if binding.owner_ids_json else [],
            allowed_models=json.loads(binding.allowed_models_json) if binding.allowed_models_json else [],
            budget_limit=binding.budget_limit,
            tpm_limit=binding.tpm_limit,
            expires_at=binding.expires_at,
            status=binding.status or "unknown",
        )
    
    # Build workflow context
    nodes = db.query(WorkflowNode).join(WorkflowVersion).filter(
        WorkflowVersion.workflow_id == workflow_id,
        WorkflowVersion.is_current == True
    ).all()
    
    models_used = []
    for node in nodes:
        if node.node_type == "llm":
            cfg = json.loads(node.config) if node.config else {}
            if cfg.get("model"):
                models_used.append(cfg["model"])
    
    workflow_context = {
        "tenant_id": workflow_tenant_id,
        "workflow_id": workflow_id,
        "models_used": models_used,
    }
    
    # Evaluate constraints (sync method)
    result = adapter.evaluate_constraints(normalized, workflow_context)
    
    # Store policy evaluation result
    policy = PolicyEvaluationResult(
        id=str(uuid4()),
        provider_name=binding.provider_name,
        workflow_id=workflow_id,
        external_identity_id=binding.external_identity_id,
        evaluation_type=evaluation_type,
        is_allowed=result.is_allowed,
        reasons_json=json.dumps(result.reasons),
        metadata_json=json.dumps(result.metadata),
    )
    db.add(policy)
    db.commit()
    
    return result.is_allowed, result.reasons, result.metadata

# Schemas


class LangFlowImport(BaseModel):
    tenant_id: str
    name: str
    description: str | None = None
    flow_data: dict | None = None  # The raw Langflow JSON
    langflow_data: dict | None = None  # Backward-compatible alias


class ImportResponse(BaseModel):
    workflow_id: str
    version_id: str
    node_count: int
    edge_count: int
    issues_summary: str


class ValidationIssue(BaseModel):
    type: str  # unsupported_node, missing_config, etc.
    node_id: str | None = None
    message: str


class IdentityCheckResult(BaseModel):
    is_allowed: bool
    reasons: list[str]
    metadata: dict


class ValidationResponse(BaseModel):
    is_valid: bool
    can_publish: bool
    issues: list[ValidationIssue]
    unsupported_nodes: list[str]
    missing_configs: list[str]
    identity_check: IdentityCheckResult | None = None


class PublishResponse(BaseModel):
    workflow_id: str
    version_id: str
    artifact_id: str
    status: str


class RunResponse(BaseModel):
    run_id: str
    workflow_id: str
    status: str
    final_output: str | None = None


class RunDetailResponse(BaseModel):
    id: str
    workflow_id: str
    version_id: str
    status: str
    final_output: str | None = None
    started_at: str
    completed_at: str | None = None
    error_message: str | None = None
    steps: list
    memory_context: list[dict] = []
    memory_read_ids: list[str] = []
    memory_written_ids: list[str] = []
    resolved_skills: list[dict] = []


class RunRequest(BaseModel):
    product_id: str | None = None
    session_id: str | None = None
    persist_memory: bool = False
    persist_scope: str = "run"  # run or workflow
    persist_memory_type: str = "summary"
    persist_title: str | None = None


# Helpers


def normalize_node_type(node_data: dict) -> str:
    """Extract normalized node type from Langflow node data."""
    node_type = node_data.get("type", "").lower()
    # Map Langflow types to our types
    type_map = {
        "chatinput": "start",
        "textinput": "start",
        "prompt": "llm",
        "llm": "llm",
        "tool": "tool",
        "conditional": "condition",
        "if": "condition",
        " Router": "condition",
        "human": "human_approval",
        "chatoutput": "end",
        "textoutput": "end",
    }
    return type_map.get(node_type, node_type)


def _get_edges_for_node(node_id: str, edges: list) -> list:
    """Get outgoing edges for a node."""
    return [e for e in edges if e.get("source") == node_id]


def _resolve_skills_for_context(
    db: Session,
    tenant_id: str,
    workflow_id: str | None = None,
) -> list[dict]:
    """Resolve active skills and attach current version content where available."""
    q = db.query(SkillDefinition).filter(
        SkillDefinition.tenant_id == tenant_id,
        SkillDefinition.status == "active",
    )
    q = q.filter(
        (SkillDefinition.scope_type == "organization")
        | (
            (SkillDefinition.scope_type == "workflow")
            & (SkillDefinition.scope_id == workflow_id)
        )
    )
    skills = q.order_by(SkillDefinition.created_at.desc()).all()

    out: list[dict] = []
    for skill in skills:
        binding = None
        if workflow_id:
            binding = db.query(SkillBinding).filter(
                SkillBinding.skill_id == skill.id,
                SkillBinding.workflow_id == workflow_id,
            ).first()
        version = db.query(SkillVersion).filter(
            SkillVersion.skill_id == skill.id,
            SkillVersion.is_current == True,
        ).order_by(SkillVersion.version_number.desc()).first()
        out.append(
            {
                "id": skill.id,
                "name": skill.name,
                "slug": skill.slug,
                "scope_type": skill.scope_type,
                "scope_id": skill.scope_id,
                "skill_type": skill.skill_type,
                "binding_type": binding.binding_type if binding else None,
                "current_version_id": version.id if version else None,
                "current_version_number": version.version_number if version else None,
                "current_content_json": version.content_json if version else None,
            }
        )
    return out


# Endpoints


@router.post("/import/langflow", response_model=ImportResponse, status_code=201)
def import_langflow(import_data: LangFlowImport, db: Session = Depends(get_db)):
    """
    Import a Langflow-style workflow.
    Normalizes nodes and edges into DB records.
    """
    flow_data = import_data.flow_data or import_data.langflow_data
    if not flow_data:
        raise HTTPException(400, "flow_data (or langflow_data) is required")
    nodes = flow_data.get("nodes", [])
    edges = flow_data.get("edges", [])
    
    # Create workflow definition
    workflow = WorkflowDefinition(
        id=str(uuid4()),
        tenant_id=import_data.tenant_id,
        name=import_data.name,
        description=import_data.description,
        source_type="langflow",
        source_json=json.dumps(flow_data),
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    # Create version
    version = WorkflowVersion(
        id=str(uuid4()),
        workflow_id=workflow.id,
        version_number=1,
        is_current=True,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    
    # Normalize nodes
    node_count = 0
    unsupported_nodes = []
    
    for node in nodes:
        node_id = node.get("id", str(uuid4()))
        node_type = normalize_node_type(node)
        
        if node_type not in SUPPORTED_NODE_TYPES:
            unsupported_nodes.append(node_type)
            continue
        
        config = node.get("data", {}).get("node", {})
        
        wf_node = WorkflowNode(
            id=str(uuid4()),
            version_id=version.id,
            node_type=node_type,
            node_id=node_id,
            label=node.get("label", node_type),
            config=json.dumps(config),
            position_x=node.get("position", {}).get("x", 0),
            position_y=node.get("position", {}).get("y", 0),
        )
        db.add(wf_node)
        node_count += 1
    
    # Normalize edges
    edge_count = 0
    
    for edge in edges:
        wf_edge = WorkflowEdge(
            id=str(uuid4()),
            version_id=version.id,
            edge_id=edge.get("id"),
            source_node_id=edge.get("source"),
            target_node_id=edge.get("target"),
            edge_type=edge.get("type", "smooth"),
            label=edge.get("label"),
        )
        db.add(wf_edge)
        edge_count += 1
    
    db.commit()
    
    # Create initial validation placeholder
    issues_summary = "Imported with {} nodes, {} edges".format(node_count, edge_count)
    if unsupported_nodes:
        issues_summary += f" (warning: {len(unsupported_nodes)} unsupported node types)"
    
    return ImportResponse(
        workflow_id=workflow.id,
        version_id=version.id,
        node_count=node_count,
        edge_count=edge_count,
        issues_summary=issues_summary,
    )


@router.post("/{workflow_id}/validate", response_model=ValidationResponse)
def validate_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Validate a workflow for publish readiness.
    Checks supported node types and required config.
    Optionally evaluates identity constraints.
    """
    workflow = db.query(WorkflowDefinition).filter(
        WorkflowDefinition.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    # Get current version
    version = db.query(WorkflowVersion).filter(
        WorkflowVersion.workflow_id == workflow_id,
        WorkflowVersion.is_current == True
    ).first()
    if not version:
        raise HTTPException(400, "No current version found")
    
    # Validate nodes
    nodes = db.query(WorkflowNode).filter(
        WorkflowNode.version_id == version.id
    ).all()
    
    issues = []
    unsupported_nodes = []
    missing_configs = []
    
    for node in nodes:
        # Check node type
        if node.node_type not in SUPPORTED_NODE_TYPES:
            issues.append(ValidationIssue(
                type="unsupported_node",
                node_id=node.node_id,
                message=f"Node type '{node.node_type}' is not supported",
            ))
            unsupported_nodes.append(node.node_type)
        
        # Check required config
        config = json.loads(node.config) if node.config else {}
        
        if node.node_type == "llm" and not config.get("model"):
            issues.append(ValidationIssue(
                type="missing_config",
                node_id=node.node_id,
                message="LLM node missing 'model' config",
            ))
            missing_configs.append(node.node_id)
        
        if node.node_type == "tool" and not config.get("tool_name"):
            issues.append(ValidationIssue(
                type="missing_config",
                node_id=node.node_id,
                message="Tool node missing 'tool_name' config",
            ))
            missing_configs.append(node.node_id)
    
    # Check for start and end nodes
    node_types = {n.node_type for n in nodes}
    
    if "start" not in node_types:
        issues.append(ValidationIssue(
            type="missing_node",
            node_id=None,
            message="Workflow missing 'start' node",
        ))
        missing_configs.append("start")
    
    if "end" not in node_types:
        issues.append(ValidationIssue(
            type="missing_node",
            node_id=None,
            message="Workflow missing 'end' node",
        ))
        missing_configs.append("end")
    
    is_valid = len(issues) == 0
    can_publish = is_valid
    
    # Evaluate identity constraints (optional - record results but don't block validation)
    identity_allowed, identity_reasons, identity_metadata = _evaluate_identity_for_workflow(
        db, workflow_id, workflow.tenant_id, "validate"
    )
    
    # Store validation result
    validation = WorkflowValidationResult(
        id=str(uuid4()),
        workflow_id=workflow_id,
        version_id=version.id,
        is_valid=is_valid,
        issues_json=json.dumps([i.model_dump() for i in issues]),
        can_publish=can_publish,
    )
    db.add(validation)
    db.commit()
    
    # Add identity info to response
    return ValidationResponse(
        is_valid=is_valid,
        can_publish=can_publish,
        issues=issues,
        unsupported_nodes=list(set(unsupported_nodes)),
        missing_configs=missing_configs,
        identity_check=IdentityCheckResult(
            is_allowed=identity_allowed,
            reasons=identity_reasons,
            metadata=identity_metadata,
        ) if identity_metadata.get("has_binding", True) else None,
    )


@router.post("/{workflow_id}/publish", response_model=PublishResponse, status_code=201)
def publish_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Publish a workflow.
    Creates a publish artifact and marks version as published.
    Blocks publish if identity-backed policy fails.
    """
    workflow = db.query(WorkflowDefinition).filter(
        WorkflowDefinition.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    # Check latest validation
    validation = db.query(WorkflowValidationResult).filter(
        WorkflowValidationResult.workflow_id == workflow_id
    ).order_by(WorkflowValidationResult.created_at.desc()).first()
    
    if validation and not validation.can_publish:
        raise HTTPException(400, "Workflow cannot be published - fix validation issues first")
    
    # Evaluate identity constraints - block publish if fails
    identity_allowed, identity_reasons, _ = _evaluate_identity_for_workflow(
        db, workflow_id, workflow.tenant_id, "publish"
    )
    
    if not identity_allowed:
        raise HTTPException(403, f"Publish blocked by identity policy: {'; '.join(identity_reasons)}")
    
    # Get current version
    version = db.query(WorkflowVersion).filter(
        WorkflowVersion.workflow_id == workflow_id,
        WorkflowVersion.is_current == True
    ).first()
    if not version:
        raise HTTPException(400, "No current version found")
    
    # Build runtime spec
    nodes = db.query(WorkflowNode).filter(
        WorkflowNode.version_id == version.id
    ).all()
    edges = db.query(WorkflowEdge).filter(
        WorkflowEdge.version_id == version.id
    ).all()
    
    runtime_spec = {
        "workflow_id": workflow_id,
        "version_id": version.id,
        "nodes": [
            {
                "id": n.node_id,
                "type": n.node_type,
                "label": n.label,
                "config": json.loads(n.config) if n.config else {},
            }
            for n in nodes
        ],
        "edges": [
            {
                "source": e.source_node_id,
                "target": e.target_node_id,
                "label": e.label,
            }
            for e in edges
        ],
    }
    
    # Create publish artifact
    artifact = WorkflowPublishArtifact(
        id=str(uuid4()),
        workflow_id=workflow_id,
        version_id=version.id,
        artifact_json=json.dumps(runtime_spec),
    )
    db.add(artifact)
    
    # Update workflow
    workflow.is_published = True
    workflow.published_version_id = version.id
    
    db.commit()
    
    return PublishResponse(
        workflow_id=workflow_id,
        version_id=version.id,
        artifact_id=artifact.id,
        status="published",
    )


@router.post("/{workflow_id}/run", response_model=RunResponse)
def run_workflow(
    workflow_id: str,
    run_request: RunRequest | None = Body(default=None),
    db: Session = Depends(get_db),
):
    """
    Execute a workflow.
    Simple interpreted execution for supported node types.
    Blocks run if identity-backed policy fails.
    """
    workflow = db.query(WorkflowDefinition).filter(
        WorkflowDefinition.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    if not workflow.is_published:
        raise HTTPException(400, "Workflow must be published before running")
    

    run_request = run_request or RunRequest()
    tenant_id = workflow.tenant_id

    # Evaluate identity constraints - block run if fails
    identity_allowed, identity_reasons, _ = _evaluate_identity_for_workflow(
        db, workflow_id, workflow.tenant_id, "run"
    )
    
    if not identity_allowed:
        raise HTTPException(403, f"Run blocked by identity policy: {'; '.join(identity_reasons)}")
    
    # Get current version
    version = db.query(WorkflowVersion).filter(
        WorkflowVersion.workflow_id == workflow_id,
        WorkflowVersion.is_current == True
    ).first()
    
    # Create run
    run = WorkflowRun(
        id=str(uuid4()),
        workflow_id=workflow_id,
        version_id=version.id,
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    resolved_entries, _, resolved_context = MemoryService.resolve(
        db,
        tenant_id=tenant_id,
        scopes={
            "organization": tenant_id,
            "product": run_request.product_id,
            "workflow": workflow_id,
            "run": run.id,
            "session": run_request.session_id,
        },
        is_active=True,
    )
    memory_context = [
        {
            "scope_type": c["scope_type"],
            "scope_id": c["scope_id"],
            "entries": [
                {
                    "id": e.id,
                    "memory_type": e.memory_type,
                    "title": e.title,
                    "content": e.content[:200],
                }
                for e in c["entries"]
            ],
        }
        for c in resolved_context
    ]
    memory_read_ids = [e.id for e in resolved_entries]
    run.memory_context_json = json.dumps(memory_context)
    run.memory_read_ids_json = json.dumps(memory_read_ids)
    db.commit()
    
    # Get nodes and edges
    nodes = db.query(WorkflowNode).filter(
        WorkflowNode.version_id == version.id
    ).all()
    edges = db.query(WorkflowEdge).filter(
        WorkflowEdge.version_id == version.id
    ).all()
    
    # Build node map
    node_map = {n.node_id: n for n in nodes}
    
    # Simple execution: find start, follow edges
    start_node = next((n for n in nodes if n.node_type == "start"), None)
    if not start_node:
        run.status = "failed"
        run.error_message = "No start node found"
        db.commit()
        raise HTTPException(400, "No start node found")
    
    current_node = start_node
    outputs = {}
    
    while current_node:
        node_id = current_node.node_id
        node_type = current_node.node_type
        
        # Create step
        step = WorkflowRunStep(
            id=str(uuid4()),
            run_id=run.id,
            node_id=node_id,
            node_type=node_type,
            status="completed",
            completed_at=datetime.utcnow(),
        )
        db.add(step)
        
        # Execute based on type
        if node_type == "start":
            output = "Started workflow"
        elif node_type == "llm":
            config = json.loads(current_node.config) if current_node.config else {}
            output = f"LLM response (model: {config.get('model', 'unknown')})"
        elif node_type == "tool":
            config = json.loads(current_node.config) if current_node.config else {}
            output = f"Tool executed: {config.get('tool_name', 'unknown')}"
        elif node_type == "condition":
            # Simple branching: always take first edge
            config = json.loads(current_node.config) if current_node.config else {}
            condition = config.get("condition", "true")
            step.branch_decision = "true" if condition else "false"
            output = f"Condition evaluated: {condition}"
        elif node_type == "human_approval":
            # Mock approval
            output = "Approved (mocked)"
        elif node_type == "end":
            output = "Workflow completed"
            run.status = "completed"
            run.final_output = output
            db.commit()
            break
        else:
            output = f"Executed {node_type}"
        
        outputs[node_id] = output
        step.output = output
        db.commit()
        
        # Find next node
        outgoing = [e for e in edges if e.source_node_id == node_id]
        
        if not outgoing:
            if node_type != "end":
                run.status = "completed"
                db.commit()
            break
        
        # For conditions, follow branch decision
        next_edge = outgoing[0]
        if node_type == "condition":
            # Simple: always take first edge
            pass
        
        next_node_id = next_edge.target_node_id
        current_node = node_map.get(next_node_id)
    
    if run.status == "running":
        run.status = "completed"

    memory_written_ids: list[str] = []
    if run_request.persist_memory:
        write_scope_id = run.id if run_request.persist_scope == "run" else workflow_id
        written = MemoryService.persist_entry(
            db,
            tenant_id=tenant_id,
            scope_type=run_request.persist_scope,
            scope_id=write_scope_id,
            memory_type=run_request.persist_memory_type,
            title=run_request.persist_title or f"Workflow run summary {run.id}",
            content=run.final_output or "Workflow completed without explicit output",
            tags=["workflow", "writeback"],
            source_type="run",
            source_id=run.id,
            source_metadata={"workflow_id": workflow_id},
            metadata={"write_mode": "explicit"},
        )
        memory_written_ids.append(written.id)
        run.memory_write_mode = "explicit"

    run.memory_written_ids_json = json.dumps(memory_written_ids)
    
    db.commit()
    
    return RunResponse(
        run_id=run.id,
        workflow_id=workflow_id,
        status=run.status,
        final_output=run.final_output,
    )


@router.get("/{workflow_id}/runs/{run_id}", response_model=RunDetailResponse)
def get_run_detail(workflow_id: str, run_id: str, db: Session = Depends(get_db)):
    """
    Get workflow run details including steps.
    """
    run = db.query(WorkflowRun).filter(
        WorkflowRun.id == run_id,
        WorkflowRun.workflow_id == workflow_id,
    ).first()
    if not run:
        raise HTTPException(404, "Run not found")
    
    steps = db.query(WorkflowRunStep).filter(
        WorkflowRunStep.run_id == run_id
    ).order_by(WorkflowRunStep.started_at).all()
    
    memory_context = json.loads(run.memory_context_json or "[]")
    memory_read_ids = json.loads(run.memory_read_ids_json or "[]")
    memory_written_ids = json.loads(run.memory_written_ids_json or "[]")
    workflow = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == workflow_id).first()
    resolved_skills = _resolve_skills_for_context(
        db,
        tenant_id=workflow.tenant_id if workflow else "",
        workflow_id=workflow_id,
    ) if workflow else []
    
    return RunDetailResponse(
        id=run.id,
        workflow_id=run.workflow_id,
        version_id=run.version_id,
        status=run.status,
        final_output=run.final_output,
        started_at=run.started_at.isoformat() if run.started_at else None,
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
        error_message=run.error_message,
        steps=[
            {
                "node_id": s.node_id,
                "node_type": s.node_type,
                "status": s.status,
                "output": s.output,
                "branch_decision": s.branch_decision,
                "error": s.error,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in steps
        ],
        memory_context=memory_context,
        memory_read_ids=memory_read_ids,
        memory_written_ids=memory_written_ids,
        resolved_skills=resolved_skills,
    )
