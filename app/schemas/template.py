# Template Schemas - Pydantic models for template APIs

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Template Pack Schemas


class TemplatePackCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False


class TemplatePackResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplatePackUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None


# Workflow Template Schemas


class WorkflowTemplateCreate(BaseModel):
    pack_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None


class WorkflowTemplateResponse(BaseModel):
    id: str
    pack_id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    tags: Optional[list[str]]
    is_published: bool
    published_version_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    is_published: Optional[bool] = None


# Workflow Template Version Schemas


class WorkflowTemplateVersionCreate(BaseModel):
    template_id: str
    runtime_spec: dict


class WorkflowTemplateVersionResponse(BaseModel):
    id: str
    template_id: str
    version_number: int
    is_current: bool
    runtime_spec: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# Template list responses


class TemplatePackListResponse(BaseModel):
    template_packs: list[TemplatePackResponse]
    total: int


class WorkflowTemplateListResponse(BaseModel):
    templates: list[WorkflowTemplateResponse]
    total: int


class WorkflowTemplateVersionListResponse(BaseModel):
    versions: list[WorkflowTemplateVersionResponse]
    total: int


# Resolved template with version (for runtime preparation)


class WorkflowTemplateResolvedResponse(BaseModel):
    """Template with current and published versions resolved."""
    id: str
    pack_id: str
    name: str
    description: str | None
    category: str | None
    tags: list[str] | None
    is_published: bool
    current_version: dict | None  # version_id, version_number, runtime_spec
    published_version: dict | None  # version_id, version_number, runtime_spec
    created_at: datetime
    updated_at: datetime