# Agent SQLAlchemy Models
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Agent(Base):
    __tablename__ = "agent"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    name = Column(String(255), nullable=False)
    agent_type = Column(String(50))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="agents")


class AgentIdentity(Base):
    __tablename__ = "agent_identity"
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    projected_title = Column(String(255))
    projected_department = Column(String(255))
    effective_from = Column(DateTime, server_default=func.now())
    effective_to = Column(DateTime)

    agent = relationship("Agent", backref="identities")


class AgentProfile(Base):
    __tablename__ = "agent_profile"
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    behavioral_profile = Column(Text)  # JSONB - store as text
    operational_profile = Column(Text)  # JSONB - store as text

    agent = relationship("Agent", backref="profile")


class AgentSkill(Base):
    __tablename__ = "agent_skill"
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    skill_code = Column(String(50))
    skill_name = Column(String(255))
    proficiency_level = Column(String(20))
    evidence = Column(Text)
    last_assessed = Column(DateTime)

    agent = relationship("Agent", backref="skills")


class AgentGovernanceProfile(Base):
    __tablename__ = "agent_governance_profile"
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    prompt_profile_id = Column(String(36))
    guardrail_profile_id = Column(String(36))
    approval_profile_id = Column(String(36))
    channel_profile_id = Column(String(36))

    agent = relationship("Agent", backref="governance")


class AgentMemoryProfile(Base):
    __tablename__ = "agent_memory_profile"
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    memory_enabled = Column(Boolean, default=True)
    thread_retention_days = Column(Integer, default=30)
    checkpoint_interval_seconds = Column(Integer, default=60)

    agent = relationship("Agent", backref="memory")


class AgentRelationship(Base):
    __tablename__ = "agent_relationship"
    id = Column(String(36), primary_key=True)
    from_agent_id = Column(String(36), ForeignKey("agent.id"))
    from_employee_id = Column(String(36), ForeignKey("employee.id"))
    to_agent_id = Column(String(36), ForeignKey("agent.id"))
    to_employee_id = Column(String(36), ForeignKey("employee.id"))
    relationship_type = Column(String(50), nullable=False)  # reports_to/delegates_to/supervises/collaborates_with

    from_agent = relationship("Agent", foreign_keys=[from_agent_id], backref="outgoing_relationships")
    to_agent = relationship("Agent", foreign_keys=[to_agent_id], backref="incoming_relationships")


class EmployeeAgentAssignment(Base):
    __tablename__ = "employee_agent_assignment"
    id = Column(String(36), primary_key=True)
    employee_id = Column(String(36), ForeignKey("employee.id"), nullable=False)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    assignment_role = Column(String(50))  # owner/supervisor/sponsor
    assigned_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime)

    employee = relationship("Employee", backref="agent_assignments")
    agent = relationship("Agent", backref="employee_assignments")