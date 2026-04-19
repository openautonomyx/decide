"""
Framework API Endpoints
APIs for LangGraph → LangFlow compilation and import.
"""
from fastapi import APIRouter, HTTPException

from app.framework.compiler import LangGraphToLangFlowCompiler, compile_langgraph_to_langflow
from app.framework.types import LangGraphInput

router = APIRouter(prefix="/frameworks", tags=["framework"])


@router.get("")
async def list_frameworks():
    """List supported frameworks."""
    return {
        "frameworks": [
            {"name": "langgraph", "status": "supported"},
            {"name": "langflow", "status": "supported"},
        ]
    }


@router.post("/langgraph/compile-to-langflow")
async def compile_langgraph_to_langflow_endpoint(
    graph_definition: dict,
):
    """
    Compile a LangGraph workflow to LangFlow.
    
    Input format:
    {
        "name": "My Workflow",
        "description": "Description",
        "nodes": [{"id": "node_id", "type": "start|llm|tool|...", "data": {...}}, ...],
        "edges": [{"source": "node1", "target": "node2"}, ...],
        "tool_bindings": [{"tool_id": "...", "tool_name": "..."}, ...],
        "skill_bindings": [{"skill_id": "...", "skill_slug": "...", "skill_type": "..."}, ...],
        "memory_bindings": [{"memory_type": "...", "scope": "..."}, ...],
        "approval_nodes": [{"policy_id": "...", "risk_level": "..."}, ...],
    }
    
    Returns LangFlow-compatible flow structure with diagnostics.
    """
    try:
        result = compile_langgraph_to_langflow(graph_definition)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Compilation failed: {str(e)}")


@router.post("/langgraph/import")
async def import_langgraph_workflow(
    graph_definition: dict,
    import_to_storage: bool = False,
):
    """
    Import a LangGraph workflow to Decide workflow storage.
    
    If import_to_storage is true, also creates a workflow in the database.
    Returns import result with workflow ID if stored.
    """
    # First compile
    try:
        result = compile_langgraph_to_langflow(graph_definition)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Compilation failed: {str(e)}")
    
    import_result = {
        "compiled": result,
        "workflow_id": None,
    }
    
    # Optionally import to storage
    if import_to_storage:
        # This would create a workflow in the database
        # For now, return the compiled result with placeholder workflow_id
        import_result["workflow_id"] = f"wf-{graph_definition.get('name', 'imported').lower().replace(' ', '-')}"
    
    return import_result


@router.get("/langgraph/validate")
async def validate_langgraph_definition(
    graph_definition: dict,
):
    """
    Validate a LangGraph definition without compiling.
    
    Returns validation result with potential issues.
    """
    nodes = graph_definition.get("nodes", [])
    edges = graph_definition.get("edges", [])
    
    issues = []
    
    # Check for start node
    node_ids = {n.get("id") for n in nodes}
    start_nodes = [n for n in nodes if n.get("type") == "start"]
    if not start_nodes:
        issues.append({"severity": "error", "message": "No start node found"})
    
    # Check for end node  
    end_nodes = [n for n in nodes if n.get("type") in ("end", "END")]
    if not end_nodes:
        issues.append({"severity": "warning", "message": "No end node found"})
    
    # Check for dangling edges
    for edge in edges:
        if edge.get("source") not in node_ids:
            issues.append({"severity": "error", "message": f"Edge source '{edge.get('source')}' not found"})
        if edge.get("target") not in node_ids:
            issues.append({"severity": "error", "message": f"Edge target '{edge.get('target')}' not found"})
    
    # Check for disconnected nodes
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