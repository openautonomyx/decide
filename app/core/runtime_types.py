"""
Runtime Types Module
Runtime Architecture v2 - Type definitions for runtime selection
"""
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


class TaskType(str, Enum):
    """Task type categories for runtime selection"""
    CODING = "coding"
    CONVERSATION = "conversation"
    AUTONOMOUS = "autonomous"
    COLLABORATION = "collaboration"
    RESEARCH = "research"
    SIMPLE = "simple"


class RuntimeCapability(BaseModel):
    """Runtime capability definition"""
    tags: list[str] = Field(default_factory=list)
    max_context_tokens: int = 200000
    supports_streaming: bool = False
    supports_tools: bool = True
    supports_checkpoint: bool = False
    supports_parallel: bool = False
    supports_mcp: bool = False


class RuntimeStatus(str, Enum):
    """Runtime health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


__all__ = [
    "RuntimeType",
    "TaskType",
    "RuntimeCapability", 
    "RuntimeStatus",
]
