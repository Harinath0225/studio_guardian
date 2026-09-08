import pytest
from src.policy.director import safety_director, SafetyDecision

def test_human_approval_gate_blast_radius_threshold():
    decision, allowed, reason = safety_director.evaluate_predictive_proposal(
        action_type="scale_transcoder_pool",
        target_service="transcoder-worker-pool",
        blast_radius_pct=24.5, # > 20.0%
        risk_score=0.88,
        confidence_score=0.92
    )
    assert decision == SafetyDecision.HUMAN_APPROVAL_REQUIRED
    assert allowed is True
    assert "blast radius" in reason.lower()

def test_human_approval_gate_confidence_threshold():
    decision, allowed, reason = safety_director.evaluate_predictive_proposal(
        action_type="scale_transcoder_pool",
        target_service="transcoder-worker-pool",
        blast_radius_pct=14.0, # <= 20.0%
        risk_score=0.85,
        confidence_score=0.79 # < 0.85
    )
    assert decision == SafetyDecision.HUMAN_APPROVAL_REQUIRED
    assert allowed is True
    assert "confidence" in reason.lower()

def test_human_approval_gate_unallowlisted_action_rejected():
    decision, allowed, reason = safety_director.evaluate_predictive_proposal(
        action_type="drop_all_transcoding_sessions",
        target_service="transcoder-worker-pool",
        blast_radius_pct=5.0,
        risk_score=0.95,
        confidence_score=0.95
    )
    assert decision == SafetyDecision.REJECTED
    assert allowed is False
    assert "allowlist" in reason.lower()
