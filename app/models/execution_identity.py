# Execution Identity Binding SQLAlchemy Models
# Binds external execution identities from autonomyx-agent-identity to Decide workflows
from sqlalchemy import Column, String, DateTime, Text, Numeric, Integer, Boolean, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class ExecutionIdentityBinding(Base):
    __tablename__ = "execution_identity_binding"

    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36))
    workflow_version_id = Column(String(36))
    template_id = Column(String(36))
    execution_identity_id = Column(String(36), nullable=False)
    tenant_id = Column(String(36), nullable=False)
    agent_name = Column(String(255))
    agent_type = Column(String(50))
    sponsor_id = Column(String(36))
    owner_ids_json = Column(Text)  # JSON array
    manager_id = Column(String(36))
    blueprint_id = Column(String(36))
    allowed_models_json = Column(Text)  # JSON array
    budget_limit = Column(Numeric(12, 2))
    tpm_limit = Column(Integer)
    expires_at = Column(DateTime)
    status = Column(String(50), default="active")
    source_system = Column(String(50), default="autonomyx-agent-identity")
    last_synced_at = Column(DateTime)
    metadata_json = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PolicyEvaluationResult(Base):
    __tablename__ = "policy_evaluation_result"

    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36))
    workflow_version_id = Column(String(36))
    run_id = Column(String(36))
    execution_identity_id = Column(String(36))
    evaluation_type = Column(String(50), nullable=False)  # validate, publish, run
    is_allowed = Column(Boolean, nullable=False)
    reasons_json = Column(Text)  # JSON array
    metadata_json = Column(Text)
    created_at = Column(DateTime, server_default=func.now())