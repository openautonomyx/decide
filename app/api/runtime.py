"""
Runtime API Endpoints
Phase 0 - Runtime registry and selection APIs

Admin APIs:
- GET /runtimes - List all runtimes
- GET /runtimes/{id} - Get runtime by ID
- POST /runtimes - Create runtime
- PATCH /runtimes/{id} - Update runtime

Runtime APIs:
- GET /runtimes/select - Select runtime for task type
- GET /health - Health check summary
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.runtime import get_runtime_registry_service

router = APIRouter(prefix="/runtimes", tags=["runtime"])


@router.get("")
async def list_runtimes(enabled_only: bool = Query(False)):
    """List all runtimes."""
    service = get_runtime_registry_service()
    return service.list_runtimes(enabled_only=enabled_only)


@router.get("/select")
async def select_runtime(
    task_type: str = Query(..., description="Task type (coding, conversation, etc.)"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID for policy lookup"),
):
    """Select best runtime for task type."""
    service = get_runtime_registry_service()
    runtime_id = service.select_runtime(task_type, tenant_id)
    
    if not runtime_id:
        raise HTTPException(status_code=404, detail="No suitable runtime found")
    
    runtime = service.get_runtime(runtime_id)
    return {"runtime_id": runtime_id, "runtime": runtime}


@router.get("/health")
async def get_health():
    """Get overall health summary."""
    service = get_runtime_registry_service()
    return service.get_health_summary()


@router.get("/{runtime_id}")
async def get_runtime(runtime_id: str):
    """Get runtime by ID."""
    service = get_runtime_registry_service()
    runtime = service.get_runtime(runtime_id)
    
    if not runtime:
        raise HTTPException(status_code=404, detail="Runtime not found")
    
    return runtime


@router.post("")
async def create_runtime(
    name: str,
    type: str = "langgraph",
    description: str = "",
    max_context_tokens: int = 200000,
    supports_tools: bool = True,
    supports_checkpoint: bool = False,
):
    """Create a new runtime."""
    import uuid
    runtime_id = f"runtime-{uuid.uuid4().hex[:12]}"
    
    service = get_runtime_registry_service()
    service.register_runtime(runtime_id, {
        "name": name,
        "type": type,
        "description": description,
        "max_context_tokens": max_context_tokens,
        "supports_tools": supports_tools,
        "supports_checkpoint": supports_checkpoint,
    })
    
    return {"id": runtime_id, "status": "created"}


@router.patch("/{runtime_id}")
async def update_runtime(runtime_id: str, updates: dict):
    """Update runtime configuration."""
    service = get_runtime_registry_service()
    success = service.update_runtime(runtime_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Runtime not found")
    
    return {"id": runtime_id, "status": "updated"}


# Instance endpoints
@router.get("/instances")
async def list_instances(runtime_id: Optional[str] = None):
    """List runtime instances."""
    service = get_runtime_registry_service()
    return service.list_instances(runtime_id)


@router.get("/instances/{instance_id}")
async def get_instance(instance_id: str):
    """Get instance by ID."""
    service = get_runtime_registry_service()
    instance = service.get_instance(instance_id)
    
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return instance