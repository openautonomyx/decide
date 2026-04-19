"""
Framework Compiler Tests
Tests for LangGraph → LangFlow compiler.
"""
from app.framework.compiler import compile_langgraph_to_langflow, LangGraphToLangFlowCompiler
from app.framework.types import LangGraphInput, LangGraphNode, LangGraphEdge


class TestSimpleLinearGraph:
    """Test simple linear graph compilation."""

    def test_simple_linear(self):
        """Test simple linear graph."""
        graph = {
            "name": "Simple Linear",
            "nodes": [
                {"id": "start", "type": "start", "data": {}},
                {"id": "llm", "type": "llm", "data": {"model": "gpt-4"}},
                {"id": "end", "type": "end", "data": {}},
            ],
            "edges": [
                {"source": "start", "target": "llm"},
                {"source": "llm", "target": "end"},
            ],
        }
        
        result = compile_langgraph_to_langflow(graph)
        
        assert result["success"] == True
        assert result["nodes_mapped"] == 3
        assert result["edges_mapped"] == 2
        assert result["preserved_metadata"]["original_name"] == "Simple Linear"


class TestConditionalBranch:
    """Test graph with conditional branch."""

    def test_condition_branch(self):
        """Test graph with condition."""
        graph = {
            "name": "Condition Test",
            "nodes": [
                {"id": "start", "type": "start", "data": {}},
                {"id": "router", "type": "condition", "data": {}},
                {"id": "path_a", "type": "llm", "data": {"model": "gpt-4"}},
                {"id": "path_b", "type": "llm", "data": {"model": "claude"}},
                {"id": "end", "type": "end", "data": {}},
            ],
            "edges": [
                {"source": "start", "target": "router"},
                {"source": "router", "target": "path_a"},
                {"source": "router", "target": "path_b"},
                {"source": "path_a", "target": "end"},
                {"source": "path_b", "target": "end"},
            ],
        }
        
        result = compile_langgraph_to_langflow(graph)
        
        assert result["success"] == True
        assert result["nodes_mapped"] == 5
        assert result["edges_mapped"] == 5


class TestToolNode:
    """Test graph with tool node."""

    def test_tool_node(self):
        """Test graph with tool."""
        graph = {
            "name": "Tool Test",
            "nodes": [
                {"id": "start", "type": "start", "data": {}},
                {"id": "tool_node", "type": "tool", "data": {"tool_name": "search"}},
                {"id": "end", "type": "end", "data": {}},
            ],
            "edges": [
                {"source": "start", "target": "tool_node"},
                {"source": "tool_node", "target": "end"},
            ],
        }
        
        result = compile_langgraph_to_langflow(graph)
        
        assert result["success"] == True
        assert result["nodes_mapped"] == 3
        assert "search" in result["tool_bindings_detected"]


class TestSkillMetadata:
    """Test graph with skill metadata."""

    def test_skill_metadata(self):
        """Test skill preservation."""
        graph = {
            "name": "Skill Test",
            "nodes": [
                {"id": "start", "type": "start", "data": {}},
                {"id": "skill_node", "type": "skill", "data": {"skill_id": "skill-123", "skill_slug": "demo-skill"}},
                {"id": "end", "type": "end", "data": {}},
            ],
            "edges": [
                {"source": "start", "target": "skill_node"},
                {"source": "skill_node", "target": "end"},
            ],
        }
        
        result = compile_langgraph_to_langflow(graph)
        
        assert result["success"] == True
        assert "demo-skill" in result["skill_bindings_detected"]


class TestMemoryMetadata:
    """Test graph with memory metadata."""

    def test_memory_metadata(self):
        """Test memory preservation."""
        graph = {
            "name": "Memory Test",
            "nodes": [
                {"id": "start", "type": "start", "data": {}},
                {"id": "mem_node", "type": "memory", "data": {"memory_type": "context", "scope": "workflow"}},
                {"id": "end", "type": "end", "data": {}},
            ],
            "edges": [
                {"source": "start", "target": "mem_node"},
                {"source": "mem_node", "target": "end"},
            ],
        }
        
        result = compile_langgraph_to_langflow(graph)
        
        assert result["success"] == True
        assert "context:workflow" in result["memory_bindings_detected"]


class TestApprovalNode:
    """Test graph with approval node."""

    def test_approval_node(self):
        """Test approval node."""
        graph = {
            "name": "Approval Test",
            "nodes": [
                {"id": "start", "type": "start", "data": {}},
                {"id": "approval", "type": "approval", "data": {"policy_id": "policy-123", "risk_level": "high"}},
                {"id": "end", "type": "end", "data": {}},
            ],
            "edges": [
                {"source": "start", "target": "approval"},
                {"source": "approval", "target": "end"},
            ],
        }
        
        result = compile_langgraph_to_langflow(graph)
        
        assert result["success"] == True
        assert "policy-123" in result["approval_nodes_detected"]


class TestUnsupportedNode:
    """Test graph with unsupported node."""

    def test_unsupported_node_warning(self):
        """Test warning for unsupported node."""
        graph = {
            "name": "Unsupported Test",
            "nodes": [
                {"id": "start", "type": "start", "data": {}},
                {"id": "unknown", "type": "custom_unsupported_node", "data": {}},
                {"id": "end", "type": "end", "data": {}},
            ],
            "edges": [
                {"source": "start", "target": "unknown"},
                {"source": "unknown", "target": "end"},
            ],
        }
        
        result = compile_langgraph_to_langflow(graph)
        
        # Should produce warning but not crash
        assert result["nodes_mapped"] == 3
        assert len(result["warnings"]) > 0
        assert any("unsupported" in w.get("category", "") for w in result["warnings"])


class TestToolSkillApprovalMemory:
    """Test full graph with all features."""

    def test_full_graph(self):
        """Test graph with tool + skill + approval + memory."""
        graph = {
            "name": "Full Test",
            "description": "Complete workflow with all bindings",
            "nodes": [
                {"id": "start", "type": "start", "data": {}},
                {"id": "tool_node", "type": "tool", "data": {"tool_name": "search_api"}},
                {"id": "llm", "type": "llm", "data": {"model": "gpt-4"}},
                {"id": "skill", "type": "skill", "data": {"skill_id": "skill-1", "skill_slug": "analyze"}},
                {"id": "approval", "type": "approval", "data": {"policy_id": "policy-1", "risk_level": "medium"}},
                {"id": "memory", "type": "memory", "data": {"memory_type": "context", "scope": "workflow"}},
                {"id": "end", "type": "end", "data": {}},
            ],
            "edges": [
                {"source": "start", "target": "tool_node"},
                {"source": "tool_node", "target": "llm"},
                {"source": "llm", "target": "skill"},
                {"source": "skill", "target": "approval"},
                {"source": "approval", "target": "memory"},
                {"source": "memory", "target": "end"},
            ],
        }
        
        result = compile_langgraph_to_langflow(graph)
        
        assert result["success"] == True
        assert result["nodes_mapped"] == 7
        assert result["edges_mapped"] == 6
        assert "search_api" in result["tool_bindings_detected"]
        assert "analyze" in result["skill_bindings_detected"]
        assert "policy-1" in result["approval_nodes_detected"]
        assert "context:workflow" in result["memory_bindings_detected"]