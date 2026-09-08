import pytest
from src.simulator.media_env import media_env, StreamState
from src.agents.predictive_risk_agent import PredictiveRiskAgent
from src.prediction.schemas import PredictiveStatusResponse

@pytest.mark.asyncio
async def test_predictive_risk_agent_healthy_state():
    media_env.set_state(StreamState.HEALTHY)
    agent = PredictiveRiskAgent()
    assert agent.name == "PredictiveRiskAgent"

    status = await agent.evaluate_operational_risk()
    assert isinstance(status, PredictiveStatusResponse)
    assert status.state == "HEALTHY"
    assert status.risk_score < 0.40
    assert status.risk_level in ["HEALTHY", "WATCH", "LOW"]
    assert status.confidence_score >= 0.50
    assert status.runtime_metadata.active_agent == "PredictiveRiskAgent"
    assert "Vertex AI" in status.runtime_metadata.agent_engine
    assert len(status.contributors) >= 4

@pytest.mark.asyncio
async def test_predictive_risk_agent_surge_saturation():
    # Set to LOAD_SURGE in media_env
    media_env.set_state(StreamState.LOAD_SURGE)
    agent = PredictiveRiskAgent()

    status = await agent.evaluate_operational_risk()
    assert isinstance(status, PredictiveStatusResponse)
    assert status.state in ["HIGH_RISK", "IMMINENT_RISK", "ELEVATED_RISK"]


    assert status.risk_score >= 0.60
    assert status.predicted_failure_mode is not None
    assert "transcoder" in status.predicted_failure_mode.lower() or "saturation" in status.predicted_failure_mode.lower() or "capacity" in status.predicted_failure_mode.lower()
    assert status.failure_hypothesis is not None
    assert len(status.failure_hypothesis) > 10
    assert status.estimated_window_minutes is not None
    assert status.estimated_window_minutes.min >= 1
    assert status.estimated_window_minutes.max <= 30
    assert len(status.contributors) >= 4
