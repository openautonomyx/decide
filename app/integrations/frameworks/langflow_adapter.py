# Langflow Adapter
# Adapter for importing workflows from Langflow format into Decide
import uuid
from typing import Dict, Any, List, Optional
from app.integrations.frameworks.base import (
    BaseFrameworkAdapter,
    FrameworkType,
    FrameworkCapabilityProfile,
    FrameworkImportResult,
)

# Langflow node types we can map to Decide
LANGFLOW_NODE_TYPES = {
    "ChatInput": "input",
    "ChatOutput": "output", 
    "Agent": "agent",
    "Tool": "tool",
    "Condition": "conditional",
    "Loop": "loop",
    "Merge": "merge",
    "Split": "split",
    "Webhook": "webhook",
    "PromptTemplate": "prompt",
    "StructuredOutput": "structured_output",
}


class LangflowAdapter(BaseFrameworkAdapter):
    """Adapter for Langflow workflow import."""

    def get_framework_type(self) -> FrameworkType:
        return FrameworkType.LANGFLOW

    def get_capabilities(self) -> FrameworkCapabilityProfile:
        return FrameworkCapabilityProfile(
            framework_type=FrameworkType.LANGFLOW,
            supports_stateful_execution=True,
            supports_parallel_execution=True,
            supports_conditional_branches=True,
            supports_tool_binding=True,
            supports_human_in_loop=True,
            supports_streaming=True,
            supports_async=True,
            supported_input_modes=["chat", "api", "webhook"],
            supported_output_modes=["chat", "json", "stream"],
            version="1.0.0",
        )

    def validate_import(self, raw_data: Dict[str, Any]) -> List[str]:
        """Validate Langflow export format."""
        errors = []
        
        # Check top-level structure
        if not isinstance(raw_data, dict):
            errors.append("Root must be a dictionary")
            return errors
        
        # Check for required fields
        if "flows" not in raw_data and "flow" not in raw_data:
            errors.append("Missing 'flows' or 'flow' key")
            return errors
        
        # Check flows structure
        flows = raw_data.get("flows", raw_data.get("flow", []))
        if not isinstance(flows, list):
            errors.append("'flows' must be an array")
            return errors
        
        for i, flow in enumerate(flows):
            if not isinstance(flow, dict):
                errors.append(f"Flow at index {i} must be a dictionary")
                continue
                
            if "nodes" not in flow:
                errors.append(f"Flow at index {i} missing 'nodes' array")
                continue
                
            nodes = flow.get("nodes", [])
            if not isinstance(nodes, list):
                errors.append(f"Flow at index {i} 'nodes' must be an array")
                
        return errors

    async def import_workflow(self, raw_data: Dict[str, Any]) -> FrameworkImportResult:
        """Import a workflow from Langflow format."""
        errors = self.validate_import(raw_data)
        if errors:
            return FrameworkImportResult(
                success=False,
                errors=errors,
                source_framework=FrameworkType.LANGFLOW,
            )

        warnings = []
        workflow_data = {"nodes": [], "edges": [], "metadata": {}}
        
        try:
            flows = raw_data.get("flows", raw_data.get("flow", []))
            
            for flow in flows:
                flow_id = flow.get("id", str(uuid.uuid4()))
                flow_name = flow.get("name", "Imported Flow")
                
                # Import nodes
                for node in flow.get("nodes", []):
                    node_id = node.get("id", str(uuid.uuid4()))
                    node_type = node.get("type", "Unknown")
                    
                    # Map Langflow node type to Decide node type
                    decide_node_type = LANGFLOW_NODE_TYPES.get(node_type, "custom")
                    
                    # Map node data
                    node_data = node.get("data", {})
                    properties = node_data.get("node", {}).get("base", {})
                    
                    node_obj = {
                        "id": node_id,
                        "type": decide_node_type,
                        "label": properties.get("label", node.get("label", node_type)),
                        "config": properties.get("config", {}),
                        "position": node.get("position", {}),
                        "metadata": {
                            "source_flow_id": flow_id,
                            "source_node_type": node_type,
                        },
                    }
                    workflow_data["nodes"].append(node_obj)
                
                # Import edges (connections between nodes)
                for edge in flow.get("edges", []):
                    edge_obj = {
                        "id": edge.get("id", str(uuid.uuid4())),
                        "source": edge.get("source"),
                        "target": edge.get("target"),
                        "source_handle": edge.get("sourceHandle"),
                        "target_handle": edge.get("targetHandle"),
                        "type": edge.get("type", "default"),
                    }
                    workflow_data["edges"].append(edge_obj)
                
                # Import metadata
                if "metadata" in flow:
                    workflow_data["metadata"][flow_id] = flow.get("metadata", {})
                
                workflow_data["metadata"]["name"] = flow_name
                workflow_data["metadata"]["source_flow_id"] = flow_id
                
        except Exception as e:
            return FrameworkImportResult(
                success=False,
                errors=[f"Import failed: {str(e)}"],
                source_framework=FrameworkType.LANGFLOW,
            )

        return FrameworkImportResult(
            success=True,
            workflow_data=workflow_data,
            warnings=warnings,
            source_framework=FrameworkType.LANGFLOW,
            import_metadata={
                "imported_at": str(uuid.uuid4()),
                "flows_count": len(flows),
                "nodes_count": len(workflow_data["nodes"]),
                "edges_count": len(workflow_data["edges"]),
            },
        )
    
    async def compile_workflow(
        self,
        workflow_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ) -> FrameworkImportResult:
        """Compile to Langflow format (export path)."""
        # This would be the export path - Langflow is primarily an import target
        return FrameworkImportResult(
            success=False,
            errors=["Langflow is an import-only target. Use LangGraph for export."],
            source_framework=FrameworkType.LANGFLOW,
        )