"""
Runtime Invoker
Phase 3 - Runtime invocation orchestration

Handles runtime invocation with:
- Adapter selection
- Error handling and fallback
- Normalized response
- Execution history updates
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.orchestrator.types import (
    ExecutionState,
    OrchestratorRequest,
    OrchestratorStatus,
    NextAction,
)

logger = logging.getLogger(__name__)


class RuntimeInvocationError(Exception):
    """Runtime invocation error"""
    def __init__(self, message: str, runtime_id: str, is_retryable: bool = False):
        super().__init__(message)
        self.runtime_id = runtime_id
        self.is_retryable = is_retryable


class RuntimeOutput:
    """Normalized runtime output"""
    def __init__(
        self,
        status: str,
        output_text: str = "",
        structured_output: Optional[Dict[str, Any]] = None,
        usage: Optional[Dict[str, int]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        warnings: Optional[List[str]] = None,
        raw_ref: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        self.status = status  # success, failed, timeout
        self.output_text = output_text
        self.structured_output = structured_output
        self.usage = usage or {"input_tokens": 0, "output_tokens": 0}
        self.tool_calls = tool_calls or []
        self.warnings = warnings or []
        self.raw_ref = raw_ref
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "output_text": self.output_text,
            "structured_output": self.structured_output,
            "usage": self.usage,
            "tool_calls": self.tool_calls,
            "warnings": self.warnings,
            "raw_ref": self.raw_ref,
            "error": self.error,
        }


class RuntimeInvoker:
    """
    Runtime invoker handles execution via runtime adapters.
    
    Supports:
    - Primary runtime invocation
    - Fallback on failure
    - Error handling
    - Normalized output
    """
    
    def __init__(self):
        self._adapters: Dict[str, Any] = {}
        self._register_default_adapters()
    
    def _register_default_adapters(self):
        """Register default runtime adapters."""
        from app.orchestrator.runtime_adapters import (
            OpenAIAgentsAdapter,
            ClaudeWorkerAdapter,
            GenericWorkerAdapter,
        )
        
        self._adapters["openai_agents"] = OpenAIAgentsAdapter()
        self._adapters["claude_agent"] = ClaudeWorkerAdapter()
        self._adapters["langgraph"] = GenericWorkerAdapter()
        self._adapters["generic"] = GenericWorkerAdapter()
    
    def register_adapter(self, runtime_id: str, adapter: Any):
        """Register a custom adapter."""
        self._adapters[runtime_id] = adapter
        logger.info(f"Registered adapter for runtime: {runtime_id}")
    
    def invoke(
        self,
        runtime_id: str,
        state: ExecutionState,
        request: OrchestratorRequest,
    ) -> RuntimeOutput:
        """
        Invoke runtime with fallback support.
        
        Args:
            runtime_id: Selected runtime ID
            state: Execution state
            request: Original request
            
        Returns:
            RuntimeOutput: Normalized output
        """
        # Get adapter
        adapter = self._adapters.get(runtime_id)
        
        if not adapter:
            logger.warning(f"No adapter for runtime {runtime_id}, using generic")
            adapter = self._adapters.get("generic")
        
        if not adapter:
            return RuntimeOutput(
                status="failed",
                error="No adapter available",
            )
        
        try:
            # Invoke adapter
            logger.info(f"Invoking runtime: {runtime_id}")
            output = adapter.execute(state, request)
            
            # Log success
            logger.info(f"Runtime {runtime_id} completed with status: {output.status}")
            
            return output
            
        except RuntimeInvocationError as e:
            logger.error(f"Runtime invocation error: {e}")
            return self._handle_invocation_error(e, runtime_id, request)
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return RuntimeOutput(
                status="failed",
                error=str(e),
            )
    
    def _handle_invocation_error(
        self,
        error: RuntimeInvocationError,
        runtime_id: str,
        request: OrchestratorRequest,
    ) -> RuntimeOutput:
        """Handle runtime invocation error."""
        if error.is_retryable:
            # Try fallback
            logger.warning(f"Retryable error for {runtime_id}, trying fallback")
            
            # Try generic adapter
            generic = self._adapters.get("generic")
            if generic:
                try:
                    return generic.execute_fallback(request)
                except Exception as e:
                    pass
        
        return RuntimeOutput(
            status="failed",
            error=str(error),
        )
    
    def get_available_runtimes(self) -> List[str]:
        """Get list of available runtime IDs."""
        return list(self._adapters.keys())


# Global instance
_invoker: Optional[RuntimeInvoker] = None


def get_runtime_invoker() -> RuntimeInvoker:
    """Get global runtime invoker."""
    global _invoker
    if _invoker is None:
        _invoker = RuntimeInvoker()
    return _invoker


__all__ = [
    "RuntimeInvocationError",
    "RuntimeOutput",
    "RuntimeInvoker",
    "get_runtime_invoker",
]