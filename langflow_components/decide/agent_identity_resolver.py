"""
Agent Identity Resolver Component for LangFlow

Purpose:
    Queries agent identity from Autonomyx agent registry.
    Given employee ID from SSO/HRMS, resolves the assigned agent.
    
Config Fields:
    - agent_identity_url: Autonomyx Agent Identity service URL
    - fallback_agent_id: Default agent if not found
    
Input:
    - employee_id: Employee ID from SSO or HRMS
    
Output:
    - agent_id: Resolved agent ID from Autonomyx
    - agent_config: Full agent configuration
    - agent_type: Type of agent (coding, research, etc.)
    - sponsor_id: Agent sponsor ID
    - allowed_models: List of allowed LLM models

Decide Concept Mapping:
    Maps to Agent, AgentIdentity, EmployeeAgentAssignment.
    See: app/models/agent.py, app/integrations/identity/
"""

from langflow.base import Component
from langflow.inputs import AnyInput, StrInput
from langflow.outputs import AnyOutput

from app.integrations.identity import get_identity_adapter, NormalizedIdentity


class AgentIdentityResolver(Component):
    """Resolve agent identity for employee from Autonomyx."""
    
    display_name = "Agent Identity Resolver"
    description = "Query agent identity from Autonomyx for employee-SSO."
    documentation_urls = ["https://docs.decide.ai/agent-identity"]
    
    inputs = [
        AnyInput(
            name="employee_id",
            display_name="Employee ID",
            required=True,
            info="SSO/HRMS employee ID",
        ),
    ]
    
    outputs = [
        AnyOutput(
            name="agent_id",
            display_name="Agent ID",
            info="Autonomyx agent ID",
        ),
        AnyOutput(
            name="agent_config",
            display_name="Agent Config",
            info="Full agent configuration",
        ),
        AnyOutput(
            name="agent_data",
            display_name="Agent Data",
            info="Complete agent identity data",
        ),
    ]
    
    config_fields = [
        StrInput(
            name="agent_identity_url",
            display_name="Agent Identity URL",
            value="",
            info="Autonomyx Agent Identity service URL",
        ),
        StrInput(
            name="fallback_agent_id",
            display_name="Fallback Agent ID",
            value="",
            info="Default agent if not found",
        ),
    ]
    
    def run(self) -> None:
        """Resolve agent identity for employee."""
        employee_id = self.inputs.employee_id
        agent_identity_url = self.config.agent_identity_url
        fallback_agent_id = self.config.fallback_agent_id
        
        # Get identity adapter
        adapter = get_identity_adapter("autonomyx_agent_identity")
        
        try:
            # The employee_id is used to find assigned agent
            # In Autonomyx, we look up the employee -> agent mapping
            # via the agent's owner_ids or sponsor_id
            identity_data = await adapter.get_identity(employee_id)
            
            if identity_data:
                # Normalize the response
                normalized = adapter.normalize_identity(identity_data)
                
                self.re_outputs.agent_id.send(normalized.external_identity_id)
                self.re_outputs.agent_config.send({
                    "agent_name": normalized.agent_name,
                    "agent_type": normalized.agent_type,
                    "sponsor_id": normalized.sponsor_id,
                    "owner_ids": normalized.owner_ids,
                    "allowed_models": normalized.allowed_models,
                    "budget_limit": normalized.budget_limit,
                    "tpm_limit": normalized.tpm_limit,
                    "status": normalized.status,
                })
                self.re_outputs.agent_data.send(identity_data)
            else:
                # Use fallback or return empty
                if fallback_agent_id:
                    self.re_outputs.agent_id.send(fallback_agent_id)
                    self.re_outputs.agent_config.send({"fallback": True})
                else:
                    self.re_outputs.agent_id.send(None)
                    self.re_outputs.agent_config.send({})
                self.re_outputs.agent_data.send({"not_found": True, "employee_id": employee_id})
                
        except Exception as e:
            # Fallback on error
            if fallback_agent_id:
                self.re_outputs.agent_id.send(fallback_agent_id)
                self.re_outputs.agent_config.send({"fallback": True, "error": str(e)})
            else:
                self.re_outputs.agent_id.send(None)
                self.re_outputs.agent_config.send({"error": str(e)})
            self.re_outputs.agent_data.send({"error": str(e)})