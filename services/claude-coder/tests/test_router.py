"""
Tests for router module.
"""
import pytest
from router import select_backend, BackendRoutingError


# Sample registry for testing
TEST_REGISTRY = {
    "claude_premium": {
        "capability": "coding",
        "config": {"enabled": True, "provider": "anthropic"},
    },
    "devstral_local": {
        "capability": "coding",
        "config": {"enabled": True, "provider": "litellm"},
    },
    "openai_coding": {
        "capability": "coding",
        "config": {"enabled": False},
    },
    "gpt_image": {
        "capability": "image_editing",
        "config": {"enabled": True},
    },
}


TEST_POLICIES = {
    "routing_policies": [
        {
            "when": {"capability": "coding", "quality": "premium"},
            "use": "claude_premium",
            "fallback_order": ["devstral_local"],
        },
        {
            "when": {"capability": "coding", "locality": "local_only"},
            "use": "devstral_local",
        },
        {
            "when": {"capability": "image_editing", "quality": "premium"},
            "use": "gpt_image",
        },
    ]
}


def test_routing_premium_coding():
    """Test premium coding routes to claude_premium."""
    request = {"capability": "coding", "quality": "premium"}
    decision = select_backend(request, TEST_REGISTRY, TEST_POLICIES)
    assert decision.backend_id == "claude_premium"


def test_routing_local_only():
    """Test local_only routes to devstral_local."""
    request = {"capability": "coding", "locality": "local_only"}
    decision = select_backend(request, TEST_REGISTRY, TEST_POLICIES)
    assert decision.backend_id == "devstral_local"


def test_routing_preferred_backend():
    """Test preferred_backend is respected."""
    request = {"capability": "coding", "preferred_backend": "devstral_local"}
    decision = select_backend(request, TEST_REGISTRY, TEST_POLICIES)
    assert decision.backend_id == "devstral_local"


def test_routing_fallback_order():
    """Test fallback_order is included in decision."""
    request = {"capability": "coding", "quality": "premium"}
    decision = select_backend(request, TEST_REGISTRY, TEST_POLICIES)
    assert "devstral_local" in decision.fallback_order


def test_routing_disabled_backend():
    """Test disabled backends raise error."""
    request = {"capability": "coding", "preferred_backend": "openai_coding"}
    with pytest.raises(BackendRoutingError):
        select_backend(request, TEST_REGISTRY, TEST_POLICIES)


def test_routing_image_editing():
    """Test image_editing routes to gpt_image."""
    request = {"capability": "image_editing", "quality": "premium"}
    decision = select_backend(request, TEST_REGISTRY, TEST_POLICIES)
    assert decision.backend_id == "gpt_image"


def test_routing_no_match():
    """Test fallback to first enabled when no policy matches."""
    request = {"capability": "unknown"}
    with pytest.raises(BackendRoutingError):
        select_backend(request, TEST_REGISTRY, TEST_POLICIES)


def test_routing_error_no_backends():
    """Test error when no backends available."""
    empty_registry = {}
    request = {"capability": "coding"}
    with pytest.raises(BackendRoutingError):
        select_backend(request, empty_registry, TEST_POLICIES)