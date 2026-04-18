"""
Tenant API Router - simplified, no auth for local smoke test
"""
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tenant_employee import Tenant as TenantModel
from app.schemas.tenant import TenantCreate, TenantUpdate, Tenant as TenantSchema, TenantList

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=TenantList)
def list_tenants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    total = db.query(TenantModel).count()
    items = db.query(TenantModel).offset(skip).limit(limit).all()
    return TenantList(total=total, items=items)


@router.get("/{tenant_id}", response_model=TenantSchema)
def get_tenant(tenant_id: str, db: Session = Depends(get_db)):
    t = db.query(TenantModel).filter(TenantModel.id == tenant_id).first()
    if not t:
        raise HTTPException(404, "Tenant not found")
    return t


@router.post("", response_model=TenantSchema, status_code=201)
def create_tenant(tenant_in: TenantCreate, db: Session = Depends(get_db)):
    t = TenantModel(id=str(uuid4()), **tenant_in.model_dump())
    db.add(t); db.commit(); db.refresh(t)
    return t


@router.patch("/{tenant_id}", response_model=TenantSchema)
def update_tenant(tenant_id: str, tenant_in: TenantUpdate, db: Session = Depends(get_db)):
    t = db.query(TenantModel).filter(TenantModel.id == tenant_id).first()
    if not t:
        raise HTTPException(404, "Tenant not found")
    for f, v in tenant_in.model_dump(exclude_unset=True).items():
        setattr(t, f, v)
    db.commit(); db.refresh(t)
    return t


@router.delete("/{tenant_id}", status_code=204)
def delete_tenant(tenant_id: str, db: Session = Depends(get_db)):
    t = db.query(TenantModel).filter(TenantModel.id == tenant_id).first()
    if not t:
        raise HTTPException(404, "Tenant not found")
    db.delete(t); db.commit()
    return None
