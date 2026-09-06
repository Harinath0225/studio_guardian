import pytest
from src.policy.director import safety_director, SafetyDecision
from src.agents.schemas import RemediationPlan

def test_safety_director_auto_execute():
    plan = RemediationPlan(
        incident_id="inc-safe-01",
        action_type="TRAFFIC_SHIFT",
        target_component="transcoder-syd-01",
        target_cluster="transcoder-us-01",
        parameters={},
        estimated_blast_radius_pct=14.0, # <= 25%
        risk_level="LOW",
        rationale="Safe regional shift"
    )
    result = safety_director.evaluate(plan, diagnostic_confidence=0.92) # >= 0.85
    assert result.decision == SafetyDecision.AUTO_EXECUTE
    assert result.allowed is True

def test_safety_director_blast_radius_exceeded():
    plan = RemediationPlan(
        incident_id="inc-safe-02",
        action_type="TRAFFIC_SHIFT",
        target_component="transcoder-syd-01",
        target_cluster="transcoder-us-01",
        parameters={},
        estimated_blast_radius_pct=35.0, # > 25%
        risk_level="HIGH",
        rationale="Broad shift affecting multiple global zones"
    )
    result = safety_director.evaluate(plan, diagnostic_confidence=0.95)
    assert result.decision == SafetyDecision.HUMAN_APPROVAL_REQUIRED
    assert result.allowed is True
    assert "blast radius" in result.reason.lower()

def test_safety_director_low_confidence_requires_approval():
    plan = RemediationPlan(
        incident_id="inc-safe-03",
        action_type="CONTAINER_RESTART",
        target_component="edge-proxy-01",
        target_cluster="mumbai",
        parameters={},
        estimated_blast_radius_pct=10.0,
        risk_level="LOW",
        rationale="Restart proxy container"
    )
    result = safety_director.evaluate(plan, diagnostic_confidence=0.75) # < 0.85
    assert result.decision == SafetyDecision.HUMAN_APPROVAL_REQUIRED
    assert "confidence" in result.reason.lower()

def test_safety_director_forbidden_action_rejected():
    plan = RemediationPlan(
        incident_id="inc-safe-04",
        action_type="TERMINATE_ORIGIN_CLUSTER",
        target_component="origin-main",
        target_cluster="global",
        parameters={},
        estimated_blast_radius_pct=100.0,
        risk_level="HIGH",
        rationale="Dangerous shutdown"
    )
    result = safety_director.evaluate(plan, diagnostic_confidence=0.99)
    assert result.decision == SafetyDecision.REJECTED
    assert result.allowed is False
