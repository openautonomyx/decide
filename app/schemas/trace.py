# Traceability Pydantic Schemas
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TraceSessionBase(BaseModel):
    tenant_id: str
    trace_id: str
    session_type: Optional[str] = None
    status: Optional[str] = "started"
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class TraceSessionCreate(TraceSessionBase):
    pass


class TraceSessionUpdate(BaseModel):
    status: Optional[str] = None
    ended_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class TraceSession(TraceSessionBase):
    id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TraceSessionList(BaseModel):
    total: int
    items: List[TraceSession]


class TraceSpanRecordBase(BaseModel):
    trace_session_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service_name: Optional[str] = None
    operation_name: Optional[str] = None
    duration_ms: Optional[float] = None
    status_code: Optional[str] = None
    status_message: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    logs: Optional[List[Dict[str, Any]]] = None


class TraceSpanRecordCreate(TraceSpanRecordBase):
    pass


class TraceSpanRecord(TraceSpanRecordBase):
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TraceSpanRecordList(BaseModel):
    total: int
    items: List[TraceSpanRecord]


class TraceLinkBase(BaseModel):
    from_trace_session_id: str
    to_trace_session_id: Optional[str] = None
    to_span_id: Optional[str] = None
    link_type: Optional[str] = "reference"
    metadata: Optional[Dict[str, Any]] = None


class TraceLinkCreate(TraceLinkBase):
    pass


class TraceLink(TraceLinkBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UsageRecordBase(BaseModel):
    tenant_id: str
    trace_session_id: Optional[str] = None
    metric_name: str
    quantity: float = 0.0
    unit: Optional[str] = None
    cost: Optional[float] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class UsageRecordCreate(UsageRecordBase):
    pass


class UsageRecord(UsageRecordBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UsageRecordList(BaseModel):
    total: int
    items: List[UsageRecord]