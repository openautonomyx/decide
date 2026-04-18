from typing import Optional
"""
Employee Pydantic Schemas
"""
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
# from uuid import UUID (DB uses VARCHAR(36))


class EmployeeBase(BaseModel):
    name: str
    email: EmailStr


class EmployeeCreate(EmployeeBase):
    tenant_id: str


class EmployeeUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class Employee(EmployeeBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeWithIdentity(Employee):
    current_identity: Optional["EmployeeIdentity"] = None


class EmployeeIdentityBase(BaseModel):
    job_title: str | None = None
    department: str | None = None
    seniority: str | None = None
    reporting_to_employee_id: str | None = None


class EmployeeIdentityCreate(EmployeeIdentityBase):
    employee_id: str


class EmployeeIdentity(EmployeeIdentityBase):
    id: str
    employee_id: str
    effective_from: datetime
    effective_to: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeList(BaseModel):
    total: int
    items: list[Employee]


# Resolve forward refs
EmployeeWithIdentity.model_rebuild()