"""
Task and Execution API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.session import get_db
from app.models.workflow import Task as TaskModel
from app.models.control_plane import ExecutionRequest as ExecutionRequestModel, ApprovalRequest as ApprovalRequestModel
from app.schemas.task import (
    TaskCreate, TaskUpdate, Task, TaskList,
    ExecutionRequestCreate, ExecutionRequest, ExecutionRequestList,
    ApprovalRequestCreate, ApprovalRequest,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskList)
def list_tasks(
    tenant_id: str = None,
    project_id: str = None,
    status: str = None,
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(get_db)
):
    query = db.query(TaskModel)
    if tenant_id:
        query = query.filter(TaskModel.tenant_id == tenant_id)
    if project_id:
        query = query.filter(TaskModel.project_id == project_id)
    if status:
        query = query.filter(TaskModel.status == status)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return TaskList(total=total, items=items)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=Task, status_code=201)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    task = TaskModel(id=str(uuid4()), **task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: str, task_in: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


# Execution Requests
exec_router = APIRouter(prefix="/execution", tags=["execution"])


@exec_router.get("/requests", response_model=ExecutionRequestList)
def list_execution_requests(
    tenant_id: str = None,
    status: str = None,
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(get_db)
):
    query = db.query(ExecutionRequestModel)
    if tenant_id:
        query = query.filter(ExecutionRequestModel.tenant_id == tenant_id)
    if status:
        query = query.filter(ExecutionRequestModel.status == status)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return ExecutionRequestList(total=total, items=items)


@exec_router.post("/requests", response_model=ExecutionRequest, status_code=201)
def create_execution_request(req_in: ExecutionRequestCreate, db: Session = Depends(get_db)):
    req = ExecutionRequestModel(id=str(uuid4()), **req_in.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@exec_router.get("/requests/{request_id}", response_model=ExecutionRequest)
def get_execution_request(request_id: str, db: Session = Depends(get_db)):
    req = db.query(ExecutionRequestModel).filter(ExecutionRequestModel.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Execution request not found")
    return req


# Approvals
approval_router = APIRouter(prefix="/approvals", tags=["approvals"])


@approval_router.post("", response_model=ApprovalRequest, status_code=201)
def create_approval_request(req_in: ApprovalRequestCreate, db: Session = Depends(get_db)):
    # Verify execution request exists
    exec_req = db.query(ExecutionRequestModel).filter(ExecutionRequestModel.id == req_in.execution_request_id).first()
    if not exec_req:
        raise HTTPException(status_code=404, detail="Execution request not found")
    
    approval = ApprovalRequest(
        id=str(uuid4()),
        execution_request_id=req_in.execution_request_id,
        requested_by_type=req_in.requested_by_type,
        requested_by_id=req_in.requested_by_id,
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


@approval_router.get("/{approval_id}", response_model=ApprovalRequest)
def get_approval_request(approval_id: str, db: Session = Depends(get_db)):
    approval = db.query(ApprovalRequestModel).filter(ApprovalRequestModel.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return approval


@approval_router.post("/{approval_id}/approve", response_model=ApprovalRequest)
def approve_request(approval_id: str, approver_id: str, notes: str = None, db: Session = Depends(get_db)):
    approval = db.query(ApprovalRequestModel).filter(ApprovalRequestModel.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    approval.status = "approved"
    approval.approver = approver_id
    approval.approver_notes = notes
    db.commit()
    db.refresh(approval)
    return approval


@approval_router.post("/{approval_id}/deny", response_model=ApprovalRequest)
def deny_request(approval_id: str, approver_id: str, notes: str = None, db: Session = Depends(get_db)):
    approval = db.query(ApprovalRequestModel).filter(ApprovalRequestModel.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    approval.status = "denied"
    approval.approver = approver_id
    approval.approver_notes = notes
    db.commit()
    db.refresh(approval)
    return approval