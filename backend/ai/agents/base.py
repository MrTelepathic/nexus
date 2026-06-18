"""Base agent class for all AI agents."""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Base class for all Nexus AI agents.

    Each agent has:
    - A system prompt defining its role
    - Access to tools (function calling)
    - A model (can be cheap or expensive)
    - Max iterations guard
    """

    name: str
    system_prompt: str
    model: str = "gpt-4o-mini"
    max_iterations: int = 5
    tools: list = []

    @abstractmethod
    async def process(self, messages: list[dict], context: dict[str, Any]) -> str:
        """Process messages and return a response."""
        ...

    def get_system_message(self) -> dict:
        return {"role": "system", "content": self.system_prompt}
