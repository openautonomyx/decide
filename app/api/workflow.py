"""
Workflow API Router
Import, validate, publish, and run workflows.
"""
import json
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
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

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Supported node types for MVP
SUPPORTED_NODE_TYPES = {"start", "llm", "tool", "condition", "human_approval", "end"}

# Schemas


class LangFlowImport(BaseModel):
    tenant_id: str
    name: str
    description: str | None = None
    flow_data: dict  # The raw Langflow JSON


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


class ValidationResponse(BaseModel):
    is_valid: bool
    can_publish: bool
    issues: list[ValidationIssue]
    unsupported_nodes: list[str]
    missing_configs: list[str]


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


# Endpoints


@router.post("/import/langflow", response_model=ImportResponse)
def import_langflow(import_data: LangFlowImport, db: Session = Depends(get_db)):
    """
    Import a Langflow-style workflow.
    Normalizes nodes and edges into DB records.
    """
    flow_data = import_data.flow_data
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
                type="unssupported_node",
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
    
    return ValidationResponse(
        is_valid=is_valid,
        can_publish=can_publish,
        issues=issues,
        unsupported_nodes=list(set(unsupported_nodes)),
        missing_configs=missing_configs,
    )


@router.post("/{workflow_id}/publish", response_model=PublishResponse)
def publish_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Publish a workflow.
    Creates a publish artifact and marks version as published.
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
def run_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Execute a workflow.
    Simple interpreted execution for supported node types.
    """
    workflow = db.query(WorkflowDefinition).filter(
        WorkflowDefinition.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    if not workflow.is_published:
        raise HTTPException(400, "Workflow must be published before running")
    
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
    )