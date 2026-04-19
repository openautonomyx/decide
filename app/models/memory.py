# Memory Space and Entry SQLAlchemy Models
# Scoped memory substrate for Decide
from sqlalchemy import Column, String, DateTime, Text, Boolean, func
from app.db.base import Base


class MemorySpace(Base):
    __tablename__ = "memory_space"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    scope_type = Column(String(50), nullable=False)  # organization, workflow, run, agent_role, product
    scope_id = Column(String(36), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MemoryEntry(Base):
    __tablename__ = "memory_entry"

    id = Column(String(36), primary_key=True)
    memory_space_id = Column(String(36), nullable=False, index=True)
    memory_type = Column(String(50), nullable=False)  # fact, policy, instruction, summary, preference, artifact_reference, lesson, template_hint
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags_json = Column(Text)  # JSON array of tags
    source_type = Column(String(50))  # workflow, run, human, agent, system
    source_id = Column(String(36))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())