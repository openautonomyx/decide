from abc import ABC, abstractmethod
from typing import Any, Dict


class CodingBackend(ABC):
    def __init__(self, backend_id: str, backend: Dict[str, Any]):
        self.backend_id = backend_id
        self.backend = backend
        self.config = backend.get("config", {})

    @abstractmethod
    async def run(self, task: Any) -> Dict[str, Any]:
        raise NotImplementedError


class ClaudeCodingBackend(CodingBackend):
    async def run(self, task: Any) -> Dict[str, Any]:
        return {
            "status": "success",
            "execution_mode": "stub",
            "summary": f"Selected premium coding backend for goal: {task.goal}",
            "files_changed": [],
            "artifacts": {},
            "next_actions": ["Wire this adapter to Claude Agent SDK execution"],
        }


class DevstralLiteLLMBackend(CodingBackend):
    async def run(self, task: Any) -> Dict[str, Any]:
        return {
            "status": "success",
            "execution_mode": "stub",
            "summary": f"Selected local LiteLLM coding backend for goal: {task.goal}",
            "files_changed": [],
            "artifacts": {},
            "next_actions": ["Wire this adapter to LiteLLM chat completions"],
        }


class GenericCodingBackend(CodingBackend):
    async def run(self, task: Any) -> Dict[str, Any]:
        return {
            "status": "success",
            "execution_mode": "stub",
            "summary": f"Selected generic coding backend for goal: {task.goal}",
            "files_changed": [],
            "artifacts": {},
            "next_actions": ["Add a provider-specific adapter for this backend"],
        }


def get_coding_backend(backend_id: str, backend: Dict[str, Any]) -> CodingBackend:
    provider = backend.get("config", {}).get("provider", "")
    transport = backend.get("config", {}).get("transport", "") or backend.get("transport", "")

    if provider == "anthropic":
        return ClaudeCodingBackend(backend_id, backend)
    if provider == "litellm" or transport == "openai_compatible":
        return DevstralLiteLLMBackend(backend_id, backend)
    return GenericCodingBackend(backend_id, backend)
