# Collaboration Container SQLAlchemy Models
from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Product(Base):
    __tablename__ = "product"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    name = Column(String(255), nullable=False)
    strategy = Column(String)  # Text in schema
    primary_channel_id = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="products")


class Project(Base):
    __tablename__ = "project"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    channel_id = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="projects")


class GroupEntity(Base):
    __tablename__ = "group_entity"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    name = Column(String(255), nullable=False)
    group_type = Column(String(50))
    primary_channel_id = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="groups")
    memberships = relationship("GroupMembership", back_populates="group")


class GroupMembership(Base):
    __tablename__ = "group_membership"
    id = Column(String(36), primary_key=True)
    group_id = Column(String(36), ForeignKey("group_entity.id"), nullable=False)
    member_type = Column(String(20), nullable=False)
    member_id = Column(String(36), nullable=False)
    joined_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime)

    group = relationship("GroupEntity", back_populates="memberships")


class Channel(Base):
    __tablename__ = "channel"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    context_type = Column(String(50))
    context_id = Column(String(36))
    name = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="channels")
    memberships = relationship("ChannelMembership", back_populates="channel")
    messages = relationship("ChannelMessage", back_populates="channel")


class ChannelMembership(Base):
    __tablename__ = "channel_membership"
    id = Column(String(36), primary_key=True)
    channel_id = Column(String(36), ForeignKey("channel.id"), nullable=False)
    member_type = Column(String(20), nullable=False)
    member_id = Column(String(36), nullable=False)
    role = Column(String(50), default="member")
    joined_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime)

    channel = relationship("Channel", back_populates="memberships")


class ChannelMessage(Base):
    __tablename__ = "channel_message"
    id = Column(String(36), primary_key=True)
    channel_id = Column(String(36), ForeignKey("channel.id"), nullable=False)
    author_type = Column(String(20), nullable=False)
    author_id = Column(String(36), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    channel = relationship("Channel", back_populates="messages")


class FileAsset(Base):
    __tablename__ = "file_asset"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    uploaded_by_type = Column(String(20))
    uploaded_by_id = Column(String(36))
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255))
    file_size = Column(String(20))
    mime_type = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


class ChannelFile(Base):
    __tablename__ = "channel_file"
    id = Column(String(36), primary_key=True)
    channel_id = Column(String(36), ForeignKey("channel.id"), nullable=False)
    file_asset_id = Column(String(36), ForeignKey("file_asset.id"), nullable=False)
    uploaded_by = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())