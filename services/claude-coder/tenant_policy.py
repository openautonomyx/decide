"""
Tenant policy storage and management.

This module provides:
- File-based tenant policy persistence
- Tenant policy model/schema
- Admin APIs for tenant policy management
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


TENANT_POLICIES_DIR = os.getenv("TENANT_POLICIES_DIR", "/workspace/project/agent/data/tenant_policies")


# Ensure directory exists
Path(TENANT_POLICIES_DIR).mkdir(parents=True, exist_ok=True)


class TenantPolicy:
    """Tenant policy configuration."""
    
    def __init__(
        self,
        tenant_id: str,
        name: str = "",
        enabled: bool = True,
        allowed_backends: Optional[List[str]] = None,
        denied_backends: Optional[List[str]] = None,
        max_budget_monthly: Optional[float] = None,
        max_requests_per_hour: Optional[int] = None,
        quality_default: Optional[str] = None,
        allow_fallback: Optional[bool] = None,
        max_retries: Optional[int] = None,
        approval_required_for: Optional[List[str]] = None,
        capability_policies: Optional[Dict[str, Any]] = None,
    ):
        self.tenant_id = tenant_id
        self.name = name
        self.enabled = enabled
        self.allowed_backends = allowed_backends or []
        self.denied_backends = denied_backends or []
        self.max_budget_monthly = max_budget_monthly
        self.max_requests_per_hour = max_requests_per_hour
        self.quality_default = quality_default
        self.allow_fallback = allow_fallback
        self.max_retries = max_retries
        self.approval_required_for = approval_required_for or []
        self.capability_policies = capability_policies or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tenant_id": self.tenant_id,
            "name": self.name,
            "enabled": self.enabled,
            "allowed_backends": self.allowed_backends,
            "denied_backends": self.denied_backends,
            "max_budget_monthly": self.max_budget_monthly,
            "max_requests_per_hour": self.max_requests_per_hour,
            "quality_default": self.quality_default,
            "allow_fallback": self.allow_fallback,
            "max_retries": self.max_retries,
            "approval_required_for": self.approval_required_for,
            "capability_policies": self.capability_policies,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TenantPolicy":
        """Create from dictionary."""
        return cls(
            tenant_id=data.get("tenant_id", ""),
            name=data.get("name", ""),
            enabled=data.get("enabled", True),
            allowed_backends=data.get("allowed_backends"),
            denied_backends=data.get("denied_backends"),
            max_budget_monthly=data.get("max_budget_monthly"),
            max_requests_per_hour=data.get("max_requests_per_hour"),
            quality_default=data.get("quality_default"),
            allow_fallback=data.get("allow_fallback"),
            max_retries=data.get("max_retries"),
            approval_required_for=data.get("approval_required_for"),
            capability_policies=data.get("capability_policies"),
        )
    
    @classmethod
    def load(cls, tenant_id: str) -> Optional["TenantPolicy"]:
        """Load tenant policy from file."""
        path = Path(TENANT_POLICIES_DIR) / f"{tenant_id}.json"
        if not path.exists():
            return None
        try:
            with open(path) as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return None
    
    def save(self) -> bool:
        """Save tenant policy to file."""
        path = Path(TENANT_POLICIES_DIR) / f"{self.tenant_id}.json"
        try:
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    def delete(self) -> bool:
        """Delete tenant policy."""
        path = Path(TENANT_POLICIES_DIR) / f"{self.tenant_id}.json"
        try:
            if path.exists():
                path.unlink()
            return True
        except Exception:
            return False


class ExecutionHistory:
    """Execution history for audit and budget tracking."""
    
    def __init__(
        self,
        tenant_id: str,
        user_id: str = "",
        thread_id: str = "",
        request_data: Optional[Dict[str, Any]] = None,
        backend_used: str = "",
        status: str = "",
        cost: Optional[float] = None,
        usage_tokens: Optional[int] = None,
    ):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.thread_id = thread_id
        self.request_data = request_data or {}
        self.backend_used = backend_used
        self.status = status
        self.cost = cost
        self.usage_tokens = usage_tokens
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "thread_id": self.thread_id,
            "request_data": self.request_data,
            "backend_used": self.backend_used,
            "status": self.status,
            "cost": self.cost,
            "usage_tokens": self.usage_tokens,
            "timestamp": self.timestamp,
        }


import time


def write_execution_history(
    execution: ExecutionHistory,
) -> bool:
    """Write execution to history file."""
    tenant_dir = Path(TENANT_POLICIES_DIR) / "history" / execution.tenant_id
    tenant_dir.mkdir(parents=True, exist_ok=True)
    path = tenant_dir / f"{execution.thread_id}.json"
    try:
        with open(path, "w") as f:
            json.dump(execution.to_dict(), f, indent=2)
        return True
    except Exception:
        return False