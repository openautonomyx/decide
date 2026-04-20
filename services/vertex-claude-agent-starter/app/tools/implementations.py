from datetime import datetime, timezone
from typing import Any

from app.tools.base import Tool, ToolSpec


class CalculatorTool(Tool):
    spec = ToolSpec(
        name="calculator",
        description="Evaluate a simple arithmetic expression.",
        input_schema={
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
        side_effecting=False,
    )

    async def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        expr = tool_input.get("expression", "")
        if not expr:
            return {"error": "expression is required"}
        try:
            value = eval(expr, {"__builtins__": {}}, {})
            return {"expression": expr, "result": value}
        except Exception as exc:
            return {"error": f"invalid expression: {exc}"}


class CurrentDatetimeTool(Tool):
    spec = ToolSpec(
        name="current_datetime",
        description="Return the current UTC datetime in ISO-8601 format.",
        input_schema={"type": "object", "properties": {}},
        side_effecting=False,
    )

    async def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        return {"utc_iso": datetime.now(timezone.utc).isoformat()}


class WebSearchStubTool(Tool):
    spec = ToolSpec(
        name="web_search_stub",
        description="Stubbed web search for controlled enterprise environments.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 5},
            },
            "required": ["query"],
        },
        side_effecting=False,
    )

    async def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        query = tool_input.get("query", "")
        top_k = int(tool_input.get("top_k", 3))
        return {
            "query": query,
            "results": [
                {
                    "title": f"Stub result {i + 1} for '{query}'",
                    "url": f"https://example.com/search/{i + 1}",
                    "snippet": "Replace with real enterprise search integration.",
                }
                for i in range(max(1, min(top_k, 5)))
            ],
        }
