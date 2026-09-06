import pytest
from src.simulator.media_env import media_env, StreamState
from src.agents.investigator import ObservabilityInvestigatorAgent
from src.agents.schemas import InvestigationInput, InvestigationReport

@pytest.mark.asyncio
async def test_observability_investigator_degraded_incident():
    # Setup degraded incident state
    media_env.set_state(StreamState.DEGRADED)

    agent = ObservabilityInvestigatorAgent()
    assert agent.name == "ObservabilityInvestigator"

    input_data = InvestigationInput(
        incident_id="inc-test-401",
        event_title="India vs Australia Final",
        triggered_at=1725660000.0,
        trigger_reason="Prometheus alert HighMediaBufferRatioAlert firing"
    )

    report = await agent.investigate(input_data)
    assert isinstance(report, InvestigationReport)
    assert report.incident_id == "inc-test-401"
    assert len(report.observations) == 4 # Prometheus, Loki, Tempo, Alerts

    # Verify signals detected failure
    prom_obs = next(o for o in report.observations if o.source == "Prometheus")
    assert prom_obs.status == "CRITICAL"
    assert prom_obs.value >= 5.0

    loki_obs = next(o for o in report.observations if o.source == "Loki")
    assert loki_obs.status == "CRITICAL"

    alerts_obs = next(o for o in report.observations if o.source == "Grafana Alerts")
    assert alerts_obs.value >= 2

    # Verify root-cause ranking
    assert len(report.hypotheses) >= 1
    top_hypothesis = report.hypotheses[0]
    assert top_hypothesis.confidence >= 0.80
    assert "transcoder" in top_hypothesis.component or "transcoder" in top_hypothesis.title.lower()
    assert top_hypothesis.recommended_action == "TRAFFIC_SHIFT"
    assert len(report.investigation_summary) > 20

@pytest.mark.asyncio
async def test_observability_investigator_healthy_state():
    media_env.set_state(StreamState.HEALTHY)

    agent = ObservabilityInvestigatorAgent()
    input_data = InvestigationInput(
        incident_id="inc-test-healthy",
        event_title="India vs Australia Final",
        triggered_at=1725660000.0,
        trigger_reason="Routine telemetry sweep"
    )

    report = await agent.investigate(input_data)
    assert isinstance(report, InvestigationReport)
    prom_obs = next(o for o in report.observations if o.source == "Prometheus")
    assert prom_obs.status == "NORMAL"
    assert prom_obs.value < 1.0
