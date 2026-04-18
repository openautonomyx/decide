"""
Approval persistence and management.

This module provides:
- Approval record schema
- File-based approval persistence
- Approval lifecycle management
"""
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


APPROVALS_DIR = os.getenv("APPROVALS_DIR", "/workspace/project/agent/data/approvals")

# Ensure directory exists
Path(APPROVALS_DIR).mkdir(parents=True, exist_ok=True)


class ApprovalStatus:
    """Approval status constants."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class Approval:
    """Approval request record."""
    
    def __init__(
        self,
        approval_id: str,
        thread_id: str,
        tenant_id: str = "",
        user_id: str = "",
        goal: str = "",
        capability: str = "coding",
        requested_backend: str = "",
        reason: str = "",
        status: str = ApprovalStatus.PENDING,
        requester_notes: str = "",
        approver: str = "",
        approver_notes: str = "",
        task_data: Optional[Dict[str, Any]] = None,
    ):
        self.approval_id = approval_id
        self.thread_id = thread_id
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.goal = goal
        self.capability = capability
        self.requested_backend = requested_backend
        self.reason = reason
        self.status = status
        self.requester_notes = requester_notes
        self.approver = approver
        self.approver_notes = approver_notes
        self.task_data = task_data or {}
        self.created_at = time.time()
        self.updated_at = time.time()
    
    @classmethod
    def create(
        cls,
        thread_id: str,
        tenant_id: str = "",
        user_id: str = "",
        goal: str = "",
        capability: str = "coding",
        requested_backend: str = "",
        reason: str = "",
        requester_notes: str = "",
        task_data: Optional[Dict[str, Any]] = None,
    ) -> "Approval":
        """Create a new approval request."""
        return cls(
            approval_id=str(uuid.uuid4())[:8],
            thread_id=thread_id,
            tenant_id=tenant_id,
            user_id=user_id,
            goal=goal,
            capability=capability,
            requested_backend=requested_backend,
            reason=reason,
            requester_notes=requester_notes,
            task_data=task_data,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "approval_id": self.approval_id,
            "thread_id": self.thread_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "goal": self.goal,
            "capability": self.capability,
            "requested_backend": self.requested_backend,
            "reason": self.reason,
            "status": self.status,
            "requester_notes": self.requester_notes,
            "approver": self.approver,
            "approver_notes": self.approver_notes,
            "task_data": self.task_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Approval":
        """Create from dictionary."""
        approval = cls(
            approval_id=data.get("approval_id", ""),
            thread_id=data.get("thread_id", ""),
            tenant_id=data.get("tenant_id", ""),
            user_id=data.get("user_id", ""),
            goal=data.get("goal", ""),
            capability=data.get("capability", "coding"),
            requested_backend=data.get("requested_backend", ""),
            reason=data.get("reason", ""),
            status=data.get("status", ApprovalStatus.PENDING),
            requester_notes=data.get("requester_notes", ""),
            approver=data.get("approver", ""),
            approver_notes=data.get("approver_notes", ""),
            task_data=data.get("task_data"),
        )
        approval.created_at = data.get("created_at", time.time())
        approval.updated_at = data.get("updated_at", time.time())
        return approval
    
    @classmethod
    def load(cls, approval_id: str) -> Optional["Approval"]:
        """Load approval from file."""
        path = Path(APPROVALS_DIR) / f"{approval_id}.json"
        if not path.exists():
            return None
        try:
            with open(path) as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return None
    
    @classmethod
    def load_by_thread(cls, thread_id: str, status: Optional[str] = None) -> Optional["Approval"]:
        """Load most recent approval by thread_id, optionally filtered by status."""
        approvals = []
        # Scan all approval files
        for path in Path(APPROVALS_DIR).glob("*.json"):
            try:
                with open(path) as f:
                    data = json.load(f)
                if data.get("thread_id") == thread_id:
                    if status is None or data.get("status") == status:
                        approvals.append(cls.from_dict(data))
            except Exception:
                continue
        
        if not approvals:
            return None
        
        # Return most recent
        approvals.sort(key=lambda a: a.created_at, reverse=True)
        return approvals[0]
    
    @classmethod
    def load_approved_by_thread(cls, thread_id: str) -> Optional["Approval"]:
        """Load most recent approved approval by thread_id."""
        return cls.load_by_thread(thread_id, status=ApprovalStatus.APPROVED)
    
    def save(self) -> bool:
        """Save approval to file."""
        path = Path(APPROVALS_DIR) / f"{self.approval_id}.json"
        try:
            self.updated_at = time.time()
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    def approve(self, approver: str = "admin", notes: str = "") -> bool:
        """Mark as approved."""
        self.status = ApprovalStatus.APPROVED
        self.approver = approver
        self.approver_notes = notes
        self.updated_at = time.time()
        return self.save()
    
    def deny(self, approver: str = "admin", notes: str = "") -> bool:
        """Mark as denied."""
        self.status = ApprovalStatus.DENIED
        self.approver = approver
        self.approver_notes = notes
        self.updated_at = time.time()
        return self.save()


def list_approvals(
    status: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> List[Approval]:
    """List all approvals, optionally filtered."""
    approvals = []
    for path in Path(APPROVALS_DIR).glob("*.json"):
        try:
            with open(path) as f:
                data = json.load(f)
            
            # Apply filters
            if status and data.get("status") != status:
                continue
            if tenant_id and data.get("tenant_id") != tenant_id:
                continue
            
            approvals.append(Approval.from_dict(data))
        except Exception:
            continue
    
    # Sort by created_at descending
    approvals.sort(key=lambda a: a.created_at, reverse=True)
    return approvals