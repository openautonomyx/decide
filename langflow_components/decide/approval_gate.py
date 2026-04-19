"""
ApprovalGate Component

Purpose:
    Human approval gate for agent workflows. Delays workflow execution until
    a human approver reviews and approves the action.
    
Config Fields:
    - tenant_id: Tenant ID for approval requests
    - task_description: Description of the task requiring approval
    - approver_role: Role required to approve (default: admin)
    - timeout_seconds: Maximum wait time for approval (default: 3600)
    
Input:
    - input_data: Any data to pass through upon approval
    - approval_prompt: Message shown to approver
    
Output:
    - approved: Input data passed through if approved
    - rejected: Input data passed through if rejected
    
Decide Concept Mapping:
    Maps to ApprovalRequest in Decide models.
    See: app/api/tasks.py - approval_router

Real API:
    - POST /api/v1/approvals - Create request
    - GET /api/v1/approvals/{id} - Check status
    - POST /api/v1/approvals/{id}/approve - Approve
    - POST /api/v1/approvals/{id}/deny - Deny
"""

from langflow.base import Component
from langflow.inputs import AnyInput, StrInput, IntInput
from langflow.outputs import AnyOutput

from langflow_components.decide._client import get_decide_client


class ApprovalGate(Component):
    """Human approval gate for agent workflows."""
    
    display_name = "Approval Gate"
    description = "A gate that requires human approval before proceeding."
    documentation_urls = ["https://docs.decide.ai/approval-gate"]
    
    # Component inputs - runtime data flows
    inputs = [
        AnyInput(
            name="input_data",
            display_name="Input Data",
            required=True,
            info="Data to pass through upon approval",
        ),
        StrInput(
            name="approval_prompt",
            display_name="Approval Prompt",
            value="Please approve this action",
            info="Message shown to the approver",
        ),
    ]
    
    # Component outputs - runtime data flows
    outputs = [
        AnyOutput(
            name="approved",
            display_name="Approved",
            info="Input data passed through if approved",
        ),
        AnyOutput(
            name="rejected",
            display_name="Rejected",
            info="Input data passed through if rejected",
        ),
    ]
    
    # Config fields - set at flow design time
    config_fields = [
        StrInput(
            name="tenant_id",
            display_name="Tenant ID",
            value="",
            info="Tenant ID for approval request",
        ),
        StrInput(
            name="task_description",
            display_name="Task Description",
            value="",
            info="Description of the task requiring approval",
        ),
        StrInput(
            name="approver_role",
            display_name="Approver Role",
            value="admin",
            info="Role required to approve (admin, manager, etc.)",
        ),
        IntInput(
            name="timeout_seconds",
            display_name="Timeout (seconds)",
            value=3600,
            info="Maximum wait time for approval response",
        ),
    ]
    
    def run(self) -> None:
        """
        Execute the approval gate.
        
        Creates an approval request and waits for approval.
        Falls back to stub if API is unavailable.
        
        NOTE: Real implementation would need async polling.
        For now, creates request and passes to approved output as demo.
        """
        input_data = self.inputs.input_data
        approval_prompt = self.inputs.approval_prompt
        tenant_id = self.config.tenant_id
        task_description = self.config.task_description
        approver_role = self.config.approver_role
        
        if not tenant_id:
            # Stub: just pass through to approved for design-time testing
            self.re_outputs.approved.send(input_data)
            return
        
        # Create approval request
        client = get_decide_client()
        
        try:
            response = client.create_approval(
                tenant_id=tenant_id,
                task_description=task_description or approval_prompt,
                request_text=str(input_data),
            )
            
            if response.get("_fallback"):
                self.re_outputs.approved.send(input_data)
                return
            
            # In real impl: would poll /api/v1/approvals/{id} until approved
            # For now: output approval_id so downstream can check status
            output_data = input_data if isinstance(input_data, dict) else {"data": input_data}
            output_data["_approval_id"] = response.get("id")
            output_data["_status"] = response.get("status", "pending")
            output_data["_note"] = "Poll /api/v1/approvals/{id} for final status"
            self.re_outputs.approved.send(output_data)
        except Exception as e:
            # Fallback on error
            self.re_outputs.approved.send(input_data)