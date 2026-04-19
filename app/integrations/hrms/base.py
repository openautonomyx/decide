"""
HRMS Base Adapter - Abstract interface for HR system integrations
All HRMS adapters implement this interface to normalize employee, department, policy data
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class HREmployee(BaseModel):
    """Normalized employee data from any HRMS."""
    employee_id: str
    tenant_id: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    department: str
    department_id: str
    job_title: str
    job_level: Optional[str] = None
    manager_id: Optional[str] = None
    manager_name: Optional[str] = None
    hire_date: Optional[datetime] = None
    employment_status: str = "active"
    employee_type: str = "full-time"  # full-time, part-time, contractor
    location: Optional[str] = None
    cost_center: Optional[str] = None
    metadata: Dict[str, Any] = {}


class HRDepartment(BaseModel):
    """Normalized department data."""
    department_id: str
    tenant_id: str
    name: str
    parent_department_id: Optional[str] = None
    manager_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class HRPolicy(BaseModel):
    """Normalized policy data."""
    policy_id: str
    tenant_id: str
    name: str
    category: str  # leave, expense, travel, etc.
    description: str
    rules: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class BaseHRMSAdapter(ABC):
    """Abstract base class all HRMS adapters implement."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name (workday, bamboohr, sap, etc.)"""
        pass

    @abstractmethod
    async def get_employee(self, employee_id: str) -> Optional[HREmployee]:
        """Get single employee by ID."""
        pass

    @abstractmethod
    async def list_employees(
        self,
        department_id: Optional[str] = None,
        status: str = "active",
        limit: int = 100,
    ) -> List[HREmployee]:
        """List employees with optional filters."""
        pass

    @abstractmethod
    async def get_department(self, department_id: str) -> Optional[HRDepartment]:
        """Get department by ID."""
        pass

    @abstractmethod
    async def list_departments(self, tenant_id: str) -> List[HRDepartment]:
        """List all departments for tenant."""
        pass

    @abstractmethod
    async def get_policy(self, policy_id: str) -> Optional[HRPolicy]:
        """Get policy by ID."""
        pass

    @abstractmethod
    async def list_policies(
        self,
        tenant_id: str,
        category: Optional[str] = None,
    ) -> List[HRPolicy]:
        """List policies for tenant."""
        pass

    @abstractmethod
    async def search_employees(
        self,
        query: str,
        limit: int = 10,
    ) -> List[HREmployee]:
        """Search employees by name, email, department."""
        pass