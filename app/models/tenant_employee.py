# Tenant and Employee SQLAlchemy Models
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Tenant(Base):
    __tablename__ = "tenant"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Employee(Base):
    __tablename__ = "employee"
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="employees")


class EmployeeIdentity(Base):
    __tablename__ = "employee_identity"
    id = Column(String(36), primary_key=True)
    employee_id = Column(String(36), ForeignKey("employee.id"), nullable=False)
    job_title = Column(String(255))
    department = Column(String(255))
    seniority = Column(String(50))
    reporting_to_employee_id = Column(String(36), ForeignKey("employee.id"))
    effective_from = Column(DateTime, server_default=func.now())
    effective_to = Column(DateTime)

    employee = relationship("Employee", foreign_keys=[employee_id], backref="identities")


class EmployeeEmployment(Base):
    __tablename__ = "employee_employment"
    id = Column(String(36), primary_key=True)
    employee_id = Column(String(36), ForeignKey("employee.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    employment_type = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


class EmployeeEducation(Base):
    __tablename__ = "employee_education"
    id = Column(String(36), primary_key=True)
    employee_id = Column(String(36), ForeignKey("employee.id"), nullable=False)
    institution = Column(String(255))
    degree = Column(String(255))
    field_of_study = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)


class EmployeeCertification(Base):
    __tablename__ = "employee_certification"
    id = Column(String(36), primary_key=True)
    employee_id = Column(String(36), ForeignKey("employee.id"), nullable=False)
    certification_code = Column(String(50))
    certification_name = Column(String(255))
    issued_date = Column(DateTime)
    expiry_date = Column(DateTime)