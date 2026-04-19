"""
Orchestrator Engine
Phase 1 - Core orchestrator execution engine
"""
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from app.orchestrator.types import (
    OrchestratorRequest,
    OrchestratorResult,
    OrchestratorStatus,
    ExecutionStage,
    ExecutionState,
    NextAction,
    TaskType,
)
from app.orchestrator.state import get_state_store, ExecutionStateStore
from app.orchestrator.router import get_router, OrchestratorRouter
from app.services.channel import get_channel_service, get_branch_service, get_worker_service
from app.services.context import get_context_budget_service, get_token_accounting_service

logger = logging.getLogger(__name__)


class OrchestratorEngine:
    """
    Core orchestrator engine.
    
    Orchestrates request execution through stages:
    1. Intake - Create execution context
    2. Task Detection - Detect task type
    3. Runtime Selection - Select appropriate runtime
    4. Context Setup - Create channel/branch if needed
    5. Budget Check - Verify context budget
    6. Tool/Skill Resolution - Resolve required tools/skills
    7. Execution - Execute via worker path
    8. Compaction Check - Check if compaction needed
    9. Result Aggregation - Build normalized result
    """
    
    def __init__(
        self,
        state_store: Optional[ExecutionStateStore] = None,
        router: Optional[OrchestratorRouter] = None,
    ):
        self._state_store = state_store or get_state_store()
        self._router = router or get_router()
        self._channel_service = get_channel_service()
        self._branch_service = get_branch_service()
        self._worker_service = get_worker_service()
        self._budget_service = get_context_budget_service()
        self._token_service = get_token_accounting_service()
    
    def execute(self, request: OrchestratorRequest) -> OrchestratorResult:
        """
        Execute orchestrator flow.
        
        Returns normalized OrchestratorResult.
        """
        execution_id = f"exec-{uuid.uuid4().hex[:12]}"
        
        try:
            # Stage 1: Intake
            self._stage_intake(execution_id, request)
            
            # Stage 2: State Init
            state = self._stage_state_init(execution_id, request)
            
            # Stage 3: Task Detection
            self._stage_task_detection(state, request)
            
            # Stage 4: Runtime Selection
            self._stage_runtime_selection(state, request)
            
            # Stage 5: Context Setup
            self._stage_context_setup(state, request)
            
            # Stage 6: Budget Check
            budget_check = self._stage_budget_check(state)
            
            # Stage 7: Tool/Skill Resolution
            self._stage_tool_resolution(state, request)
            self._stage_skill_resolution(state, request)
            
            # Stage 8: Execution (STUBBED - calls would go to runtime)
            output = self._stage_execution(state, request)
            
            # Stage 9: Compaction Check
            needs_compaction = self._stage_compaction_check(state, budget_check)
            
            # Stage 10: Result Aggregation
            result = self._stage_result_aggregation(
                execution_id=execution_id,
                state=state,
                output=output,
                needs_compaction=needs_compaction,
            )
            
            logger.info(f"Execution {execution_id} completed with status: {result.status}")
            return result
            
        except Exception as e:
            logger.error(f"Execution {execution_id} failed: {e}")
            return self._build_error_result(execution_id, str(e))
    
    def _stage_intake(self, execution_id: str, request: OrchestratorRequest):
        """Stage 1: Initial intake."""
        logger.info(f"[{execution_id}] Stage: INTAKE")
        # Creates state in state_init
    
    def _stage_state_init(
        self,
        execution_id: str,
        request: OrchestratorRequest,
    ) -> ExecutionState:
        """Stage 2: Initialize execution state."""
        logger.info(f"[{execution_id}] Stage: STATE_INIT")
        
        state = self._state_store.create(
            execution_id=execution_id,
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            thread_id=request.thread_id,
        )
        
        self._state_store.advance_stage(execution_id, ExecutionStage.STATE_INIT)
        self._state_store.set_status(execution_id, OrchestratorStatus.RUNNING)
        
        return state
    
    def _stage_task_detection(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ):
        """Stage 3: Detect task type."""
        logger.info(f"[{state.execution_id}] Stage: TASK_DETECTION")
        
        task_type, confidence = self._router.detect_task_type(
            request_text=request.request_text,
            metadata=request.request_metadata,
        )
        
        self._state_store.set_task_type(state.execution_id, task_type)
        
        # Update state with detection info
        self._state_store.update(
            state.execution_id,
            metadata={
                "task_detection": {
                    "task_type": task_type.value,
                    "confidence": confidence,
                }
            },
        )
        
        self._state_store.advance_stage(state.execution_id, ExecutionStage.TASK_DETECTION)
    
    def _stage_runtime_selection(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ):
        """Stage 4: Select runtime."""
        logger.info(f"[{state.execution_id}] Stage: RUNTIME_SELECTION")
        
        runtime_id, runtime_info = self._router.select_runtime(
            task_type=state.task_type or TaskType.SIMPLE,
            tenant_id=request.tenant_id,
            preferred_runtime=request.preferred_runtime,
        )
        
        self._state_store.set_runtime(state.execution_id, runtime_id)
        
        self._state_store.advance_stage(state.execution_id, ExecutionStage.RUNTIME_SELECTION)
    
    def _stage_context_setup(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ):
        """Stage 5: Setup context (channel/branch)."""
        logger.info(f"[{state.execution_id}] Stage: CONTEXT_SETUP")
        
        # Create or attach channel/branch for new threads
        if request.thread_id:
            # Load existing branch for thread
            branches = self._branch_service.list_branches(request.thread_id)
            if branches:
                main_branch = branches[0]
                self._state_store.set_branch(state.execution_id, main_branch["id"])
        else:
            # Create new channel for request (web channel as default)
            channel = self._channel_service.create_channel(
                name=f"channel-{request.tenant_id}",
                channel_type="web",
            )
            
            # Create branch for new thread
            thread_id = f"thread-{uuid.uuid4().hex[:12]}"
            branch = self._branch_service.create_branch(
                thread_id=thread_id,
                channel_id=channel["id"],
                branch_type="main",
            )
            
            self._state_store.update(
                state.execution_id,
                thread_id=thread_id,
            )
            self._state_store.set_branch(state.execution_id, branch["id"])
        
        # Create worker for execution
        worker = self._worker_service.create_worker(
            branch_id=state.branch_id,
            worker_type="execution",
            runtime_id=state.runtime_id,
        )
        
        self._state_store.set_worker(state.execution_id, worker["id"])
        self._state_store.advance_stage(state.execution_id, ExecutionStage.CONTEXT_SETUP)
    
    def _stage_budget_check(self, state: ExecutionState) -> Dict[str, Any]:
        """Stage 6: Check context budget."""
        logger.info(f"[{state.execution_id}] Stage: BUDGET_CHECK")
        
        task_type = state.task_type.value if state.task_type else "simple"
        
        budget_check = self._budget_service.check_budget(
            tenant_id=state.tenant_id,
            task_type=task_type,
            current_tokens=state.context_tokens,
        )
        
        self._state_store.advance_stage(state.execution_id, ExecutionStage.BUDGET_CHECK)
        
        return budget_check
    
    def _stage_tool_resolution(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ):
        """Stage 7a: Resolve required tools."""
        logger.info(f"[{state.execution_id}] Stage: TOOL_RESOLUTION")
        
        # Resolve requested tools
        for tool_name in request.required_tools:
            self._state_store.add_tool(state.execution_id, tool_name)
        
        self._state_store.advance_stage(state.execution_id, ExecutionStage.TOOL_RESOLUTION)
    
    def _stage_skill_resolution(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ):
        """Stage 7b: Resolve required skills."""
        logger.info(f"[{state.execution_id}] Stage: SKILL_RESOLUTION")
        
        # Resolve requested skills
        for skill_name in request.required_skills:
            self._state_store.add_skill(state.execution_id, skill_name)
        
        self._state_store.advance_stage(state.execution_id, ExecutionStage.SKILL_RESOLUTION)
    
    def _stage_execution(
        self,
        state: ExecutionState,
        request: OrchestratorRequest,
    ) -> str:
        """
        Stage 8: Execute via worker path.
        
        STUBBED: Actual execution would call runtime.
        """
        logger.info(f"[{state.execution_id}] Stage: EXECUTION (STUBBED)")
        
        # Start the worker
        self._worker_service.start_worker(state.worker_id)
        
        # STUBBED: Would call runtime.execute() here
        # For now, simulate execution with request text as output
        output = f"Processed: {request.request_text[:100]}..."
        
        # Mark worker complete
        self._worker_service.complete_worker(state.worker_id)
        
        # Update token accounting
        estimated_tokens = len(request.request_text) // 4
        self._token_service.record_usage(
            thread_id=state.thread_id or "unknown",
            tenant_id=state.tenant_id,
            input_tokens=estimated_tokens,
            output_tokens=len(output) // 4,
            runtime_id=state.runtime_id,
        )
        
        self._state_store.update_tokens(
            state.execution_id,
            input_tokens=estimated_tokens,
            output_tokens=len(output) // 4,
        )
        
        self._state_store.advance_stage(state.execution_id, ExecutionStage.EXECUTION)
        
        return output
    
    def _stage_compaction_check(
        self,
        state: ExecutionState,
        budget_check: Dict[str, Any],
    ) -> bool:
        """Stage 9: Check if compaction needed."""
        logger.info(f"[{state.execution_id}] Stage: COMPACTION_CHECK")
        
        should_compact = budget_check.get("should_compact", False)
        
        if should_compact:
            self._state_store.update(
                state.execution_id,
                metadata={**state.metadata, "compaction_triggered": True},
            )
        
        self._state_store.advance_stage(state.execution_id, ExecutionStage.COMPACTION_CHECK)
        
        return should_compact
    
    def _stage_result_aggregation(
        self,
        execution_id: str,
        state: ExecutionState,
        output: str,
        needs_compaction: bool,
    ) -> OrchestratorResult:
        """Stage 10: Build normalized result."""
        logger.info(f"[{execution_id}] Stage: RESULT_AGGREGATION")
        
        # Determine next action
        if needs_compaction:
            next_action = NextAction.NEEDS_COMPACTION
        else:
            next_action = NextAction.COMPLETE
        
        # Build audit refs (stubbed - would include actual audit log refs)
        audit_refs = {
            "execution_id": execution_id,
            "thread_id": state.thread_id,
            "branch_id": state.branch_id,
            "worker_id": state.worker_id,
        }
        
        # Get completed stages
        stages = [h["stage"] for h in state.history]
        
        self._state_store.set_status(execution_id, OrchestratorStatus.COMPLETED)
        self._state_store.advance_stage(execution_id, ExecutionStage.COMPLETE)
        
        result = OrchestratorResult(
            execution_request_id=execution_id,
            status=OrchestratorStatus.COMPLETED,
            selected_runtime=state.runtime_id,
            selected_tools=state.tools,
            selected_skills=state.skills,
            branch_id=state.branch_id,
            output_summary=output,
            next_action=next_action,
            audit_refs=audit_refs,
            metadata={
                "task_type": state.task_type.value if state.task_type else None,
                "input_tokens": state.input_tokens,
                "output_tokens": state.output_tokens,
                "compaction_triggered": needs_compaction,
            },
            stages_completed=stages,
            completed_at=datetime.utcnow(),
        )
        
        return result
    
    def _build_error_result(
        self,
        execution_id: str,
        error: str,
    ) -> OrchestratorResult:
        """Build error result."""
        logger.error(f"Building error result for {execution_id}: {error}")
        
        self._state_store.set_status(execution_id, OrchestratorStatus.FAILED)
        
        return OrchestratorResult(
            execution_request_id=execution_id,
            status=OrchestratorStatus.FAILED,
            error=error,
            next_action=NextAction.FALLBACK,
            completed_at=datetime.utcnow(),
        )


# Global instance
_engine: Optional[OrchestratorEngine] = None


def get_orchestrator_engine() -> OrchestratorEngine:
    """Get global orchestrator engine."""
    global _engine
    if _engine is None:
        _engine = OrchestratorEngine()
    return _engine


def execute_request(request: OrchestratorRequest) -> OrchestratorResult:
    """Convenience function to execute request."""
    engine = get_orchestrator_engine()
    return engine.execute(request)


__all__ = [
    "OrchestratorEngine",
    "get_orchestrator_engine",
    "execute_request",
]