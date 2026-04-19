"""
ModelProfile Component

Purpose:
    Model governance and selection profile. Applies model selection
    constraints based on governance rules for an agent execution.
    
Config Fields:
    - profile_id: ID of the model governance profile
    - governance_rules: JSON-encoded governance rules
    
Input:
    - request: The request to apply governance to
    
Output:
    - profile: The selected model governance profile
    - constraints: Runtime constraints to apply
    
Decide Concept Mapping:
    Maps to AgentGovernanceProfile in Decide models.
    See: app/models/agent.py - AgentGovernanceProfile
"""

from langflow.base import Component
from langflow.inputs import AnyInput, StrInput
from langflow.outputs import AnyOutput


class ModelProfile(Component):
    """Model governance and selection profile component."""
    
    display_name = "Model Profile"
    description = "Applies model governance profile for agent execution."
    documentation_urls = ["https://docs.decide.ai/model-profile"]
    
    inputs = [
        AnyInput(
            name="request",
            display_name="Request",
            required=True,
            info="Request to apply governance profile to",
        ),
    ]
    
    outputs = [
        AnyOutput(
            name="profile",
            display_name="Model Profile",
            info="Selected governance profile",
        ),
        AnyOutput(
            name="constraints",
            display_name="Constraints",
            info="Runtime constraints to apply",
        ),
    ]
    
    config_fields = [
        StrInput(
            name="profile_id",
            display_name="Profile ID",
            value="",
            info="ID of the model governance profile",
        ),
        StrInput(
            name="governance_rules",
            display_name="Governance Rules",
            value="",
            info="JSON-encoded governance rules",
        ),
    ]
    
    def run(self) -> None:
        """
        Apply model governance profile.
        
        This is a stub implementation. In a full integration:
        1. Lookup governance profile by ID
        2. Apply constraints to request
        3. Return profile and constraints
        
        Decide API integration:
        - GET /api/v1/agents/{id}/governance-profile
        """
        # TODO: Integrate with Decide AgentGovernanceProfile
        request = self.inputs.request
        profile_id = self.config.profile_id
        
        self.re_outputs.profile.send({
            "profile_id": profile_id,
            "status": "stub",
        })
        self.re_outputs.constraints.send({})