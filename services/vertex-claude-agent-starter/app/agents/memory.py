from typing import Protocol

from app.schemas.chat import ChatMessage


class ConversationMemory(Protocol):
    def build_messages(self, latest_user_message: str, history: list[ChatMessage]) -> list[dict]:
        ...


class SimpleConversationMemory:
    def build_messages(self, latest_user_message: str, history: list[ChatMessage]) -> list[dict]:
        messages = [{"role": msg.role, "content": msg.content} for msg in history]
        messages.append({"role": "user", "content": latest_user_message})
        return messages
