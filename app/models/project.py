# Project SQLAlchemy Model
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class Project(Base):
    """Project model for organizing decisions and workflows"""
    __tablename__ = "project"
    __table_args__ = {"extend_existing": True}
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")  # active, completed, archived
    
    # Optional parent project for hierarchy
    parent_project_id = Column(String(36), ForeignKey("project.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", backref="projects")
    parent_project = relationship("Project", remote_side=[id], backref="sub_projects")
