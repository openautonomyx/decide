"""
Worker Runtime Registry and Selection Policy
Runtime Architecture v2 - Additive layer on top of control plane
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RuntimeType(str, Enum):
    """Supported worker runtime types"""
    LANGGRAPH_ORCHESTRATOR = "langgraph"
    OPENAI_AGENTS_SDK = "openai_agents"
    CLAUDE_AGENT_SDK = "claude_agent"
    DEEP_AGENTS = "deep_agents"
    CREWAI = "crewai"
    LANGCHAIN = "langchain"


class RuntimeCapability(BaseModel):
    """Runtime capability definition"""
    tags: list[str] = Field(default_factory=list)  # coding, research, conversation, autonomous
    max_context_tokens: int = 200000
    supports_streaming: bool = False
    supports_tools: bool = True
    supports_checkpoint: bool = False
    supports_parallel: bool = False
    supports_mcp: bool = False


class WorkerRuntime(BaseModel):
    """Worker runtime configuration"""
    runtime_id: str
    runtime_type: RuntimeType
    backend_provider: Optional[str] = None  # openai, anthropic, etc.
    backend_model: Optional[str] = None  # gemma3:27b, claude-3, etc.
    endpoint_url: Optional[str] = None
    config: dict = Field(default_factory=dict)
    capabilities: RuntimeCapability = Field(default_factory=RuntimeCapability)
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class RuntimeSelectionRule(BaseModel):
    """Rule for runtime selection"""
    task_type: str  # coding, conversation, autonomous, collaboration, simple
    preferred_runtime: RuntimeType
    fallback_runtime: Optional[RuntimeType] = None
    reason: str = ""
    enabled: bool = True


class RuntimeSelectionPolicy(BaseModel):
    """Tenant-configurable runtime selection policy"""
    policy_id: str
    tenant_id: str
    rules: list[RuntimeSelectionRule] = Field(default_factory=list)
    default_for_unknown: RuntimeType = RuntimeType.OPENAI_AGENTS_SDK
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Default runtime selection policies
DEFAULT_RUNTIME_POLICIES = {
    "coding": RuntimeSelectionRule(
        task_type="coding",
        preferred_runtime=RuntimeType.CLAUDE_AGENT_SDK,
        fallback_runtime=RuntimeType.LANGCHAIN,
        reason="Premium coding requires strong reasoning"
    ),
    "conversation": RuntimeSelectionRule(
        task_type="conversation",
        preferred_runtime=RuntimeType.OPENAI_AGENTS_SDK,
        fallback_runtime=RuntimeType.LANGCHAIN,
        reason="Human-facing interaction needs OpenAI SDK"
    ),
    "autonomous": RuntimeSelectionRule(
        task_type="autonomous",
        preferred_runtime=RuntimeType.DEEP_AGENTS,
        fallback_runtime=RuntimeType.CREWAI,
        reason="Long-running execution with checkpoints"
    ),
    "collaboration": RuntimeSelectionRule(
        task_type="collaboration",
        preferred_runtime=RuntimeType.CREWAI,
        fallback_runtime=RuntimeType.LANGCHAIN,
        reason="Flat volunteer/student team collaboration"
    ),
    "simple": RuntimeSelectionRule(
        task_type="simple",
        preferred_runtime=RuntimeType.LANGCHAIN,
        fallback_runtime=None,
        reason="Lightweight retrieval task"
    ),
}


class WorkerRuntimeRegistry:
    """In-memory runtime registry (can be backed by DB)"""
    
    def __init__(self):
        self._runtimes: dict[str, WorkerRuntime] = {}
        self._policies: dict[str, RuntimeSelectionPolicy] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize with default runtimes"""
        # OpenAI Agents SDK - human-facing
        self.register_runtime(WorkerRuntime(
            runtime_id="openai_agents",
            runtime_type=RuntimeType.OPENAI_AGENTS_SDK,
            backend_provider="openai",
            backend_model="gemma3:27b",
            capabilities=RuntimeCapability(
                tags=["conversation", "general"],
                supports_streaming=True,
                supports_tools=True,
                supports_mcp=True
            ),
            cost_per_1k_input=0.005,
            cost_per_1k_output=0.015
        ))
        
        # Claude Agent SDK - premium coding/research
        self.register_runtime(WorkerRuntime(
            runtime_id="claude_agent",
            runtime_type=RuntimeType.CLAUDE_AGENT_SDK,
            backend_provider="anthropic",
            backend_model="claude-sonnet-4-20250514",
            capabilities=RuntimeCapability(
                tags=["coding", "research"],
                max_context_tokens=200000,
                supports_streaming=True,
                supports_tools=True,
                supports_checkpoint=True
            ),
            cost_per_1k_input=0.003,
            cost_per_1k_output=0.015
        ))
        
        # Deep Agents - long-running
        self.register_runtime(WorkerRuntime(
            runtime_id="deep_agents",
            runtime_type=RuntimeType.DEEP_AGENTS,
            backend_provider="openai",
            backend_model="gemma3:27b",
            capabilities=RuntimeCapability(
                tags=["autonomous", "research"],
                supports_streaming=True,
                supports_tools=True,
                supports_checkpoint=True,
                supports_parallel=True
            ),
            cost_per_1k_input=0.01,
            cost_per_1k_output=0.03
        ))
        
        # CrewAI - collaborative
        self.register_runtime(WorkerRuntime(
            runtime_id="crewai",
            runtime_type=RuntimeType.CREWAI,
            backend_provider="openai",
            backend_model="gemma3:27b",
            capabilities=RuntimeCapability(
                tags=["collaboration", "research"],
                supports_tools=True,
                supports_parallel=True
            ),
            cost_per_1k_input=0.005,
            cost_per_1k_output=0.015
        ))
        
        # LangChain - lightweight
        self.register_runtime(WorkerRuntime(
            runtime_id="langchain",
            runtime_type=RuntimeType.LANGCHAIN,
            backend_provider="openai",
            backend_model="gemma3:27b",
            capabilities=RuntimeCapability(
                tags=["simple", "retrieval"],
                max_context_tokens=128000,
                supports_tools=True
            ),
            cost_per_1k_input=0.00015,
            cost_per_1k_output=0.0006
        ))
    
    def register_runtime(self, runtime: WorkerRuntime):
        """Register a runtime"""
        self._runtimes[runtime.runtime_id] = runtime
    
    def get_runtime(self, runtime_id: str) -> Optional[WorkerRuntime]:
        """Get runtime by ID"""
        return self._runtimes.get(runtime_id)
    
    def list_runtimes(self, enabled_only: bool = True) -> list[WorkerRuntime]:
        """List available runtimes"""
        runtimes = list(self._runtimes.values())
        if enabled_only:
            runtimes = [r for r in runtimes if r.enabled]
        return runtimes
    
    def select_runtime(
        self,
        task_type: str,
        tenant_id: str,
        policy: Optional[RuntimeSelectionPolicy] = None
    ) -> WorkerRuntime:
        """Select runtime based on task type and policy"""
        # Use policy if provided, otherwise defaults
        rules = policy.rules if policy else []
        
        # Find matching rule
        for rule in rules:
            if rule.task_type == task_type and rule.enabled:
                runtime = self.get_runtime(rule.preferred_runtime.value)
                if runtime and runtime.enabled:
                    return runtime
        
        # Fall back to default policies
        default = DEFAULT_RUNTIME_POLICIES.get(task_type)
        if default:
            runtime = self.get_runtime(default.preferred_runtime.value)
            if runtime and runtime.enabled:
                return runtime
        
        # Ultimate fallback to OpenAI Agents
        return self.get_runtime("openai_agents") or self.list_runtimes()[0]
    
    def set_policy(self, policy: RuntimeSelectionPolicy):
        """Set tenant policy"""
        self._policies[policy.tenant_id] = policy
    
    def get_policy(self, tenant_id: str) -> Optional[RuntimeSelectionPolicy]:
        """Get tenant policy"""
        return self._policies.get(tenant_id)


# Global registry instance
registry = WorkerRuntimeRegistry()


async def get_runtime_registry() -> WorkerRuntimeRegistry:
    """Dependency for getting runtime registry"""
    return registry


async def select_runtime(
    task_type: str,
    tenant_id: str,
    registry: WorkerRuntimeRegistry = None
) -> WorkerRuntime:
    """Convenience function for runtime selection"""
    if registry is None:
        registry = WorkerRuntimeRegistry()
    
    policy = registry.get_policy(tenant_id)
    return registry.select_runtime(task_type, tenant_id, policy)


# Task type detection heuristics
def detect_task_type(goal: str, capability: Optional[str] = None) -> str:
    """
    Detect task type from execution request goal and capability.
    This is a heuristic - actual typing could come from LLM classification.
    """
    goal_lower = goal.lower()
    
    # Explicit capability takes precedence
    if capability:
        capability_lower = capability.lower()
        if "code" in capability_lower or "coding" in capability_lower:
            return "coding"
        if "research" in capability_lower:
            return "research"
        if "conversation" in capability_lower or "chat" in capability_lower:
            return "conversation"
    
    # Heuristics from goal
    if any(kw in goal_lower for kw in ["refactor", "implement", "fix", "debug", "write code", "create function"]):
        return "coding"
    
    if any(kw in goal_lower for kw in ["research", "analyze", "find information", "search"]):
        return "research"
    
    if any(kw in goal_lower for kw in ["collaborate", "team", "work together", "group"]):
        return "collaboration"
    
    if any(kw in goal_lower for kw in ["explain", "what", "how do", "list", "show me"]):
        return "conversation"
    
    # Check for long-running patterns
    if any(kw in goal_lower for kw in ["comprehensive", "entire", "full", "complete analysis"]):
        return "autonomous"
    
    # Default to conversation
    return "conversation"


__all__ = [
    "RuntimeType",
    "RuntimeCapability", 
    "WorkerRuntime",
    "RuntimeSelectionRule",
    "RuntimeSelectionPolicy",
    "WorkerRuntimeRegistry",
    "DEFAULT_RUNTIME_POLICIES",
    "registry",
    "get_runtime_registry",
    "select_runtime",
    "detect_task_type",
]