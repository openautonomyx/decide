# Workflow SQLAlchemy Models
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Task(Base):
    __tablename__ = "task"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("project.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")
    priority = Column(String(20), default="medium")
    assigned_to_employee_id = Column(String(36))
    assigned_to_agent_id = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="tasks")
    project = relationship("Project", backref="tasks")
    comments = relationship("TaskComment", back_populates="task")
    attachments = relationship("TaskAttachment", back_populates="task")


class TaskDependency(Base):
    __tablename__ = "task_dependency"
    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), ForeignKey("task.id"), nullable=False)
    depends_on_task_id = Column(String(36), ForeignKey("task.id"), nullable=False)
    dependency_type = Column(String(50))

    task = relationship("Task", foreign_keys=[task_id], backref="dependencies")


class TaskAssignmentHistory(Base):
    __tablename__ = "task_assignment_history"
    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), ForeignKey("task.id"), nullable=False)
    assigned_from_type = Column(String(20))
    assigned_from_id = Column(String(36))
    assigned_to_type = Column(String(20))
    assigned_to_id = Column(String(36))
    assigned_by = Column(String(36))
    assigned_at = Column(DateTime, server_default=func.now())


class Milestone(Base):
    __tablename__ = "milestone"
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("project.id"), nullable=False)
    name = Column(String(255), nullable=False)
    target_date = Column(DateTime)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", backref="milestones")


class MilestoneTask(Base):
    __tablename__ = "milestone_task"
    id = Column(String(36), primary_key=True)
    milestone_id = Column(String(36), ForeignKey("milestone.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("task.id"), nullable=False)


class Deadline(Base):
    __tablename__ = "deadline"
    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), ForeignKey("task.id"), nullable=False)
    due_at = Column(DateTime, nullable=False)
    reminder_at = Column(DateTime)


class Escalation(Base):
    __tablename__ = "escalation"
    id = Column(String(36), primary_key=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    escalation_type = Column(String(50), nullable=False)
    reason = Column(Text)
    escalated_to = Column(String(36))
    status = Column(String(50), default="open")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Reminder(Base):
    __tablename__ = "reminder"
    id = Column(String(36), primary_key=True)
    reminder_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    message = Column(Text)
    status = Column(String(50), default="scheduled")
    created_at = Column(DateTime, server_default=func.now())


class TaskComment(Base):
    __tablename__ = "task_comment"
    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), ForeignKey("task.id"), nullable=False)
    author_type = Column(String(20), nullable=False)
    author_id = Column(String(36), nullable=False)
    content = Column(Text, nullable=False)
    parent_comment_id = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="comments")


class TaskAttachment(Base):
    __tablename__ = "task_attachment"
    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), ForeignKey("task.id"), nullable=False)
    file_asset_id = Column(String(36))
    uploaded_by = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="attachments")


class TaskCommentAttachment(Base):
    __tablename__ = "task_comment_attachment"
    id = Column(String(36), primary_key=True)
    task_comment_id = Column(String(36), ForeignKey("task_comment.id"), nullable=False)
    file_asset_id = Column(String(36), ForeignKey("file_asset.id"), nullable=False)


class TaskRating(Base):
    __tablename__ = "task_rating"
    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), ForeignKey("task.id"), nullable=False)
    rating_type = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)
    rated_by = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())


class TaskFeedback(Base):
    __tablename__ = "task_feedback"
    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), ForeignKey("task.id"), nullable=False)
    content = Column(Text, nullable=False)
    provided_by = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())