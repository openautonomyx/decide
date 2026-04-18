"""
Tenant Service - Business logic for tenant operations
"""
from uuid import uuid4
from sqlalchemy.orm import Session
from typing import Optional

from app.models.tenant_employee import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    @staticmethod
    def create(db: Session, tenant_in: TenantCreate) -> Tenant:
        """Create a new tenant."""
        tenant = Tenant(
            id=str(uuid4()),
            name=tenant_in.name,
            enabled=tenant_in.enabled,
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant

    @staticmethod
    def get(db: Session, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID."""
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[Tenant], int]:
        """List tenants with pagination."""
        total = db.query(Tenant).count()
        items = db.query(Tenant).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, tenant_id: str, tenant_in: TenantUpdate) -> Optional[Tenant]:
        """Update a tenant."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return None
        for field, value in tenant_in.model_dump(exclude_unset=True).items():
            setattr(tenant, field, value)
        db.commit()
        db.refresh(tenant)
        return tenant

    @staticmethod
    def delete(db: Session, tenant_id: str) -> bool:
        """Delete a tenant."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return False
        db.delete(tenant)
        db.commit()
        return True
