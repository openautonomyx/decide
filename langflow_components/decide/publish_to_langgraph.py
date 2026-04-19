"""
PublishToLangGraph Component

Purpose:
    Compile and publish a Langflow workflow to LangGraph.
    Creates a compiled LangGraph that can be executed standalone.
    
Config Fields:
    - graph_name: Name for the published graph
    - checkpointer: Type of checkpointer to use (memory, sqlite, postgres)
    
Input:
    - graph_definition: The graph definition to compile
    
Output:
    - compiled_graph: The compiled LangGraph
    
Decide Concept Mapping:
    Integrates with LangGraph for agent execution.
    See: app/orchestrator/ - LangGraph integration
"""

import asyncio
from langflow.base import Component
from langflow.inputs import AnyInput, StrInput
from langflow.outputs import AnyOutput

from langflow_components.decide._client import get_decide_client


class PublishToLangGraph(Component):
    """Publish workflow to LangGraph."""
    
    display_name = "Publish to LangGraph"
    description = "Compiles and publishes workflow to LangGraph."
    documentation_urls = ["https://docs.decide.ai/langgraph"]
    
    inputs = [
        AnyInput(
            name="graph_definition",
            display_name="Graph Definition",
            required=True,
            info="Graph definition to compile (nodes and edges)",
        ),
    ]
    
    outputs = [
        AnyOutput(
            name="compiled_graph",
            display_name="Compiled Graph",
            info="Compiled LangGraph for execution",
        ),
    ]
    
    config_fields = [
        StrInput(
            name="graph_name",
            display_name="Graph Name",
            value="",
            info="Name for the published graph",
        ),
        StrInput(
            name="checkpointer",
            display_name="Checkpointer Type",
            value="memory",
            info="Type of checkpointer (memory, sqlite, postgres)",
        ),
    ]
    
    def run(self) -> None:
        """
        Compile workflow to LangGraph.
        
        Calls the Decide client to compile the graph definition.
        Falls back to stub if compilation fails.
        """
        graph_definition = self.inputs.graph_definition
        graph_name = self.config.graph_name
        checkpointer = self.config.checkpointer
        
        if not graph_name:
            graph_name = f"graph-{id(graph_definition) or 'untitled'}"
        
        # Get client and compile
        client = get_decide_client()
        
        try:
            response = asyncio.get_event_loop().run_until_complete(
                client.compile_langgraph(
                    graph_definition=graph_definition,
                    graph_name=graph_name,
                    checkpointer=checkpointer,
                )
            )
            self.re_outputs.compiled_graph.send(response)
        except Exception as e:
            # Fall back to stub
            self.re_outputs.compiled_graph.send({
                "graph_name": graph_name,
                "checkpointer": checkpointer,
                "nodes": graph_definition.get("nodes", []) if graph_definition else [],
                "edges": graph_definition.get("edges", []) if graph_definition else [],
                "status": "stub",
                "fallback": True,
                "error": str(e),
            })