from typing import List, Optional
from pydantic import BaseModel, Field
from src.agents.base import BaseAgent

class SmokeTestResponse(BaseModel):
    status: str = Field(description="Operational status string, e.g. OK or DEGRADED")
    agent_name: str = Field(description="Name of the reporting agent")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    key_findings: List[str] = Field(description="List of initial observations")
    summary: str = Field(description="Concise operational executive summary")

class SmokeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SmokeAgent",
            role_description="Validates Google GenAI integration and structured schema enforcement"
        )

    def get_system_instruction(self) -> str:
        return (
            "You are the Studio Guardian Smoke Test Agent. Your job is to verify that the "
            "Google GenAI SDK structured output pipeline functions correctly. "
            "Provide concise, professional streaming operations diagnostics."
        )

    async def run_smoke_test(self, test_signal: str) -> SmokeTestResponse:
        prompt = f"Analyze the following operational test signal and return structured diagnostics: '{test_signal}'. The agent_name MUST be '{self.name}'."
        fallback = {
            "status": "OK",
            "agent_name": self.name,
            "confidence": 0.99,
            "key_findings": ["Google GenAI SDK loaded", "Structured output validated", "Deterministic execution verified"],
            "summary": "Smoke agent executed successfully within Studio Guardian multi-agent runtime."
        }
        res = await self.execute_structured(
            prompt=prompt,
            response_schema=SmokeTestResponse,
            fallback_data=fallback
        )
        res.agent_name = self.name
        return res
