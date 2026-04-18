"""
Runtime Configuration Module
Runtime Architecture v2 - Configuration for runtime selection
"""
import os
from typing import Optional
from pydantic import BaseModel, Field


class RuntimeFeatureFlags(BaseModel):
    """Feature flags for runtime selection"""
    enabled_runtimes: list[str] = Field(default_factory=lambda: [
        "openai_agents",
        "claude_agent", 
        "deep_agents",
        "crewai",
        "langchain",
    ])
    enable_task_type_detection: bool = True
    enable_runtime_fallback: bool = True
    enable_runtime_health_check: bool = False  # Phase 2
    default_fallback_order: list[str] = Field(default_factory=lambda: [
        "openai_agents",
        "langchain",
    ])


class RuntimeConfig(BaseModel):
    """Runtime configuration from environment"""
    redis_url: str = Field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    runtime_feature_flags: RuntimeFeatureFlags = Field(default_factory=RuntimeFeatureFlags)
    
    # Optional: External runtime registry URL (for distributed setup)
    registry_url: Optional[str] = None
    
    # Default timeouts
    runtime_timeout_seconds: int = 300  # 5 minutes
    checkpoint_interval_steps: int = 50
    
    # Memory feature flags
    memory_working_enabled: bool = True
    memory_episodic_enabled: bool = True
    memory_semantic_enabled: bool = False  # Requires SingleStore
    memory_cortex_enabled: bool = False  # Phase 2


def get_runtime_config() -> RuntimeConfig:
    """Get runtime configuration from environment"""
    return RuntimeConfig()


__all__ = [
    "RuntimeConfig",
    "RuntimeFeatureFlags", 
    "get_runtime_config",
]
