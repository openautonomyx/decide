# Component Models - ComponentDefinition, ComponentVersion, ComponentCapability

import json
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.db.base import Base


# Component Definition - represents a reusable component type

class ComponentDefinition(Base):
    __tablename__ = "component_definition"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)  # e.g., "start", "llm", "tool"
    display_name = Column(String(255))
    description = Column(Text)
    category = Column(String(100))  # e.g., "control", "ai", "integration"
    icon = Column(String(50))  # Icon name for UI
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    versions = relationship("ComponentVersion", back_populates="component", cascade="all, delete-orphan")
    capabilities = relationship("ComponentCapability", back_populates="component", cascade="all, delete-orphan")


# Component Version - versioned component definition

class ComponentVersion(Base):
    __tablename__ = "component_version"
    id = Column(String(36), primary_key=True)
    component_id = Column(String(36), ForeignKey("component_definition.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    is_current = Column(Boolean, default=True)
    schema_json = Column(Text)  # JSON schema for component config
    created_at = Column(DateTime, server_default=func.now())

    component = relationship("ComponentDefinition", back_populates="versions")


# Component Capability - defines what a component can do

class ComponentCapability(Base):
    __tablename__ = "component_capability"
    id = Column(String(36), primary_key=True)
    component_id = Column(String(36), ForeignKey("component_definition.id"), nullable=False)
    capability_type = Column(String(100), nullable=False)  # e.g., "execute_llm", "call_tool", "await_approval"
    capability_config = Column(Text)  # JSON config for the capability
    created_at = Column(DateTime, server_default=func.now())

    component = relationship("ComponentDefinition", back_populates="capabilities")