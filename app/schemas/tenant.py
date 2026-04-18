"""
Tenant Pydantic Schemas
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
# from uuid import UUID (DB uses VARCHAR(36))


# Schemas
class TenantBase(BaseModel):
    name: str
    enabled: bool = True


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: str | None = None
    enabled: bool | None = None


class Tenant(TenantBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TenantList(BaseModel):
    total: int
    items: list[Tenant]