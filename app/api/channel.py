"""
Channel API Endpoints
Phase 0 - Channel, branch, worker, cortex APIs

Admin APIs:
- GET /channels - List channels
- POST /channels - Create channel
- PATCH /channels/{id} - Update channel

Runtime APIs:
- GET /threads/{id}/branches - List branches for thread
- POST /threads/{id}/branch - Create branch
- POST /workers - Create worker
- PATCH /workers/{id}/state - Update worker state
- GET /cortex/{thread_id}/summary - Get latest summary
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.channel import (
    get_channel_service,
    get_branch_service,
    get_worker_service,
    get_cortex_service,
)

router = APIRouter(prefix="", tags=["channel"])


# ========== Channel Endpoints ==========

@router.get("/channels")
async def list_channels(enabled_only: bool = Query(False)):
    """List all channels."""
    service = get_channel_service()
    return service.list_channels(enabled_only=enabled_only)


@router.post("/channels")
async def create_channel(
    name: str,
    channel_type: str = "web",
    config: Optional[dict] = None,
):
    """Create a new channel."""
    service = get_channel_service()
    channel = service.create_channel(name, channel_type, config)
    return channel


@router.get("/channels/{channel_id}")
async def get_channel(channel_id: str):
    """Get channel by ID."""
    service = get_channel_service()
    channel = service.get_channel(channel_id)
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return channel


@router.patch("/channels/{channel_id}")
async def update_channel(channel_id: str, updates: dict):
    """Update channel."""
    service = get_channel_service()
    success = service.update_channel(channel_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return {"id": channel_id, "status": "updated"}


# ========== Branch Endpoints ==========

@router.get("/threads/{thread_id}/branches")
async def list_branches(thread_id: str):
    """List branches for a thread."""
    service = get_branch_service()
    return service.list_branches(thread_id)


@router.post("/threads/{thread_id}/branch")
async def create_branch(
    thread_id: str,
    channel_id: str,
    parent_branch_id: Optional[str] = None,
    branch_type: str = "main",
):
    """Create a new branch for a thread."""
    service = get_branch_service()
    branch = service.create_branch(thread_id, channel_id, parent_branch_id, branch_type)
    return branch


@router.get("/branches/{branch_id}")
async def get_branch(branch_id: str):
    """Get branch by ID."""
    service = get_branch_service()
    branch = service.get_branch(branch_id)
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    return branch


@router.post("/branches/{branch_id}/merge")
async def merge_branch(branch_id: str):
    """Mark branch as merged."""
    service = get_branch_service()
    success = service.merge_branch(branch_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    return {"id": branch_id, "status": "merged"}


@router.post("/branches/{branch_id}/close")
async def close_branch(branch_id: str):
    """Close a branch."""
    service = get_branch_service()
    success = service.close_branch(branch_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    return {"id": branch_id, "status": "closed"}


# ========== Worker Endpoints ==========

@router.post("/workers")
async def create_worker(
    branch_id: str,
    worker_type: str = "execution",
    runtime_id: Optional[str] = None,
):
    """Create a new worker."""
    service = get_worker_service()
    worker = service.create_worker(branch_id, worker_type, runtime_id)
    return worker


@router.get("/workers/{worker_id}")
async def get_worker(worker_id: str):
    """Get worker by ID."""
    service = get_worker_service()
    worker = service.get_worker(worker_id)
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return worker


@router.patch("/workers/{worker_id}/state")
async def update_worker_state(worker_id: str, state: dict):
    """Update worker state."""
    service = get_worker_service()
    success = service.update_worker_state(worker_id, state)
    
    if not success:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return {"id": worker_id, "status": "state_updated"}


@router.post("/workers/{worker_id}/start")
async def start_worker(worker_id: str):
    """Mark worker as started."""
    service = get_worker_service()
    success = service.start_worker(worker_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return {"id": worker_id, "status": "started"}


@router.post("/workers/{worker_id}/complete")
async def complete_worker(worker_id: str, final_state: Optional[dict] = None):
    """Mark worker as completed."""
    service = get_worker_service()
    success = service.complete_worker(worker_id, final_state)
    
    if not success:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return {"id": worker_id, "status": "completed"}


@router.post("/workers/{worker_id}/fail")
async def fail_worker(worker_id: str, error: str):
    """Mark worker as failed."""
    service = get_worker_service()
    success = service.fail_worker(worker_id, error)
    
    if not success:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return {"id": worker_id, "status": "failed", "error": error}


# ========== Cortex Endpoints ==========

@router.get("/cortex/{thread_id}/summary")
async def get_cortex_summary(thread_id: str):
    """Get latest cortex summary for a thread."""
    service = get_cortex_service()
    summary = service.get_latest_summary(thread_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="No summary found")
    
    return summary


@router.get("/cortex/{thread_id}/summaries")
async def list_cortex_summaries(thread_id: str, limit: int = Query(10)):
    """List cortex summaries for a thread."""
    service = get_cortex_service()
    return service.list_summaries(thread_id, limit)