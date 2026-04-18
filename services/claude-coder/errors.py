"""
Consistent error model for backend failures, entitlement denials, and approval requirements.
"""
from typing import Any, Dict, List, Optional
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for the coding service."""
    BACKEND_FAILURE = "BACKEND_FAILURE"
    ENTITLEMENT_DENIED = "ENTITLEMENT_DENIED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    FALLBACK_EXHAUSTED = "FALLBACK_EXHAUSTED"
    ROUTING_ERROR = "ROUTING_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"


class BackendError(Exception):
    """Error during backend execution."""
    
    def __init__(
        self,
        message: str,
        backend_id: str,
        error_code: str = ErrorCode.BACKEND_FAILURE,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.backend_id = backend_id
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.error_code,
            "message": self.message,
            "backend_id": self.backend_id,
            "details": self.details,
        }


class EntitlementDeniedError(Exception):
    """Entitlement check failed for backend."""
    
    def __init__(
        self,
        message: str,
        backend_id: str,
        denied_backends: List[str],
        entitlement_tier: str,
    ):
        self.message = message
        self.backend_id = backend_id
        self.denied_backends = denied_backends
        self.entitlement_tier = entitlement_tier
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": ErrorCode.ENTITLEMENT_DENIED,
            "message": self.message,
            "backend_id": self.backend_id,
            "denied_backends": self.denied_backends,
            "entitlement_tier": self.entitlement_tier,
        }


class ApprovalRequiredError(Exception):
    """Human approval required before execution."""
    
    def __init__(
        self,
        message: str,
        reason: str,
        requested_backend: Optional[str] = None,
        auto_approved: bool = False,
    ):
        self.message = message
        self.reason = reason
        self.requested_backend = requested_backend
        self.auto_approved = auto_approved
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": ErrorCode.APPROVAL_REQUIRED,
            "message": self.message,
            "reason": self.reason,
            "requested_backend": self.requested_backend,
            "auto_approved": self.auto_approved,
        }


class FallbackExhaustedError(Exception):
    """All fallback backends have been exhausted."""
    
    def __init__(
        self,
        message: str,
        attempted_backends: List[str],
        last_error: Optional[str] = None,
    ):
        self.message = message
        self.attempted_backends = attempted_backends
        self.last_error = last_error
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": ErrorCode.FALLBACK_EXHAUSTED,
            "message": self.message,
            "attempted_backends": self.attempted_backends,
            "last_error": self.last_error,
        }


def error_response(
    error_code: str,
    message: str,
    **kwargs,
) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "status": "error",
        "error": error_code,
        "message": message,
        **kwargs,
    }