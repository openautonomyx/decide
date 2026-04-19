"""
ApprovalGate Component

Purpose:
    Human approval gate for agent workflows. Delays workflow execution until
    a human approver reviews and approves the action.
    
Config Fields:
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
    Maps to ApprovalRequest + DecisionRecord in Decide models.
    See: app/models/control_plane.py - ApprovalRequest, DecisionRecord
"""

from langflow.base import Component
from langflow.inputs import AnyInput, StrInput, IntInput
from langflow.outputs import AnyOutput


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
        
        This is a stub implementation. In a full integration:
        1. Create an ApprovalRequest in Decide
        2. Wait for approval via Decide's approval API
        3. Route to approved or rejected output
        
        Decide API integration:
        - POST /api/v1/approvals (create request)
        - GET /api/v1/approvals/{id}/status (poll)
        - POST /api/v1/approvals/{id}/approve
        - POST /api/v1/approvals/{id}/deny
        """
        # TODO: Integrate with Decide Approval API
        # from app.api.approvals import router as approval_router
        
        input_data = self.inputs.input_data
        approval_prompt = self.inputs.approval_prompt
        
        # Stub: pass through to approved for now
        # Full impl would call Decide approval endpoints
        self.re_outputs.approved.send(input_data)