# Template Models - TemplatePack, WorkflowTemplate, WorkflowTemplateVersion

import json
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.db.base import Base


# Template Pack - groups related templates

class TemplatePack(Base):
    __tablename__ = "template_pack"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    templates = relationship("WorkflowTemplate", back_populates="pack", cascade="all, delete-orphan")


# Workflow Template - reusable workflow templates

class WorkflowTemplate(Base):
    __tablename__ = "workflow_template"
    id = Column(String(36), primary_key=True)
    pack_id = Column(String(36), ForeignKey("template_pack.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # e.g., "publish", "approval", "data_processing"
    tags = Column(Text)  # JSON array of tags
    is_published = Column(Boolean, default=False)
    published_version_id = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    pack = relationship("TemplatePack", back_populates="templates")
    versions = relationship("WorkflowTemplateVersion", back_populates="template", cascade="all, delete-orphan")


# Workflow Template Version - versioned template content

class WorkflowTemplateVersion(Base):
    __tablename__ = "workflow_template_version"
    id = Column(String(36), primary_key=True)
    template_id = Column(String(36), ForeignKey("workflow_template.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    is_current = Column(Boolean, default=True)
    runtime_spec = Column(Text)  # Normalized runtime spec JSON
    created_at = Column(DateTime, server_default=func.now())

    template = relationship("WorkflowTemplate", back_populates="versions")