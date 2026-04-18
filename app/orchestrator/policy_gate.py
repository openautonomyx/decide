"""
Policy Gate
Phase 2 - Policy evaluation before execution

Evaluates policy hooks before runtime execution:
- allow: Proceed with execution
- deny: Block execution
- require_approval: Pause for human approval
- escalate: Route to admin review
"""
import logging
from typing import Optional, Dict, Any, List
from enum import Enum

from app.orchestrator.types import ExecutionState, OrchestratorRequest

logger = logging.getLogger(__name__)


class PolicyDecision(str, Enum):
    """Policy evaluation decisions"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    ESCALATE = "escalate"


class PolicyGate:
    """
    Policy gate evaluates execution policies before runtime.
    
    Uses a simple rule-based approach (extensible to OPA).
    """
    
    def __init__(self):
        self._rules: List[Dict[str, Any]] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default policy rules."""
        # High-risk tool rules
        self.add_rule(
            name="block_execute_code",
            condition={
                "tool": "execute_code",
                "risk": "high",
            },
            decision=PolicyDecision.REQUIRE_APPROVAL,
            reason="High-risk tool requires approval",
        )
        
        # Block dangerous commands
        self.add_rule(
            name="block_destructive",
            condition={
                "request_pattern": "rm -rf|delete all|drop table",
            },
            decision=PolicyDecision.DENY,
            reason="Destructive commands blocked",
        )
        
        # Rate limit check (placeholder)
        self.add_rule(
            name="rate_limit_check",
            condition={
                "tenant_quota_exceeded": True,
            },
            decision=PolicyDecision.ESCALATE,
            reason="Tenant quota exceeded",
        )
        
        # Tenant policy override
        self.add_rule(
            name="tenant_policy_block",
            condition={
                "tenant_policy": "deny_all",
            },
            decision=PolicyDecision.DENY,
            reason="Tenant policy denies all",
        )
    
    def add_rule(
        self,
        name: str,
        condition: Dict[str, Any],
        decision: PolicyDecision,
        reason: str,
    ):
        """Add a policy rule."""
        self._rules.append({
            "name": name,
            "condition": condition,
            "decision": decision,
            "reason": reason,
        })
    
    def evaluate(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ) -> Dict[str, Any]:
        """
        Evaluate policies for execution.
        
        Returns:
            {
                "decision": PolicyDecision,
                "reason": str,
                "rule_matched": str,
                "details": dict,
            }
        """
        # Check each rule
        for rule in self._rules:
            match = self._check_rule(rule, state, request)
            if match:
                logger.info(f"Policy rule matched: {rule['name']} -> {rule['decision'].value}")
                
                return {
                    "decision": rule["decision"],
                    "reason": rule["reason"],
                    "rule_matched": rule["name"],
                    "details": match,
                }
        
        # Default: allow
        return {
            "decision": PolicyDecision.ALLOW,
            "reason": "No policy rules matched",
            "rule_matched": None,
            "details": {},
        }
    
    def _check_rule(
        self,
        rule: Dict[str, Any],
        state: ExecutionState,
        request: OrchestratorRequest,
    ) -> Optional[Dict[str, Any]]:
        """Check if a rule matches the current execution context."""
        condition = rule["condition"]
        
        # Check tool-based rules
        if "tool" in condition:
            tool = condition.get("tool")
            if tool in state.tools or tool in request.required_tools:
                return {"tool": tool}
        
        # Check request pattern (simple keyword check)
        if "request_pattern" in condition:
            pattern = condition["request_pattern"]
            request_lower = request.request_text.lower()
            if any(p in request_lower for p in pattern.split("|")):
                return {"pattern": pattern}
        
        # Check tenant quota (placeholder)
        if "tenant_quota_exceeded" in condition:
            # TODO: Check actual tenant quota
            if state.metadata.get("quota_exceeded"):
                return {"quota": "exceeded"}
        
        # Check tenant policy (placeholder)
        if "tenant_policy" in condition:
            # TODO: Fetch from PolicyService
            policy = state.metadata.get("tenant_policy")
            if policy == condition["tenant_policy"]:
                return {"policy": policy}
        
        return None
    
    def evaluate_tools(
        self,
        tools: List[str],
    ) -> Dict[str, Any]:
        """
        Evaluate tool policy specifically.
        
        Returns policy decision for tool list.
        """
        # High-risk tools that require approval
        approval_required_tools = {"execute_code", "shell_exec", "database_write"}
        
        for tool in tools:
            if tool in approval_required_tools:
                return {
                    "decision": PolicyDecision.REQUIRE_APPROVAL,
                    "reason": f"Tool '{tool}' requires approval",
                    "rule_matched": "tool_approval_required",
                    "details": {"tool": tool},
                }
        
        return {
            "decision": PolicyDecision.ALLOW,
            "reason": "All tools approved",
            "rule_matched": None,
            "details": {},
        }
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """Get all policy rules."""
        return self._rules.copy()


# Global instance
_policy_gate: Optional[PolicyGate] = None


def get_policy_gate() -> PolicyGate:
    """Get global policy gate."""
    global _policy_gate
    if _policy_gate is None:
        _policy_gate = PolicyGate()
    return _policy_gate


__all__ = [
    "PolicyDecision",
    "PolicyGate",
    "get_policy_gate",
]