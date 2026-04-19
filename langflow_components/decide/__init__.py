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

Loading:
    Place this package in Langflow's custom components directory:
    ~/.langflow/custom_components/decide
    
    Or add to Python path and import the components.
"""

# Import all components for discovery by Langflow
from langflow_components.decide.approval_gate import ApprovalGate
from langflow_components.decide.policy_check import PolicyCheck
from langflow_components.decide.model_profile import ModelProfile
from langflow_components.decide.memory_resolver import MemoryResolver
from langflow_components.decide.skill_resolver import SkillResolver
from langflow_components.decide.export_to_decide import ExportToDecide
from langflow_components.decide.publish_to_langgraph import PublishToLangGraph


# Component registry - used by Langflow for component discovery
COMPONENTS = {
    "ApprovalGate": ApprovalGate,
    "PolicyCheck": PolicyCheck,
    "ModelProfile": ModelProfile,
    "MemoryResolver": MemoryResolver,
    "SkillResolver": SkillResolver,
    "ExportToDecide": ExportToDecide,
    "PublishToLangGraph": PublishToLangGraph,
}


__all__ = [
    "ApprovalGate",
    "PolicyCheck",
    "ModelProfile",
    "MemoryResolver",
    "SkillResolver",
    "ExportToDecide",
    "PublishToLangGraph",
    "COMPONENTS",
]