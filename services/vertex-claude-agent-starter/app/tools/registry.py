from app.tools.base import Tool
from app.tools.implementations import CalculatorTool, CurrentDatetimeTool, WebSearchStubTool


class ToolRegistry:
    def __init__(self, allowlist: set[str]) -> None:
        all_tools: list[Tool] = [CalculatorTool(), CurrentDatetimeTool(), WebSearchStubTool()]
        self._tools = {tool.spec.name: tool for tool in all_tools if tool.spec.name in allowlist}

    def tool_specs_for_model(self) -> list[dict]:
        return [
            {
                "name": tool.spec.name,
                "description": tool.spec.description,
                "input_schema": tool.spec.input_schema,
            }
            for tool in self._tools.values()
        ]

    async def dispatch(self, name: str, tool_input: dict) -> dict:
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Tool '{name}' is not enabled"}
        return await tool.run(tool_input)
