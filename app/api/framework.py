"""
Framework API Endpoints
APIs for LangGraph -> LangFlow compilation and import into Decide.
"""
import json
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.framework.compiler import compile_langgraph_to_langflow
from app.models.workflow_definition import WorkflowDefinition, WorkflowVersion, WorkflowNode, WorkflowEdge

router = APIRouter(prefix="/frameworks", tags=["framework"])

DECIDE_SUPPORTED_NODE_TYPES = {"start", "llm", "tool", "condition", "human_approval", "end", "memory", "skill", "approval"}


def normalize_node_type(node_type: str) -> str:
    """Normalize LangGraph node type to Decide node type."""
    mapping = {
        "start": "start",
        "end": "end",
        "END": "end",
        "llm": "llm",
        "tool": "tool",
        "prompt": "llm",
        "condition": "condition",
        "decision": "condition",
        "router": "condition",
        "approval": "human_approval",
        "memory": "memory",
        "skill": "skill",
    }
    return mapping.get(node_type, node_type)


@router.get("")
async def list_frameworks():
    return {
        "frameworks": [
            {"name": "langgraph", "status": "supported"},
            {"name": "langflow", "status": "supported"},
        ]
    }


@router.post("/langgraph/compile-to-langflow")
async def compile_langgraph_to_langflow_endpoint(graph_definition: dict):
    try:
        result = compile_langgraph_to_langflow(graph_definition)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Compilation failed: {str(e)}")


@router.post("/langgraph/import")
async def import_langgraph_workflow(
    tenant_id: str,
    graph_definition: dict,
    db: Session = Depends(get_db),
):
    """Import a LangGraph workflow to Decide workflow storage."""
    try:
        compile_result = compile_langgraph_to_langflow(graph_definition)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Compilation failed: {str(e)}")

    workflow_id = str(uuid4())
    workflow_name = graph_definition.get("name", "Imported Workflow")
    workflow_description = graph_definition.get("description", "")

    workflow = WorkflowDefinition(
        id=workflow_id,
        tenant_id=tenant_id,
        name=workflow_name,
        description=workflow_description,
        source_type="langgraph",
        source_json=json.dumps(compile_result["langflow_flow"]),
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    version_id = str(uuid4())
    version = WorkflowVersion(
        id=version_id,
        workflow_id=workflow_id,
        version_number=1,
        is_current=True,
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    nodes_imported = 0
    lf_flow = compile_result["langflow_flow"]
    for node in lf_flow.get("nodes", []):
        node_type = node.get("type", "unknown")
        normalized = normalize_node_type(node_type)
        if normalized not in DECIDE_SUPPORTED_NODE_TYPES:
            continue

        node_db_id = str(uuid4())

        node_data = node.get("data", {})
        metadata = node_data.get("metadata", {})

        config = {
            "original_type": metadata.get("original_type", node_type),
            "original_data": node_data.get("node", {}),
            "tool_config": node_data.get("tool_config", {}),
            "skill_config": node_data.get("skill_config", {}),
            "memory_config": node_data.get("memory_config", {}),
            "approval_config": node_data.get("approval_config", {}),
        }

        wf_node = WorkflowNode(
            id=node_db_id,
            version_id=version_id,
            node_type=normalized,
            node_id=node.get("id", ""),
            label=node.get("label", normalized),
            config=json.dumps(config),
            position_x=node.get("position", {}).get("x", 0),
            position_y=node.get("position", {}).get("y", 0),
        )
        db.add(wf_node)
        nodes_imported += 1

    edges_imported = 0
    for edge in lf_flow.get("edges", []):
        source_original = edge.get("source", "")
        target_original = edge.get("target", "")
        if source_original and target_original:
            wf_edge = WorkflowEdge(
                id=str(uuid4()),
                version_id=version_id,
                source_node_id=source_original,
                target_node_id=target_original,
                edge_type="direct",
            )
            db.add(wf_edge)
            edges_imported += 1

    db.commit()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "version_id": version_id,
        "name": workflow_name,
        "nodes_imported": nodes_imported,
        "edges_imported": edges_imported,
    }


@router.get("/langgraph/validate")
async def validate_langgraph_definition(graph_definition: dict):
    """Validate a LangGraph definition without compiling."""
    nodes = graph_definition.get("nodes", [])
    edges = graph_definition.get("edges", [])

    issues = []
    node_ids = {n.get("id") for n in nodes}

    start_nodes = [n for n in nodes if n.get("type") == "start"]
    if not start_nodes:
        issues.append({"severity": "error", "message": "No start node found"})

    end_nodes = [n for n in nodes if n.get("type") in ("end", "END")]
    if not end_nodes:
        issues.append({"severity": "warning", "message": "No end node found"})

    for edge in edges:
        if edge.get("source") not in node_ids:
            issues.append({"severity": "error", "message": f"Edge source '{edge.get('source')}' not found"})
        if edge.get("target") not in node_ids:
            issues.append({"severity": "error", "message": f"Edge target '{edge.get('target')}' not found"})

    for node in nodes:
        node_type = node.get("type", "")
        normalized = normalize_node_type(node_type)
        if normalized not in DECIDE_SUPPORTED_NODE_TYPES:
            issues.append({
                "severity": "warning",
                "message": f"Node type '{node_type}' may not fully import to Decide",
                "node_id": node.get("id"),
            })

    connected = set()
    for edge in edges:
        connected.add(edge.get("source"))
        connected.add(edge.get("target"))

    for node in nodes:
        if node.get("id") not in connected and node.get("type") not in ("start", "end", "END"):
            issues.append({"severity": "warning", "message": f"Node '{node.get('id')}' may be disconnected"})

    return {
        "valid": len([i for i in issues if i.get("severity") == "error"]) == 0,
        "issues": issues,
    }


@router.get("/roundtrip/{workflow_id}")
async def roundtrip_export(workflow_id: str, db: Session = Depends(get_db)):
    """Export a Decide workflow back to LangGraph format."""
    workflow = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    version = db.query(WorkflowVersion).filter(
        WorkflowVersion.workflow_id == workflow_id,
        WorkflowVersion.is_current == True
    ).first()

    if not version:
        raise HTTPException(status_code=404, detail="No current version found")

    nodes = db.query(WorkflowNode).filter(WorkflowNode.version_id == version.id).all()
    edges = db.query(WorkflowEdge).filter(WorkflowEdge.version_id == version.id).all()

    langgraph_nodes = []
    for node in nodes:
        config = json.loads(node.config) if node.config else {}

        langgraph_nodes.append({
            "id": node.node_id,
            "legacy_id": node.id,
            "type": node.node_type,
            "data": config.get("original_data", {}),
            "metadata": {
                "decide_node_db_id": node.id,
                "original_type": config.get("original_type"),
                "tool_config": config.get("tool_config", {}),
                "skill_config": config.get("skill_config", {}),
                "memory_config": config.get("memory_config", {}),
                "approval_config": config.get("approval_config", {}),
            },
            "position": {"x": node.position_x, "y": node.position_y},
        })

    langgraph_edges = []
    for edge in edges:
        source_node = next((n for n in nodes if n.id == edge.source_node_id), None)
        target_node = next((n for n in nodes if n.id == edge.target_node_id), None)
        if source_node and target_node:
            langgraph_edges.append({
                "source": source_node.node_id,
                "target": target_node.node_id,
            })

    return {
        "name": workflow.name,
        "description": workflow.description,
        "source_type": workflow.source_type,
        "nodes": langgraph_nodes,
        "edges": langgraph_edges,
    }
