# Skill API Router
# Continuous skill and tool-pattern substrate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import json
import re

from app.db.session import get_db
from app.models.skill import SkillDefinition, SkillVersion, SkillBinding, SkillPromotionRecord
from app.schemas.skill import (
    SkillDefinitionCreate,
    SkillDefinitionUpdate,
    SkillDefinitionResponse,
    SkillDefinitionList,
    SkillVersionCreate,
    SkillVersionUpdate,
    SkillVersionResponse,
    SkillVersionList,
    SkillBindingCreate,
    SkillBindingResponse,
    SkillBindingList,
    SkillPromotionRecordCreate,
    SkillPromotionRecordResponse,
    SkillPromotionRecordList,
    SkillResolveParams,
    SkillResolveResponse,
)

router = APIRouter(prefix="/skills", tags=["skills"])

SCOPE_PRIORITY = ["organization", "product", "workflow", "agent_role"]


def _slugify(name: str) -> str:
    """Simple slug generation."""
    slug = name.lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9-]", "", slug)


@router.post("", response_model=SkillDefinitionResponse)
async def create_skill(
    body: SkillDefinitionCreate,
    db: Session = Depends(get_db),
):
    """Create a skill definition."""
    # Check tenant exists
    from app.models.tenant_employee import Tenant
    tenant = db.query(Tenant).filter(Tenant.id == body.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Check slug is unique
    existing = db.query(SkillDefinition).filter(SkillDefinition.slug == body.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill slug already exists")
    
    skill = SkillDefinition(
        id=str(uuid.uuid4()),
        tenant_id=body.tenant_id,
        scope_type=body.scope_type,
        scope_id=body.scope_id,
        name=body.name,
        slug=body.slug,
        description=body.description,
        skill_type=body.skill_type,
        status=body.status,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("", response_model=SkillDefinitionList)
async def list_skills(
    tenant_id: Optional[str] = None,
    scope_type: Optional[str] = None,
    skill_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List skill definitions."""
    q = db.query(SkillDefinition)
    if tenant_id:
        q = q.filter(SkillDefinition.tenant_id == tenant_id)
    if scope_type:
        q = q.filter(SkillDefinition.scope_type == scope_type)
    if skill_type:
        q = q.filter(SkillDefinition.skill_type == skill_type)
    if status:
        q = q.filter(SkillDefinition.status == status)
    
    items = q.order_by(SkillDefinition.created_at.desc()).limit(limit).all()
    return SkillDefinitionList(items=items, total=len(items))


@router.get("/resolve", response_model=SkillResolveResponse)
async def resolve_skills(
    tenant_id: str,
    workflow_id: Optional[str] = None,
    template_id: Optional[str] = None,
    component_id: Optional[str] = None,
    agent_role: Optional[str] = None,
    product: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Resolve applicable skills for a context.
    
    Priority order:
    1. organization (tenant-level)
    2. product (product-specific)
    3. workflow (workflow-specific)
    4. agent_role (role-specific)
    5. component/template (component or template specific)
    
    Supports filtering by workflow_id, template_id, component_id, agent_role, product.
    """
    # Collect scopes to search, with priority ordering
    scopes = []
    
    # Priority 5: component/template specific (lowest priority)
    if component_id:
        scopes.append(("component", component_id))
    if template_id:
        scopes.append(("template", template_id))
    
    # Priority 4: agent_role
    if agent_role:
        scopes.append(("agent_role", agent_role))
    
    # Priority 3: workflow
    if workflow_id:
        scopes.append(("workflow", workflow_id))
    
    # Priority 2: product
    if product:
        scopes.append(("product", product))
    
    # Priority 1: organization (always included, highest priority)
    scopes.append(("organization", tenant_id))
    
    # Lookup order: organization -> product -> workflow -> agent_role -> component -> template
    lookup_order = ["organization", "product", "workflow", "agent_role", "component", "template"]
    
    entries_by_scope = {}
    
    for scope_type, scope_id in scopes:
        q = db.query(SkillDefinition).filter(
            SkillDefinition.tenant_id == tenant_id,
            SkillDefinition.status == "active",
        )
        if scope_type == "organization":
            q = q.filter(SkillDefinition.scope_type == "organization")
        else:
            q = q.filter(
                SkillDefinition.scope_type == scope_type,
                SkillDefinition.scope_id == scope_id,
            )
        
        skills = q.all()
        entries_by_scope[scope_type] = skills
    
    # Flatten in priority order
    resolved = []
    for scope in lookup_order:
        if scope in entries_by_scope:
            resolved.extend(entries_by_scope[scope])
    
    return SkillResolveResponse(
        items=resolved,
        total=len(resolved),
        resolved_scopes=list(entries_by_scope.keys()),
    )


@router.get("/{skill_id}", response_model=SkillDefinitionResponse)
async def get_skill(
    skill_id: str,
    db: Session = Depends(get_db),
):
    """Get a skill definition."""
    skill = db.query(SkillDefinition).filter(SkillDefinition.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.patch("/{skill_id}", response_model=SkillDefinitionResponse)
async def update_skill(
    skill_id: str,
    body: SkillDefinitionUpdate,
    db: Session = Depends(get_db),
):
    """Update a skill definition."""
    skill = db.query(SkillDefinition).filter(SkillDefinition.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    if body.name is not None:
        skill.name = body.name
    if body.description is not None:
        skill.description = body.description
    if body.status is not None:
        skill.status = body.status
    
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: str,
    db: Session = Depends(get_db),
):
    """Delete a skill definition and its versions/bindings."""
    skill = db.query(SkillDefinition).filter(SkillDefinition.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    db.query(SkillVersion).filter(SkillVersion.skill_id == skill_id).delete()
    db.query(SkillBinding).filter(SkillBinding.skill_id == skill_id).delete()
    db.delete(skill)
    db.commit()
    return {"deleted": True}


@router.post("/{skill_id}/versions", response_model=SkillVersionResponse)
async def create_version(
    skill_id: str,
    body: SkillVersionCreate,
    db: Session = Depends(get_db),
):
    """Create a skill version."""
    skill = db.query(SkillDefinition).filter(SkillDefinition.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Check version number
    existing = db.query(SkillVersion).filter(
        SkillVersion.skill_id == skill_id,
        SkillVersion.version_number == body.version_number,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Version number already exists")
    
    version = SkillVersion(
        id=str(uuid.uuid4()),
        skill_id=skill_id,
        version_number=body.version_number,
        content_json=body.content_json,
        input_schema_json=body.input_schema_json,
        output_schema_json=body.output_schema_json,
        tool_requirements_json=body.tool_requirements_json,
        metadata_json=body.metadata_json,
        is_current=body.is_current,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.get("/{skill_id}/versions", response_model=SkillVersionList)
async def list_versions(
    skill_id: str,
    db: Session = Depends(get_db),
):
    """List skill versions."""
    versions = db.query(SkillVersion).filter(
        SkillVersion.skill_id == skill_id
    ).order_by(SkillVersion.version_number.desc()).all()
    return SkillVersionList(items=versions, total=len(versions))


@router.get("/{skill_id}/versions/{version_id}", response_model=SkillVersionResponse)
async def get_version(
    skill_id: str,
    version_id: str,
    db: Session = Depends(get_db),
):
    """Get a skill version."""
    version = db.query(SkillVersion).filter(
        SkillVersion.id == version_id,
        SkillVersion.skill_id == skill_id,
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.post("/{skill_id}/bind", response_model=SkillBindingResponse)
async def create_binding(
    skill_id: str,
    body: SkillBindingCreate,
    db: Session = Depends(get_db),
):
    """Bind a skill to workflow/template/component/agent_role."""
    skill = db.query(SkillDefinition).filter(SkillDefinition.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    binding = SkillBinding(
        id=str(uuid.uuid4()),
        skill_id=skill_id,
        workflow_id=body.workflow_id,
        template_id=body.template_id,
        component_id=body.component_id,
        agent_role=body.agent_role,
        binding_type=body.binding_type,
    )
    db.add(binding)
    db.commit()
    db.refresh(binding)
    return binding


@router.get("/{skill_id}/bindings", response_model=SkillBindingList)
async def list_bindings(
    skill_id: str,
    db: Session = Depends(get_db),
):
    """List skill bindings."""
    bindings = db.query(SkillBinding).filter(
        SkillBinding.skill_id == skill_id
    ).all()
    return SkillBindingList(items=bindings, total=len(bindings))


@router.post("/promote", response_model=SkillPromotionRecordResponse)
async def promote_skill(
    body: SkillPromotionRecordCreate,
    db: Session = Depends(get_db),
):
    """Promote a skill from run/eval/template."""
    skill = db.query(SkillDefinition).filter(
        SkillDefinition.id == body.skill_id
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    record = SkillPromotionRecord(
        id=str(uuid.uuid4()),
        source_type=body.source_type,
        source_id=body.source_id,
        skill_id=body.skill_id,
        promoted_by=body.promoted_by,
        reason=body.reason,
        evidence_json=body.evidence_json,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/promotions", response_model=SkillPromotionRecordList)
async def list_promotions(
    skill_id: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List skill promotions."""
    q = db.query(SkillPromotionRecord)
    if skill_id:
        q = q.filter(SkillPromotionRecord.skill_id == skill_id)
    if source_type:
        q = q.filter(SkillPromotionRecord.source_type == source_type)
    
    items = q.order_by(SkillPromotionRecord.created_at.desc()).limit(limit).all()
    return SkillPromotionRecordList(items=items, total=len(items))