# Traceability SQLAlchemy Models
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class TraceSession(Base):
    __tablename__ = "trace_session"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    trace_id = Column(String(64), nullable=False, index=True)
    session_type = Column(String(50))
    status = Column(String(20))
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime)
    duration_ms = Column(Float)
    metadata = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="trace_sessions")


class TraceSpanRecord(Base):
    __tablename__ = "trace_span_record"
    id = Column(String(36), primary_key=True)
    trace_session_id = Column(String(36), ForeignKey("trace_session.id"), nullable=False)
    span_id = Column(String(64), nullable=False, index=True)
    parent_span_id = Column(String(64))
    service_name = Column(String(255))
    operation_name = Column(String(255))
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime)
    duration_ms = Column(Float)
    status_code = Column(String(20))
    status_message = Column(Text)
    attributes = Column(Text)
    logs = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    trace_session = relationship("TraceSession", backref="spans")


class TraceLink(Base):
    __tablename__ = "trace_link"
    id = Column(String(36), primary_key=True)
    from_trace_session_id = Column(String(36), ForeignKey("trace_session.id"), nullable=False)
    to_trace_session_id = Column(String(36), ForeignKey("trace_session.id"))
    to_span_id = Column(String(36))
    link_type = Column(String(50))
    metadata = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    from_session = relationship("TraceSession", foreign_keys=[from_trace_session_id], backref="outgoing_links")
    to_session = relationship("TraceSession", foreign_keys=[to_trace_session_id], backref="incoming_links")


class UsageRecord(Base):
    __tablename__ = "usage_record"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    trace_session_id = Column(String(36), ForeignKey("trace_session.id"))
    metric_name = Column(String(100), nullable=False)
    quantity = Column(Float, default=0.0)
    unit = Column(String(20))
    cost = Column(Float)
    period_start = Column(DateTime, server_default=func.now())
    period_end = Column(DateTime)
    metadata = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    tenant = relationship("Tenant", backref="usage_records")
    trace_session = relationship("TraceSession", backref="usage_records")