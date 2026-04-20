from functools import lru_cache

from app.agents.claude_agent import ClaudeEnterpriseAgent
from app.core.config import get_settings
from app.services.claude_vertex_provider import ClaudeVertexProvider
from app.tools.registry import ToolRegistry


@lru_cache(maxsize=1)
def get_agent() -> ClaudeEnterpriseAgent:
    settings = get_settings()
    provider = ClaudeVertexProvider(settings)
    registry = ToolRegistry(settings.tool_allowlist)
    return ClaudeEnterpriseAgent(settings=settings, provider=provider, tool_registry=registry)
