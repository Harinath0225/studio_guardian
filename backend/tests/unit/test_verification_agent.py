import pytest
from src.simulator.media_env import media_env, StreamState
from src.agents.verifier import VerificationAgent

@pytest.mark.asyncio
async def test_verification_agent_preventive_verification():
    agent = VerificationAgent()
    assert agent.name == "VerificationAgent"

    # Simulate pre-action surge state (GPU 93.4%, Latency 470ms, Risk 0.85)
    pre_metrics = {
        "gpu_utilization_pct": 93.4,
        "transcoder_latency_ms": 470.0,
        "queue_depth": 48,
        "playback_error_rate_pct": 0.48,
        "risk_score": 0.85
    }

    # Execute scaling in media env to reach Step 4 (PREVENTED)
    media_env.scale_transcoder_pool(scale_factor=2.0)

    # Verify prevention
    result = await agent.verify_prevention(
        action_id="act-test-01",
        pre_action_metrics=pre_metrics
    )

    assert result["verdict"] == "VERIFIED_SUCCESSFUL"
    assert result["comparison"]["gpu_utilization_pct"]["delta"] <= -20.0
    assert result["comparison"]["risk_score"]["after"] < 0.35
    assert result["counterfactual"]["estimated_exposure_avoided"] > 10000.0
