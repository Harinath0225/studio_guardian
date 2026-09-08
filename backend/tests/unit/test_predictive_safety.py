import pytest
from src.policy.director import safety_director, SafetyDecision
from src.prediction.schemas import PreventionProposalResponse

def test_predictive_safety_director_auto_execute():
    # Meets all autonomous criteria:
    # risk >= 0.80, confidence >= 0.85, blast_radius <= 20.0%, allowlisted action
    decision, allowed, reason = safety_director.evaluate_predictive_proposal(
        action_type="scale_transcoder_pool",
        target_service="transcoder-pool",
        blast_radius_pct=15.0,
        risk_score=0.85,
        confidence_score=0.90
    )
    assert decision == SafetyDecision.AUTO_EXECUTE
    assert allowed is True
    assert "conforms to autonomous criteria" in reason.lower() or "auto" in reason.lower()

def test_predictive_safety_director_blast_radius_exceeded():
    # Blast radius 25% > 20% max -> requires human approval
    decision, allowed, reason = safety_director.evaluate_predictive_proposal(
        action_type="scale_transcoder_pool",
        target_service="transcoder-pool",
        blast_radius_pct=25.0,
        risk_score=0.85,
        confidence_score=0.90
    )
    assert decision == SafetyDecision.HUMAN_APPROVAL_REQUIRED
    assert allowed is True
    assert "blast radius" in reason.lower()

def test_predictive_safety_director_low_confidence():
    # Confidence 0.75 < 0.85 min -> requires human approval
    decision, allowed, reason = safety_director.evaluate_predictive_proposal(
        action_type="scale_transcoder_pool",
        target_service="transcoder-pool",
        blast_radius_pct=12.0,
        risk_score=0.85,
        confidence_score=0.75
    )
    assert decision == SafetyDecision.HUMAN_APPROVAL_REQUIRED
    assert allowed is True
    assert "confidence" in reason.lower()

def test_predictive_safety_director_unallowlisted_action():
    decision, allowed, reason = safety_director.evaluate_predictive_proposal(
        action_type="terminate_active_encoders",
        target_service="transcoder-pool",
        blast_radius_pct=5.0,
        risk_score=0.90,
        confidence_score=0.95
    )
    assert decision == SafetyDecision.REJECTED
    assert allowed is False
    assert "allowlist" in reason.lower()

def test_predictive_safety_director_low_risk_gated():
    # Risk 0.65 < 0.80 min for auto-prevention -> does not auto-execute
    decision, allowed, reason = safety_director.evaluate_predictive_proposal(
        action_type="scale_transcoder_pool",
        target_service="transcoder-pool",
        blast_radius_pct=15.0,
        risk_score=0.65,
        confidence_score=0.90
    )
    assert decision in [SafetyDecision.HUMAN_APPROVAL_REQUIRED, SafetyDecision.REJECTED]
    assert "risk" in reason.lower()
