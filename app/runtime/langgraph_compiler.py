"""
LangGraph Compiler - Langflow to LangGraph compilation

Compiles a Langflow workflow definition (nodes + edges) into a compiled
LangGraph StateGraph that can be executed with the LangGraph runtime.

Usage:
    compiler = LangGraphCompiler()
    graph = compiler.compile(
        graph_definition={
            "nodes": [{"id": "start", "type": "start"}, ...],
            "edges": [{"source": "start", "target": "end"}],
        },
        graph_name="my-workflow",
    )
"""
from typing import Any, Optional, TypedDict

from langgraph.graph import StateGraph, END


class LangGraphState(TypedDict, total=False):
    """Workflow state passed between nodes."""
    node_id: str
    node_type: str
    payload: dict
    outputs: dict
    errors: list[str]


class InMemoryChecker:
    """Simple in-memory checkpointer for langgraph >= 0.2."""
    
    def __init__(self):
        self._store: dict = {}
    
    def get(self, config: dict):
        key = config.get("configurable", {}).get("thread_id", "default")
        return self._store.get(key)
    
    def put(self, config: dict, checkpoint: Any):
        key = config.get("configurable", {}).get("thread_id", "default")
        self._store[key] = checkpoint


class LangGraphCompiler:
    """Compiles Langflow definitions to LangGraph."""

    # Node type to handler mapping
    NODE_HANDLERS = {
        "start": "_handle_start",
        "end": "_handle_end",
        "llm": "_handle_llm",
        "tool": "_handle_tool",
        "condition": "_handle_condition",
        "http": "_handle_http",
    }

    def __init__(self):
        self._checkpointer = InMemoryChecker()

    def _handle_start(self, state: LangGraphState) -> str:
        """Start node - always goes to first edge target."""
        return "continue"

    def _handle_end(self, state: LangGraphState) -> str:
        """End node - terminates the graph."""
        return END

    def _handle_llm(self, state: LangGraphState) -> str:
        """LLM node - calls model."""
        return "continue"

    def _handle_tool(self, state: LangGraphState) -> str:
        """Tool node - executes MCP tool."""
        return "continue"

    def _handle_condition(self, state: LangGraphState) -> str:
        """Condition node - branches based on logic."""
        return "continue"

    def _handle_http(self, state: LangGraphState) -> str:
        """HTTP node - makes external call."""
        return "continue"

    def _build_node_handler(self, node_type: str):
        """Create a handler function for a node type."""
        handler_name = self.NODE_HANDLERS.get(node_type, "_handle_generic")
        handler = getattr(self, handler_name, self._handle_generic)

        def node_handler(state: LangGraphState) -> str:
            node_id = state.get("node_id", "")
            node_type = state.get("node_type", "")
            # Execute node logic here
            state["outputs"] = {"node_id": node_id, "result": "done"}
            return handler(state)

        return node_handler

    def _handle_generic(self, state: LangGraphState) -> str:
        """Generic handler for unknown node types."""
        return "continue"

    def compile(
        self,
        graph_definition: dict,
        graph_name: str = "workflow",
        checkpointer: str = "memory",
    ) -> StateGraph:
        """
        Compile a Langflow workflow definition to LangGraph.

        Args:
            graph_definition: Dict with "nodes" and "edges" lists
            graph_name: Name for the compiled graph
            checkpointer: Type of checkpointer (memory, sqlite, postgres)

        Returns:
            Compiled StateGraph ready for execution
        """
        nodes = graph_definition.get("nodes", [])
        edges = graph_definition.get("edges", [])

        # Build edge map: source -> list of targets
        edge_map: dict[str, list[str]] = {}
        for edge in edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            if source not in edge_map:
                edge_map[source] = []
            edge_map[source].append(target)

        # Create the state graph
        workflow = StateGraph(LangGraphState)

        # Add nodes
        node_types = {}
        for node in nodes:
            node_id = node.get("id", "")
            node_type = node.get("type", "")
            node_types[node_id] = node_type

            # Add the node to the graph
            handler = self._build_node_handler(node_type)
            workflow.add_node(node_id, handler)

        # Add edges
        for node in nodes:
            node_id = node.get("id", "")
            targets = edge_map.get(node_id, [])

            for target in targets:
                if target in node_types:
                    workflow.add_edge(node_id, target)
                else:
                    # Edge to END if target doesn't exist as node
                    workflow.add_edge(node_id, END)

        # Set entry point
        start_nodes = [n for n in nodes if n.get("type") == "start"]
        if start_nodes:
            workflow.set_entry_point(start_nodes[0]["id"])

        # Set exit point
        end_nodes = [n for n in nodes if n.get("type") == "end"]
        if end_nodes:
            workflow.set_finish_point(end_nodes[0]["id"])

        # Compile the graph
        compiled = workflow.compile()
        return compiled

    def compile_and_run(
        self,
        graph_definition: dict,
        initial_state: dict,
        graph_name: str = "workflow",
        checkpointer: str = "memory",
    ) -> dict:
        """
        Compile and execute the workflow.

        Returns final state after execution.
        """
        graph = self.compile(graph_definition, graph_name, checkpointer)

        # Run the workflow
        result = graph.invoke(initial_state)
        return result

    def get_graph_config(
        self,
        checkpointer: str = "memory",
        configurable: Optional[dict] = None,
    ) -> dict:
        """Get configuration for graph execution."""
        config = {"configurable": configurable or {}}

        if checkpointer == "memory":
            config["checkpointer"] = InMemoryChecker()

        return config