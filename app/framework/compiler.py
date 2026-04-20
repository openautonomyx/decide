"""
LangGraph → LangFlow Compiler
Main compiler class that translates LangGraph workflows to LangFlow.

Primary outcome:
A LangGraph-defined workflow should be transformable into a LangFlow flow with:
- nodes
- edges
- branching
- metadata
- tool references
- skill references
- memory/context hooks
- approval/governance hooks where applicable
"""
import uuid
from typing import Any, Optional

from app.framework.types import (
    LangGraphInput,
    LangGraphNode,
    LangGraphEdge,
    LangGraphToolBinding,
    LangGraphSkillBinding,
    LangGraphMemoryBinding,
    LangGraphApprovalNode,
    LangflowFlow,
    LangflowNode,
    LangflowEdge,
    CompilerResult,
    CompilerWarning,
    CompilerUnsupportedConstruct,
)
from app.framework.mapper import (
    NODE_MAPPINGS,
    get_mapping,
    get_fallback_mapping,
    is_supported,
    preserve_node_metadata,
    map_tool_to_langflow,
    map_skill_to_langflow,
    inject_workflow_skills,
    map_memory_to_langflow,
    map_approval_to_langflow,
)


class LangGraphToLangFlowCompiler:
    """Compiler that translates LangGraph workflows to LangFlow."""

    def __init__(self):
        self._node_position = {"x": 100, "y": 100}
        self._node_spacing = {"x": 250, "y": 150}

    def _next_position(self) -> dict:
        """Get next node position."""
        pos = self._node_position.copy()
        self._node_position["x"] += self._node_spacing["x"]
        self._node_position["y"] += self._node_spacing["y"]
        return pos

    def _reset_positions(self):
        """Reset position counter."""
        self._node_position = {"x": 100, "y": 100}

    def compile(self, input: LangGraphInput) -> CompilerResult:
        """
        Compile a LangGraph input to LangFlow.
        
        Args:
            input: LangGraph workflow definition
            
        Returns:
            CompilerResult with LangFlow flow and diagnostics
        """
        warnings: list[CompilerWarning] = []
        unsupported_nodes: list[CompilerUnsupportedConstruct] = []
        unsupported_edges: list[CompilerUnsupportedConstruct] = []
        
        nodes: list[LangflowNode] = []
        edges: list[LangflowEdge] = []
        
        tool_bindings_detected: list[str] = []
        skill_bindings_detected: list[str] = []
        memory_bindings_detected: list[str] = []
        approval_nodes_detected: list[str] = []
        
        # Track node type mappings for edge validation
        node_type_map: dict[str, str] = {}
        
        # Process nodes
        self._reset_positions()
        for idx, lg_node in enumerate(input.nodes):
            node_id = lg_node.id
            node_type = lg_node.type
            
            mapping = get_mapping(node_type)
            
            if mapping is None:
                # Unsupported node - emit warning but try to preserve
                warnings.append(CompilerWarning(
                    category="unsupported_node",
                    message=f"Node type '{node_type}' not directly supported, using fallback",
                    node_id=node_id,
                ))
                mapping = get_fallback_mapping(node_type)
                unsupported_nodes.append(CompilerUnsupportedConstruct(
                    construct_type="node",
                    identifier=node_id,
                    suggestion=f"Consider using: {', '.join(NODE_MAPPINGS.keys())}",
                ))
            
            # Create LangFlow node
            lf_node = self._map_node(lg_node, mapping)
            nodes.append(lf_node)
            node_type_map[node_id] = mapping.langflow_type
            
            # Track bindings - extract from node data
            if node_type == "tool":
                tool_name = lg_node.data.get("tool_name", node_id)
                tool_bindings_detected.append(tool_name)
            if node_type == "skill":
                skill_slug = lg_node.data.get("skill_slug", node_id)
                skill_bindings_detected.append(skill_slug)
            if node_type == "memory":
                mem_type = lg_node.data.get("memory_type", "unknown")
                scope = lg_node.data.get("scope", "workflow")
                memory_bindings_detected.append(f"{mem_type}:{scope}")
            if node_type == "approval":
                policy_id = lg_node.data.get("policy_id", "default")
                approval_nodes_detected.append(policy_id)
        
        # Process edges
        for lg_edge in input.edges:
            source = lg_edge.source
            target = lg_edge.target
            
            # Check if source/target exist
            if source not in node_type_map:
                warnings.append(CompilerWarning(
                    category="missing_node",
                    message=f"Edge source '{source}' not found in nodes",
                ))
                unsupported_edges.append(CompilerUnsupportedConstruct(
                    construct_type="edge",
                    identifier=f"{source}->{target}",
                    suggestion="Remove or add the missing node",
                ))
                continue
                
            if target not in node_type_map:
                warnings.append(CompilerWarning(
                    category="missing_node",
                    message=f"Edge target '{target}' not found in nodes",
                ))
                unsupported_edges.append(CompilerUnsupportedConstruct(
                    construct_type="edge",
                    identifier=f"{source}->{target}",
                    suggestion="Remove or add the missing node",
                ))
                continue
            
            # Check if edge is from conditional node
            source_type = node_type_map.get(source, "")
            if source_type in ("Condition", "DecisionGate", "router"):
                # Conditional edge - could preserve condition in edge data
                lf_edge = LangflowEdge(
                    source=source,
                    target=target,
                    sourceHandle="true",  # Default handle for conditionals
                )
            else:
                lf_edge = LangflowEdge(
                    source=source,
                    target=target,
                )
            edges.append(lf_edge)
        
        # Inject workflow-level metadata
        preserved_metadata = {
            "original_name": input.name,
            "original_description": input.description,
        }
        
        # Add skill bindings to metadata
        if input.skill_bindings:
            skill_data = inject_workflow_skills([
                sb.model_dump() for sb in input.skill_bindings
            ])
            preserved_metadata.update(skill_data)
            for sb in input.skill_bindings:
                skill_bindings_detected.append(sb.skill_slug)
        
        # Add memory bindings to metadata
        if input.memory_bindings:
            preserved_metadata["memory"] = [
                mb.model_dump() for mb in input.memory_bindings
            ]
            for mb in input.memory_bindings:
                memory_bindings_detected.append(f"{mb.memory_type}:{mb.scope}")
        
        # Add tool bindings to metadata
        if input.tool_bindings:
            preserved_metadata["tools"] = [
                tb.model_dump() for tb in input.tool_bindings
            ]
            for tb in input.tool_bindings:
                tool_bindings_detected.append(tb.tool_name)
        
        # Add approval nodes to metadata
        if input.approval_nodes:
            preserved_metadata["approvals"] = [
                an.model_dump() for an in input.approval_nodes
            ]
            for an in input.approval_nodes:
                approval_nodes_detected.append(an.policy_id or "default")
        
        # Add original metadata
        preserved_metadata.update(input.metadata)
        
        # Create LangFlow flow
        lf_flow = LangflowFlow(
            name=input.name,
            description=input.description,
            nodes=nodes,
            edges=edges,
            metadata=preserved_metadata,
        )
        
        return CompilerResult(
            success=len(unsupported_nodes) == 0,
            langflow_flow=lf_flow,
            nodes_mapped=len(nodes),
            edges_mapped=len(edges),
            warnings=warnings,
            unsupported_nodes=unsupported_nodes,
            unsupported_edges=unsupported_edges,
            preserved_metadata=preserved_metadata,
            tool_bindings_detected=tool_bindings_detected,
            skill_bindings_detected=skill_bindings_detected,
            memory_bindings_detected=memory_bindings_detected,
            approval_nodes_detected=approval_nodes_detected,
        )

    def _map_node(self, lg_node: LangGraphNode, mapping) -> LangflowNode:
        """Map a single LangGraph node to LangFlow node."""
        node_id = f"{lg_node.id}-{uuid.uuid4().hex[:8]}"
        
        # Build node data
        data = {
            "node": lg_node.data.copy() if lg_node.data else {},
        }
        
        # Add metadata from mapping
        if mapping.preserve_metadata:
            data["metadata"] = preserve_node_metadata(
                lg_node.model_dump(),
                mapping,
            )
        
        # Handle specific node types
        node_type = lg_node.type
        
        if node_type == "tool":
            data["tool_config"] = map_tool_to_langflow(lg_node.data)
        elif node_type == "skill":
            data["skill_config"] = map_skill_to_langflow(lg_node.data, lg_node.id)
        elif node_type == "memory":
            data["memory_config"] = map_memory_to_langflow(lg_node.data)
        elif node_type == "approval":
            data["approval_config"] = map_approval_to_langflow(lg_node.data, lg_node.id)
        
        return LangflowNode(
            id=node_id,
            type=mapping.langflow_type,
            position=self._next_position(),
            data=data,
        )


# ================================================
# SIMPLE COMPILE FUNCTION
# ================================================


def compile_langgraph_to_langflow(graph_definition: dict) -> dict:
    """
    Convenience function to compile a LangGraph-style dict to LangFlow.
    
    Example input:
    {
        "name": "My Workflow",
        "description": "A test workflow",
        "nodes": [
            {"id": "start", "type": "start", "data": {}, "metadata": {}},
            {"id": "llm_node", "type": "llm", "data": {"model": "gemma3:27b"}, "metadata": {}},
            {"id": "end", "type": "end", "data": {}, "metadata": {}},
        ],
        "edges": [
            {"source": "start", "target": "llm_node"},
            {"source": "llm_node", "target": "end"},
        ],
    }
    
    Returns dict with:
    - langflow_flow: Dict representation of LangFlow flow
    - success: bool
    - diagnostics: dict with warnings, counts, etc.
    """
    # Convert dict to LangGraphInput
    input_data = graph_definition.copy()
    
    nodes = [
        LangGraphNode(**n) for n in input_data.get("nodes", [])
    ]
    edges = [
        LangGraphEdge(**e) for e in input_data.get("edges", [])
    ]
    tool_bindings = [
        LangGraphToolBinding(**tb) for tb in input_data.get("tool_bindings", [])
    ]
    skill_bindings = [
        LangGraphSkillBinding(**sb) for sb in input_data.get("skill_bindings", [])
    ]
    memory_bindings = [
        LangGraphMemoryBinding(**mb) for mb in input_data.get("memory_bindings", [])
    ]
    approval_nodes = [
        LangGraphApprovalNode(**an) for an in input_data.get("approval_nodes", [])
    ]
    
    lg_input = LangGraphInput(
        name=input_data.get("name", "Unnamed"),
        description=input_data.get("description", ""),
        nodes=nodes,
        edges=edges,
        tool_bindings=tool_bindings,
        skill_bindings=skill_bindings,
        memory_bindings=memory_bindings,
        approval_nodes=approval_nodes,
        metadata=input_data.get("metadata", {}),
    )
    
    # Compile
    compiler = LangGraphToLangFlowCompiler()
    result = compiler.compile(lg_input)
    
    return {
        "langflow_flow": result.langflow_flow.model_dump(),
        "success": result.success,
        "nodes_mapped": result.nodes_mapped,
        "edges_mapped": result.edges_mapped,
        "warnings": [w.model_dump() for w in result.warnings],
        "unsupported_nodes": [u.model_dump() for u in result.unsupported_nodes],
        "unsupported_edges": [u.model_dump() for u in result.unsupported_edges],
        "preserved_metadata": result.preserved_metadata,
        "tool_bindings_detected": result.tool_bindings_detected,
        "skill_bindings_detected": result.skill_bindings_detected,
        "memory_bindings_detected": result.memory_bindings_detected,
        "approval_nodes_detected": result.approval_nodes_detected,
    }