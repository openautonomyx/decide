"""
Guardrails
Phase 2 - Input/output guardrail checks

Evaluates guardrails for:
- Request text (input)
- Selected tools (action)
- Selected skills (capability)
- Output (future: response validation)
"""
import logging
import re
from typing import Optional, Dict, Any, List
from enum import Enum

from app.orchestrator.types import ExecutionState, OrchestratorRequest

logger = logging.getLogger(__name__)


class GuardrailDecision(str, Enum):
    """Guardrail evaluation decisions"""
    ALLOW = "allow"
    BLOCK = "block"
    MASK = "mask"
    FLAG = "flag"


class GuardrailResult:
    """Guardrail evaluation result"""
    def __init__(
        self,
        decision: GuardrailDecision,
        reason: str,
        guardrail_name: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.decision = decision
        self.reason = reason
        self.guardrail_name = guardrail_name
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "guardrail_name": self.guardrail_name,
            "details": self.details,
        }


class Guardrails:
    """
    Guardrail evaluation service.
    
    Evaluates input/output against configured guardrails.
    """
    
    def __init__(self):
        self._input_rules: List[Dict[str, Any]] = []
        self._tool_rules: List[Dict[str, Any]] = []
        self._skill_rules: List[Dict[str, Any]] = []
        self._output_rules: List[Dict[str, Any]] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default guardrail rules."""
        # Input: Block PII patterns
        self._input_rules.append({
            "name": "block_sensitive_data",
            "pattern": r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            "action": GuardrailDecision.BLOCK,
            "reason": "SSN pattern detected",
        })
        
        self._input_rules.append({
            "name": "block_credit_card",
            "pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            "action": GuardrailDecision.BLOCK,
            "reason": "Credit card pattern detected",
        })
        
        # Input: Flag sensitive topics
        self._input_rules.append({
            "name": "flag_confidential",
            "keywords": ["confidential", "private key", "api secret", "password"],
            "action": GuardrailDecision.FLAG,
            "reason": "Sensitive keyword detected",
        })
        
        # Tool: Block dangerous tools in prod
        self._tool_rules.append({
            "name": "block_shell_exec",
            "tool": "shell_exec",
            "action": GuardrailDecision.BLOCK,
            "reason": "Shell execution not allowed",
        })
        
        self._tool_rules.append({
            "name": "block_file_delete",
            "tool": "delete_file",
            "action": GuardrailDecision.BLOCK,
            "reason": "File deletion not allowed",
        })
        
        # Skill: Flag high-capability skills
        self._skill_rules.append({
            "name": "flag_admin_skill",
            "skill": "admin_access",
            "action": GuardrailDecision.FLAG,
            "reason": "Admin skill flagged for review",
        })
    
    def check_input(self, text: str) -> GuardrailResult:
        """
        Check input text against guardrails.
        
        Returns first matching guardrail result.
        """
        for rule in self._input_rules:
            # Check pattern
            if "pattern" in rule:
                if re.search(rule["pattern"], text, re.IGNORECASE):
                    return GuardrailResult(
                        decision=rule["action"],
                        reason=rule["reason"],
                        guardrail_name=rule["name"],
                        details={"matched": "pattern"},
                    )
            
            # Check keywords
            if "keywords" in rule:
                text_lower = text.lower()
                for keyword in rule["keywords"]:
                    if keyword in text_lower:
                        return GuardrailResult(
                            decision=rule["action"],
                            reason=rule["reason"],
                            guardrail_name=rule["name"],
                            details={"keyword": keyword},
                        )
        
        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            reason="No guardrails triggered",
            guardrail_name=None,
        )
    
    def check_tools(self, tools: List[str]) -> List[GuardrailResult]:
        """
        Check tools against guardrails.
        
        Returns list of guardrail results.
        """
        results = []
        
        for tool in tools:
            for rule in self._tool_rules:
                if rule.get("tool") == tool:
                    results.append(GuardrailResult(
                        decision=rule["action"],
                        reason=rule["reason"],
                        guardrail_name=rule["name"],
                        details={"tool": tool},
                    ))
        
        return results
    
    def check_skills(self, skills: List[str]) -> List[GuardrailResult]:
        """
        Check skills against guardrails.
        
        Returns list of guardrail results.
        """
        results = []
        
        for skill in skills:
            for rule in self._skill_rules:
                if rule.get("skill") == skill:
                    results.append(GuardrailResult(
                        decision=rule["action"],
                        reason=rule["reason"],
                        guardrail_name=rule["name"],
                        details={"skill": skill},
                    ))
        
        return results
    
    def check_output(self, output: str) -> GuardrailResult:
        """
        Check output against guardrails.
        
        Returns first matching guardrail result.
        """
        # Same logic as input for now
        return self.check_input(output)
    
    def evaluate(
        self,
        request: OrchestratorRequest,
        tools: Optional[List[str]] = None,
        skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate all guardrails.
        
        Returns aggregated result.
        """
        all_results = []
        
        # Check input
        input_result = self.check_input(request.request_text)
        if input_result.decision != GuardrailDecision.ALLOW:
            all_results.append(input_result.to_dict())
        
        # Check tools
        if tools:
            tool_results = self.check_tools(tools)
            for result in tool_results:
                if result.decision != GuardrailDecision.ALLOW:
                    all_results.append(result.to_dict())
        
        # Check skills
        if skills:
            skill_results = self.check_skills(skills)
            for result in skill_results:
                if result.decision != GuardrailDecision.ALLOW:
                    all_results.append(result.to_dict())
        
        # Determine overall decision
        blocked = any(r["decision"] == GuardrailDecision.BLOCK.value for r in all_results)
        flagged = any(r["decision"] == GuardrailDecision.FLAG.value for r in all_results)
        
        if blocked:
            return {
                "decision": GuardrailDecision.BLOCK,
                "results": all_results,
                "blocked": True,
                "flagged": False,
            }
        
        if flagged:
            return {
                "decision": GuardrailDecision.FLAG,
                "results": all_results,
                "blocked": False,
                "flagged": True,
            }
        
        return {
            "decision": GuardrailDecision.ALLOW,
            "results": all_results,
            "blocked": False,
            "flagged": False,
        }


# Global instance
_guardrails: Optional[Guardrails] = None


def get_guardrails() -> Guardrails:
    """Get global guardrails service."""
    global _guardrails
    if _guardrails is None:
        _guardrails = Guardrails()
    return _guardrails


__all__ = [
    "GuardrailDecision",
    "GuardrailResult",
    "Guardrails",
    "get_guardrails",
]