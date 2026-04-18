"""
Collaboration Schemas: Product, Project, Group, Channel
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
# from uuid import UUID (DB uses VARCHAR(36))


# Product
class ProductBase(BaseModel):
    name: str
    strategy: str | None = None


class ProductCreate(ProductBase):
    tenant_id: str


class ProductUpdate(BaseModel):
    name: str | None = None
    strategy: str | None = None


class Product(ProductBase):
    id: str
    tenant_id: str
    primary_channel_id: str | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    total: int
    items: list[Product]


# Project
class ProjectBase(BaseModel):
    name: str
    start_date: date | None = None
    end_date: date | None = None


class ProjectCreate(ProjectBase):
    tenant_id: str


class ProjectUpdate(BaseModel):
    name: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class Project(ProjectBase):
    id: str
    tenant_id: str
    channel_id: str | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProjectList(BaseModel):
    total: int
    items: list[Project]


# Group
class GroupBase(BaseModel):
    name: str
    group_type: str | None = None  # community/interest/committee/guild


class GroupCreate(GroupBase):
    tenant_id: str


class GroupUpdate(BaseModel):
    name: str | None = None
    group_type: str | None = None


class Group(GroupBase):
    id: str
    tenant_id: str
    primary_channel_id: str | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GroupList(BaseModel):
    total: int
    items: list[Group]


# Group Membership
class GroupMembershipBase(BaseModel):
    member_type: str
    member_id: str


class GroupMembershipCreate(GroupMembershipBase):
    group_id: str


class GroupMembership(GroupMembershipBase):
    id: str
    group_id: str
    joined_at: datetime
    ended_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


# Channel
class ChannelBase(BaseModel):
    name: str
    context_type: str | None = None  # product/project/group/task/direct
    context_id: str | None = None
    is_primary: bool = False


class ChannelCreate(ChannelBase):
    tenant_id: str


class ChannelUpdate(BaseModel):
    name: str | None = None
    is_primary: bool | None = None


class Channel(ChannelBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChannelList(BaseModel):
    total: int
    items: list[Channel]