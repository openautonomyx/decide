# Billing Pydantic Schemas
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class BillingAdapterBindingBase(BaseModel):
    tenant_id: str
    adapter_name: str
    adapter_type: Optional[str] = None
    is_active: bool = True
    config: Optional[Dict[str, Any]] = None


class BillingAdapterBindingCreate(BillingAdapterBindingBase):
    pass


class BillingAdapterBinding(BillingAdapterBindingBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillingAdapterBindingList(BaseModel):
    total: int
    items: List[BillingAdapterBinding]


class BillingAccountBindingBase(BaseModel):
    tenant_id: str
    adapter_binding_id: Optional[str] = None
    external_account_id: Optional[str] = None
    account_name: Optional[str] = None
    status: Optional[str] = "active"


class BillingAccountBindingCreate(BillingAccountBindingBase):
    pass


class BillingAccountBindingBind(BaseModel):
    adapter_binding_id: str
    external_account_id: str
    account_name: Optional[str] = None


class BillingAccountBinding(BillingAccountBindingBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillingAccountBindingList(BaseModel):
    total: int
    items: List[BillingAccountBinding]


class BillingEventBase(BaseModel):
    tenant_id: str
    account_binding_id: Optional[str] = None
    event_type: str
    event_name: Optional[str] = None
    quantity: float = 0.0
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    currency: str = "USD"
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class BillingEventCreate(BillingEventBase):
    pass


class BillingEvent(BillingEventBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class BillingEventList(BaseModel):
    total: int
    items: List[BillingEvent]


class MeterDefinitionBase(BaseModel):
    tenant_id: str
    meter_name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    aggregation_type: str = "sum"
    is_active: bool = True


class MeterDefinitionCreate(MeterDefinitionBase):
    pass


class MeterDefinition(MeterDefinitionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeterDefinitionList(BaseModel):
    total: int
    items: List[MeterDefinition]