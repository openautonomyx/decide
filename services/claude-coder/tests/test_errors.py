"""
Tests for errors module.
"""
import pytest
from errors import (
    ErrorCode,
    BackendError,
    EntitlementDeniedError,
    ApprovalRequiredError,
    FallbackExhaustedError,
    error_response,
)


class TestErrorCodes:
    """Test error codes enum."""
    
    def test_error_codes_exist(self):
        """Test all error codes are defined."""
        assert ErrorCode.BACKEND_FAILURE.value == "BACKEND_FAILURE"
        assert ErrorCode.ENTITLEMENT_DENIED.value == "ENTITLEMENT_DENIED"
        assert ErrorCode.APPROVAL_REQUIRED.value == "APPROVAL_REQUIRED"
        assert ErrorCode.FALLBACK_EXHAUSTED.value == "FALLBACK_EXHAUSTED"
        assert ErrorCode.ROUTING_ERROR.value == "ROUTING_ERROR"
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"


class TestBackendError:
    """Test BackendError."""
    
    def test_backend_error_to_dict(self):
        """Test conversion to dict."""
        error = BackendError(
            message="Connection failed",
            backend_id="claude_premium",
            error_code=ErrorCode.BACKEND_FAILURE,
            details={"retry_count": 3},
        )
        
        result = error.to_dict()
        
        assert result["error"] == ErrorCode.BACKEND_FAILURE
        assert result["message"] == "Connection failed"
        assert result["backend_id"] == "claude_premium"
        assert result["details"]["retry_count"] == 3


class TestEntitlementDeniedError:
    """Test EntitlementDeniedError."""
    
    def test_entitlement_denied_to_dict(self):
        """Test conversion to dict."""
        error = EntitlementDeniedError(
            message="Backend denied by policy",
            backend_id="claude_premium",
            denied_backends=["claude_premium", "openai_coding"],
            entitlement_tier="free",
        )
        
        result = error.to_dict()
        
        assert result["error"] == ErrorCode.ENTITLEMENT_DENIED
        assert result["backend_id"] == "claude_premium"
        assert result["denied_backends"] == ["claude_premium", "openai_coding"]
        assert result["entitlement_tier"] == "free"


class TestApprovalRequiredError:
    """Test ApprovalRequiredError."""
    
    def test_approval_required_to_dict(self):
        """Test conversion to dict."""
        error = ApprovalRequiredError(
            message="Approval required for premium backend",
            reason="Backend claude_premium requires approval for tier pro",
            requested_backend="claude_premium",
            auto_approved=False,
        )
        
        result = error.to_dict()
        
        assert result["error"] == ErrorCode.APPROVAL_REQUIRED
        assert result["requested_backend"] == "claude_premium"
        assert result["auto_approved"] is False


class TestFallbackExhaustedError:
    """Test FallbackExhaustedError."""
    
    def test_fallback_exhausted_to_dict(self):
        """Test conversion to dict."""
        error = FallbackExhaustedError(
            message="All backends failed",
            attempted_backends=["claude_premium", "devstral_local"],
            last_error="Connection refused",
        )
        
        result = error.to_dict()
        
        assert result["error"] == ErrorCode.FALLBACK_EXHAUSTED
        assert result["attempted_backends"] == ["claude_premium", "devstral_local"]
        assert result["last_error"] == "Connection refused"


class TestErrorResponse:
    """Test error_response helper."""
    
    def test_error_response_basic(self):
        """Test basic error response."""
        result = error_response(
            error_code=ErrorCode.BACKEND_FAILURE,
            message="Something went wrong",
        )
        
        assert result["status"] == "error"
        assert result["error"] == ErrorCode.BACKEND_FAILURE
        assert result["message"] == "Something went wrong"
    
    def test_error_response_with_extra(self):
        """Test error response with extra fields."""
        result = error_response(
            error_code=ErrorCode.ENTITLEMENT_DENIED,
            message="Access denied",
            backend_id="claude_premium",
            thread_id="abc123",
        )
        
        assert result["backend_id"] == "claude_premium"
        assert result["thread_id"] == "abc123"