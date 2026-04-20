from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)
    system_prompt: str | None = None
    max_turns: int | None = None


class AuditLog(BaseModel):
    turns: int
    tool_calls: int
    tools_invoked: list[str]
    model: str
    token_usage: dict[str, Any] = Field(default_factory=dict)
    estimated_cost_usd: float | None = None


class ChatResponse(BaseModel):
    answer: str
    request_id: str
    audit: AuditLog


class ToolEvent(BaseModel):
    type: Literal["thinking_started", "tool_requested", "tool_completed", "answer_chunk", "completed"]
    payload: dict[str, Any]
