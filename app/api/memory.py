# Memory API Router
# Scoped persistent memory CRUD, resolution, and run inspection
from __future__ import annotations

import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.memory import MemorySpace, MemoryEntry
from app.models.tenant_employee import Tenant
from app.models.workflow_definition import WorkflowRun
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
    MemoryContextItem,
    MemoryPersistRequest,
    MemoryRunInspection,
)
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/spaces", response_model=MemorySpaceResponse, status_code=201)
async def create_space(body: MemorySpaceCreate, db: Session = Depends(get_db)):
    """Create a memory space."""
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
        metadata_json=body.metadata_json,
        is_active=body.is_active,
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
    is_active: Optional[bool] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(MemorySpace)
    if tenant_id:
        q = q.filter(MemorySpace.tenant_id == tenant_id)
    if scope_type:
        q = q.filter(MemorySpace.scope_type == scope_type)
    if scope_id:
        q = q.filter(MemorySpace.scope_id == scope_id)
    if is_active is not None:
        q = q.filter(MemorySpace.is_active == is_active)
    items = q.order_by(MemorySpace.created_at.desc()).limit(limit).all()
    return MemorySpaceList(items=items, total=len(items))


@router.post("/spaces/{space_id}", response_model=MemorySpaceResponse)
async def update_space(space_id: str, body: MemorySpaceUpdate, db: Session = Depends(get_db)):
    space = db.query(MemorySpace).filter(MemorySpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    if body.name is not None:
        space.name = body.name
    if body.description is not None:
        space.description = body.description
    if body.is_active is not None:
        space.is_active = body.is_active
    db.commit()
    db.refresh(space)
    return space


@router.post("/entries", response_model=MemoryEntryResponse, status_code=201)
async def create_entry(body: MemoryEntryCreate, db: Session = Depends(get_db)):
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
        source_metadata_json=body.source_metadata_json,
        metadata_json=body.metadata_json,
        is_active=body.is_active,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.patch("/entries/{entry_id}", response_model=MemoryEntryResponse)
async def update_entry(entry_id: str, body: MemoryEntryUpdate, db: Session = Depends(get_db)):
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)

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
    tags: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(MemoryEntry)

    if tenant_id or scope_type or scope_id:
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
    if tags:
        tag_set = {t.strip().lower() for t in tags.split(",") if t.strip()}
        items = [
            i for i in items
            if any(t.lower() in tag_set for t in json.loads(i.tags_json or "[]"))
        ]

    return MemoryEntryList(items=items, total=len(items))


@router.post("/resolve", response_model=MemoryResolveResponse)
async def resolve_memory(body: MemoryResolveParams, db: Session = Depends(get_db)):
    scopes = {
        "organization": body.organization_scope_id,
        "product": body.product_scope_id,
        "workflow": body.workflow_scope_id,
        "run": body.run_scope_id,
        "session": body.session_scope_id,
    }

    if body.scope_type and body.scope_id and body.scope_type in scopes and not scopes[body.scope_type]:
        scopes[body.scope_type] = body.scope_id

    entries, resolved_scopes, context = MemoryService.resolve(
        db,
        tenant_id=body.tenant_id,
        scopes={k: v for k, v in scopes.items() if v},
        memory_type=body.memory_type,
        tags=body.tags,
        is_active=body.is_active,
        limit_per_scope=body.limit_per_scope,
    )

    return MemoryResolveResponse(
        items=entries,
        total=len(entries),
        resolved_scopes=resolved_scopes,
        context=[MemoryContextItem(**item) for item in context],
    )


@router.post("/persist", response_model=MemoryEntryResponse, status_code=201)
async def persist_memory(body: MemoryPersistRequest, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == body.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    entry = MemoryService.persist_entry(
        db,
        tenant_id=body.tenant_id,
        scope_type=body.scope_type,
        scope_id=body.scope_id,
        memory_type=body.memory_type,
        title=body.title,
        content=body.content,
        tags=body.tags,
        source_type=body.source_type,
        source_id=body.source_id,
        source_metadata=body.source_metadata,
        metadata=body.metadata,
        space_name=body.space_name,
    )
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/runs/{run_id}", response_model=MemoryRunInspection)
async def inspect_run_memory(run_id: str, db: Session = Depends(get_db)):
    run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return MemoryRunInspection(
        run_id=run.id,
        memory_context=json.loads(run.memory_context_json or "[]"),
        memory_read_ids=json.loads(run.memory_read_ids_json or "[]"),
        memory_written_ids=json.loads(run.memory_written_ids_json or "[]"),
    )
