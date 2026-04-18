"""
Orchestrator Tests
Phase 1 - Minimal in-process tests for orchestrator core
"""
import pytest
from datetime import datetime

from app.orchestrator.types import (
    OrchestratorRequest,
    TaskType,
    OrchestratorStatus,
    NextAction,
)
from app.orchestrator.engine import OrchestratorEngine, execute_request


class TestOrchestratorEngine:
    """Test orchestrator engine."""
    
    def test_execute_simple_request(self):
        """Test execution of a simple request."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="hello, how are you?",
        )
        
        result = execute_request(request)
        
        assert result.execution_request_id is not None
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.selected_runtime is not None
        assert result.next_action == NextAction.COMPLETE
    
    def test_execute_coding_request(self):
        """Test execution of a coding request."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="write a python function to calculate fibonacci",
        )
        
        result = execute_request(request)
        
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.selected_runtime is not None
        # Coding tasks should have task type detected
        assert result.metadata.get("task_type") == "coding"
    
    def test_execute_with_thread(self):
        """Test execution with existing thread."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            thread_id="existing-thread-123",
            request_text="continue working on the code",
        )
        
        result = execute_request(request)
        
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.branch_id is not None
    
    def test_execute_with_preferred_runtime(self):
        """Test execution with preferred runtime."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="analyze this data",
            preferred_runtime="langgraph",
        )
        
        result = execute_request(request)
        
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.selected_runtime == "langgraph"
    
    def test_execute_with_required_tools(self):
        """Test execution with required tools."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="search for information",
            required_tools=["search_web"],
        )
        
        result = execute_request(request)
        
        assert result.status == OrchestratorStatus.COMPLETED
        assert "search_web" in result.selected_tools
    
    def test_execute_with_required_skills(self):
        """Test execution with required skills."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="review this code",
            required_skills=["code_review"],
        )
        
        result = execute_request(request)
        
        assert result.status == OrchestratorStatus.COMPLETED
        assert "code_review" in result.selected_skills
    
    def test_execute_research_request(self):
        """Test execution of a research request."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="search for information about quantum computing",
        )
        
        result = execute_request(request)
        
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.metadata.get("task_type") == "research"
    
    def test_execute_autonomous_request(self):
        """Test execution of an autonomous request."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="analyze the system performance and optimize",
        )
        
        result = execute_request(request)
        
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.metadata.get("task_type") == "autonomous"
    
    def test_result_has_audit_refs(self):
        """Test that result includes audit refs."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="test request",
        )
        
        result = execute_request(request)
        
        assert "execution_id" in result.audit_refs
        assert "thread_id" in result.audit_refs
    
    def test_result_has_stages_completed(self):
        """Test that result includes completed stages."""
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="test request",
        )
        
        result = execute_request(request)
        
        assert len(result.stages_completed) > 0
        assert "intake" in result.stages_completed
        assert "complete" in result.stages_completed
    
    def test_engine_instance(self):
        """Test that engine can be instantiated directly."""
        engine = OrchestratorEngine()
        
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="simple test",
        )
        
        result = engine.execute(request)
        
        assert result.status == OrchestratorStatus.COMPLETED


class TestOrchestratorTypes:
    """Test orchestrator types."""
    
    def test_task_type_enum(self):
        """Test TaskType enum values."""
        assert TaskType.CODING.value == "coding"
        assert TaskType.CONVERSATION.value == "conversation"
        assert TaskType.AUTONOMOUS.value == "autonomous"
    
    def test_orchestrator_status_enum(self):
        """Test OrchestratorStatus enum values."""
        assert OrchestratorStatus.PENDING.value == "pending"
        assert OrchestratorStatus.RUNNING.value == "running"
        assert OrchestratorStatus.COMPLETED.value == "completed"
        assert OrchestratorStatus.FAILED.value == "failed"
    
    def test_next_action_enum(self):
        """Test NextAction enum values."""
        assert NextAction.COMPLETE.value == "complete"
        assert NextAction.AWAIT_INPUT.value == "await_input"
        assert NextAction.NEEDS_APPROVAL.value == "needs_approval"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])