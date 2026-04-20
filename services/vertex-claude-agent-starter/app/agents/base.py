from abc import ABC, abstractmethod

from app.schemas.chat import AuditLog, ChatRequest


class BaseAgent(ABC):
    @abstractmethod
    async def run(self, request: ChatRequest) -> tuple[str, AuditLog]:
        raise NotImplementedError
