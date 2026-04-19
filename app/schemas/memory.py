# Memory Schemas
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class MemorySpaceBase(BaseModel):
    tenant_id: str
    scope_type: str  # organization, workflow, run, agent_role, product
    scope_id: Optional[str] = None
    name: str
    description: Optional[str] = None


class MemorySpaceCreate(MemorySpaceBase):
    pass


class MemorySpaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


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
    is_active: bool = True


class MemoryEntryCreate(MemoryEntryBase):
    pass


class MemoryEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags_json: Optional[str] = None
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
    scope_type: Optional[str] = None  # organization, workflow, run, agent_role, product
    scope_id: Optional[str] = None
    memory_type: Optional[str] = None
    is_active: bool = True


class MemoryResolveResponse(BaseModel):
    items: List[MemoryEntryResponse] = []
    total: int = 0
    resolved_scopes: List[str] = []