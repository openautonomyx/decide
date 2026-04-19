"""
Traceability API Router
"""
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.trace import TraceSession, TraceSpanRecord, UsageRecord
from app.schemas.trace import (
    TraceSession as TraceSessionSchema,
    TraceSessionCreate,
    TraceSessionUpdate,
    TraceSessionList,
    TraceSpanRecord as TraceSpanRecordSchema,
    TraceSpanRecordCreate,
    TraceSpanRecordList,
    UsageRecord as UsageRecordSchema,
    UsageRecordCreate,
    UsageRecordList,
)

router = APIRouter(prefix="/trace", tags=["trace"])


# Trace Sessions

@router.get("/sessions", response_model=TraceSessionList)
def list_trace_sessions(
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(TraceSession)
    if tenant_id:
        query = query.filter(TraceSession.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return TraceSessionList(total=total, items=items)


@router.get("/sessions/{session_id}", response_model=TraceSessionSchema)
def get_trace_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TraceSession).filter(TraceSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Trace session not found")
    return session


@router.post("/sessions", response_model=TraceSessionSchema, status_code=201)
def create_trace_session(session_in: TraceSessionCreate, db: Session = Depends(get_db)):
    session = TraceSession(id=str(uuid4()), **session_in.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.patch("/sessions/{session_id}", response_model=TraceSessionSchema)
def update_trace_session(
    session_id: str,
    session_in: TraceSessionUpdate,
    db: Session = Depends(get_db),
):
    session = db.query(TraceSession).filter(TraceSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Trace session not found")
    for field, value in session_in.model_dump(exclude_unset=True).items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)
    return session


# Trace Spans

@router.get("/spans", response_model=TraceSpanRecordList)
def list_trace_spans(
    skip: int = 0,
    limit: int = 100,
    trace_session_id: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(TraceSpanRecord)
    if trace_session_id:
        query = query.filter(TraceSpanRecord.trace_session_id == trace_session_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return TraceSpanRecordList(total=total, items=items)


@router.post("/spans", response_model=TraceSpanRecordSchema, status_code=201)
def create_trace_span(span_in: TraceSpanRecordCreate, db: Session = Depends(get_db)):
    span = TraceSpanRecord(id=str(uuid4()), **span_in.model_dump())
    db.add(span)
    db.commit()
    db.refresh(span)
    return span


# Usage Records

@router.get("/usage", response_model=UsageRecordList)
def list_usage_records(
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = None,
    metric_name: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(UsageRecord)
    if tenant_id:
        query = query.filter(UsageRecord.tenant_id == tenant_id)
    if metric_name:
        query = query.filter(UsageRecord.metric_name == metric_name)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return UsageRecordList(total=total, items=items)


@router.post("/usage", response_model=UsageRecordSchema, status_code=201)
def create_usage_record(record_in: UsageRecordCreate, db: Session = Depends(get_db)):
    record = UsageRecord(id=str(uuid4()), **record_in.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record