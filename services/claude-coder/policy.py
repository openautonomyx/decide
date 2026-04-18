"""
Policy resolution layer combining platform defaults and tenant/user overrides.
"""
import time
from typing import Any, Dict, List, Optional

try:
    from tenant_policy import TenantPolicy
except ImportError:
    TenantPolicy = None


class PolicyResolver:
    """
    Resolves routing policy with support for:
    - Platform defaults (from policies.yaml)
    - Tenant overrides
    - User/license overrides
    """
    
    def __init__(self, registry: Dict[str, Any], policies: Dict[str, Any]):
        self.registry = registry
        self.policies = policies.get("routing_policies", [])
    
    def resolve(
        self,
        request: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Resolve effective policy for a request.
        
        Priority: user_license > tenant_id > platform defaults
        """
        metadata = metadata or {}
        
        # Start with request params as base
        effective = {
            **request,
            "tenant_id": metadata.get("tenant_id"),
            "user_id": metadata.get("user_id"),
            "user_license": metadata.get("user_license"),
            "task_risk": metadata.get("task_risk"),
            "budget_tier": metadata.get("budget_tier"),
        }
        
        # Resolve overrides based on license tier
        license_tier = metadata.get("user_license", "")
        if license_tier:
            overrides = self._get_license_overrides(license_tier)
            effective = {**effective, **overrides}
        
        # Resolve overrides based on tenant
        tenant_id = metadata.get("tenant_id", "")
        if tenant_id:
            overrides = self._get_tenant_overrides(tenant_id)
            effective = {**effective, **overrides}
        
        return effective
    
    def _get_license_overrides(self, license_tier: str) -> Dict[str, Any]:
        """Get policy overrides for a license tier."""
        # In production, load from database or config
        # For now, simple tier-based defaults
        tier_overrides = {
            "enterprise": {
                "default_quality": "premium",
                "allow_fallback": True,
                "max_retries": 3,
                "allowed_backends": ["claude_premium", "devstral_local", "openai_coding"],
                "denied_backends": [],
                "premium_allowed": True,
                "approval_required_for": [],
            },
            "pro": {
                "default_quality": "standard",
                "allow_fallback": True,
                "max_retries": 2,
                "allowed_backends": ["devstral_local", "openai_coding"],
                "denied_backends": ["claude_premium"],
                "premium_allowed": False,
                "approval_required_for": ["claude_premium"],
            },
            "free": {
                "default_quality": "basic",
                "allow_fallback": False,
                "max_retries": 0,
                "allowed_backends": ["devstral_local"],
                "denied_backends": ["claude_premium", "openai_coding"],
                "premium_allowed": False,
                "approval_required_for": ["devstral_local"],
            },
        }
        return tier_overrides.get(license_tier, {})
    
    def _get_tenant_overrides(self, tenant_id: str) -> Dict[str, Any]:
        """Get policy overrides for a tenant from storage."""
        if not tenant_id or TenantPolicy is None:
            return {}
        
        # Load tenant policy from storage
        tenant = TenantPolicy.load(tenant_id)
        if not tenant or not tenant.enabled:
            return {}
        
        return {
            "allowed_backends": tenant.allowed_backends,
            "denied_backends": tenant.denied_backends,
            "default_quality": tenant.quality_default,
            "allow_fallback": tenant.allow_fallback,
            "max_retries": tenant.max_retries,
            "approval_required_for": tenant.approval_required_for,
            "max_budget_monthly": tenant.max_budget_monthly,
            "max_requests_per_hour": tenant.max_requests_per_hour,
            "capability_policies": tenant.capability_policies,
        }
    
    def get_matching_policy(
        self,
        request: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Find the first policy that matches request conditions."""
        for policy in self.policies:
            conditions = policy.get("when", {})
            if all(
                request.get(key) == value 
                for key, value in conditions.items()
            ):
                return policy
        return None


class EntitlementResolver:
    """
    Resolves entitlement checks for backend access.
    Combines platform defaults, tenant overrides, and license tier.
    """
    
    def __init__(self, policy_resolver: PolicyResolver):
        self.policy_resolver = policy_resolver
    
    def check_entitlement(
        self,
        backend_id: str,
        request: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check if backend is entitled for request.
        Returns: {"allowed": bool, "reason": str, "denied_backends": List[str]}
        """
        effective = self.policy_resolver.resolve(request, metadata)
        
        allowed_backends = effective.get("allowed_backends", [])
        denied_backends = effective.get("denied_backends", [])
        
        # Check explicit deny
        if backend_id in denied_backends:
            return {
                "allowed": False,
                "reason": f"Backend {backend_id} denied by policy",
                "denied_backends": denied_backends,
                "entitlement_tier": metadata.get("user_license", "unknown") if metadata else "unknown",
            }
        
        # Check explicit allow
        if allowed_backends and backend_id not in allowed_backends:
            return {
                "allowed": False,
                "reason": f"Backend {backend_id} not in allowed list {allowed_backends}",
                "denied_backends": denied_backends,
                "entitlement_tier": metadata.get("user_license", "unknown") if metadata else "unknown",
            }
        
        # Default allow if no restrictions
        return {
            "allowed": True,
            "reason": "Entitlement check passed",
            "denied_backends": denied_backends,
            "entitlement_tier": metadata.get("user_license", "unknown") if metadata else "unknown",
        }
    
    def get_entitlements(
        self,
        request: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get all entitlements for a request."""
        effective = self.policy_resolver.resolve(request, metadata)
        
        return {
            "allowed_backends": effective.get("allowed_backends", []),
            "denied_backends": effective.get("denied_backends", []),
            "premium_allowed": effective.get("premium_allowed", False),
            "entitlement_tier": metadata.get("user_license", "free") if metadata else "free",
        }


class ApprovalChecker:
    """
    Determines if a request requires human approval.
    """
    
    def __init__(self, policy_resolver: PolicyResolver):
        self.policy_resolver = policy_resolver
    
    def check_approval_required(
        self,
        request: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        approval_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check if approval is required for this request.
        
        Approval is required when:
        1. Backend is in approval_required_for list
        2. require_human_approval is explicitly set
        3. Task risk is high and not auto-approved
        """
        metadata = metadata or {}
        approval_context = approval_context or {}
        
        effective = self.policy_resolver.resolve(request, metadata)
        
        # Check explicit require_human_approval from request
        if approval_context.get("require_human_approval"):
            return {
                "approval_required": True,
                "reason": "Explicitly requested in approval_context",
                "auto_approved": False,
            }
        
        # Check if backend requires approval
        approval_required_for = effective.get("approval_required_for", [])
        
        # Determine requested backend
        matched_policy = self.policy_resolver.get_matching_policy(request)
        requested_backend = matched_policy.get("use") if matched_policy else None
        
        if requested_backend in approval_required_for:
            return {
                "approval_required": True,
                "reason": f"Backend {requested_backend} requires approval for tier {metadata.get('user_license', 'unknown')}",
                "auto_approved": False,
                "requested_backend": requested_backend,
            }
        
        # Check task risk
        task_risk = metadata.get("task_risk", "")
        if task_risk == "high":
            return {
                "approval_required": True,
                "reason": "High risk task requires approval",
                "auto_approved": False,
                "task_risk": task_risk,
            }
        
        return {
            "approval_required": False,
            "reason": "No approval required",
            "auto_approved": True,
        }
    
    def approve(
        self,
        approval_decision: str,
        approver: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create approval decision record."""
        return {
            "approved": approval_decision.lower() == "approved",
            "approver": approver or "system",
            "timestamp": time.time(),
        }


class PolicyAudit:
    """Generate audit metadata for policy decisions."""
    
    @staticmethod
    def create(
        request: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        entitlement_result: Optional[Dict[str, Any]] = None,
        approval_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create audit record for a policy decision."""
        return {
            "request_id": request.get("request_id", ""),
            "timestamp": time.time(),
            "tenant_id": metadata.get("tenant_id") if metadata else None,
            "user_id": metadata.get("user_id") if metadata else None,
            "user_license": metadata.get("user_license") if metadata else None,
            "entitlement": entitlement_result,
            "approval": approval_result,
        }


class UsageTracker:
    """Track normalized usage for backend executions."""
    
    @staticmethod
    def start() -> float:
        """Start timing."""
        return time.time()
    
    @staticmethod
    def complete(
        start_time: float,
        backend_id: str,
        config: Dict[str, Any],
        response: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create normalized usage record."""
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract usage from response
        usage = response.get("usage", {}) if response else {}
        
        # Estimate cost (would use provider pricing in production)
        cost_estimate = None
        if usage.get("total_tokens"):
            # Rough estimate: $0.001 per 1K tokens
            cost_estimate = round(usage["total_tokens"] / 1000 * 0.001, 6)
        
        return {
            "backend_used": backend_id,
            "provider": config.get("provider"),
            "model": config.get("model"),
            "latency_ms": latency_ms,
            "usage_input": usage.get("prompt_tokens") or usage.get("input_tokens"),
            "usage_output": usage.get("completion_tokens") or usage.get("output_tokens"),
            "usage_total": usage.get("total_tokens"),
            "cost_estimate": cost_estimate,
        }
    
    @staticmethod
    def from_response(
        response: Dict[str, Any],
        start_time: float,
    ) -> Dict[str, Any]:
        """Extract usage from adapter response."""
        return UsageTracker.complete(
            start_time=start_time,
            backend_id=response.get("backend_used", "unknown"),
            config={},
            response=response,
        )