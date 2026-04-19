# Component API Router
# Component registry APIs
import json
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.component import (
    ComponentDefinition,
    ComponentVersion,
    ComponentCapability,
)
from app.schemas.component import (
    ComponentDefinitionCreate,
    ComponentDefinitionUpdate,
    ComponentDefinitionResponse,
    ComponentDefinitionListResponse,
    ComponentVersionCreate,
    ComponentVersionResponse,
    ComponentVersionListResponse,
    ComponentCapabilityCreate,
    ComponentCapabilityResponse,
    ComponentCapabilityListResponse,
    ComponentResolvedResponse,
)

router = APIRouter(prefix="/components", tags=["components"])


# ===== Component Definition Endpoints =====


@router.post("", response_model=ComponentDefinitionResponse)
def create_component(
    body: ComponentDefinitionCreate,
    db: Session = Depends(get_db),
):
    """Create a component definition."""
    component = ComponentDefinition(
        id=str(uuid4()),
        name=body.name,
        display_name=body.display_name,
        description=body.description,
        category=body.category,
        icon=body.icon,
    )
    db.add(component)
    db.commit()
    db.refresh(component)
    return component


@router.get("", response_model=ComponentDefinitionListResponse)
def list_components(
    category: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all component definitions."""
    q = db.query(ComponentDefinition)
    if category:
        q = q.filter(ComponentDefinition.category == category)
    
    items = q.order_by(ComponentDefinition.created_at.desc()).limit(limit).all()
    
    return ComponentDefinitionListResponse(
        components=[ComponentDefinitionResponse(**{
            "id": c.id,
            "name": c.name,
            "display_name": c.display_name,
            "description": c.description,
            "category": c.category,
            "icon": c.icon,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }) for c in items],
        total=len(items),
    )


@router.get("/{component_id}", response_model=ComponentDefinitionResponse)
def get_component(
    component_id: str,
    db: Session = Depends(get_db),
):
    """Get a component definition by ID."""
    component = db.query(ComponentDefinition).filter(
        ComponentDefinition.id == component_id
    ).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return component


# ===== Component Version Endpoints =====


@router.post("/{component_id}/versions", response_model=ComponentVersionResponse)
def create_component_version(
    component_id: str,
    body: ComponentVersionCreate,
    db: Session = Depends(get_db),
):
    """Create a new version for a component."""
    # Check component exists
    component = db.query(ComponentDefinition).filter(
        ComponentDefinition.id == component_id
    ).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Get latest version number
    latest = db.query(ComponentVersion).filter(
        ComponentVersion.component_id == component_id
    ).order_by(ComponentVersion.version_number.desc()).first()
    
    next_version = (latest.version_number + 1) if latest else 1
    
    # Mark previous versions as not current
    if latest:
        latest.is_current = False
    
    version = ComponentVersion(
        id=str(uuid4()),
        component_id=component_id,
        version_number=next_version,
        is_current=True,
        schema_json=json.dumps(body.schema) if body.schema else None,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    
    return ComponentVersionResponse(**{
        "id": version.id,
        "component_id": version.component_id,
        "version_number": version.version_number,
        "is_current": version.is_current,
        "schema": json.loads(version.schema_json) if version.schema_json else None,
        "created_at": version.created_at,
    })


@router.get("/{component_id}/versions", response_model=ComponentVersionListResponse)
def list_component_versions(
    component_id: str,
    db: Session = Depends(get_db),
):
    """List all versions for a component."""
    items = db.query(ComponentVersion).filter(
        ComponentVersion.component_id == component_id
    ).order_by(ComponentVersion.version_number.desc()).all()
    
    return ComponentVersionListResponse(
        versions=[ComponentVersionResponse(**{
            "id": v.id,
            "component_id": v.component_id,
            "version_number": v.version_number,
            "is_current": v.is_current,
            "schema": json.loads(v.schema_json) if v.schema_json else None,
            "created_at": v.created_at,
        }) for v in items],
        total=len(items),
    )


# ===== Component Capability Endpoints =====


@router.post("/{component_id}/capabilities", response_model=ComponentCapabilityResponse)
def create_component_capability(
    component_id: str,
    body: ComponentCapabilityCreate,
    db: Session = Depends(get_db),
):
    """Create a capability for a component."""
    # Check component exists
    component = db.query(ComponentDefinition).filter(
        ComponentDefinition.id == component_id
    ).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    capability = ComponentCapability(
        id=str(uuid4()),
        component_id=component_id,
        capability_type=body.capability_type,
        capability_config=json.dumps(body.capability_config) if body.capability_config else None,
    )
    db.add(capability)
    db.commit()
    db.refresh(capability)
    
    return ComponentCapabilityResponse(**{
        "id": capability.id,
        "component_id": capability.component_id,
        "capability_type": capability.capability_type,
        "capability_config": json.loads(capability.capability_config) if capability.capability_config else None,
        "created_at": capability.created_at,
    })


@router.get("/{component_id}/capabilities", response_model=ComponentCapabilityListResponse)
def list_component_capabilities(
    component_id: str,
    db: Session = Depends(get_db),
):
    """List all capabilities for a component."""
    items = db.query(ComponentCapability).filter(
        ComponentCapability.component_id == component_id
    ).all()
    
    return ComponentCapabilityListResponse(
        capabilities=[ComponentCapabilityResponse(**{
            "id": c.id,
            "component_id": c.component_id,
            "capability_type": c.capability_type,
            "capability_config": json.loads(c.capability_config) if c.capability_config else None,
            "created_at": c.created_at,
        }) for c in items],
        total=len(items),
    )


# ===== Helper Functions for Runtime =====


def get_component_current_version(db: Session, component_id: str) -> dict | None:
    """Get the current version schema for a component."""
    version = db.query(ComponentVersion).filter(
        ComponentVersion.component_id == component_id,
        ComponentVersion.is_current == True
    ).first()
    if not version:
        return None
    return {
        "version_id": version.id,
        "version_number": version.version_number,
        "schema": json.loads(version.schema_json) if version.schema_json else None,
    }


def get_component_capabilities(db: Session, component_id: str) -> list[dict]:
    """Get all capabilities for a component."""
    capabilities = db.query(ComponentCapability).filter(
        ComponentCapability.component_id == component_id
    ).all()
    return [
        {
            "capability_id": c.id,
            "capability_type": c.capability_type,
            "capability_config": json.loads(c.capability_config) if c.capability_config else None,
        }
        for c in capabilities
    ]


# ===== Endpoint for Runtime Preparation =====


@router.get("/{component_id}/resolved", response_model=ComponentResolvedResponse)
def get_resolved_component(
    component_id: str,
    db: Session = Depends(get_db),
):
    """Get a component with current version and capabilities resolved for runtime."""
    component = db.query(ComponentDefinition).filter(
        ComponentDefinition.id == component_id
    ).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    current_version = get_component_current_version(db, component_id)
    capabilities = get_component_capabilities(db, component_id)
    
    return ComponentResolvedResponse(
        id=component.id,
        name=component.name,
        display_name=component.display_name,
        description=component.description,
        category=component.category,
        icon=component.icon,
        current_version=current_version,
        capabilities=capabilities,
        created_at=component.created_at,
        updated_at=component.updated_at,
    )