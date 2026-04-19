"""
SkillResolver Component

Purpose:
    Skill resolution and routing. Resolves skills based on request
    type and requirements from the skill registry.
    
Config Fields:
    - tenant_id: Tenant ID for skill resolution
    - skill_categories: Comma-separated skill categories to consider
    - routing_strategy: Strategy for skill selection (auto, explicit, llm_routed)
    
Input:
    - request: The request to resolve skills for
    
Output:
    - skills: Selected skills to apply
    - tool_patterns: Tool patterns to use
    
Decide Concept Mapping:
    Maps to AgentSkill + SkillService in Decide.
    See: app/models/skill.py - AgentSkill

Real API:
    GET /api/v1/skills/resolve
"""

from langflow.base import Component
from langflow.inputs import AnyInput, StrInput, DropdownInput
from langflow.outputs import AnyOutput

from langflow_components.decide._client import get_decide_client


class SkillResolver(Component):
    """Skill resolution and routing component."""
    
    display_name = "Skill Resolver"
    description = "Resolves skills based on request type and requirements."
    documentation_urls = ["https://docs.decide.ai/skill-resolver"]
    
    inputs = [
        AnyInput(
            name="request",
            display_name="Request",
            required=True,
            info="Request to resolve skills for",
        ),
    ]
    
    outputs = [
        AnyOutput(
            name="skills",
            display_name="Skills",
            info="Selected skills to apply",
        ),
        AnyOutput(
            name="tool_patterns",
            display_name="Tool Patterns",
            info="Tool patterns to use",
        ),
    ]
    
    config_fields = [
        StrInput(
            name="tenant_id",
            display_name="Tenant ID",
            value="",
            info="Tenant ID for skill resolution",
        ),
        StrInput(
            name="skill_categories",
            display_name="Skill Categories",
            value="",
            info="Comma-separated skill categories to consider",
        ),
        DropdownInput(
            name="routing_strategy",
            display_name="Routing Strategy",
            options=["auto", "explicit", "llm_routed"],
            value="auto",
            info="Strategy for skill selection",
        ),
    ]
    
    def run(self) -> None:
        """
        Resolve skills for request.
        
        Calls Decide's skill resolve API.
        Falls back to stub if API is unavailable.
        """
        request = self.inputs.request
        tenant_id = self.config.tenant_id
        skill_categories = self.config.skill_categories
        routing_strategy = self.config.routing_strategy
        
        if not tenant_id:
            self.re_outputs.skills.send({
                "categories": skill_categories,
                "routing_strategy": routing_strategy,
                "items": [],
                "status": "stub",
            })
            self.re_outputs.tool_patterns.send([])
            return
        
        client = get_decide_client()
        
        try:
            response = client.resolve_skills(
                tenant_id=tenant_id,
            )
            self.re_outputs.skills.send(response)
            self.re_outputs.tool_patterns.send([])
        except Exception as e:
            self.re_outputs.skills.send({
                "tenant_id": tenant_id,
                "categories": skill_categories,
                "routing_strategy": routing_strategy,
                "items": [],
                "status": "stub",
                "fallback": True,
                "error": str(e),
            })
            self.re_outputs.tool_patterns.send([])