from typing import Dict, Any, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from src.config import settings
from src.policy.rules import ALLOWLISTED_ACTIONS, FORBIDDEN_ACTIONS, PREDICTIVE_ALLOWLISTED_ACTIONS
from src.agents.schemas import RemediationPlan

class SafetyDecision(str, Enum):
    AUTO_EXECUTE = "AUTO_EXECUTE"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    REJECTED = "REJECTED"

class PolicyEvaluationResult(BaseModel):
    decision: SafetyDecision
    allowed: bool
    confidence_score: float
    blast_radius_pct: float
    reason: str
    action_type: str

class SafetyDirector:
    """
    Deterministic Safety Policy Engine.
    Constitution Principles:
    - Blast radius > 25% requires human approval (reactive) / > 20% (predictive).
    - Diagnostic confidence < 0.85 requires human approval.
    - Actions outside allowlist are strictly REJECTED.
    - Disallowed/destructive actions are strictly REJECTED.
    """
    def __init__(self):
        self.max_blast_radius = settings.AUTO_EXECUTE_MAX_BLAST_RADIUS_PCT
        self.min_confidence = settings.AUTO_EXECUTE_MIN_CONFIDENCE
        self.predictive_max_blast_radius = settings.PREDICTIVE_BLAST_RADIUS_MAX_AUTO_PREVENT
        self.predictive_min_confidence = settings.PREDICTIVE_CONFIDENCE_THRESHOLD_AUTO_PREVENT
        self.predictive_min_risk = settings.PREDICTIVE_RISK_THRESHOLD_AUTO_PREVENT

    def evaluate(self, plan: RemediationPlan, diagnostic_confidence: float) -> PolicyEvaluationResult:
        action = plan.action_type
        blast_radius = plan.estimated_blast_radius_pct

        # 1. Check forbidden / non-allowlisted actions
        if action in FORBIDDEN_ACTIONS or action not in ALLOWLISTED_ACTIONS:
            return PolicyEvaluationResult(
                decision=SafetyDecision.REJECTED,
                allowed=False,
                confidence_score=diagnostic_confidence,
                blast_radius_pct=blast_radius,
                reason=f"Action '{action}' is not on the permitted allowlist.",
                action_type=action
            )

        # 2. Check blast radius threshold (> 25%)
        if blast_radius > self.max_blast_radius:
            return PolicyEvaluationResult(
                decision=SafetyDecision.HUMAN_APPROVAL_REQUIRED,
                allowed=True,
                confidence_score=diagnostic_confidence,
                blast_radius_pct=blast_radius,
                reason=f"Estimated blast radius ({blast_radius:.1f}%) exceeds autonomous threshold of {self.max_blast_radius:.1f}%.",
                action_type=action
            )

        # 3. Check diagnostic confidence threshold (< 0.85)
        if diagnostic_confidence < self.min_confidence:
            return PolicyEvaluationResult(
                decision=SafetyDecision.HUMAN_APPROVAL_REQUIRED,
                allowed=True,
                confidence_score=diagnostic_confidence,
                blast_radius_pct=blast_radius,
                reason=f"Diagnostic confidence ({diagnostic_confidence:.2f}) is below autonomous execution threshold of {self.min_confidence:.2f}.",
                action_type=action
            )

        # 4. Safe for autonomous execution
        return PolicyEvaluationResult(
            decision=SafetyDecision.AUTO_EXECUTE,
            allowed=True,
            confidence_score=diagnostic_confidence,
            blast_radius_pct=blast_radius,
            reason="Action conforms to all safety policies: allowlisted, blast radius <= 25%, confidence >= 0.85.",
            action_type=action
        )

    def evaluate_predictive_proposal(
        self,
        action_type: str,
        target_service: str,
        blast_radius_pct: float,
        risk_score: float,
        confidence_score: float,
    ) -> Tuple[SafetyDecision, bool, str]:
        """
        Evaluates a predictive prevention proposal against deterministic safety rules:
        - Must be in PREDICTIVE_ALLOWLISTED_ACTIONS
        - Risk score must reach PREDICTIVE_RISK_THRESHOLD_AUTO_PREVENT (>= 0.80)
        - Blast radius <= 20.0%
        - Confidence >= 0.85
        """
        if action_type not in PREDICTIVE_ALLOWLISTED_ACTIONS:
            return (
                SafetyDecision.REJECTED,
                False,
                f"Action '{action_type}' is not on the permitted predictive prevention allowlist."
            )

        if risk_score < self.predictive_min_risk:
            return (
                SafetyDecision.HUMAN_APPROVAL_REQUIRED,
                True,
                f"Risk score ({risk_score:.2f}) is below autonomous threshold ({self.predictive_min_risk:.2f}); action requires review."
            )

        if blast_radius_pct > self.predictive_max_blast_radius:
            return (
                SafetyDecision.HUMAN_APPROVAL_REQUIRED,
                True,
                f"Estimated blast radius ({blast_radius_pct:.1f}%) exceeds predictive autonomous threshold of {self.predictive_max_blast_radius:.1f}%."
            )

        if confidence_score < self.predictive_min_confidence:
            return (
                SafetyDecision.HUMAN_APPROVAL_REQUIRED,
                True,
                f"Prediction confidence ({confidence_score:.2f}) is below autonomous execution threshold of {self.predictive_min_confidence:.2f}."
            )

        return (
            SafetyDecision.AUTO_EXECUTE,
            True,
            "Action conforms to autonomous criteria: allowlisted, risk >= 0.80, blast radius <= 20%, confidence >= 0.85."
        )

safety_director = SafetyDirector()

