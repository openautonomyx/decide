# LangGraph Compiler
# Compiler for exporting Decide workflows to LangGraph format
import uuid
from typing import Dict, Any, List, Optional
from app.integrations.frameworks.base import (
    BaseFrameworkAdapter,
    FrameworkType,
    FrameworkCapabilityProfile,
    FrameworkCompileResult,
)


# Mapping from Decide node types to LangGraph node types
DECIDE_TO_LANGGRAPH = {
    "input": "start",
    "output": "end",
    "agent": "agent",
    "tool": "tool",
    "conditional": "decision",
    "loop": "loop",
    "custom": "task",
}


class LangGraphCompiler(BaseFrameworkAdapter):
    """Compiler for LangGraph workflow export."""

    def get_framework_type(self) -> FrameworkType:
        return FrameworkType.LANGGRAPH

    def get_capabilities(self) -> FrameworkCapabilityProfile:
        return FrameworkCapabilityProfile(
            framework_type=FrameworkType.LANGGRAPH,
            supports_stateful_execution=True,
            supports_parallel_execution=True,
            supports_conditional_branches=True,
            supports_loops=True,
            supports_tool_binding=True,
            supports_human_in_loop=True,
            supports_memory_persistence=True,
            supports_streaming=True,
            supports_async=True,
            supports_multi_agent=True,
            supported_input_modes=["chat", "api", "stream"],
            supported_output_modes=["chat", "json", "stream"],
            version="0.1.0",
        )

    def validate_compile_input(self, workflow_data: Dict[str, Any]) -> List[str]:
        """Validate workflow data before compiling to LangGraph."""
        errors = []
        
        if not isinstance(workflow_data, dict):
            errors.append("Workflow data must be a dictionary")
            return errors
        
        # Check for required fields
        if "nodes" not in workflow_data:
            errors.append("Missing 'nodes' array in workflow data")
            
        if "edges" not in workflow_data:
            errors.append("Missing 'edges' array in workflow data")
            
        return errors

    async def import_workflow(
        self,
        raw_data: Dict[str, Any],
    ) -> FrameworkCompileResult:
        """Import from LangGraph format (not the primary use case)."""
        return FrameworkCompileResult(
            success=False,
            errors=["LangGraph is primarily an export target. Use LangflowAdapter for import."],
            target_framework=FrameworkType.LANGGRAPH,
        )

    async def compile_workflow(
        self,
        workflow_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ) -> FrameworkCompileResult:
        """Compile a Decide workflow to LangGraph format."""
        errors = self.validate_compile_input(workflow_data)
        if errors:
            return FrameworkCompileResult(
                success=False,
                errors=errors,
                target_framework=FrameworkType.LANGGRAPH,
            )

        warnings = []
        options = options or {}
        
        try:
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            metadata = workflow_data.get("metadata", {})
            
            # Build LangGraph state graph
            graph_nodes: Dict[str, Any] = {}
            graph_edges: List[Dict[str, Any]] = []
            
            # Process nodes
            for node in nodes:
                node_id = node.get("id")
                if not node_id:
                    continue
                    
                node_type = node.get("type", "custom")
                langgraph_type = DECIDE_TO_LANGGRAPH.get(node_type, "task")
                
                node_config = node.get("config", {})
                node_label = node.get("label", node_id)
                
                # Build the node specification
                graph_nodes[node_id] = {
                    "id": node_id,
                    "type": langgraph_type,
                    "label": node_label,
                    "config": node_config,
                    "tool_names": node_config.get("tools", []),
                    "has_condition": langgraph_type == "decision",
                    "is_loop": langgraph_type == "loop",
                }
            
            # Process edges
            for edge in edges:
                source = edge.get("source")
                target = edge.get("target")
                
                if not source or not target:
                    continue
                
                edge_type = edge.get("type", "normal")
                
                # Handle conditional edges
                if edge_type == "conditional":
                    graph_edges.append({
                        "from": source,
                        "to": target,
                        "condition": edge.get("condition"),
                    })
                else:
                    graph_edges.append({
                        "from": source,
                        "to": target,
                    })
            
            # Build the compiled LangGraph structure
            compiled = {
                "graph": {
                    "nodes": graph_nodes,
                    "edges": graph_edges,
                    "entry_point": nodes[0].get("id") if nodes else None,
                },
                "state_schema": options.get("state_schema"),
                "checkpoint": options.get("checkpoint", True),
                "stream_mode": options.get("stream_mode", "values"),
            }
            
            # Generate Python code for the workflow
            if options.get("generate_code", True):
                code = self._generate_langgraph_code(
                    graph_nodes,
                    graph_edges,
                    metadata,
                )
                compiled["generated_code"] = code
                
        except Exception as e:
            return FrameworkCompileResult(
                success=False,
                errors=[f"Compilation failed: {str(e)}"],
                target_framework=FrameworkType.LANGGRAPH,
            )

        return FrameworkCompileResult(
            success=True,
            compiled_output=compiled,
            warnings=warnings,
            target_framework=FrameworkType.LANGGRAPH,
            compile_metadata={
                "compiled_at": str(uuid.uuid4()),
                "nodes_count": len(graph_nodes),
                "edges_count": len(graph_edges),
            },
        )

    def _generate_langgraph_code(
        self,
        nodes: Dict[str, Any],
        edges: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> str:
        """Generate Python code for the LangGraph workflow."""
        lines = [
            "# Generated LangGraph workflow",
            "# DO NOT EDIT - Generated from Decide workflow",
            "",
            "from typing import TypedDict, Annotated",
            "from langgraph.graph import StateGraph, END",
            "from langgraph.prebuilt import tool_node",
            "",
            "",
            "class GraphState(TypedDict):",
            "    messages: Annotated[list, add]",
            "    workflow_context: dict",
            "    current_node: str",
            "",
        ]
        
        # Add node functions
        for node_id, node in nodes.items():
            node_type = node.get("type", "task")
            node_label = node.get("label", node_id)
            
            lines.append("")
            lines.append(f"def node_{node_id}(state: GraphState) -> GraphState:")
            lines.append(f"    # Node: {node_label}")
            lines.append("    # TODO: Implement node logic")
            lines.append("    return state")
        
        # Build the graph
        lines.append("")
        lines.append("")
        lines.append("def create_graph():")
        lines.append("    workflow = StateGraph(GraphState)")
        
        # Add nodes to graph
        for node_id in nodes.keys():
            lines.append(f"    workflow.add_node('{node_id}', node_{node_id})")
        
        # Add edges
        for edge in edges:
            from_node = edge.get("from")
            to_node = edge.get("to")
            condition = edge.get("condition")
            
            if from_node and to_node:
                if condition:
                    lines.append(
                        f"    workflow.add_conditional_edges("
                        f"'{from_node}', {condition}, ['{to_node}'])"
                    )
                else:
                    lines.append(f"    workflow.add_edge('{from_node}', '{to_node}')")
        
        # Set entry and compile
        if nodes:
            first_node = list(nodes.keys())[0]
            lines.append(f"    workflow.set_entry_point('{first_node}')")
        
        lines.append("    workflow.set_finish_point(END)")
        lines.append("    return workflow.compile()")
        
        return "\n".join(lines)