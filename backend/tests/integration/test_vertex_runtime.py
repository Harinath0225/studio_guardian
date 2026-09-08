import pytest
from src.integrations.google_genai import genai_client
from pydantic import BaseModel

class DummyResponse(BaseModel):
    summary: str
    risk: float

@pytest.mark.asyncio
async def test_vertex_runtime_execution():
    runtime_info = genai_client.get_runtime_info()
    assert "agent_runtime" in runtime_info
    
    resp = await genai_client.generate_structured(
        prompt="Output a summary saying System stable with risk 0.1",
        response_schema=DummyResponse,
        fallback_data={"summary": "System stable", "risk": 0.1}
    )
    
    assert resp.summary
    assert resp.risk is not None