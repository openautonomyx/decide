import pytest

from app.agents.claude_agent import ClaudeEnterpriseAgent
from app.core.config import Settings
from app.schemas.chat import ChatRequest
from app.tools.registry import ToolRegistry


class FakeProvider:
    def __init__(self):
        self.calls = 0

    def generate_with_tools(self, messages, system_prompt, tools):
        self.calls += 1
        if self.calls == 1:
            return {
                "text": "",
                "tool_calls": [
                    {"id": "t1", "name": "calculator", "input": {"expression": "3*3"}},
                ],
            }
        return {"text": "The result is 9.", "tool_calls": []}

    async def stream_response(self, messages, system_prompt, tools):
        yield {"type": "answer_chunk", "payload": {"text": "The "}}


@pytest.mark.asyncio
async def test_tool_dispatch_loop():
    settings = Settings(
        service_api_key="1234567890abcdef",
        google_cloud_project="x",
        google_application_credentials="/tmp/fake.json",
    )
    agent = ClaudeEnterpriseAgent(settings, FakeProvider(), ToolRegistry({"calculator"}))
    answer, audit = await agent.run(ChatRequest(message="what is 3*3"))
    assert "9" in answer
    assert audit.tool_calls == 1
