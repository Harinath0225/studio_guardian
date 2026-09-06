import pytest
from pydantic import ValidationError
from src.agents.schemas import (
    TelemetryEvidence,
    RootCauseHypothesis,
    InvestigationInput,
    InvestigationReport,
    BusinessImpactInput,
    BusinessImpactAssessment,
    RemediationPlan,
    RemediationExecutionResult,
    VerificationInput,
    VerificationVerdict
)

def test_telemetry_evidence_schema():
    ev = TelemetryEvidence(
        source="Prometheus",
        signal_name="media_playback_buffer_ratio",
        value=8.7,
        status="CRITICAL",
        timestamp=1725660000.0
    )
    assert ev.source == "Prometheus"
    assert ev.status == "CRITICAL"

def test_root_cause_hypothesis_confidence_bounds():
    # Confidence must be between 0.0 and 1.0
    with pytest.raises(ValidationError):
        RootCauseHypothesis(
            title="Invalid confidence hypothesis",
            component="transcoder-syd-01",
            confidence=1.5, # Exceeds 1.0
            supporting_evidence=["err"],
            recommended_action="TRAFFIC_SHIFT"
        )

    with pytest.raises(ValidationError):
        RootCauseHypothesis(
            title="Negative confidence hypothesis",
            component="transcoder-syd-01",
            confidence=-0.1,
            supporting_evidence=["err"],
            recommended_action="TRAFFIC_SHIFT"
        )

def test_business_impact_schemas():
    inp = BusinessImpactInput(
        incident_id="inc-1",
        total_viewers=12400000,
        affected_regions=["AU", "SG"],
        playback_error_rate_pct=8.7,
        incident_duration_seconds=300.0
    )
    assert inp.total_viewers == 12400000

    assessment = BusinessImpactAssessment(
        incident_id="inc-1",
        affected_viewers=1820000,
        affected_vip_viewers=72800,
        ad_revenue_at_risk_usd=18750.0,
        sla_breach_risk="CRITICAL",
        sla_penalty_exposure_usd=37500.0,
        executive_summary="Critical playback degradation",
        recommendation_urgency="IMMEDIATE"
    )
    assert assessment.sla_breach_risk == "CRITICAL"

def test_remediation_plan_blast_radius_bounds():
    with pytest.raises(ValidationError):
        RemediationPlan(
            incident_id="inc-1",
            action_type="TRAFFIC_SHIFT",
            target_component="transcoder",
            target_cluster="cluster",
            parameters={},
            estimated_blast_radius_pct=105.0, # Exceeds 100.0
            risk_level="HIGH",
            rationale="Invalid"
        )

def test_verification_verdict_schema():
    verdict = VerificationVerdict(
        incident_id="inc-1",
        recovered=True,
        current_playback_error_rate_pct=0.38,
        current_transcoder_latency_ms=19.2,
        error_rate_delta_pct=8.32,
        latency_delta_pct=465.8,
        status_summary="Recovered nominal operation",
        recommendation="RESOLVE_INCIDENT"
    )
    assert verdict.recovered is True
    assert verdict.recommendation == "RESOLVE_INCIDENT"
