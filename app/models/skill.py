# Skill SQLAlchemy Models
# Continuous skill and tool-pattern substrate for Decide
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, func
from app.db.base import Base


class SkillDefinition(Base):
    __tablename__ = "skill_definition"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    scope_type = Column(String(50))  # organization, product, workflow, agent_role, global
    scope_id = Column(String(36), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    skill_type = Column(String(50), nullable=False)  # prompt_skill, procedure, tool_sequence, workflow_fragment, evaluation_pattern, reviewer_pattern
    status = Column(String(50), default="draft")  # draft, active, deprecated
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SkillVersion(Base):
    __tablename__ = "skill_version"

    id = Column(String(36), primary_key=True)
    skill_id = Column(String(36), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content_json = Column(Text, nullable=False)  # structured skill content
    input_schema_json = Column(Text)  # JSON schema for inputs
    output_schema_json = Column(Text)  # JSON schema for outputs
    tool_requirements_json = Column(Text)  # required tools/permissions
    metadata_json = Column(Text)  # additional metadata
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class SkillBinding(Base):
    __tablename__ = "skill_binding"

    id = Column(String(36), primary_key=True)
    skill_id = Column(String(36), nullable=False, index=True)
    workflow_id = Column(String(36), nullable=True)
    template_id = Column(String(36), nullable=True)
    component_id = Column(String(36), nullable=True)
    agent_role = Column(String(50), nullable=True)
    binding_type = Column(String(50), nullable=False)  # suggested, required, default
    created_at = Column(DateTime, server_default=func.now())


class SkillPromotionRecord(Base):
    __tablename__ = "skill_promotion_record"

    id = Column(String(36), primary_key=True)
    source_type = Column(String(50), nullable=False)  # run, eval, manual, template, imported
    source_id = Column(String(36), nullable=False)
    skill_id = Column(String(36), nullable=False, index=True)
    promoted_by = Column(String(36))  # employee_id or system
    reason = Column(Text)
    evidence_json = Column(Text)  # context about promotion
    created_at = Column(DateTime, server_default=func.now())