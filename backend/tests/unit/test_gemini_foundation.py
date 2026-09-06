import pytest
from src.integrations.google_genai import GoogleGenAIClient, genai_client
from src.agents.smoke_agent import SmokeAgent, SmokeTestResponse

@pytest.mark.asyncio
async def test_google_genai_client_initialization():
    client = GoogleGenAIClient()
    assert client is not None
    # Client should be initialized in either live mode or deterministic offline mode
    assert isinstance(client.is_live, bool)

@pytest.mark.asyncio
async def test_smoke_agent_structured_execution():
    agent = SmokeAgent()
    assert agent.name == "SmokeAgent"
    assert "Smoke" in agent.get_system_instruction()

    result = await agent.run_smoke_test("Buffer ratio elevated to 8.2% on Mumbai CDN edge")
    assert isinstance(result, SmokeTestResponse)
    assert result.status in ["OK", "DEGRADED"]
    assert result.agent_name == "SmokeAgent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_findings) > 0
    assert len(result.summary) > 5

@pytest.mark.asyncio
async def test_structured_fallback_synthesis():
    client = GoogleGenAIClient()
    # Force offline invocation
    res = await client.generate_structured(
        prompt="Test prompt",
        response_schema=SmokeTestResponse,
        fallback_data={
            "status": "DEGRADED",
            "agent_name": "FallbackVerifier",
            "confidence": 0.88,
            "key_findings": ["Edge transcode failure detected"],
            "summary": "Verified fallback synthesis."
        }
    )
    assert res.status == "DEGRADED"
    assert res.confidence == 0.88
    assert res.agent_name == "FallbackVerifier"
