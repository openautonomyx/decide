"""
Custom HRMS Adapter - Generic REST API adapter for any HR system
Works with any HRMS that exposes REST APIs for employees, departments, policies
"""
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

import httpx
from pydantic import BaseModel

from app.integrations.hrms.base import (
    BaseHRMSAdapter,
    HREmployee,
    HRDepartment,
    HRPolicy,
)


class CustomHRMSSettings(BaseModel):
    """Configuration for custom HRMS REST API."""
    base_url: str = ""  # e.g. https://api.company.com/hr/v1
    api_key: str = ""
    api_secret: str = ""
    tenant_id: str = ""
    timeout: float = 30.0
    # Optional field mappings
    employee_id_field: str = "employee_id"
    department_id_field: str = "department_id"
    policy_id_field: str = "policy_id"


class CustomHRMSAdapter(BaseHRMSAdapter):
    """
    Generic adapter that connects to any HRMS REST API.
    Configure via environment variables:
    - HRMS_API_URL: Base URL of HRMS API
    - HRMS_API_KEY: API key/token
    - HRMS_TENANT_ID: Tenant/customer ID
    """

    def __init__(self, settings: Optional[CustomHRMSSettings] = None):
        settings = settings or CustomHRMSSettings(
            base_url=os.environ.get("HRMS_API_URL", ""),
            api_key=os.environ.get("HRMS_API_KEY", ""),
            tenant_id=os.environ.get("HRMS_TENANT_ID", ""),
        )
        self._settings = settings
        self._client = httpx.Client(
            base_url=settings.base_url,
            headers={
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json",
                "X-Tenant-ID": settings.tenant_id,
            },
            timeout=settings.timeout,
        )

    def get_provider_name(self) -> str:
        return "custom"

    def _map_employee(self, data: Dict[str, Any]) -> HREmployee:
        """Map HRMS employee data to normalized format."""
        emp_id_field = self._settings.employee_id_field
        dept_id_field = self._settings.department_id_field
        
        return HREmployee(
            employee_id=data.get(emp_id_field, ""),
            tenant_id=self._settings.tenant_id,
            email=data.get("email", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            display_name=data.get("display_name", "") or f"{data.get('first_name', '')} {data.get('last_name', '')}",
            department=data.get("department", {}).get("name", "") if isinstance(data.get("department"), dict) else data.get("department", ""),
            department_id=data.get("department", {}).get(dept_id_field, "") if isinstance(data.get("department"), dict) else data.get(dept_id_field, ""),
            job_title=data.get("job_title", ""),
            job_level=data.get("job_level"),
            manager_id=data.get("manager", {}).get(emp_id_field) if isinstance(data.get("manager"), dict) else data.get("manager_id"),
            manager_name=data.get("manager", {}).get("display_name") if isinstance(data.get("manager"), dict) else data.get("manager_name"),
            hire_date=datetime.fromisoformat(data["hire_date"]) if data.get("hire_date") else None,
            employment_status=data.get("status", "active"),
            employee_type=data.get("employee_type", "full-time"),
            location=data.get("location"),
            cost_center=data.get("cost_center"),
            metadata=data,
        )

    def _map_department(self, data: Dict[str, Any]) -> HRDepartment:
        dept_id_field = self._settings.department_id_field
        return HRDepartment(
            department_id=data.get(dept_id_field, ""),
            tenant_id=self._settings.tenant_id,
            name=data.get("name", ""),
            parent_department_id=data.get("parent_department_id"),
            manager_id=data.get("manager_id"),
            metadata=data,
        )

    def _map_policy(self, data: Dict[str, Any]) -> HRPolicy:
        return HRPolicy(
            policy_id=data.get(self._settings.policy_id_field, ""),
            tenant_id=self._settings.tenant_id,
            name=data.get("name", ""),
            category=data.get("category", "general"),
            description=data.get("description", ""),
            rules=data.get("rules", {}),
            metadata=data,
        )

    async def get_employee(self, employee_id: str) -> Optional[HREmployee]:
        """GET /employees/{id} - Get employee by ID."""
        try:
            resp = self._client.get(f"/employees/{employee_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            # Handle wrapping
            if "data" in data:
                data = data["data"]
            return self._map_employee(data)
        except httpx.HTTPError:
            return None

    async def list_employees(
        self,
        department_id: Optional[str] = None,
        status: str = "active",
        limit: int = 100,
    ) -> List[HREmployee]:
        """GET /employees - List employees with filters."""
        try:
            params = {"limit": limit, "status": status}
            if department_id:
                params["department_id"] = department_id
            resp = self._client.get("/employees", params=params)
            resp.raise_for_status()
            data = resp.json()
            employees = data.get("data", data.get("employees", []))
            return [self._map_employee(e) for e in employees]
        except httpx.HTTPError:
            return []

    async def get_department(self, department_id: str) -> Optional[HRDepartment]:
        """GET /departments/{id} - Get department by ID."""
        try:
            resp = self._client.get(f"/departments/{department_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            if "data" in data:
                data = data["data"]
            return self._map_department(data)
        except httpx.HTTPError:
            return None

    async def list_departments(self, tenant_id: str) -> List[HRDepartment]:
        """GET /departments - List all departments."""
        try:
            resp = self._client.get("/departments")
            resp.raise_for_status()
            data = resp.json()
            depts = data.get("data", data.get("departments", []))
            return [self._map_department(d) for d in depts]
        except httpx.HTTPError:
            return []

    async def get_policy(self, policy_id: str) -> Optional[HRPolicy]:
        """GET /policies/{id} - Get policy by ID."""
        try:
            resp = self._client.get(f"/policies/{policy_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            if "data" in data:
                data = data["data"]
            return self._map_policy(data)
        except httpx.HTTPError:
            return None

    async def list_policies(
        self,
        tenant_id: str,
        category: Optional[str] = None,
    ) -> List[HRPolicy]:
        """GET /policies - List policies."""
        try:
            params = {}
            if category:
                params["category"] = category
            resp = self._client.get("/policies", params=params)
            resp.raise_for_status()
            data = resp.json()
            policies = data.get("data", data.get("policies", []))
            return [self._map_policy(p) for p in policies]
        except httpx.HTTPError:
            return []

    async def search_employees(
        self,
        query: str,
        limit: int = 10,
    ) -> List[HREmployee]:
        """GET /employees/search?q=... - Search employees."""
        try:
            resp = self._client.get("/employees/search", params={"q": query, "limit": limit})
            resp.raise_for_status()
            data = resp.json()
            employees = data.get("data", data.get("employees", []))
            return [self._map_employee(e) for e in employees]
        except httpx.HTTPError:
            return []

    def close(self):
        """Close HTTP client."""
        self._client.close()