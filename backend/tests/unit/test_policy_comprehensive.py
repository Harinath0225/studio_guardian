import pytest
from src.policy.director import safety_director, SafetyDecision
from src.agents.schemas import RemediationPlan

def test_policy_exact_boundary_blast_radius():
    # Exactly 25.0% blast radius with high confidence -> AUTO_EXECUTE
    plan = RemediationPlan(
        incident_id="test-boundary-1",
        action_type="TRAFFIC_SHIFT",
        target_component="transcoder-syd-01",
        target_cluster="transcoder-us-01",
        parameters={},
        estimated_blast_radius_pct=25.0,
        risk_level="LOW",
        rationale="Exact threshold boundary"
    )
    res = safety_director.evaluate(plan, diagnostic_confidence=0.85)
    assert res.decision == SafetyDecision.AUTO_EXECUTE
    assert res.allowed is True

def test_policy_exceeds_blast_radius_by_fraction():
    # 25.1% blast radius -> HUMAN_APPROVAL_REQUIRED
    plan = RemediationPlan(
        incident_id="test-boundary-2",
        action_type="TRAFFIC_SHIFT",
        target_component="transcoder-syd-01",
        target_cluster="transcoder-us-01",
        parameters={},
        estimated_blast_radius_pct=25.1,
        risk_level="MEDIUM",
        rationale="Exceeds threshold by 0.1%"
    )
    res = safety_director.evaluate(plan, diagnostic_confidence=0.90)
    assert res.decision == SafetyDecision.HUMAN_APPROVAL_REQUIRED
    assert res.allowed is True
    assert "blast radius" in res.reason.lower()

def test_policy_exact_boundary_confidence():
    # Exactly 0.85 confidence -> AUTO_EXECUTE
    plan = RemediationPlan(
        incident_id="test-boundary-3",
        action_type="CONTAINER_RESTART",
        target_component="edge-proxy-01",
        target_cluster="mumbai",
        parameters={},
        estimated_blast_radius_pct=10.0,
        risk_level="LOW",
        rationale="Exact confidence threshold"
    )
    res = safety_director.evaluate(plan, diagnostic_confidence=0.85)
    assert res.decision == SafetyDecision.AUTO_EXECUTE

def test_policy_below_confidence_threshold():
    # 0.849 confidence -> HUMAN_APPROVAL_REQUIRED
    plan = RemediationPlan(
        incident_id="test-boundary-4",
        action_type="CONTAINER_RESTART",
        target_component="edge-proxy-01",
        target_cluster="mumbai",
        parameters={},
        estimated_blast_radius_pct=10.0,
        risk_level="LOW",
        rationale="Slightly below confidence threshold"
    )
    res = safety_director.evaluate(plan, diagnostic_confidence=0.849)
    assert res.decision == SafetyDecision.HUMAN_APPROVAL_REQUIRED
    assert "confidence" in res.reason.lower()

def test_policy_allowlisted_actions():
    for action in ["TRAFFIC_SHIFT", "CONTAINER_RESTART", "SCALE_REPLICAS"]:
        plan = RemediationPlan(
            incident_id=f"test-allow-{action}",
            action_type=action,
            target_component="component-test",
            target_cluster="cluster-test",
            parameters={},
            estimated_blast_radius_pct=15.0,
            risk_level="LOW",
            rationale=f"Test allowlist for {action}"
        )
        res = safety_director.evaluate(plan, diagnostic_confidence=0.90)
        assert res.decision == SafetyDecision.AUTO_EXECUTE

def test_policy_forbidden_and_unknown_actions():
    forbidden_list = ["DATABASE_DROP", "FLUSH_ALL_KEYS", "TERMINATE_ORIGIN_CLUSTER", "GLOBAL_DNS_PURGE", "RANDOM_MUTATION"]
    for action in forbidden_list:
        plan = RemediationPlan(
            incident_id=f"test-forbidden-{action}",
            action_type=action,
            target_component="core-db",
            target_cluster="prod",
            parameters={},
            estimated_blast_radius_pct=1.0,
            risk_level="HIGH",
            rationale="Disallowed action test"
        )
        res = safety_director.evaluate(plan, diagnostic_confidence=0.99)
        assert res.decision == SafetyDecision.REJECTED
        assert res.allowed is False
