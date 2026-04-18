"""
Tests for policy module - entitlements and approvals.
"""
import pytest
from policy import PolicyResolver, EntitlementResolver, ApprovalChecker


TEST_REGISTRY = {
    "claude_premium": {"capability": "coding"},
    "devstral_local": {"capability": "coding"},
}


TEST_POLICIES = {
    "routing_policies": [
        {
            "when": {"capability": "coding", "quality": "premium"},
            "use": "claude_premium",
            "fallback_order": ["devstral_local"],
        },
    ]
}


@pytest.fixture
def policy_resolver():
    return PolicyResolver(TEST_REGISTRY, TEST_POLICIES)


@pytest.fixture
def entitlement_resolver(policy_resolver):
    return EntitlementResolver(policy_resolver)


@pytest.fixture
def approval_checker(policy_resolver):
    return ApprovalChecker(policy_resolver)


class TestEntitlements:
    """Test entitlement resolution."""
    
    def test_enterprise_allowed_all(self, entitlement_resolver):
        """Enterprise tier allows all backends."""
        metadata = {"user_license": "enterprise"}
        entitlements = entitlement_resolver.get_entitlements({}, metadata)
        
        assert "claude_premium" in entitlements["allowed_backends"]
        assert "devstral_local" in entitlements["allowed_backends"]
        assert entitlements["premium_allowed"] is True
    
    def test_free_denied_premium(self, entitlement_resolver):
        """Free tier denied premium backend."""
        metadata = {"user_license": "free"}
        
        result = entitlement_resolver.check_entitlement("claude_premium", {}, metadata)
        assert result["allowed"] is False
        assert "denied" in result["reason"].lower()
    
    def test_free_allowed_local(self, entitlement_resolver):
        """Free tier allowed local backend."""
        metadata = {"user_license": "free"}
        
        result = entitlement_resolver.check_entitlement("devstral_local", {}, metadata)
        assert result["allowed"] is True
    
    def test_pro_denied_claude(self, entitlement_resolver):
        """Pro tier denied claude_premium."""
        metadata = {"user_license": "pro"}
        
        result = entitlement_resolver.check_entitlement("claude_premium", {}, metadata)
        assert result["allowed"] is False
        assert result["entitlement_tier"] == "pro"
    
    def test_pro_allowed_devstral(self, entitlement_resolver):
        """Pro tier allowed devstral_local."""
        metadata = {"user_license": "pro"}
        
        result = entitlement_resolver.check_entitlement("devstral_local", {}, metadata)
        assert result["allowed"] is True
    
    def test_default_free_tier(self, entitlement_resolver):
        """No license defaults to free tier."""
        entitlements = entitlement_resolver.get_entitlements({}, {})
        
        assert entitlements["entitlement_tier"] == "free"
        # free tier doesn't allow any premium backends by default (no premium_allowed)


class TestApprovals:
    """Test approval requirement checks."""
    
    def test_enterprise_no_approval(self, approval_checker):
        """Enterprise tier doesn't require approval."""
        request = {"capability": "coding", "quality": "premium"}
        metadata = {"user_license": "enterprise"}
        
        result = approval_checker.check_approval_required(request, metadata, {})
        
        assert result["approval_required"] is False
        assert result["auto_approved"] is True
    
    def test_pro_requires_approval_premium(self, approval_checker):
        """Pro tier requires approval for premium."""
        request = {"capability": "coding", "quality": "premium"}
        metadata = {"user_license": "pro"}
        
        result = approval_checker.check_approval_required(request, metadata, {})
        
        assert result["approval_required"] is True
        assert result["auto_approved"] is False
        assert "claude_premium" in result["reason"]
    
    def test_explicit_approval_requested(self, approval_checker):
        """Explicit require_human_approval triggers approval."""
        request = {"capability": "coding"}
        metadata = {"user_license": "enterprise"}
        approval_context = {"require_human_approval": True}
        
        result = approval_checker.check_approval_required(request, metadata, approval_context)
        
        assert result["approval_required"] is True
        assert result["auto_approved"] is False
    
    def test_high_risk_requires_approval(self, approval_checker):
        """High risk tasks require approval."""
        request = {"capability": "coding"}
        metadata = {"user_license": "enterprise", "task_risk": "high"}
        
        result = approval_checker.check_approval_required(request, metadata, {})
        
        assert result["approval_required"] is True
        assert result["auto_approved"] is False
        assert "high risk" in result["reason"].lower()
    
    def test_free_requires_approval_local(self, approval_checker):
        """Free tier allows local backend without explicit approval if allowed."""
        request = {"capability": "coding", "locality": "local_only"}
        metadata = {"user_license": "enterprise"}  # enterprise allows local only
        
        result = approval_checker.check_approval_required(request, metadata, {})
        
        # enterprise allows local_only without approval
        assert result["approval_required"] is False
        assert result["auto_approved"] is True


class TestPolicyResolution:
    """Test policy resolution."""
    
    def test_resolve_enterprise_overrides(self, policy_resolver):
        """Enterprise license adds tier overrides."""
        request = {"capability": "coding"}
        metadata = {"user_license": "enterprise"}
        
        effective = policy_resolver.resolve(request, metadata)
        
        assert effective["default_quality"] == "premium"
        assert effective["allow_fallback"] is True
        assert effective["max_retries"] == 3
    
    def test_resolve_pro_overrides(self, policy_resolver):
        """Pro license adds tier overrides."""
        request = {"capability": "coding"}
        metadata = {"user_license": "pro"}
        
        effective = policy_resolver.resolve(request, metadata)
        
        assert effective["default_quality"] == "standard"
        assert effective["premium_allowed"] is False
        assert "claude_premium" in effective["denied_backends"]
    
    def test_resolve_free_overrides(self, policy_resolver):
        """Free license adds tier overrides."""
        request = {"capability": "coding"}
        metadata = {"user_license": "free"}
        
        effective = policy_resolver.resolve(request, metadata)
        
        assert effective["default_quality"] == "basic"
        assert effective["allow_fallback"] is False
    
    def test_get_matching_policy(self, policy_resolver):
        """Test policy matching."""
        request = {"capability": "coding", "quality": "premium"}
        
        policy = policy_resolver.get_matching_policy(request)
        
        assert policy["use"] == "claude_premium"
        assert policy["fallback_order"] == ["devstral_local"]
    
    def test_no_matching_policy(self, policy_resolver):
        """Test no policy matches."""
        request = {"capability": "unknown"}
        
        policy = policy_resolver.get_matching_policy(request)
        
        assert policy is None