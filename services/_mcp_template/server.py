"""
MCP template — FastMCP over SSE.

Each MCP service in services/*-mcp/ copies this file and replaces:
  - SERVICE_NAME
  - base URL + auth env vars
  - tool implementations
"""
import os
import httpx
from mcp.server.fastmcp import FastMCP

SERVICE_NAME = os.environ.get("MCP_SERVICE_NAME", "template")
BASE_URL = os.environ.get("MCP_BASE_URL", "")
API_TOKEN = os.environ.get("MCP_API_TOKEN", "")
BIND_HOST = os.environ.get("MCP_BIND_HOST", "0.0.0.0")
BIND_PORT = int(os.environ.get("MCP_BIND_PORT", "3100"))

mcp = FastMCP(SERVICE_NAME, host=BIND_HOST, port=BIND_PORT)


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if API_TOKEN:
        h["Authorization"] = f"Bearer {API_TOKEN}"
    return h


def _get(path: str, params: dict | None = None) -> dict:
    r = httpx.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict | None = None) -> dict:
    r = httpx.post(f"{BASE_URL}{path}", headers=_headers(), json=body, timeout=30)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def health() -> dict:
    return {"service": SERVICE_NAME, "base_url": BASE_URL, "ok": True}


if __name__ == "__main__":
    mcp.run(transport="sse")
