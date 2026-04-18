"""
Master Data SQLAlchemy Models - 12 tables
Source: docs/data-model/schema-v1.sql
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, func
from app.db.base import Base


class DepartmentMaster(Base):
    __tablename__ = "department_master"
    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    parent_department_code = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)


class JobTitleMaster(Base):
    __tablename__ = "job_title_master"
    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class SeniorityLevelMaster(Base):
    __tablename__ = "seniority_level_master"
    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    level_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


class SfiaSkillMaster(Base):
    __tablename__ = "sfia_skill_master"
    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


class CertificationMaster(Base):
    __tablename__ = "certification_master"
    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    provider = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)


class InstitutionMaster(Base):
    __tablename__ = "institution_master"
    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    institution_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


class QualificationTypeMaster(Base):
    __tablename__ = "qualification_type_master"
    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class TopicMaster(Base):
    __tablename__ = "topic_master"
    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class PromptProfileMaster(Base):
    __tablename__ = "prompt_profile_master"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=func.now)


class GuardrailProfileMaster(Base):
    __tablename__ = "guardrail_profile_master"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    rules = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=func.now)


class ApprovalProfileMaster(Base):
    __tablename__ = "approval_profile_master"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    rules = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=func.now)


class ChannelProfileMaster(Base):
    __tablename__ = "channel_profile_master"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    settings = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=func.now)
