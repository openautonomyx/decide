"""
Orchestrator Module
Phase 1, 2, 3 & 4 - Core orchestrator implementation

This module provides the orchestrator engine that coordinates
request execution through the Phase 0 services.

Phase 1: Core execution pipeline
Phase 2: Policy gates, guardrails, and approval handling
Phase 3: Runtime invocation with adapters
Phase 4: Compaction execution and audit logging
"""
from app.orchestrator.types import (
    TaskType,
    OrchestratorStatus,
    ExecutionStage,
    NextAction,
    OrchestratorRequest,
    OrchestratorResult,
    ExecutionState,
    StageResult,
)

from app.orchestrator.state import (
    ExecutionStateStore,
    get_state_store,
)

from app.orchestrator.router import (
    OrchestratorRouter,
    get_router,
)

from app.orchestrator.engine import (
    OrchestratorEngine,
    get_orchestrator_engine,
    execute_request,
)

# Phase 2 additions
from app.orchestrator.policy_gate import (
    PolicyDecision,
    PolicyGate,
    get_policy_gate,
)

from app.orchestrator.guardrails import (
    GuardrailDecision,
    GuardrailResult,
    Guardrails,
    get_guardrails,
)

from app.orchestrator.approval_gate import (
    ApprovalStatus,
    ApprovalRequest,
    ApprovalGate,
    get_approval_gate,
)

# Phase 3 additions
from app.orchestrator.runtime_invoker import (
    RuntimeInvocationError,
    RuntimeOutput,
    RuntimeInvoker,
    get_runtime_invoker,
)

from app.orchestrator.runtime_adapters import (
    BaseRuntimeAdapter,
    OpenAIAgentsAdapter,
    ClaudeWorkerAdapter,
    GenericWorkerAdapter,
    get_adapter,
)

# Phase 4 additions
from app.orchestrator.compaction_executor import (
    CompactionResult,
    CompactionExecutor,
    get_compaction_executor,
)

from app.orchestrator.audit_logger import (
    AuditEventType,
    AuditEvent,
    AuditLogger,
    get_audit_logger,
)

__all__ = [
    # Types
    "TaskType",
    "OrchestratorStatus",
    "ExecutionStage",
    "NextAction",
    "OrchestratorRequest",
    "OrchestratorResult",
    "ExecutionState",
    "StageResult",
    # State
    "ExecutionStateStore",
    "get_state_store",
    # Router
    "OrchestratorRouter",
    "get_router",
    # Engine
    "OrchestratorEngine",
    "get_orchestrator_engine",
    "execute_request",
    # Phase 2: Policy
    "PolicyDecision",
    "PolicyGate",
    "get_policy_gate",
    # Phase 2: Guardrails
    "GuardrailDecision",
    "GuardrailResult",
    "Guardrails",
    "get_guardrails",
    # Phase 2: Approval
    "ApprovalStatus",
    "ApprovalRequest",
    "ApprovalGate",
    "get_approval_gate",
    # Phase 3: Runtime Invocation
    "RuntimeInvocationError",
    "RuntimeOutput",
    "RuntimeInvoker",
    "get_runtime_invoker",
    # Phase 3: Adapters
    "BaseRuntimeAdapter",
    "OpenAIAgentsAdapter",
    "ClaudeWorkerAdapter",
    "GenericWorkerAdapter",
    "get_adapter",
    # Phase 4: Compaction
    "CompactionResult",
    "CompactionExecutor",
    "get_compaction_executor",
    # Phase 4: Audit
    "AuditEventType",
    "AuditEvent",
    "AuditLogger",
    "get_audit_logger",
]