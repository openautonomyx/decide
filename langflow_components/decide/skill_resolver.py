"""
SkillResolver Component

Purpose:
    Skill resolution and routing. Resolves skills based on request
    type and requirements from the skill registry.
    
Config Fields:
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
"""

from langflow.base import Component
from langflow.inputs import AnyInput, StrInput, DropdownInput
from langflow.outputs import AnyOutput


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
        
        This is a stub implementation. In a full integration:
        1. Analyze request to determine required skills
        2. Lookup skills from registry
        3. Return skills and tool patterns
        
        Decide API integration:
        - POST /api/v1/skills/resolve
        """
        # TODO: Integrate with Decide Skill API
        request = self.inputs.request
        skill_categories = self.config.skill_categories
        routing_strategy = self.config.routing_strategy
        
        self.re_outputs.skills.send({
            "skills": [],
            "categories": skill_categories,
            "routing_strategy": routing_strategy,
            "status": "stub",
        })
        self.re_outputs.tool_patterns.send([])