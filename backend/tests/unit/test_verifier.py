import pytest
from src.simulator.media_env import media_env, StreamState
from src.agents.verifier import VerificationAgent
from src.agents.schemas import VerificationInput, VerificationVerdict

@pytest.mark.asyncio
async def test_verification_agent_successful_recovery():
    # Setup recovered state
    media_env.reset()
    media_env.apply_traffic_shift(target_cluster="transcoder-us-01", shift_pct=100.0)
    assert media_env.state == StreamState.RECOVERED

    agent = VerificationAgent()
    input_data = VerificationInput(
        incident_id="inc-verif-01",
        action_executed="TRAFFIC_SHIFT: transcoder-us-01 (100%)",
        pre_remediation_error_rate=8.7,
        pre_remediation_latency=485.0
    )

    verdict = await agent.verify_recovery(input_data)
    assert isinstance(verdict, VerificationVerdict)
    assert verdict.recovered is True
    assert verdict.current_playback_error_rate_pct < 1.0
    assert verdict.error_rate_delta_pct > 7.0
    assert verdict.recommendation == "RESOLVE_INCIDENT"
    assert "confirmed healthy" in verdict.status_summary.lower()

@pytest.mark.asyncio
async def test_verification_agent_failed_recovery():
    # Force failure injection
    media_env.reset()
    media_env.trigger_incident()
    media_env.force_recovery_failure = True
    media_env.apply_traffic_shift(target_cluster="transcoder-us-01", shift_pct=100.0)
    # State remains degraded
    assert media_env.state == StreamState.DEGRADED

    agent = VerificationAgent()
    input_data = VerificationInput(
        incident_id="inc-verif-02",
        action_executed="TRAFFIC_SHIFT: transcoder-us-01 (100%)",
        pre_remediation_error_rate=8.7,
        pre_remediation_latency=485.0
    )

    verdict = await agent.verify_recovery(input_data)
    assert verdict.recovered is False
    assert verdict.current_playback_error_rate_pct >= 5.0
    assert verdict.recommendation == "REINVESTIGATE"
    assert "persistent degradation" in verdict.status_summary.lower()
