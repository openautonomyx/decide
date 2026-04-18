"""
Audit Logger
Phase 4 - Orchestrator audit logging

Records major orchestrator events for compliance and debugging.
"""
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Audit event types"""
    INTAKE = "intake"
    TASK_DETECTION = "task_detection"
    RUNTIME_SELECTION = "runtime_selection"
    POLICY_DECISION = "policy_decision"
    GUARDRAIL_DECISION = "guardrail_decision"
    APPROVAL_PAUSE = "approval_pause"
    APPROVAL_RESUME = "approval_resume"
    APPROVAL_REJECT = "approval_reject"
    RUNTIME_INVOCATION = "runtime_invocation"
    RUNTIME_SUCCESS = "runtime_success"
    RUNTIME_FAILURE = "runtime_failure"
    FALLBACK = "fallback"
    COMPACTION = "compaction"
    CHECKPOINT = "checkpoint"
    RESULT = "result"


class AuditEvent:
    """Represents a single audit event"""
    def __init__(
        self,
        event_type: str,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ):
        self.event_type = event_type
        self.execution_id = execution_id
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "execution_id": self.execution_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    Audit logger records orchestrator events.
    
    Stores events in memory (extensible to persistent storage).
    """
    
    def __init__(self):
        self._events: List[AuditEvent] = []
        self._max_events = 10000  # In-memory limit
    
    def log(
        self,
        event_type: str,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            execution_id: Execution ID
            tenant_id: Tenant ID
            user_id: User ID
            data: Event data
            
        Returns:
            AuditEvent: The logged event
        """
        event = AuditEvent(
            event_type=event_type,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data=data or {},
        )
        
        # Store event
        self._events.append(event)
        
        # Trim if needed
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
        
        logger.debug(f"Audit: {event_type} for {execution_id}")
        
        return event
    
    def log_intake(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        request_text: str,
        thread_id: Optional[str] = None,
    ) -> AuditEvent:
        """Log intake event."""
        return self.log(
            event_type=AuditEventType.INTAKE,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={
                "request_text": request_text[:100],  # Truncate for log
                "thread_id": thread_id,
            },
        )
    
    def log_task_detection(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        task_type: str,
        confidence: float,
    ) -> AuditEvent:
        """Log task detection event."""
        return self.log(
            event_type=AuditEventType.TASK_DETECTION,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={
                "task_type": task_type,
                "confidence": confidence,
            },
        )
    
    def log_runtime_selection(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        runtime_id: str,
    ) -> AuditEvent:
        """Log runtime selection event."""
        return self.log(
            event_type=AuditEventType.RUNTIME_SELECTION,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={"runtime_id": runtime_id},
        )
    
    def log_policy_decision(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        decision: str,
        reason: str,
        rule_matched: Optional[str] = None,
    ) -> AuditEvent:
        """Log policy decision event."""
        return self.log(
            event_type=AuditEventType.POLICY_DECISION,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={
                "decision": decision,
                "reason": reason,
                "rule_matched": rule_matched,
            },
        )
    
    def log_guardrail_decision(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        decision: str,
        blocked: bool,
        flagged: bool,
    ) -> AuditEvent:
        """Log guardrail decision event."""
        return self.log(
            event_type=AuditEventType.GUARDRAIL_DECISION,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={
                "decision": decision,
                "blocked": blocked,
                "flagged": flagged,
            },
        )
    
    def log_approval_pause(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        approval_id: str,
        reason: str,
    ) -> AuditEvent:
        """Log approval pause event."""
        return self.log(
            event_type=AuditEventType.APPROVAL_PAUSE,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={
                "approval_id": approval_id,
                "reason": reason,
            },
        )
    
    def log_approval_resume(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        approval_id: str,
    ) -> AuditEvent:
        """Log approval resume event."""
        return self.log(
            event_type=AuditEventType.APPROVAL_RESUME,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={"approval_id": approval_id},
        )
    
    def log_runtime_invocation(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        runtime_id: str,
        status: str,
    ) -> AuditEvent:
        """Log runtime invocation event."""
        event_type = (
            AuditEventType.RUNTIME_SUCCESS 
            if status == "success" 
            else AuditEventType.RUNTIME_FAILURE
        )
        return self.log(
            event_type=event_type,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={"runtime_id": runtime_id, "status": status},
        )
    
    def log_fallback(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        from_runtime: str,
        to_runtime: str,
    ) -> AuditEvent:
        """Log fallback event."""
        return self.log(
            event_type=AuditEventType.FALLBACK,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={
                "from_runtime": from_runtime,
                "to_runtime": to_runtime,
            },
        )
    
    def log_compaction(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        tokens_before: int,
        tokens_after: int,
        tokens_saved: int,
    ) -> AuditEvent:
        """Log compaction event."""
        return self.log(
            event_type=AuditEventType.COMPACTION,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={
                "tokens_before": tokens_before,
                "tokens_after": tokens_after,
                "tokens_saved": tokens_saved,
            },
        )
    
    def log_result(
        self,
        execution_id: str,
        tenant_id: str,
        user_id: str,
        status: str,
        next_action: str,
    ) -> AuditEvent:
        """Log final result event."""
        return self.log(
            event_type=AuditEventType.RESULT,
            execution_id=execution_id,
            tenant_id=tenant_id,
            user_id=user_id,
            data={
                "status": status,
                "next_action": next_action,
            },
        )
    
    def get_events_for_execution(
        self,
        execution_id: str,
    ) -> List[AuditEvent]:
        """Get all events for an execution."""
        return [
            e for e in self._events
            if e.execution_id == execution_id
        ]
    
    def get_events_for_tenant(
        self,
        tenant_id: str,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Get recent events for a tenant."""
        tenant_events = [
            e for e in self._events
            if e.tenant_id == tenant_id
        ]
        return tenant_events[-limit:]
    
    def get_all_events(self) -> List[AuditEvent]:
        """Get all events."""
        return self._events.copy()
    
    def clear(self):
        """Clear all events (for testing)."""
        self._events.clear()


# Global instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


__all__ = [
    "AuditEventType",
    "AuditEvent",
    "AuditLogger",
    "get_audit_logger",
]