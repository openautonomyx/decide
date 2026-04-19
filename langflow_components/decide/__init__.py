"""
Decide Custom Component Pack for Langflow

This package provides Decide-native components for visual authoring in Langflow.

Components:
- ApprovalGate: Human approval gate for agent workflows
- PolicyCheck: Policy validation and enforcement
- ModelProfile: Model governance and selection
- MemoryResolver: Memory context resolution
- SkillResolver: Skill resolution and routing
- ExportToDecide: Export results to Decide platform
- PublishToLangGraph: Publish workflow to LangGraph
"""

from langflow.base import Component
from langflow.inputs import AnyInput, DropdownInput, StrInput, BoolInput, IntInput
from langflow.outputs import AnyOutput, BoolOutput


class ApprovalGate(Component):
    """Human approval gate for agent workflows."""

    name = "ApprovalGate"
    description = "A gate that requires human approval before proceeding."
    
    inputs = [
        AnyInput(name="input_data", display_name="Input Data", required=True),
        StrInput(name="approval_prompt", display_name="Approval Prompt", value="Please approve this action"),
    ]
    
    outputs = [
        AnyOutput(name="approved", display_name="Approved"),
        AnyOutput(name="rejected", display_name="Rejected"),
    ]
    
    config_fields = [
        StrInput(name="task_description", display_name="Task Description", value=""),
        StrInput(name="approver_role", display_name="Approver Role", value="admin"),
        IntInput(name="timeout_seconds", display_name="Timeout (seconds)", value=3600),
    ]


class PolicyCheck(Component):
    """Policy validation and enforcement component."""

    name = "PolicyCheck"
    description = "Validates and enforces policy rules before proceeding."
    
    inputs = [
        AnyInput(name="input_data", display_name="Input Data", required=True),
    ]
    
    outputs = [
        AnyOutput(name="passed", display_name="Passed"),
        AnyOutput(name="violated", display_name="Violated"),
        AnyOutput(name="audit_record", display_name="Audit Record"),
    ]
    
    config_fields = [
        StrInput(name="policy_id", display_name="Policy ID", value=""),
        StrInput(name="enforcement_mode", display_name="Enforcement Mode", value="soft"),
    ]


class ModelProfile(Component):
    """Model governance and selection profile."""

    name = "ModelProfile"
    description = "Applies model governance profile for agent execution."
    
    inputs = [
        AnyInput(name="request", display_name="Request", required=True),
    ]
    
    outputs = [
        AnyOutput(name="profile", display_name="Model Profile"),
        AnyOutput(name="constraints", display_name="Constraints"),
    ]
    
    config_fields = [
        StrInput(name="profile_id", display_name="Profile ID", value=""),
        StrInput(name="governance_rules", display_name="Governance Rules", value=""),
    ]


class MemoryResolver(Component):
    """Memory context resolution component."""

    name = "MemoryResolver"
    description = "Resolves memory context for agent execution."
    
    inputs = [
        StrInput(name="thread_id", display_name="Thread ID", required=True),
        StrInput(name="user_id", display_name="User ID", required=True),
    ]
    
    outputs = [
        AnyOutput(name="context", display_name="Context"),
        AnyOutput(name="checkpoint_id", display_name="Checkpoint ID"),
    ]
    
    config_fields = [
        IntInput(name="max_history", display_name="Max History Items", value=10),
        BoolInput(name="include_shared", display_name="Include Shared Memory", value=False),
    ]


class SkillResolver(Component):
    """Skill resolution and routing component."""

    name = "SkillResolver"
    description = "Resolves skills based on request type and requirements."
    
    inputs = [
        AnyInput(name="request", display_name="Request", required=True),
    ]
    
    outputs = [
        AnyOutput(name="skills", display_name="Skills"),
        AnyOutput(name="tool_patterns", display_name="Tool Patterns"),
    ]
    
    config_fields = [
        StrInput(name="skill_categories", display_name="Skill Categories", value=""),
        DropdownInput(name="routing_strategy", display_name="Routing Strategy", options=["auto", "explicit", "llm_routed"]),
    ]


class ExportToDecide(Component):
    """Export results to Decide platform."""

    name = "ExportToDecide"
    description = "Exports workflow results to the Decide platform."
    
    inputs = [
        AnyInput(name="results", display_name="Results", required=True),
    ]
    
    outputs = [
        AnyOutput(name="export_ref", display_name="Export Reference"),
    ]
    
    config_fields = [
        StrInput(name="tenant_id", display_name="Tenant ID", value=""),
        StrInput(name="export_format", display_name="Export Format", value="json"),
    ]


class PublishToLangGraph(Component):
    """Publish workflow to LangGraph."""

    name = "PublishToLangGraph"
    description = "Compiles and publishes workflow to LangGraph."
    
    inputs = [
        AnyInput(name="graph_definition", display_name="Graph Definition", required=True),
    ]
    
    outputs = [
        AnyOutput(name="compiled_graph", display_name="Compiled Graph"),
    ]
    
    config_fields = [
        StrInput(name="graph_name", display_name="Graph Name", value=""),
        StrInput(name="checkpointer", display_name="Checkpointer Type", value="memory"),
    ]


# Component registry - do not modify
COMPONENTS = {
    "ApprovalGate": ApprovalGate,
    "PolicyCheck": PolicyCheck,
    "ModelProfile": ModelProfile,
    "MemoryResolver": MemoryResolver,
    "SkillResolver": SkillResolver,
    "ExportToDecide": ExportToDecide,
    "PublishToLangGraph": PublishToLangGraph,
}