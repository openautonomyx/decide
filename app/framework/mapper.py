"""
Framework Mapper Utilities
Explicit mapping table for LangGraph → LangFlow node types.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class NodeMapping:
    """Mapping from LangGraph node type to LangFlow component."""
    langgraph_type: str
    langflow_type: str
    langflow_component: str  # Custom component name if needed
    description: str
    preserve_metadata: bool = True


# ================================================
# CORE NODE MAPPINGS
# ================================================


NODE_MAPPINGS: dict[str, NodeMapping] = {
    # --- Basic graph structure ---
    "start": NodeMapping(
        langgraph_type="start",
        langflow_type="start",
        langflow_component="Start",
        description="Workflow start node",
    ),
    "end": NodeMapping(
        langgraph_type="end",
        langflow_type="end",
        langflow_component="End",
        description="Workflow end node",
    ),
    "END": NodeMapping(
        langgraph_type="end",
        langflow_type="end",
        langflow_component="End",
        description="Workflow end node",
    ),
    
    # --- Execution nodes ---
    "llm": NodeMapping(
        langgraph_type="llm",
        langflow_type="LLM",
        langflow_component="OpenAI",
        description="LLM execution node",
    ),
    "tool": NodeMapping(
        langgraph_type="tool",
        langflow_type="Tool",
        langflow_component="Tool",
        description="Tool execution node",
    ),
    "prompt": NodeMapping(
        langgraph_type="prompt",
        langflow_type="Prompt",
        langflow_component="Prompt",
        description="Prompt template node",
    ),
    "transform": NodeMapping(
        langgraph_type="transform",
        langflow_type="Function",
        langflow_component="Function",
        description="Transform/function node",
    ),
    "condition": NodeMapping(
        langgraph_type="condition",
        langflow_type="Condition",
        langflow_component="DecisionGate",
        description="Conditional routing node",
    ),
    "decision": NodeMapping(
        langgraph_type="decision",
        langflow_type="Condition",
        langflow_component="DecisionGate",
        description="Decision/gate node",
    ),
    "router": NodeMapping(
        langgraph_type="router",
        langflow_type="Condition",
        langflow_component="Router",
        description="Router node",
    ),
    
    # --- Context/governance nodes ---
    "approval": NodeMapping(
        langgraph_type="approval",
        langflow_type="Custom",
        langflow_component="ApprovalGate",
        description="Approval checkpoint node",
    ),
    "memory": NodeMapping(
        langgraph_type="memory",
        langflow_type="Custom",
        langflow_component="MemoryRecall",
        description="Memory fetch/injection node",
    ),
    "skill": NodeMapping(
        langgraph_type="skill",
        langflow_type="Custom",
        langflow_component="SkillResolver",
        description="Skill resolution node",
    ),
    
    # --- Advanced nodes ---
    "chat": NodeMapping(
        langgraph_type="chat",
        langflow_type="Chat",
        langflow_component="Chat",
        description="Chat interface node",
    ),
    "agent": NodeMapping(
        langgraph_type="agent",
        langflow_type="Agent",
        langflow_component="Agent",
        description="Agent execution node",
    ),
    "chain": NodeMapping(
        langgraph_type="chain",
        langflow_type="Chain",
        langflow_component="LLMChain",
        description="LLM chain node",
    ),
    "rag": NodeMapping(
        langgraph_type="rag",
        langflow_type="RAG",
        langflow_component="VectorStore",
        description="RAG/vector store node",
    ),
}


# ================================================
# TOOL MAPPINGS
# ================================================


def map_tool_to_langflow(tool_binding: dict) -> dict:
    """Map a tool binding to LangFlow tool node data."""
    return {
        "tool_name": tool_binding.get("tool_name", ""),
        "tool_id": tool_binding.get("tool_id", ""),
        "input_schema": tool_binding.get("input_schema", {}),
        "output_schema": tool_binding.get("output_schema", {}),
        "retry_config": tool_binding.get("retry_config", {}),
    }


def map_tool_chain_to_langflow(tool_bindings: list[dict]) -> list[dict]:
    """Map multiple tool bindings to LangFlow tool chain."""
    return [map_tool_to_langflow(tb) for tb in tool_bindings]


# ================================================
# SKILL MAPPINGS
# ================================================


def map_skill_to_langflow(skill_binding: dict, node_id: str) -> dict:
    """Map a skill binding to LangFlow/SkillResolver node."""
    return {
        "node_id": node_id,
        "skill_id": skill_binding.get("skill_id", ""),
        "skill_slug": skill_binding.get("skill_slug", ""),
        "skill_type": skill_binding.get("skill_type", "prompt_skill"),
        "scope": skill_binding.get("scope", "workflow"),
    }


def inject_workflow_skills(skill_bindings: list[dict]) -> dict:
    """Inject workflow-level skills as metadata."""
    return {
        "skills": [
            {
                "skill_id": sb.get("skill_id", ""),
                "skill_slug": sb.get("skill_slug", ""),
                "skill_type": sb.get("skill_type", ""),
            }
            for sb in skill_bindings
            if sb.get("scope") == "workflow"
        ]
    }


# ================================================
# MEMORY MAPPINGS
# ================================================


def map_memory_to_langflow(memory_binding: dict) -> dict:
    """Map memory binding to LangFlow/MemoryRecall component."""
    return {
        "memory_type": memory_binding.get("memory_type", ""),
        "scope": memory_binding.get("scope", "workflow"),
        "injection_point": memory_binding.get("injection_point", "start"),
    }


# ================================================
# APPROVAL MAPPINGS
# ================================================


def map_approval_to_langflow(approval_node: dict, node_id: str) -> dict:
    """Map approval node to LangFlow/ApprovalGate component."""
    return {
        "node_id": node_id,
        "policy_id": approval_node.get("policy_id"),
        "risk_level": approval_node.get("risk_level", "medium"),
        "approver_type": approval_node.get("approver_type", "human"),
    }


# ================================================
# METADATA PRESERVATION
# ================================================


def preserve_node_metadata(node: dict, mapping: NodeMapping) -> dict:
    """Preserve original node metadata in LangFlow node."""
    original_metadata = node.get("metadata", {})
    
    preserved = {
        "original_type": node.get("type"),
        "original_data": node.get("data", {}),
    }
    
    # Copy all original metadata
    preserved.update(original_metadata)
    
    return preserved


def get_mapping_category(node_type: str) -> str:
    """Get category for node type."""
    if node_type in ("start", "END"):
        return "basic"
    elif node_type in ("llm", "chat", "agent", "chain", "rag"):
        return "execution"
    elif node_type in ("approval",):
        return "governance"
    elif node_type in ("memory", "skill"):
        return "context"
    elif node_type in ("tool", "transform"):
        return "tool"
    else:
        return "other"


def is_supported(node_type: str) -> bool:
    """Check if node type is directly supported."""
    return node_type in NODE_MAPPINGS


def get_mapping(node_type: str) -> Optional[NodeMapping]:
    """Get mapping for node type."""
    return NODE_MAPPINGS.get(node_type)


def get_fallback_mapping(node_type: str) -> NodeMapping:
    """Get fallback mapping for unsupported node types."""
    return NodeMapping(
        langgraph_type=node_type,
        langflow_type="Custom",
        langflow_component="Passthrough",
        description=f"Unsupported node type: {node_type}",
        preserve_metadata=True,
    )