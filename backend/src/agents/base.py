from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Any, Dict
from pydantic import BaseModel
from src.integrations.google_genai import genai_client, GoogleGenAIClient

T = TypeVar("T", bound=BaseModel)

class BaseAgent(ABC):
    """
    Abstract Base Class for all specialist agents in Studio Guardian.
    Guarantees:
    - Dedicated specialist role and system instruction
    - Pydantic v2 structured output validation
    - Deterministic fallbacks for offline demo reproducibility
    - Clean separation of concerns (no monolithic single agent)
    """

    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description
        self.ai_client: GoogleGenAIClient = genai_client

    @abstractmethod
    def get_system_instruction(self) -> str:
        """Returns the specific persona and rule set for this agent."""
        pass

    async def execute_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        fallback_data: Optional[Dict[str, Any]] = None
    ) -> T:
        """
        Executes a prompt against Gemini with the agent's system instruction,
        validating and enforcing strict Pydantic v2 output.
        """
        system_instruction = self.get_system_instruction()
        return await self.ai_client.generate_structured(
            prompt=prompt,
            response_schema=response_schema,
            system_instruction=system_instruction,
            fallback_data=fallback_data
        )
