import pytest
from src.simulator.media_env import media_env, StreamState
from src.agents.remediation import RemediationAgent
from src.agents.schemas import RemediationPlan

@pytest.mark.asyncio
async def test_remediation_agent_proposal():
    agent = RemediationAgent()
    plan = await agent.propose_remediation(
        incident_id="inc-rem-101",
        primary_root_cause="Transcoder segmentation fault in worker pool pod 7b",
        target_component="transcoder-syd-01"
    )

    assert isinstance(plan, RemediationPlan)
    assert plan.incident_id == "inc-rem-101"
    assert plan.action_type == "TRAFFIC_SHIFT"
    assert plan.target_cluster == "transcoder-us-01"
    assert plan.estimated_blast_radius_pct <= 25.0
    assert plan.risk_level in ["LOW", "MEDIUM"]

@pytest.mark.asyncio
async def test_remediation_execution_traffic_shift():
    # Setup degraded environment
    media_env.reset()
    media_env.trigger_incident()
    assert media_env.state == StreamState.DEGRADED
    assert media_env.routing_weights["transcoder-us-01"] == 0.0

    agent = RemediationAgent()
    plan = RemediationPlan(
        incident_id="inc-rem-102",
        action_type="TRAFFIC_SHIFT",
        target_component="transcoder-syd-01",
        target_cluster="transcoder-us-01",
        parameters={"target_cluster": "transcoder-us-01", "shift_pct": 100.0},
        estimated_blast_radius_pct=14.7,
        risk_level="LOW",
        rationale="Divert traffic to warm standby."
    )

    result = await agent.execute_remediation(plan)
    assert result.status == "EXECUTED"
    assert media_env.state == StreamState.RECOVERED
    assert media_env.routing_weights["transcoder-us-01"] == 1.00
    assert media_env.routing_weights["transcoder-syd-01"] == 0.00
