"""
MCP tool loader — connects to SSE MCP servers, exposes tools to LangGraph workers.

Registry reads MCP endpoints from env (MCP_FLEET_ENDPOINTS as JSON) or config,
connects via mcp.client.sse, lists tools, and produces LangChain-compatible
tools for ReAct workers.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass
class MCPEndpoint:
    name: str        # e.g. "liferay"
    url: str         # e.g. "http://liferay-mcp:3101/sse"
    tool_hint: str   # e.g. "publish" — matches planner tool_hint taxonomy


def load_endpoints() -> list[MCPEndpoint]:
    raw = os.environ.get("MCP_FLEET_ENDPOINTS", "[]")
    return [MCPEndpoint(**e) for e in json.loads(raw)]


async def connect_and_list_tools(endpoint: MCPEndpoint) -> list[dict]:
    """Task #3: connect via mcp.client.sse, return tool schemas."""
    raise NotImplementedError("Task #3")


async def bind_tools_for_worker(tool_hint: str) -> list:
    """Filter endpoints by tool_hint, return LangChain tools for a worker subtask."""
    raise NotImplementedError("Task #3")
