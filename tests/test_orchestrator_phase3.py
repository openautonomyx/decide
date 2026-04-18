"""
Orchestrator Phase 3 Tests
Phase 3 - Runtime invocation and adapter tests
"""
import pytest
from datetime import datetime

from app.orchestrator.types import OrchestratorRequest, OrchestratorStatus, NextAction, ExecutionState
from app.orchestrator.runtime_invoker import RuntimeOutput, RuntimeInvoker, get_runtime_invoker
from app.orchestrator.runtime_adapters import (
    OpenAIAgentsAdapter,
    ClaudeWorkerAdapter,
    GenericWorkerAdapter,
    get_adapter,
)


class TestRuntimeOutput:
    """Test RuntimeOutput."""
    
    def test_runtime_output_creation(self):
        """Test creating RuntimeOutput."""
        output = RuntimeOutput(
            status="success",
            output_text="test output",
            usage={"input_tokens": 100, "output_tokens": 50},
        )
        
        assert output.status == "success"
        assert output.output_text == "test output"
        assert output.usage["input_tokens"] == 100
    
    def test_runtime_output_to_dict(self):
        """Test RuntimeOutput to dict."""
        output = RuntimeOutput(
            status="success",
            output_text="test",
        )
        
        d = output.to_dict()
        assert d["status"] == "success"
        assert d["output_text"] == "test"


class TestRuntimeAdapters:
    """Test runtime adapters."""
    
    def test_generic_adapter_execute(self):
        """Test generic adapter execution."""
        adapter = GenericWorkerAdapter()
        
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="hello world",
        )
        
        output = adapter.execute(state, request)
        
        assert output.status == "success"
        assert "hello" in output.output_text.lower()
        assert output.raw_ref["adapter"] == "generic_worker"
    
    def test_generic_adapter_fallback(self):
        """Test generic adapter fallback."""
        adapter = GenericWorkerAdapter()
        
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="fallback test",
        )
        
        output = adapter.execute_fallback(request)
        
        assert output.status == "success"
    
    def test_openai_adapter_stub(self):
        """Test OpenAI adapter stub response."""
        adapter = OpenAIAgentsAdapter()
        
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="test request",
        )
        
        output = adapter.execute(state, request)
        
        assert output.status == "success"
        assert "stub" in output.warnings[0].lower()
    
    def test_claude_adapter_stub(self):
        """Test Claude adapter stub response."""
        adapter = ClaudeWorkerAdapter()
        
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="test request",
        )
        
        output = adapter.execute(state, request)
        
        assert output.status == "success"
        assert "stub" in output.warnings[0].lower()
    
    def test_get_adapter(self):
        """Test getting adapter by runtime ID."""
        adapter = get_adapter("openai_agents")
        assert adapter is not None
        assert isinstance(adapter, OpenAIAgentsAdapter)
        
        adapter = get_adapter("claude_agent")
        assert isinstance(adapter, ClaudeWorkerAdapter)
        
        adapter = get_adapter("unknown")
        assert isinstance(adapter, GenericWorkerAdapter)


class TestRuntimeInvoker:
    """Test runtime invoker."""
    
    def test_invoker_creation(self):
        """Test creating invoker."""
        invoker = RuntimeInvoker()
        runtimes = invoker.get_available_runtimes()
        
        assert "openai_agents" in runtimes
        assert "claude_agent" in runtimes
        assert "generic" in runtimes
    
    def test_invoker_generic_runtime(self):
        """Test invoking generic runtime."""
        invoker = RuntimeInvoker()
        
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="invoke test",
        )
        
        output = invoker.invoke("generic", state, request)
        
        assert output.status == "success"
        assert output.output_text is not None
    
    def test_invoker_unknown_runtime(self):
        """Test invoking unknown runtime falls back to generic."""
        invoker = RuntimeInvoker()
        
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="fallback test",
        )
        
        output = invoker.invoke("unknown-runtime", state, request)
        
        assert output.status == "success"
    
    def test_invoker_returns_normalized_output(self):
        """Test invoker returns normalized output."""
        invoker = get_runtime_invoker()
        
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="normalized output test",
        )
        
        output = invoker.invoke("generic", state, request)
        
        assert hasattr(output, "status")
        assert hasattr(output, "output_text")
        assert hasattr(output, "usage")
        assert hasattr(output, "tool_calls")
        assert hasattr(output, "warnings")
        assert hasattr(output, "raw_ref")
    
    def test_invoker_captures_usage(self):
        """Test invoker captures token usage."""
        invoker = RuntimeInvoker()
        
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="test message",
        )
        
        output = invoker.invoke("generic", state, request)
        
        assert output.usage["input_tokens"] > 0
        assert output.usage["output_tokens"] > 0
    
    def test_invoker_adds_raw_ref(self):
        """Test invoker adds raw reference for debugging."""
        invoker = RuntimeInvoker()
        
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="debug test",
        )
        
        output = invoker.invoke("generic", state, request)
        
        assert output.raw_ref is not None
        assert "adapter" in output.raw_ref


class TestAdapterRegistration:
    """Test adapter registration."""
    
    def test_custom_adapter_registration(self):
        """Test registering custom adapter."""
        invoker = RuntimeInvoker()
        
        class CustomAdapter:
            def execute(self, state, request):
                return RuntimeOutput(status="success", output_text="custom")
        
        invoker.register_adapter("custom", CustomAdapter())
        
        runtimes = invoker.get_available_runtimes()
        assert "custom" in runtimes


class TestNormalizedOutput:
    """Test normalized output shape."""
    
    def test_output_has_all_fields(self):
        """Test output has all required fields."""
        output = RuntimeOutput(
            status="success",
            output_text="test",
            structured_output={"key": "value"},
            usage={"input_tokens": 100, "output_tokens": 50},
            tool_calls=[{"name": "tool1"}],
            warnings=["warning1"],
            raw_ref={"ref": "value"},
        )
        
        d = output.to_dict()
        
        assert "status" in d
        assert "output_text" in d
        assert "structured_output" in d
        assert "usage" in d
        assert "tool_calls" in d
        assert "warnings" in d
        assert "raw_ref" in d
    
    def test_output_defaults(self):
        """Test output has sensible defaults."""
        output = RuntimeOutput(status="success")
        
        assert output.output_text == ""
        assert output.structured_output is None
        assert output.usage == {"input_tokens": 0, "output_tokens": 0}
        assert output.tool_calls == []
        assert output.warnings == []
        assert output.raw_ref is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])