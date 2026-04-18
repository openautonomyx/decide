"""
Runtime Module
Runtime Architecture v2 - Human-facing channel runtimes

Exports:
- types: Type definitions
- channel_runtime: Abstract channel runtime
- openai_channel_runtime: OpenAI Agents SDK implementation
"""
from app.runtime.types import (
    RuntimeType,
    TaskType,
    RuntimeCapability,
    RuntimeStatus,
    ChannelRuntimeType,
)

from app.runtime.channel_runtime import (
    ChannelRuntime,
    ChannelResponse,
    SessionContext,
    Message,
)

from app.runtime.openai_channel_runtime import (
    OpenAIChannelRuntime,
    create_openai_channel_runtime,
    get_channel_runtime,
    OPENAI_AGENTS_SDK_AVAILABLE,
)

__all__ = [
    # Types
    "RuntimeType",
    "TaskType",
    "RuntimeCapability",
    "RuntimeStatus",
    "ChannelRuntimeType",
    # Channel Runtime
    "ChannelRuntime",
    "ChannelResponse",
    "SessionContext",
    "Message",
    # OpenAI Channel
    "OpenAIChannelRuntime",
    "create_openai_channel_runtime",
    "get_channel_runtime",
    "OPENAI_AGENTS_SDK_AVAILABLE",
]