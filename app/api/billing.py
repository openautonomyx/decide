"""
Billing API Router
"""
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.billing import (
    BillingAdapterBinding,
    BillingAccountBinding,
    BillingEvent,
    MeterDefinition,
)
from app.schemas.billing import (
    BillingAdapterBinding as AdapterBindingSchema,
    BillingAdapterBindingCreate,
    BillingAdapterBindingList,
    BillingAccountBinding as AccountBindingSchema,
    BillingAccountBindingCreate,
    BillingAccountBindingBind,
    BillingAccountBindingList,
    BillingEvent as BillingEventSchema,
    BillingEventCreate,
    BillingEventList,
    MeterDefinition as MeterDefinitionSchema,
    MeterDefinitionCreate,
    MeterDefinitionList,
)

router = APIRouter(prefix="/billing", tags=["billing"])


# Billing Adapter Bindings

@router.get("/adapters", response_model=BillingAdapterBindingList)
def list_billing_adapters(
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(BillingAdapterBinding)
    if tenant_id:
        query = query.filter(BillingAdapterBinding.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return BillingAdapterBindingList(total=total, items=items)


@router.post("/adapters", response_model=AdapterBindingSchema, status_code=201)
def create_billing_adapter(
    adapter_in: BillingAdapterBindingCreate,
    db: Session = Depends(get_db),
):
    adapter = BillingAdapterBinding(id=str(uuid4()), **adapter_in.model_dump())
    db.add(adapter)
    db.commit()
    db.refresh(adapter)
    return adapter


# Billing Account Bindings

@router.get("/accounts", response_model=BillingAccountBindingList)
def list_billing_accounts(
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(BillingAccountBinding)
    if tenant_id:
        query = query.filter(BillingAccountBinding.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return BillingAccountBindingList(total=total, items=items)


@router.post("/accounts/bind", response_model=AccountBindingSchema, status_code=201)
def bind_billing_account(
    bind_in: BillingAccountBindingBind,
    db: Session = Depends(get_db),
):
    # Verify adapter binding exists
    adapter = db.query(BillingAdapterBinding).filter(
        BillingAdapterBinding.id == bind_in.adapter_binding_id
    ).first()
    if not adapter:
        raise HTTPException(404, "Adapter binding not found")
    
    tenant_id = adapter.tenant_id
    account = BillingAccountBinding(
        id=str(uuid4()),
        tenant_id=tenant_id,
        adapter_binding_id=bind_in.adapter_binding_id,
        external_account_id=bind_in.external_account_id,
        account_name=bind_in.account_name,
        status="active",
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


# Billing Events

@router.get("/events", response_model=BillingEventList)
def list_billing_events(
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = None,
    account_binding_id: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(BillingEvent)
    if tenant_id:
        query = query.filter(BillingEvent.tenant_id == tenant_id)
    if account_binding_id:
        query = query.filter(BillingEvent.account_binding_id == account_binding_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return BillingEventList(total=total, items=items)


@router.post("/events", response_model=BillingEventSchema, status_code=201)
def create_billing_event(event_in: BillingEventCreate, db: Session = Depends(get_db)):
    event = BillingEvent(id=str(uuid4()), **event_in.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# Meter Definitions

@router.get("/meters", response_model=MeterDefinitionList)
def list_meter_definitions(
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(MeterDefinition)
    if tenant_id:
        query = query.filter(MeterDefinition.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return MeterDefinitionList(total=total, items=items)


@router.post("/meters", response_model=MeterDefinitionSchema, status_code=201)
def create_meter_definition(
    meter_in: MeterDefinitionCreate,
    db: Session = Depends(get_db),
):
    meter = MeterDefinition(id=str(uuid4()), **meter_in.model_dump())
    db.add(meter)
    db.commit()
    db.refresh(meter)
    return meter