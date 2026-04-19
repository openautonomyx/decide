# Workflow Definition and Execution Models

import json
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.db.base import Base


# Workflow Definition and Versioning

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definition"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    source_type = Column(String(50), default="langflow")  # langflow, manual, etc.
    source_json = Column(Text)  # Raw imported JSON
    is_published = Column(Boolean, default=False)
    published_version_id = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="workflow_definitions")
    versions = relationship("WorkflowVersion", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowVersion(Base):
    __tablename__ = "workflow_version"
    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), ForeignKey("workflow_definition.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    is_current = Column(Boolean, default=True)
    runtime_spec = Column(Text)  # Normalized runtime spec JSON
    created_at = Column(DateTime, server_default=func.now())

    workflow = relationship("WorkflowDefinition", back_populates="versions")
    nodes = relationship("WorkflowNode", back_populates="version", cascade="all, delete-orphan")
    edges = relationship("WorkflowEdge", back_populates="version", cascade="all, delete-orphan")


class WorkflowNode(Base):
    __tablename__ = "workflow_node"
    id = Column(String(36), primary_key=True)
    version_id = Column(String(36), ForeignKey("workflow_version.id"), nullable=False)
    node_type = Column(String(50), nullable=False)  # start, llm, tool, condition, human_approval, end
    node_id = Column(String(100), nullable=False)  # Original node ID from source
    label = Column(String(255))
    config = Column(Text)  # JSON config for the node
    position_x = Column(Integer)
    position_y = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    version = relationship("WorkflowVersion", back_populates="nodes")


class WorkflowEdge(Base):
    __tablename__ = "workflow_edge"
    id = Column(String(36), primary_key=True)
    version_id = Column(String(36), ForeignKey("workflow_version.id"), nullable=False)
    edge_id = Column(String(100))  # Original edge ID
    source_node_id = Column(String(100), nullable=False)
    target_node_id = Column(String(100), nullable=False)
    edge_type = Column(String(50), default="smooth")  # smooth, straight, etc.
    label = Column(String(255))
    condition = Column(Text)  # For condition edges: JSON condition
    created_at = Column(DateTime, server_default=func.now())

    version = relationship("WorkflowVersion", back_populates="edges")


# Validation

class WorkflowValidationResult(Base):
    __tablename__ = "workflow_validation_result"
    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), ForeignKey("workflow_definition.id"), nullable=False)
    version_id = Column(String(36), ForeignKey("workflow_version.id"))
    is_valid = Column(Boolean, default=False)
    issues_json = Column(Text)  # JSON array of issues
    can_publish = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    workflow = relationship("WorkflowDefinition", backref="validations")


class WorkflowPublishArtifact(Base):
    __tablename__ = "workflow_publish_artifact"
    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), ForeignKey("workflow_definition.id"), nullable=False)
    version_id = Column(String(36), ForeignKey("workflow_version.id"), nullable=False)
    artifact_json = Column(Text)  # Published runtime artifact
    created_at = Column(DateTime, server_default=func.now())

    workflow = relationship("WorkflowDefinition", backref="published_artifacts")


# Execution

class WorkflowRun(Base):
    __tablename__ = "workflow_run"
    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), ForeignKey("workflow_definition.id"), nullable=False)
    version_id = Column(String(36), ForeignKey("workflow_version.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    final_output = Column(Text)
    resolved_skills_json = Column(Text)  # JSON array of resolved skills
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    error_message = Column(Text)
    memory_context_json = Column(Text)
    memory_read_ids_json = Column(Text)
    memory_written_ids_json = Column(Text)
    memory_write_mode = Column(String(50))

    workflow = relationship("WorkflowDefinition", backref="runs")
    steps = relationship("WorkflowRunStep", back_populates="run", cascade="all, delete-orphan")


class WorkflowRunStep(Base):
    __tablename__ = "workflow_run_step"
    id = Column(String(36), primary_key=True)
    run_id = Column(String(36), ForeignKey("workflow_run.id"), nullable=False)
    node_id = Column(String(100), nullable=False)
    node_type = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, skipped, failed
    output = Column(Text)
    error = Column(Text)
    branch_decision = Column(String(50))  # For condition nodes
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)

    run = relationship("WorkflowRun", back_populates="steps")
