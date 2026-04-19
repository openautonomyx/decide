# Billing SQLAlchemy Models
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class BillingAdapterBinding(Base):
    __tablename__ = "billing_adapter_binding"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    adapter_name = Column(String(100), nullable=False)
    adapter_type = Column(String(50))  # provider, sink
    is_active = Column(Boolean, default=True)
    config = Column(Text)  # JSON - encrypted config
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="billing_adapter_bindings")


class BillingAccountBinding(Base):
    __tablename__ = "billing_account_binding"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    adapter_binding_id = Column(String(36), ForeignKey("billing_adapter_binding.id"))
    external_account_id = Column(String(100))
    account_name = Column(String(255))
    status = Column(String(20))  # active, suspended, closed
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="billing_account_bindings")
    adapter_binding = relationship("BillingAdapterBinding", backref="account_bindings")


class BillingEvent(Base):
    __tablename__ = "billing_event"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    account_binding_id = Column(String(36), ForeignKey("billing_account_binding.id"))
    event_type = Column(String(50))  # usage, subscription, adjustment
    event_name = Column(String(100))
    quantity = Column(Float, default=0.0)
    unit_price = Column(Float)
    amount = Column(Float)
    currency = Column(String(3), default="USD")
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    metadata = Column(Text)  # JSON
    created_at = Column(DateTime, server_default=func.now())

    tenant = relationship("Tenant", backref="billing_events")
    account_binding = relationship("BillingAccountBinding", backref="events")


class MeterDefinition(Base):
    __tablename__ = "meter_definition"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    meter_name = Column(String(100), nullable=False)
    display_name = Column(String(255))
    description = Column(Text)
    unit = Column(String(20))  # tokens, requests, ms, gb
    unit_price = Column(Float)
    aggregation_type = Column(String(20))  # sum, count, avg, max
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="meter_definitions")