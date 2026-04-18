"""
Orchestrator Phase 2 Tests
Phase 2 - Policy, guardrails, and approval tests
"""
import pytest
from datetime import datetime

from app.orchestrator.types import OrchestratorRequest, OrchestratorStatus, NextAction
from app.orchestrator.policy_gate import PolicyDecision, PolicyGate, get_policy_gate
from app.orchestrator.guardrails import GuardrailDecision, Guardrails, get_guardrails
from app.orchestrator.approval_gate import ApprovalStatus, ApprovalGate, get_approval_gate


class TestPolicyGate:
    """Test policy gate evaluation."""
    
    def test_allow_by_default(self):
        """Test that default is allow when no rules match."""
        gate = PolicyGate()
        
        from app.orchestrator.types import ExecutionState
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="hello, how are you?",
        )
        
        result = gate.evaluate(state, request)
        
        assert result["decision"] == PolicyDecision.ALLOW
        assert result["rule_matched"] is None
    
    def test_block_destructive_pattern(self):
        """Test that destructive patterns are blocked."""
        gate = PolicyGate()
        
        from app.orchestrator.types import ExecutionState
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="please delete all files with rm -rf",
        )
        
        result = gate.evaluate(state, request)
        
        assert result["decision"] == PolicyDecision.DENY
        assert "rm -rf" in result["reason"].lower() or "destructive" in result["reason"].lower()
    
    def test_require_approval_for_high_risk_tool(self):
        """Test that high-risk tools require approval."""
        gate = PolicyGate()
        
        from app.orchestrator.types import ExecutionState
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
            tools=["execute_code"],
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="execute some code",
            required_tools=["execute_code"],
        )
        
        result = gate.evaluate(state, request)
        
        assert result["decision"] == PolicyDecision.REQUIRE_APPROVAL
    
    def test_tools_evaluation(self):
        """Test tool-specific policy evaluation."""
        gate = PolicyGate()
        
        result = gate.evaluate_tools(["search_web", "read_file"])
        assert result["decision"] == PolicyDecision.ALLOW
        
        result = gate.evaluate_tools(["execute_code"])
        assert result["decision"] == PolicyDecision.REQUIRE_APPROVAL
    
    def test_get_rules(self):
        """Test getting policy rules."""
        gate = PolicyGate()
        rules = gate.get_rules()
        
        assert len(rules) > 0
        assert any(r["name"] == "block_destructive" for r in rules)


class TestGuardrails:
    """Test guardrail evaluation."""
    
    def test_allow_clean_input(self):
        """Test that clean input is allowed."""
        guardrails = Guardrails()
        
        result = guardrails.check_input("Hello, how are you today?")
        
        assert result.decision == GuardrailDecision.ALLOW
    
    def test_block_ssn_pattern(self):
        """Test that SSN patterns are blocked."""
        guardrails = Guardrails()
        
        result = guardrails.check_input("My SSN is 123-45-6789")
        
        assert result.decision == GuardrailDecision.BLOCK
    
    def test_block_credit_card(self):
        """Test that credit card patterns are blocked."""
        guardrails = Guardrails()
        
        result = guardrails.check_input("Card: 1234 5678 9012 3456")
        
        assert result.decision == GuardrailDecision.BLOCK
    
    def test_flag_confidential_keywords(self):
        """Test that confidential keywords are flagged."""
        guardrails = Guardrails()
        
        result = guardrails.check_input("Please don't share my api secret")
        
        assert result.decision == GuardrailDecision.FLAG
    
    def test_block_dangerous_tools(self):
        """Test that dangerous tools are blocked."""
        guardrails = Guardrails()
        
        results = guardrails.check_tools(["shell_exec", "read_file"])
        
        blocked = [r for r in results if r.decision == GuardrailDecision.BLOCK]
        assert len(blocked) > 0
        assert any("shell" in r.guardrail_name for r in blocked)
    
    def test_full_evaluation(self):
        """Test full guardrail evaluation."""
        guardrails = Guardrails()
        
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="search for information",
            required_tools=["search_web"],
        )
        
        result = guardrails.evaluate(
            request=request,
            tools=["search_web"],
            skills=["web_search"],
        )
        
        assert "decision" in result
        assert "results" in result
        assert result["blocked"] is False


class TestApprovalGate:
    """Test approval gate workflow."""
    
    def test_create_approval_request(self):
        """Test creating an approval request."""
        gate = ApprovalGate()
        
        approval = gate.create_approval_request(
            execution_id="exec-123",
            tenant_id="tenant-456",
            requested_by="user-789",
            reason="High-risk tool execution",
            details={"tool": "execute_code", "risk": "high"},
        )
        
        assert approval.approval_id is not None
        assert approval.execution_id == "exec-123"
        assert approval.status == ApprovalStatus.PENDING
    
    def test_approve_request(self):
        """Test approving a request."""
        gate = ApprovalGate()
        
        approval = gate.create_approval_request(
            execution_id="exec-123",
            tenant_id="tenant-456",
            requested_by="user-789",
            reason="Tool execution",
            details={},
        )
        
        result = gate.approve(approval.approval_id, "admin-user", "Approved for testing")
        
        assert result is True
        assert approval.status == ApprovalStatus.APPROVED
        assert approval.responded_by == "admin-user"
    
    def test_reject_request(self):
        """Test rejecting a request."""
        gate = ApprovalGate()
        
        approval = gate.create_approval_request(
            execution_id="exec-123",
            tenant_id="tenant-456",
            requested_by="user-789",
            reason="Tool execution",
            details={},
        )
        
        result = gate.reject(approval.approval_id, "admin-user", "Risk too high")
        
        assert result is True
        assert approval.status == ApprovalStatus.REJECTED
    
    def test_check_approval_status_pending(self):
        """Test checking approval status for pending."""
        gate = ApprovalGate()
        
        approval = gate.create_approval_request(
            execution_id="exec-123",
            tenant_id="tenant-456",
            requested_by="user-789",
            reason="Tool execution",
            details={},
        )
        
        status = gate.check_approval_status("exec-123")
        
        assert status["requires_approval"] is True
        assert status["approval_id"] == approval.approval_id
        assert status["status"] == "pending"
        assert status["can_proceed"] is False
    
    def test_check_approval_status_approved(self):
        """Test checking approval status after approval."""
        gate = ApprovalGate()
        
        approval = gate.create_approval_request(
            execution_id="exec-123",
            tenant_id="tenant-456",
            requested_by="user-789",
            reason="Tool execution",
            details={},
        )
        
        gate.approve(approval.approval_id, "admin-user")
        
        status = gate.check_approval_status("exec-123")
        
        assert status["requires_approval"] is True
        assert status["status"] == "approved"
        assert status["can_proceed"] is True
    
    def test_check_approval_status_no_approval(self):
        """Test checking approval status when none exists."""
        gate = ApprovalGate()
        
        status = gate.check_approval_status("exec-nonexistent")
        
        assert status["requires_approval"] is False
        assert status["can_proceed"] is True
    
    def test_list_pending(self):
        """Test listing pending approvals."""
        gate = ApprovalGate()
        
        gate.create_approval_request(
            execution_id="exec-1",
            tenant_id="tenant-1",
            requested_by="user-1",
            reason="Request 1",
            details={},
        )
        gate.create_approval_request(
            execution_id="exec-2",
            tenant_id="tenant-1",
            requested_by="user-2",
            reason="Request 2",
            details={},
        )
        
        pending = gate.list_pending("tenant-1")
        
        assert len(pending) == 2


class TestPolicyGateIntegration:
    """Integration tests for policy and guardrails."""
    
    def test_policy_integration_with_orchestrator(self):
        """Test policy gate integration."""
        gate = get_policy_gate()
        guardrails = get_guardrails()
        approval_gate = get_approval_gate()
        
        # Test allow flow
        from app.orchestrator.types import ExecutionState
        state = ExecutionState(
            execution_id="test-exec",
            tenant_id="test-tenant",
            user_id="test-user",
        )
        request = OrchestratorRequest(
            tenant_id="test-tenant",
            user_id="test-user",
            request_text="hello",
        )
        
        # Policy check
        policy_result = gate.evaluate(state, request)
        
        # Guardrail check
        guardrail_result = guardrails.evaluate(request)
        
        # Both should allow
        assert policy_result["decision"] == PolicyDecision.ALLOW
        assert guardrail_result["decision"] == GuardrailDecision.ALLOW
    
    def test_approval_gate_integration(self):
        """Test approval gate integration."""
        gate = get_approval_gate()
        
        # Create approval
        approval = gate.create_approval_request(
            execution_id="exec-test",
            tenant_id="tenant-test",
            requested_by="user-test",
            reason="Test approval",
            details={},
        )
        
        # Check status
        status = gate.check_approval_status("exec-test")
        
        assert status["requires_approval"] is True
        assert status["can_proceed"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])