"""
Approval Gate
Phase 2 - Human-in-the-loop (HITL) approval handling

Manages approval states for requests that require human approval:
- Pending approval
- Approved
- Rejected
- Expired
"""
import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

from app.orchestrator.types import ExecutionState, OrchestratorStatus, NextAction

logger = logging.getLogger(__name__)


class ApprovalStatus(str, Enum):
    """Approval request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalRequest:
    """Represents an approval request"""
    def __init__(
        self,
        approval_id: str,
        execution_id: str,
        tenant_id: str,
        requested_by: str,
        reason: str,
        details: Dict[str, Any],
        status: ApprovalStatus = ApprovalStatus.PENDING,
    ):
        self.approval_id = approval_id
        self.execution_id = execution_id
        self.tenant_id = tenant_id
        self.requested_by = requested_by
        self.reason = reason
        self.details = details
        self.status = status
        self.requested_at = datetime.utcnow()
        self.responded_at: Optional[datetime] = None
        self.responded_by: Optional[str] = None
        self.response_note: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "execution_id": self.execution_id,
            "tenant_id": self.tenant_id,
            "requested_by": self.requested_by,
            "reason": self.reason,
            "details": self.details,
            "status": self.status.value,
            "requested_at": self.requested_at.isoformat(),
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "responded_by": self.responded_by,
            "response_note": self.response_note,
        }


class ApprovalGate:
    """
    Approval gate manages HITL approval workflow.
    
    Handles:
    - Creating approval requests
    - Tracking approval status
    - Auto-expiring stale requests
    """
    
    def __init__(self, expiration_hours: int = 24):
        self._approvals: Dict[str, ApprovalRequest] = {}
        self._execution_to_approval: Dict[str, str] = {}
        self._expiration_hours = expiration_hours
    
    def create_approval_request(
        self,
        execution_id: str,
        tenant_id: str,
        requested_by: str,
        reason: str,
        details: Dict[str, Any],
    ) -> ApprovalRequest:
        """Create a new approval request."""
        approval_id = f"approval-{uuid.uuid4().hex[:12]}"
        
        approval = ApprovalRequest(
            approval_id=approval_id,
            execution_id=execution_id,
            tenant_id=tenant_id,
            requested_by=requested_by,
            reason=reason,
            details=details,
        )
        
        self._approvals[approval_id] = approval
        self._execution_to_approval[execution_id] = approval_id
        
        logger.info(f"Created approval request {approval_id} for execution {execution_id}")
        
        return approval
    
    def get_approval(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Get approval by ID."""
        return self._approvals.get(approval_id)
    
    def get_approval_for_execution(self, execution_id: str) -> Optional[ApprovalRequest]:
        """Get approval for execution."""
        approval_id = self._execution_to_approval.get(execution_id)
        if approval_id:
            return self._approvals.get(approval_id)
        return None
    
    def approve(
        self,
        approval_id: str,
        responded_by: str,
        note: Optional[str] = None,
    ) -> bool:
        """Approve an approval request."""
        approval = self._approvals.get(approval_id)
        if not approval:
            return False
        
        approval.status = ApprovalStatus.APPROVED
        approval.responded_at = datetime.utcnow()
        approval.responded_by = responded_by
        approval.response_note = note
        
        logger.info(f"Approval {approval_id} approved by {responded_by}")
        return True
    
    def reject(
        self,
        approval_id: str,
        responded_by: str,
        reason: str,
    ) -> bool:
        """Reject an approval request."""
        approval = self._approvals.get(approval_id)
        if not approval:
            return False
        
        approval.status = ApprovalStatus.REJECTED
        approval.responded_at = datetime.utcnow()
        approval.responded_by = responded_by
        approval.response_note = reason
        
        logger.info(f"Approval {approval_id} rejected by {responded_by}")
        return True
    
    def check_approval_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Check approval status for execution.
        
        Returns:
            {
                "requires_approval": bool,
                "approval_id": str,
                "status": str,
                "can_proceed": bool,
            }
        """
        approval = self.get_approval_for_execution(execution_id)
        
        if not approval:
            return {
                "requires_approval": False,
                "approval_id": None,
                "status": None,
                "can_proceed": True,
            }
        
        # Check if expired
        if approval.status == ApprovalStatus.PENDING:
            expiration = approval.requested_at + timedelta(hours=self._expiration_hours)
            if datetime.utcnow() > expiration:
                approval.status = ApprovalStatus.EXPIRED
                logger.warning(f"Approval {approval.approval_id} expired")
        
        can_proceed = approval.status == ApprovalStatus.APPROVED
        
        return {
            "requires_approval": True,
            "approval_id": approval.approval_id,
            "status": approval.status.value,
            "can_proceed": can_proceed,
        }
    
    def list_pending(self, tenant_id: Optional[str] = None) -> List[ApprovalRequest]:
        """List pending approvals."""
        pending = [
            a for a in self._approvals.values()
            if a.status == ApprovalStatus.PENDING
        ]
        
        if tenant_id:
            pending = [a for a in pending if a.tenant_id == tenant_id]
        
        return pending
    
    def list_for_execution(self, execution_id: str) -> List[ApprovalRequest]:
        """List all approvals for an execution."""
        return [
            a for a in self._approvals.values()
            if a.execution_id == execution_id
        ]


# Global instance
_approval_gate: Optional[ApprovalGate] = None


def get_approval_gate() -> ApprovalGate:
    """Get global approval gate."""
    global _approval_gate
    if _approval_gate is None:
        _approval_gate = ApprovalGate()
    return _approval_gate


__all__ = [
    "ApprovalStatus",
    "ApprovalRequest",
    "ApprovalGate",
    "get_approval_gate",
]