"""
HRMS Employee Resolver Component for LangFlow

Purpose:
    Queries employee data from organization's HRMS (Workday, BambooHR, SAP, ADP, etc.)
    to provide context for agent assignment and task delegation.
    
Config Fields:
    - hrms_provider: HRMS system (workday, bamboohr, sap, adp, ukg, custom)
    - employee_id: Specific employee ID (or use input for dynamic)
    - fallback_tenant_id: Default tenant if not provided
    
Input:
    - employee_identifier: Employee ID, email, or search query
    
Output:
    - employee_data: Normalized employee data
    - department_data: Employee's department info
    - policies: Applicable policies for this employee

Decide Concept Mapping:
    Maps to Employee, EmployeeAgentAssignment in Decide models.
    See: app/models/employee.py, app/models/agent.py
"""

from langflow.base import Component
from langflow.inputs import AnyInput, StrInput, DropdownInput
from langflow.outputs import AnyOutput

from app.integrations.hrms import get_hrms_adapter, HREmployee


# HRMS Provider options
HRMS_PROVIDERS = [
    ("custom", "Custom REST API"),
    ("workday", "Workday"),
    ("bamboohr", "BambooHR"),
    ("sap_successfactors", "SAP SuccessFactors"),
    ("oracle_hcm", "Oracle HCM"),
    ("adp", "ADP"),
    ("ukg", "UKG"),
]


class HRMSEmployeeResolver(Component):
    """Query employee data from HRMS for agent context."""
    
    display_name = "HRMS Employee Resolver"
    description = "Query employee data from HRMS system for agent orchestration."
    documentation_urls = ["https://docs.decide.ai/hrms-resolver"]
    
    inputs = [
        AnyInput(
            name="employee_identifier",
            display_name="Employee ID/Email/Query",
            required=True,
            info="Employee ID, email, or search query",
        ),
    ]
    
    outputs = [
        AnyOutput(
            name="employee_data",
            display_name="Employee Data",
            info="Normalized employee data from HRMS",
        ),
        AnyOutput(
            name="department_data",
            display_name="Department Data",
            info="Employee's department information",
        ),
        AnyOutput(
            name="policies",
            display_name="Applicable Policies",
            info="HR policies applicable to this employee",
        ),
    ]
    
    config_fields = [
        DropdownInput(
            name="hrms_provider",
            display_name="HRMS Provider",
            options=HRMS_PROVIDERS,
            value="custom",
            info="HRMS system to connect to",
        ),
        StrInput(
            name="fallback_tenant_id",
            display_name="Fallback Tenant ID",
            value="",
            info="Default tenant ID if not in input",
        ),
    ]
    
    def run(self) -> None:
        """Query HRMS for employee data."""
        identifier = self.inputs.employee_identifier
        provider = self.config.hrms_provider
        tenant_id = self.config.fallback_tenant_id
        
        # Get HRMS adapter
        adapter = get_hrms_adapter(provider)
        
        # Determine if identifier is ID, email, or search query
        employee_data = None
        department_data = None
        policies = []
        
        try:
            # Try as employee ID first
            employee_data = await adapter.get_employee(identifier)
            
            if not employee_data:
                # Try as email
                results = await adapter.search_employees(identifier, limit=1)
                if results:
                    employee_data = results[0]
            
            if employee_data:
                # Get department data
                if employee_data.department_id:
                    department_data = await adapter.get_department(employee_data.department_id)
                
                # Get applicable policies
                policies = await adapter.list_policies(
                    tenant_id=employee_data.tenant_id or tenant_id,
                )
                
                # Convert to dict for output
                emp_dict = employee_data.model_dump() if hasattr(employee_data, 'model_dump') else employee_data.dict()
                dept_dict = department_data.model_dump() if department_data and hasattr(department_data, 'model_dump') else (department_data.dict() if department_data else {})
                policy_list = [p.model_dump() if hasattr(p, 'model_dump') else p.dict() for p in policies]
                
                self.re_outputs.employee_data.send(emp_dict)
                self.re_outputs.department_data.send(dept_dict)
                self.re_outputs.policies.send(policy_list)
            else:
                # Return empty on not found
                self.re_outputs.employee_data.send({"not_found": True, "identifier": identifier})
                self.re_outputs.department_data.send({})
                self.re_outputs.policies.send([])
                
        except Exception as e:
            # Fallback on error
            self.re_outputs.employee_data.send({"error": str(e), "identifier": identifier})
            self.re_outputs.department_data.send({})
            self.re_outputs.policies.send([])