# Template API Router
# Template packs and workflow templates APIs
import json
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.template import (
    TemplatePack,
    WorkflowTemplate,
    WorkflowTemplateVersion,
)
from app.schemas.template import (
    TemplatePackCreate,
    TemplatePackUpdate,
    TemplatePackResponse,
    TemplatePackListResponse,
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate,
    WorkflowTemplateResponse,
    WorkflowTemplateListResponse,
    WorkflowTemplateVersionCreate,
    WorkflowTemplateVersionResponse,
    WorkflowTemplateVersionListResponse,
    WorkflowTemplateResolvedResponse,
)

router = APIRouter(prefix="/template-packs", tags=["template-packs"])


# ===== Template Pack Endpoints =====


@router.post("", response_model=TemplatePackResponse)
def create_template_pack(
    body: TemplatePackCreate,
    db: Session = Depends(get_db),
):
    """Create a template pack."""
    pack = TemplatePack(
        id=str(uuid4()),
        name=body.name,
        description=body.description,
        is_default=body.is_default,
    )
    db.add(pack)
    db.commit()
    db.refresh(pack)
    return pack


@router.get("", response_model=TemplatePackListResponse)
def list_template_packs(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all template packs."""
    items = db.query(TemplatePack).order_by(TemplatePack.created_at.desc()).limit(limit).all()
    return TemplatePackListResponse(
        template_packs=[TemplatePackResponse(**{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "is_default": p.is_default,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }) for p in items],
        total=len(items),
    )


# ===== Workflow Template Endpoints =====


@router.post("/templates", response_model=WorkflowTemplateResponse)
def create_workflow_template(
    body: WorkflowTemplateCreate,
    db: Session = Depends(get_db),
):
    """Create a workflow template."""
    # Check pack exists
    pack = db.query(TemplatePack).filter(TemplatePack.id == body.pack_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Template pack not found")
    
    template = WorkflowTemplate(
        id=str(uuid4()),
        pack_id=body.pack_id,
        name=body.name,
        description=body.description,
        category=body.category,
        tags=json.dumps(body.tags) if body.tags else None,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return WorkflowTemplateResponse(**{
        "id": template.id,
        "pack_id": template.pack_id,
        "name": template.name,
        "description": template.description,
        "category": template.category,
        "tags": json.loads(template.tags) if template.tags else None,
        "is_published": template.is_published,
        "published_version_id": template.published_version_id,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
    })


@router.get("/templates", response_model=WorkflowTemplateListResponse)
def list_workflow_templates(
    pack_id: str = None,
    category: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List workflow templates."""
    q = db.query(WorkflowTemplate)
    if pack_id:
        q = q.filter(WorkflowTemplate.pack_id == pack_id)
    if category:
        q = q.filter(WorkflowTemplate.category == category)
    
    items = q.order_by(WorkflowTemplate.created_at.desc()).limit(limit).all()
    
    return WorkflowTemplateListResponse(
        templates=[WorkflowTemplateResponse(**{
            "id": t.id,
            "pack_id": t.pack_id,
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "tags": json.loads(t.tags) if t.tags else None,
            "is_published": t.is_published,
            "published_version_id": t.published_version_id,
            "created_at": t.created_at,
            "updated_at": t.updated_at,
        }) for t in items],
        total=len(items),
    )


# ===== Workflow Template Version Endpoints =====


@router.post("/templates/{template_id}/versions", response_model=WorkflowTemplateVersionResponse)
def create_template_version(
    template_id: str,
    body: WorkflowTemplateVersionCreate,
    db: Session = Depends(get_db),
):
    """Create a new version for a workflow template."""
    # Check template exists
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    
    # Get latest version number
    latest = db.query(WorkflowTemplateVersion).filter(
        WorkflowTemplateVersion.template_id == template_id
    ).order_by(WorkflowTemplateVersion.version_number.desc()).first()
    
    next_version = (latest.version_number + 1) if latest else 1
    
    # Mark previous versions as not current
    if latest:
        latest.is_current = False
    
    version = WorkflowTemplateVersion(
        id=str(uuid4()),
        template_id=template_id,
        version_number=next_version,
        is_current=True,
        runtime_spec=json.dumps(body.runtime_spec) if body.runtime_spec else None,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    
    return WorkflowTemplateVersionResponse(**{
        "id": version.id,
        "template_id": version.template_id,
        "version_number": version.version_number,
        "is_current": version.is_current,
        "runtime_spec": json.loads(version.runtime_spec) if version.runtime_spec else None,
        "created_at": version.created_at,
    })


@router.get("/templates/{template_id}/versions", response_model=WorkflowTemplateVersionListResponse)
def list_template_versions(
    template_id: str,
    db: Session = Depends(get_db),
):
    """List all versions for a workflow template."""
    items = db.query(WorkflowTemplateVersion).filter(
        WorkflowTemplateVersion.template_id == template_id
    ).order_by(WorkflowTemplateVersion.version_number.desc()).all()
    
    return WorkflowTemplateVersionListResponse(
        versions=[WorkflowTemplateVersionResponse(**{
            "id": v.id,
            "template_id": v.template_id,
            "version_number": v.version_number,
            "is_current": v.is_current,
            "runtime_spec": json.loads(v.runtime_spec) if v.runtime_spec else None,
            "created_at": v.created_at,
        }) for v in items],
        total=len(items),
    )


# ===== Helper Functions for Runtime =====


def get_template_current_version(db: Session, template_id: str) -> dict | None:
    """Get the current version's runtime_spec for a template."""
    version = db.query(WorkflowTemplateVersion).filter(
        WorkflowTemplateVersion.template_id == template_id,
        WorkflowTemplateVersion.is_current == True
    ).first()
    if not version:
        return None
    return {
        "version_id": version.id,
        "version_number": version.version_number,
        "runtime_spec": json.loads(version.runtime_spec) if version.runtime_spec else None,
    }


def get_template_published_version(db: Session, template_id: str) -> dict | None:
    """Get the published version's runtime_spec for a template."""
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == template_id
    ).first()
    if not template or not template.published_version_id:
        return None
    
    version = db.query(WorkflowTemplateVersion).filter(
        WorkflowTemplateVersion.id == template.published_version_id
    ).first()
    if not version:
        return None
    
    return {
        "version_id": version.id,
        "version_number": version.version_number,
        "runtime_spec": json.loads(version.runtime_spec) if version.runtime_spec else None,
    }


# ===== Endpoints for Runtime Preparation =====


@router.get("/templates/{template_id}/resolved", response_model=WorkflowTemplateResolvedResponse)
def get_resolved_template(
    template_id: str,
    db: Session = Depends(get_db),
):
    """Get a template with current and published versions resolved for runtime."""
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    current_version = get_template_current_version(db, template_id)
    published_version = get_template_published_version(db, template_id)
    
    return WorkflowTemplateResolvedResponse(
        id=template.id,
        pack_id=template.pack_id,
        name=template.name,
        description=template.description,
        category=template.category,
        tags=json.loads(template.tags) if template.tags else None,
        is_published=template.is_published,
        current_version=current_version,
        published_version=published_version,
        created_at=template.created_at,
        updated_at=template.updated_at,
    )