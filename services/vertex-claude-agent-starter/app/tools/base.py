from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    side_effecting: bool = False


class Tool(ABC):
    spec: ToolSpec

    @abstractmethod
    async def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
