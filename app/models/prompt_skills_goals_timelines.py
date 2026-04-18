# Prompt / Skills / Goals / Timelines SQLAlchemy Models
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_template"
    id = Column(String(36), primary_key=True)
    profile_id = Column(String(36), ForeignKey("prompt_profile_master.id"))
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PromptTemplateVersion(Base):
    __tablename__ = "prompt_template_version"
    id = Column(String(36), primary_key=True)
    template_id = Column(String(36), ForeignKey("prompt_template.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    change_note = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String(36), ForeignKey("employee.id"))


class AgentPromptAssignment(Base):
    __tablename__ = "agent_prompt_assignment"
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    prompt_template_id = Column(String(36), ForeignKey("prompt_template.id"), nullable=False)
    assigned_at = Column(DateTime, server_default=func.now())
    assigned_by = Column(String(36), ForeignKey("employee.id"))
    ended_at = Column(DateTime)


class SkillProfile(Base):
    __tablename__ = "skill_profile"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SkillProfileSkill(Base):
    __tablename__ = "skill_profile_skill"
    id = Column(String(36), primary_key=True)
    profile_id = Column(String(36), ForeignKey("skill_profile.id"), nullable=False)
    skill_code = Column(String(50), nullable=False)
    proficiency_level = Column(String(20), nullable=False)
    is_core = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class AgentGoal(Base):
    __tablename__ = "agent_goal"
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    goal_type = Column(String(50))
    description = Column(Text)
    target_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    agent = relationship("Agent", backref="goals")


class GoalSuccessCriteria(Base):
    __tablename__ = "goal_success_criteria"
    id = Column(String(36), primary_key=True)
    goal_id = Column(String(36), ForeignKey("agent_goal.id"), nullable=False)
    criteria_type = Column(String(50), nullable=False)
    criteria_value = Column(Text, nullable=False)
    weight = Column(Numeric(5, 2), default=1.0)
    created_at = Column(DateTime, server_default=func.now())


class GoalConstraint(Base):
    __tablename__ = "goal_constraint"
    id = Column(String(36), primary_key=True)
    goal_id = Column(String(36), ForeignKey("agent_goal.id"), nullable=False)
    constraint_type = Column(String(50), nullable=False)
    constraint_value = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Timeline(Base):
    __tablename__ = "timeline"
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    agent = relationship("Agent", backref="timelines")


class TimelineMilestone(Base):
    __tablename__ = "timeline_milestone"
    id = Column(String(36), primary_key=True)
    timeline_id = Column(String(36), ForeignKey("timeline.id"), nullable=False)
    name = Column(String(255), nullable=False)
    target_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TimelineDeadline(Base):
    __tablename__ = "timeline_deadline"
    id = Column(String(36), primary_key=True)
    timeline_id = Column(String(36), ForeignKey("timeline.id"), nullable=False)
    name = Column(String(255), nullable=False)
    due_at = Column(DateTime, nullable=False)
    reminder_at = Column(DateTime)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class TimelineDependency(Base):
    __tablename__ = "timeline_dependency"
    id = Column(String(36), primary_key=True)
    timeline_id = Column(String(36), ForeignKey("timeline.id"), nullable=False)
    depends_on_timeline_id = Column(String(36), ForeignKey("timeline.id"), nullable=False)
    dependency_type = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


class AgentGroupMembership(Base):
    __tablename__ = "agent_group_membership"
    id = Column(String(36), primary_key=True)
    group_id = Column(String(36), ForeignKey("group_entity.id"), nullable=False)
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False)
    role = Column(String(50), default="member")
    joined_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime)