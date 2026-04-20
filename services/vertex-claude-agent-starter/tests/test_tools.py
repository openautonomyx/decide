import pytest

from app.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_tool_execution():
    registry = ToolRegistry({"calculator", "current_datetime", "web_search_stub"})
    result = await registry.dispatch("calculator", {"expression": "2+2"})
    assert result["result"] == 4
