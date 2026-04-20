import logging
from collections.abc import AsyncGenerator
from typing import Any

from app.core.config import Settings

logger = logging.getLogger("claude_vertex_provider")


class ClaudeVertexProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None

    def _client_or_raise(self):
        if self._client:
            return self._client
        try:
            from anthropic import AnthropicVertex
        except ImportError as exc:
            raise RuntimeError("anthropic SDK with vertex extras is required") from exc

        self._client = AnthropicVertex(
            project_id=self.settings.google_cloud_project,
            region=self.settings.resolved_vertex_region,
            timeout=self.settings.request_timeout_seconds,
        )
        return self._client

    def _normalize_content(self, content_blocks: list[Any]) -> str:
        return "\n".join(
            getattr(block, "text", "")
            for block in content_blocks
            if getattr(block, "type", "") == "text"
        ).strip()

    def _extract_tool_calls(self, content_blocks: list[Any]) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []
        for block in content_blocks:
            if getattr(block, "type", "") == "tool_use":
                calls.append(
                    {
                        "id": getattr(block, "id", ""),
                        "name": getattr(block, "name", ""),
                        "input": getattr(block, "input", {}),
                    }
                )
        return calls

    def generate_with_tools(
        self, messages: list[dict[str, Any]], system_prompt: str, tools: list[dict]
    ) -> dict[str, Any]:
        client = self._client_or_raise()
        logger.info("model.call.start model=%s with_tools=%s", self.settings.claude_model, bool(tools))
        response = client.messages.create(
            model=self.settings.claude_model,
            max_tokens=1024,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )
        logger.info("model.call.done stop_reason=%s", response.stop_reason)
        return {
            "text": self._normalize_content(response.content),
            "tool_calls": self._extract_tool_calls(response.content),
            "raw": response,
        }

    def generate_response(self, messages: list[dict[str, Any]], system_prompt: str) -> dict[str, Any]:
        return self.generate_with_tools(messages=messages, system_prompt=system_prompt, tools=[])

    async def stream_response(
        self,
        messages: list[dict[str, Any]],
        system_prompt: str,
        tools: list[dict],
    ) -> AsyncGenerator[dict[str, Any], None]:
        client = self._client_or_raise()
        with client.messages.stream(
            model=self.settings.claude_model,
            max_tokens=1024,
            system=system_prompt,
            tools=tools,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield {"type": "answer_chunk", "payload": {"text": text}}
