"""
Workflow Service - Business logic for workflow operations
"""
from uuid import uuid4
from sqlalchemy.orm import Session
from typing import Optional

from app.models.workflow import Task
from app.models.control_plane import ExecutionRequest, ExecutionHistory
from app.schemas.workflow import (
    TaskCreate, TaskUpdate,
    ExecutionRequestCreate, ExecutionRequestUpdate,
    ExecutionHistoryCreate,
)


class WorkflowService:
    # Task operations
    @staticmethod
    def create_task(db: Session, task_in: TaskCreate) -> Task:
        task = Task(id=str(uuid4()), **task_in.model_dump())
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_task(db: Session, task_id: str) -> Optional[Task]:
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def list_tasks(db: Session, tenant_id: Optional[str] = None, project_id: Optional[str] = None,
                   status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[list[Task], int]:
        query = db.query(Task)
        if tenant_id:
            query = query.filter(Task.tenant_id == tenant_id)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update_task(db: Session, task_id: str, task_in: TaskUpdate) -> Optional[Task]:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        for field, value in task_in.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        db.commit()
        db.refresh(task)
        return task


class ExecutionService:
    # Execution Request operations
    @staticmethod
    def create_execution_request(db: Session, req_in: ExecutionRequestCreate) -> ExecutionRequest:
        req = ExecutionRequest(id=str(uuid4()), **req_in.model_dump())
        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def get_execution_request(db: Session, request_id: str) -> Optional[ExecutionRequest]:
        return db.query(ExecutionRequest).filter(ExecutionRequest.id == request_id).first()

    @staticmethod
    def list_execution_requests(db: Session, tenant_id: Optional[str] = None,
                                status: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[list[ExecutionRequest], int]:
        query = db.query(ExecutionRequest)
        if tenant_id:
            query = query.filter(ExecutionRequest.tenant_id == tenant_id)
        if status:
            query = query.filter(ExecutionRequest.status == status)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update_execution_request(db: Session, request_id: str, req_in: ExecutionRequestUpdate) -> Optional[ExecutionRequest]:
        req = db.query(ExecutionRequest).filter(ExecutionRequest.id == request_id).first()
        if not req:
            return None
        for field, value in req_in.model_dump(exclude_unset=True).items():
            setattr(req, field, value)
        db.commit()
        db.refresh(req)
        return req


class ExecutionHistoryService:
    @staticmethod
    def create_history(db: Session, request_id: str, history_in: ExecutionHistoryCreate) -> Optional[ExecutionHistory]:
        # Verify execution request exists
        req = db.query(ExecutionRequest).filter(ExecutionRequest.id == request_id).first()
        if not req:
            return None

        history = ExecutionHistory(
            id=str(uuid4()),
            execution_request_id=request_id,
            thread_id=history_in.thread_id,
            event_type=history_in.event_type,
            event_data=str(history_in.event_data) if history_in.event_data else None,
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    @staticmethod
    def list_history(db: Session, request_id: str, skip: int = 0, limit: int = 100) -> tuple[list[ExecutionHistory], int]:
        query = db.query(ExecutionHistory).filter(ExecutionHistory.execution_request_id == request_id)
        total = query.count()
        items = query.order_by(ExecutionHistory.created_at).offset(skip).limit(limit).all()
        return items, total
