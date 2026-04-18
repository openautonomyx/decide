"""
Tool API Endpoints
Phase 0 - Tool registry and governance APIs

Admin APIs:
- GET /tools - List tools
- GET /tools/{id} - Get tool
- POST /tools - Register tool
- PATCH /tools/{id} - Update tool
- DELETE /tools/{id} - Deprecate tool
- GET /tools/categories - List categories

Runtime APIs:
- GET /tools/search - Search tools
- GET /tools/{id}/schema - Get tool schema
- GET /tools/risks/{risk_level} - Get tools by risk
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.tool import get_tool_registry_service

router = APIRouter(prefix="/tools", tags=["tool"])


@router.get("")
async def list_tools(
    category: Optional[str] = None,
    enabled_only: bool = Query(False),
    status: Optional[str] = None,
):
    """List tools with optional filtering."""
    service = get_tool_registry_service()
    return service.list_tools(category=category, enabled_only=enabled_only, status=status)


@router.get("/search")
async def search_tools(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
):
    """Search tools by query."""
    service = get_tool_registry_service()
    return service.search_tools(q, category, risk_level)


@router.get("/categories")
async def list_categories():
    """List tool categories."""
    service = get_tool_registry_service()
    return service.list_categories()


@router.get("/risks/{risk_level}")
async def get_tools_by_risk(risk_level: str):
    """Get tools by risk level."""
    service = get_tool_registry_service()
    return service.get_tools_by_risk(risk_level)


@router.get("/approvals-required")
async def get_tools_requiring_approval():
    """Get tools that require approval before use."""
    service = get_tool_registry_service()
    return service.get_tools_requiring_approval()


@router.get("/{tool_id}")
async def get_tool(tool_id: str):
    """Get tool by ID."""
    service = get_tool_registry_service()
    tool = service.get_tool(tool_id)
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return tool


@router.get("/{tool_id}/schema")
async def get_tool_schema(tool_id: str):
    """Get tool schema."""
    service = get_tool_registry_service()
    tool = service.get_tool(tool_id)
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return {"schema": tool.get("schema", {})}


@router.post("")
async def create_tool(
    name: str,
    category: str,
    description: str = "",
    schema: Optional[dict] = None,
    handler: str = "",
    requires_approval: bool = False,
    risk_level: str = "low",
):
    """Register a new tool."""
    service = get_tool_registry_service()
    tool = service.register_tool(
        name=name,
        category=category,
        description=description,
        schema=schema,
        handler=handler,
        requires_approval=requires_approval,
        risk_level=risk_level,
    )
    return tool


@router.patch("/{tool_id}")
async def update_tool(tool_id: str, updates: dict):
    """Update tool configuration."""
    service = get_tool_registry_service()
    success = service.update_tool(tool_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return {"id": tool_id, "status": "updated"}


@router.delete("/{tool_id}")
async def deprecate_tool(tool_id: str):
    """Mark tool as deprecated."""
    service = get_tool_registry_service()
    success = service.deprecate_tool(tool_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return {"id": tool_id, "status": "deprecated"}


@router.post("/{tool_id}/enable")
async def enable_tool(tool_id: str, enabled: bool = True):
    """Enable or disable tool."""
    service = get_tool_registry_service()
    success = service.enable_tool(tool_id, enabled)
    
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return {"id": tool_id, "status": "enabled" if enabled else "disabled"}