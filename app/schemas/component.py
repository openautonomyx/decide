# Component Schemas - Pydantic models for component APIs

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Component Definition Schemas


class ComponentDefinitionCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None


class ComponentDefinitionResponse(BaseModel):
    id: str
    name: str
    display_name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    icon: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComponentDefinitionUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None


# Component Version Schemas


class ComponentVersionCreate(BaseModel):
    component_id: str
    version_number: int
    schema: Optional[dict] = None


class ComponentVersionResponse(BaseModel):
    id: str
    component_id: str
    version_number: int
    is_current: bool
    schema: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# Component Capability Schemas


class ComponentCapabilityCreate(BaseModel):
    component_id: str
    capability_type: str
    capability_config: Optional[dict] = None


class ComponentCapabilityResponse(BaseModel):
    id: str
    component_id: str
    capability_type: str
    capability_config: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# Component list responses


class ComponentDefinitionListResponse(BaseModel):
    components: list[ComponentDefinitionResponse]
    total: int


class ComponentVersionListResponse(BaseModel):
    versions: list[ComponentVersionResponse]
    total: int


class ComponentCapabilityListResponse(BaseModel):
    capabilities: list[ComponentCapabilityResponse]
    total: int


# Resolved component with version + capabilities (for runtime preparation)


class ComponentResolvedResponse(BaseModel):
    """Component with current version and capabilities resolved."""
    id: str
    name: str
    display_name: str | None
    description: str | None
    category: str | None
    icon: str | None
    current_version: dict | None  # version_id, version_number, schema
    capabilities: list[dict]  # capability_id, capability_type, capability_config
    created_at: datetime
    updated_at: datetime