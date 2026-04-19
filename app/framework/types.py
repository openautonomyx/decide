"""
Framework Compiler Types
Schema definitions for LangGraph → Langflow compiler input/output.
"""
from typing import Any, Optional
from pydantic import BaseModel, Field


# ================================================
# INPUT: LangGraph-style graph definition
# ================================================


class LangGraphNode(BaseModel):
    """A node in a LangGraph-style workflow."""
    id: str
    type: str = Field(description="Node type: start, end, llm, tool, condition, etc.")
    data: dict = Field(default_factory=dict, description="Node-specific data")
    metadata: dict = Field(default_factory=dict, description="Node metadata")


class LangGraphEdge(BaseModel):
    """An edge connecting nodes in a LangGraph-style workflow."""
    source: str
    target: str
    condition: Optional[str] = Field(default=None, description="Edge condition for conditionals")
    metadata: dict = Field(default_factory=dict)


class LangGraphToolBinding(BaseModel):
    """Tool binding in a LangGraph workflow."""
    tool_id: str
    tool_name: str
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    retry_config: Optional[dict] = None


class LangGraphSkillBinding(BaseModel):
    """Skill binding in a LangGraph workflow."""
    skill_id: str
    skill_slug: str
    skill_type: str
    scope: str = "workflow"  # workflow or node


class LangGraphMemoryBinding(BaseModel):
    """Memory context binding."""
    memory_type: str
    scope: str  # workflow, organization, product, workflow, run
    injection_point: str = "start"  # start, context, end


class LangGraphApprovalNode(BaseModel):
    """Approval/governance node."""
    policy_id: Optional[str] = None
    risk_level: str = "medium"
    approver_type: str = "human"  # human, model, auto


class LangGraphInput(BaseModel):
    """Complete LangGraph workflow input."""
    name: str
    description: str = ""
    nodes: list[LangGraphNode] = Field(default_factory=list)
    edges: list[LangGraphEdge] = Field(default_factory=list)
    tool_bindings: list[LangGraphToolBinding] = Field(default_factory=list)
    skill_bindings: list[LangGraphSkillBinding] = Field(default_factory=list)
    memory_bindings: list[LangGraphMemoryBinding] = Field(default_factory=list)
    approval_nodes: list[LangGraphApprovalNode] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


# ================================================
# OUTPUT: Langflow-compatible flow structure
# ================================================


class LangflowNode(BaseModel):
    """A node in a Langflow-compatible flow."""
    id: str
    type: str  # LangFlow node type
    position: dict = Field(default_factory=lambda: {"x": 0, "y": 0})
    data: dict = Field(default_factory=dict)


class LangflowEdge(BaseModel):
    """An edge connecting nodes."""
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None


class LangflowFlow(BaseModel):
    """A Langflow-compatible flow structure."""
    name: str
    description: str = ""
    nodes: list[LangflowNode] = Field(default_factory=list)
    edges: list[LangflowEdge] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


# ================================================
# COMPILER RESULT
# ================================================


class CompilerWarning(BaseModel):
    """A warning emitted during compilation."""
    category: str  # unsupported_node, lossy_translation, etc.
    message: str
    node_id: Optional[str] = None


class CompilerUnsupportedConstruct(BaseModel):
    """An unsupported construct that was detected."""
    construct_type: str
    identifier: str
    suggestion: str


class CompilerResult(BaseModel):
    """Result of compiling LangGraph to Langflow."""
    success: bool
    langflow_flow: LangflowFlow
    nodes_mapped: int
    edges_mapped: int
    warnings: list[CompilerWarning] = Field(default_factory=list)
    unsupported_nodes: list[CompilerUnsupportedConstruct] = Field(default_factory=list)
    unsupported_edges: list[CompilerUnsupportedConstruct] = Field(default_factory=list)
    preserved_metadata: dict = Field(default_factory=dict)
    tool_bindings_detected: list[str] = Field(default_factory=list)
    skill_bindings_detected: list[str] = Field(default_factory=list)
    memory_bindings_detected: list[str] = Field(default_factory=list)
    approval_nodes_detected: list[str] = Field(default_factory=list)