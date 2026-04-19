# Skill Schemas
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class SkillDefinitionBase(BaseModel):
    tenant_id: str
    scope_type: Optional[str] = None  # organization, product, workflow, agent_role, global
    scope_id: Optional[str] = None
    name: str
    slug: str
    description: Optional[str] = None
    skill_type: str  # prompt_skill, procedure, tool_sequence, workflow_fragment, evaluation_pattern, reviewer_pattern
    status: str = "draft"


class SkillDefinitionCreate(SkillDefinitionBase):
    pass


class SkillDefinitionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class SkillDefinitionResponse(SkillDefinitionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class SkillDefinitionList(BaseModel):
    items: List[SkillDefinitionResponse] = []
    total: int = 0


class SkillVersionBase(BaseModel):
    skill_id: str
    version_number: int
    content_json: str
    input_schema_json: Optional[str] = None
    output_schema_json: Optional[str] = None
    tool_requirements_json: Optional[str] = None
    metadata_json: Optional[str] = None
    is_current: bool = False


class SkillVersionCreate(SkillVersionBase):
    pass


class SkillVersionUpdate(BaseModel):
    is_current: Optional[bool] = None


class SkillVersionResponse(SkillVersionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class SkillVersionList(BaseModel):
    items: List[SkillVersionResponse] = []
    total: int = 0


class SkillBindingBase(BaseModel):
    skill_id: str
    workflow_id: Optional[str] = None
    template_id: Optional[str] = None
    component_id: Optional[str] = None
    agent_role: Optional[str] = None
    binding_type: str  # suggested, required, default


class SkillBindingCreate(SkillBindingBase):
    pass


class SkillBindingResponse(SkillBindingBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class SkillBindingList(BaseModel):
    items: List[SkillBindingResponse] = []
    total: int = 0


class SkillPromotionRecordBase(BaseModel):
    source_type: str  # run, eval, manual, template, imported
    source_id: str
    skill_id: str
    promoted_by: Optional[str] = None
    reason: Optional[str] = None
    evidence_json: Optional[str] = None


class SkillPromotionRecordCreate(SkillPromotionRecordBase):
    pass


class SkillPromotionRecordResponse(SkillPromotionRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class SkillPromotionRecordList(BaseModel):
    items: List[SkillPromotionRecordResponse] = []
    total: int = 0


class SkillResolveParams(BaseModel):
    tenant_id: str
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
    workflow_id: Optional[str] = None
    template_id: Optional[str] = None
    component_id: Optional[str] = None
    agent_role: Optional[str] = None


class SkillResolveResponse(BaseModel):
    items: List[SkillDefinitionResponse] = []
    total: int = 0
    resolved_scopes: List[str] = []