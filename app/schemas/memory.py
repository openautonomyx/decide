# Memory Schemas
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime


class MemorySpaceBase(BaseModel):
    tenant_id: str
    scope_type: str  # organization, workflow, run, agent_role, product
    scope_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    metadata_json: Optional[str] = None
    is_active: bool = True


class MemorySpaceCreate(MemorySpaceBase):
    pass


class MemorySpaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MemorySpaceResponse(MemorySpaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class MemorySpaceList(BaseModel):
    items: List[MemorySpaceResponse] = []
    total: int = 0


class MemoryEntryBase(BaseModel):
    memory_space_id: str
    memory_type: str  # fact, policy, instruction, summary, preference, artifact_reference, lesson, template_hint
    title: str
    content: str
    tags_json: Optional[str] = None
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    source_metadata_json: Optional[str] = None
    metadata_json: Optional[str] = None
    is_active: bool = True


class MemoryEntryCreate(MemoryEntryBase):
    pass


class MemoryEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags_json: Optional[str] = None
    source_metadata_json: Optional[str] = None
    metadata_json: Optional[str] = None
    is_active: Optional[bool] = None


class MemoryEntryResponse(MemoryEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class MemoryEntryList(BaseModel):
    items: List[MemoryEntryResponse] = []
    total: int = 0


class MemoryResolveParams(BaseModel):
    tenant_id: str
    organization_scope_id: Optional[str] = None
    product_scope_id: Optional[str] = None
    workflow_scope_id: Optional[str] = None
    run_scope_id: Optional[str] = None
    session_scope_id: Optional[str] = None
    scope_type: Optional[str] = None  # backward compatibility
    scope_id: Optional[str] = None  # backward compatibility
    memory_type: Optional[str] = None
    tags: Optional[List[str]] = None
    limit_per_scope: int = 100
    is_active: bool = True


class MemoryContextItem(BaseModel):
    scope_type: str
    scope_id: str
    entries: List[MemoryEntryResponse] = []


class MemoryResolveResponse(BaseModel):
    items: List[MemoryEntryResponse] = []
    total: int = 0
    resolved_scopes: List[str] = []
    context: List[MemoryContextItem] = []


class MemoryPersistRequest(BaseModel):
    tenant_id: str
    scope_type: str
    scope_id: str
    memory_type: str
    title: str
    content: str
    tags: Optional[List[str]] = None
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    source_metadata: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None
    space_name: Optional[str] = None


class MemoryRunInspection(BaseModel):
    run_id: str
    memory_context: List[dict[str, Any]] = []
    memory_read_ids: List[str] = []
    memory_written_ids: List[str] = []
