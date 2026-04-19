# Memory API Router
# Scoped memory CRUD and resolution
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import json

from app.db.session import get_db
from app.models.memory import MemorySpace, MemoryEntry
from app.schemas.memory import (
    MemorySpaceCreate,
    MemorySpaceUpdate,
    MemorySpaceResponse,
    MemorySpaceList,
    MemoryEntryCreate,
    MemoryEntryUpdate,
    MemoryEntryResponse,
    MemoryEntryList,
    MemoryResolveParams,
    MemoryResolveResponse,
)

router = APIRouter(prefix="/memory", tags=["memory"])

# Resolution priority order
SCOPE_PRIORITY = ["organization", "product", "workflow", "run"]


@router.post("/spaces", response_model=MemorySpaceResponse)
async def create_space(
    body: MemorySpaceCreate,
    db: Session = Depends(get_db),
):
    """Create a memory space."""
    # Verify tenant exists
    from app.models.tenant_employee import Tenant
    tenant = db.query(Tenant).filter(Tenant.id == body.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    space = MemorySpace(
        id=str(uuid.uuid4()),
        tenant_id=body.tenant_id,
        scope_type=body.scope_type,
        scope_id=body.scope_id,
        name=body.name,
        description=body.description,
    )
    db.add(space)
    db.commit()
    db.refresh(space)
    return space


@router.get("/spaces", response_model=MemorySpaceList)
async def list_spaces(
    tenant_id: Optional[str] = None,
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List memory spaces."""
    q = db.query(MemorySpace)
    if tenant_id:
        q = q.filter(MemorySpace.tenant_id == tenant_id)
    if scope_type:
        q = q.filter(MemorySpace.scope_type == scope_type)
    if scope_id:
        q = q.filter(MemorySpace.scope_id == scope_id)
    items = q.order_by(MemorySpace.created_at.desc()).limit(limit).all()
    return MemorySpaceList(items=items, total=len(items))


@router.get("/spaces/{space_id}", response_model=MemorySpaceResponse)
async def get_space(
    space_id: str,
    db: Session = Depends(get_db),
):
    """Get a memory space."""
    space = db.query(MemorySpace).filter(MemorySpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    return space


@router.post("/spaces/{space_id}", response_model=MemorySpaceResponse)
async def update_space(
    space_id: str,
    body: MemorySpaceUpdate,
    db: Session = Depends(get_db),
):
    """Update a memory space."""
    space = db.query(MemorySpace).filter(MemorySpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    
    if body.name is not None:
        space.name = body.name
    if body.description is not None:
        space.description = body.description
    
    db.commit()
    db.refresh(space)
    return space


@router.delete("/spaces/{space_id}")
async def delete_space(
    space_id: str,
    db: Session = Depends(get_db),
):
    """Delete a memory space and its entries."""
    space = db.query(MemorySpace).filter(MemorySpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    
    # Delete entries first
    db.query(MemoryEntry).filter(MemoryEntry.memory_space_id == space_id).delete()
    db.delete(space)
    db.commit()
    return {"deleted": True}


@router.post("/entries", response_model=MemoryEntryResponse)
async def create_entry(
    body: MemoryEntryCreate,
    db: Session = Depends(get_db),
):
    """Create a memory entry."""
    # Verify space exists
    space = db.query(MemorySpace).filter(MemorySpace.id == body.memory_space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    
    entry = MemoryEntry(
        id=str(uuid.uuid4()),
        memory_space_id=body.memory_space_id,
        memory_type=body.memory_type,
        title=body.title,
        content=body.content,
        tags_json=body.tags_json,
        source_type=body.source_type,
        source_id=body.source_id,
        is_active=body.is_active,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/entries", response_model=MemoryEntryList)
async def list_entries(
    tenant_id: Optional[str] = None,
    memory_space_id: Optional[str] = None,
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    source_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List memory entries with optional filters."""
    q = db.query(MemoryEntry)
    
    if tenant_id or scope_type or scope_id:
        # Join with space to filter by tenant
        q = q.join(MemorySpace)
        if tenant_id:
            q = q.filter(MemorySpace.tenant_id == tenant_id)
        if scope_type:
            q = q.filter(MemorySpace.scope_type == scope_type)
        if scope_id:
            q = q.filter(MemorySpace.scope_id == scope_id)
    
    if memory_space_id:
        q = q.filter(MemoryEntry.memory_space_id == memory_space_id)
    if memory_type:
        q = q.filter(MemoryEntry.memory_type == memory_type)
    if is_active is not None:
        q = q.filter(MemoryEntry.is_active == is_active)
    if source_type:
        q = q.filter(MemoryEntry.source_type == source_type)
    
    items = q.order_by(MemoryEntry.created_at.desc()).limit(limit).all()
    return MemoryEntryList(items=items, total=len(items))


@router.get("/entries/{entry_id}", response_model=MemoryEntryResponse)
async def get_entry(
    entry_id: str,
    db: Session = Depends(get_db),
):
    """Get a memory entry."""
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.patch("/entries/{entry_id}", response_model=MemoryEntryResponse)
async def update_entry(
    entry_id: str,
    body: MemoryEntryUpdate,
    db: Session = Depends(get_db),
):
    """Update a memory entry."""
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if body.title is not None:
        entry.title = body.title
    if body.content is not None:
        entry.content = body.content
    if body.tags_json is not None:
        entry.tags_json = body.tags_json
    if body.is_active is not None:
        entry.is_active = body.is_active
    
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: str,
    db: Session = Depends(get_db),
):
    """Delete a memory entry."""
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    db.delete(entry)
    db.commit()
    return {"deleted": True}


@router.post("/resolve", response_model=MemoryResolveResponse)
async def resolve_memory(
    body: MemoryResolveParams,
    db: Session = Depends(get_db),
):
    """
    Resolve memory entries for a given context.
    
    Priority order:
    1. organization (tenant-level)
    2. product (product-specific)
    3. workflow (workflow-specific)
    4. run (execution-specific)
    
    Supports both legacy single-scope and new multi-scope resolution.
    """
    # Build scope hierarchy based on provided context
    # New style: use scope_type + scope_id for single scope
    # Extended: also support direct scope lookups via scope_type/scope_id in params
    
    scopes_to_resolve = []
    
    # Support legacy single-scope param style
    if body.scope_type and body.scope_id:
        scopes_to_resolve.append((body.scope_type, body.scope_id))
    
    resolved_scopes = []
    entries_by_scope = {}
    
    for priority_scope in SCOPE_PRIORITY:
        # Check if this priority scope exists in our provided scopes
        for scope_type, scope_id in scopes_to_resolve:
            if scope_type == priority_scope:
                resolved_scopes.append(priority_scope)
                
                # Get entries for this scope
                space_q = db.query(MemorySpace).filter(
                    MemorySpace.tenant_id == body.tenant_id,
                    MemorySpace.scope_type == scope_type,
                    MemorySpace.scope_id == scope_id,
                )
                space = space_q.first()
                if space:
                    entry_q = db.query(MemoryEntry).filter(
                        MemoryEntry.memory_space_id == space.id,
                        MemoryEntry.is_active == body.is_active,
                    )
                    if body.memory_type:
                        entry_q = entry_q.filter(MemoryEntry.memory_type == body.memory_type)
                    
                    entries = entry_q.order_by(MemoryEntry.created_at.desc()).all()
                    entries_by_scope[priority_scope] = entries
    
    # Flatten all entries in priority order
    all_entries = []
    for scope in resolved_scopes:
        all_entries.extend(entries_by_scope.get(scope, []))
    
    return MemoryResolveResponse(
        items=all_entries,
        total=len(all_entries),
        resolved_scopes=resolved_scopes,
    )