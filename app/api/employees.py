"""
Employee API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.session import get_db
from app.models.tenant_employee import Employee as EmployeeModel, EmployeeIdentity
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, Employee, EmployeeList

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=EmployeeList)
def list_employees(tenant_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(EmployeeModel)
    if tenant_id:
        query = query.filter(EmployeeModel.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return EmployeeList(total=total, items=items)


@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("", response_model=Employee, status_code=201)
def create_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    employee = EmployeeModel(id=str(uuid4()), **employee_in.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.patch("/{employee_id}", response_model=Employee)
def update_employee(employee_id: str, employee_in: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in employee_in.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return None