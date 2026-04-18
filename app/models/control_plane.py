# Control Plane SQLAlchemy Models
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class ExecutionRequest(Base):
    __tablename__ = "execution_request"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    goal = Column(String, nullable=False)
    capability = Column(String(50))
    quality = Column(String(50))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    tenant = relationship("Tenant", backref="execution_requests")
    request_metadata = relationship("ExecutionRequestMetadata", back_populates="execution_request")
    history = relationship("ExecutionHistory", back_populates="execution_request")
    approvals = relationship("ApprovalRequest", back_populates="execution_request")


class ExecutionRequestMetadata(Base):
    __tablename__ = "execution_request_metadata"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text)

    execution_request = relationship("ExecutionRequest", back_populates="request_metadata")


class ExecutionHistory(Base):
    __tablename__ = "execution_history"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    thread_id = Column(String(36))
    event_type = Column(String(50), nullable=False)
    event_data = Column(Text)  # JSONB in schema
    created_at = Column(DateTime, server_default=func.now())

    execution_request = relationship("ExecutionRequest", back_populates="history")


class PolicyResolution(Base):
    __tablename__ = "policy_resolution"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    policy_id = Column(String(36))
    default_decision = Column(String(50))
    decision_reason = Column(Text)


class BackendSelection(Base):
    __tablename__ = "backend_selection"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    selected_backend = Column(String(50), nullable=False)
    selection_order = Column(Integer, default=1)
    selected_at = Column(DateTime, server_default=func.now())


class FallbackEvent(Base):
    __tablename__ = "fallback_event"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    from_backend = Column(String(50))
    to_backend = Column(String(50))
    reason = Column(Text)
    triggered_at = Column(DateTime, server_default=func.now())


class ApprovalRequest(Base):
    __tablename__ = "approval_request"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    status = Column(String(50), default="pending")
    requested_by_type = Column(String(20))
    requested_by_id = Column(String(36))
    approver = Column(String(36))
    approver_notes = Column(Text)
    requested_at = Column(DateTime, server_default=func.now())
    decided_at = Column(DateTime)

    execution_request = relationship("ExecutionRequest", back_populates="approvals")


class DecisionRecord(Base):
    __tablename__ = "decision_record"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    decision_type = Column(String(50), nullable=False)
    decision_reason = Column(Text)
    decided_at = Column(DateTime, server_default=func.now())


class OverrideRecord(Base):
    __tablename__ = "override_record"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    override_type = Column(String(50), nullable=False)
    reason = Column(Text)
    applied_by = Column(String(36))
    effective_from = Column(DateTime, server_default=func.now())
    effective_to = Column(DateTime)
    status = Column(String(50), default="active")


class ResponsibilityAssignment(Base):
    __tablename__ = "responsibility_assignment"
    id = Column(String(36), primary_key=True)
    assignment_type = Column(String(50), nullable=False)
    from_type = Column(String(20), nullable=False)
    from_id = Column(String(36), nullable=False)
    to_type = Column(String(20), nullable=False)
    to_id = Column(String(36), nullable=False)
    reason = Column(Text)
    effective_from = Column(DateTime, server_default=func.now())
    effective_to = Column(DateTime)
    status = Column(String(50), default="active")


class UsageRecord(Base):
    __tablename__ = "usage_record"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    backend_used = Column(String(50))
    provider = Column(String(50))
    model = Column(String(100))
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    cost = Column(Numeric(10, 6))
    latency_ms = Column(Integer)


class MemoryCheckpoint(Base):
    __tablename__ = "memory_checkpoint"
    id = Column(String(36), primary_key=True)
    execution_request_id = Column(String(36), ForeignKey("execution_request.id"), nullable=False)
    thread_id = Column(String(36), nullable=False)
    checkpoint_data = Column(Text)  # JSONB in schema
    created_at = Column(DateTime, server_default=func.now())


class TenantPolicy(Base):
    __tablename__ = "tenant_policy"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    name = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=True)
    quality_default = Column(String(50))
    allow_fallback = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    approval_required_for = Column(Text)  # JSONB
    max_budget_monthly = Column(Numeric(12, 2))
    max_requests_per_hour = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="policies")


class TenantPolicyBackendRule(Base):
    __tablename__ = "tenant_policy_backend_rule"
    id = Column(String(36), primary_key=True)
    policy_id = Column(String(36), ForeignKey("tenant_policy.id"), nullable=False)
    backend_id = Column(String(50), nullable=False)
    rule_action = Column(String(20), nullable=False)
    reason = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class TenantCapabilityPolicy(Base):
    __tablename__ = "tenant_capability_policy"
    id = Column(String(36), primary_key=True)
    policy_id = Column(String(36), ForeignKey("tenant_policy.id"), nullable=False)
    capability = Column(String(50), nullable=False)
    max_tokens_per_request = Column(Integer)
    max_images_per_month = Column(Integer)
    rate_limit_per_hour = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())