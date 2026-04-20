import json
import logging
from collections.abc import AsyncGenerator

from app.agents.base import BaseAgent
from app.agents.memory import ConversationMemory, SimpleConversationMemory
from app.agents.policy import BasePolicy, InputLengthPolicy
from app.core.config import Settings
from app.schemas.chat import AuditLog, ChatRequest
from app.services.claude_vertex_provider import ClaudeVertexProvider
from app.tools.registry import ToolRegistry

logger = logging.getLogger("claude_agent")


class ClaudeEnterpriseAgent(BaseAgent):
    def __init__(
        self,
        settings: Settings,
        provider: ClaudeVertexProvider,
        tool_registry: ToolRegistry,
        memory: ConversationMemory | None = None,
        policies: list[BasePolicy] | None = None,
    ) -> None:
        self.settings = settings
        self.provider = provider
        self.tool_registry = tool_registry
        self.memory = memory or SimpleConversationMemory()
        self.policies = policies or [InputLengthPolicy(settings.max_input_chars)]

    def _resolve_system_prompt(self, request: ChatRequest) -> str:
        return request.system_prompt or self.settings.enterprise_system_prompt

    def _policy_check(self, text: str) -> None:
        for policy in self.policies:
            decision = policy.evaluate(text)
            if not decision.allowed:
                raise ValueError(decision.reason or "Blocked by policy")

    async def run(self, request: ChatRequest) -> tuple[str, AuditLog]:
        self._policy_check(request.message)
        messages = self.memory.build_messages(request.message, request.history)
        system_prompt = self._resolve_system_prompt(request)

        turns = 0
        tool_calls = 0
        tools_invoked: list[str] = []
        max_turns = request.max_turns or self.settings.max_turns

        while turns < max_turns:
            turns += 1
            result = self.provider.generate_with_tools(
                messages=messages,
                system_prompt=system_prompt,
                tools=self.tool_registry.tool_specs_for_model(),
            )
            if not result["tool_calls"]:
                text = result["text"] or ""
                audit = AuditLog(
                    turns=turns,
                    tool_calls=tool_calls,
                    tools_invoked=tools_invoked,
                    model=self.settings.claude_model,
                    token_usage={},
                    estimated_cost_usd=None,
                )
                return text, audit

            assistant_content = []
            if result["text"]:
                assistant_content.append({"type": "text", "text": result["text"]})
            for tc in result["tool_calls"]:
                assistant_content.append(
                    {"type": "tool_use", "id": tc["id"], "name": tc["name"], "input": tc["input"]}
                )

            messages.append({"role": "assistant", "content": assistant_content})

            for tc in result["tool_calls"]:
                if tool_calls >= self.settings.max_tool_calls:
                    raise ValueError("Exceeded max tool calls")
                tool_calls += 1
                tools_invoked.append(tc["name"])
                logger.info("tool.call tool=%s tool_input=%s", tc["name"], tc["input"])
                tool_result = await self.tool_registry.dispatch(tc["name"], tc["input"])
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tc["id"],
                                "content": json.dumps(tool_result),
                            }
                        ],
                    }
                )

        raise ValueError("Max turns reached without final answer")

    async def stream_run(self, request: ChatRequest) -> AsyncGenerator[dict, None]:
        self._policy_check(request.message)
        messages = self.memory.build_messages(request.message, request.history)
        system_prompt = self._resolve_system_prompt(request)
        turns = 0
        tool_calls = 0

        while turns < (request.max_turns or self.settings.max_turns):
            turns += 1
            yield {"type": "thinking_started", "payload": {"turn": turns}}
            result = self.provider.generate_with_tools(
                messages=messages,
                system_prompt=system_prompt,
                tools=self.tool_registry.tool_specs_for_model(),
            )

            if result["tool_calls"]:
                assistant_content = []
                if result["text"]:
                    assistant_content.append({"type": "text", "text": result["text"]})
                for tc in result["tool_calls"]:
                    yield {"type": "tool_requested", "payload": tc}
                    tool_calls += 1
                    tool_result = await self.tool_registry.dispatch(tc["name"], tc["input"])
                    yield {"type": "tool_completed", "payload": {"name": tc["name"], "result": tool_result}}
                    assistant_content.append(
                        {"type": "tool_use", "id": tc["id"], "name": tc["name"], "input": tc["input"]}
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tc["id"],
                                    "content": json.dumps(tool_result),
                                }
                            ],
                        }
                    )
                messages.append({"role": "assistant", "content": assistant_content})
                continue

            async for event in self.provider.stream_response(
                messages=messages,
                system_prompt=system_prompt,
                tools=[],
            ):
                yield event
            yield {
                "type": "completed",
                "payload": {"turns": turns, "tool_calls": tool_calls, "model": self.settings.claude_model},
            }
            return

        raise ValueError("Max turns reached without final answer")
