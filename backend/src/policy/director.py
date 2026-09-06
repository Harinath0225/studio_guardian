from typing import Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from src.config import settings
from src.policy.rules import ALLOWLISTED_ACTIONS, FORBIDDEN_ACTIONS
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
    - Blast radius > 25% requires human approval.
    - Diagnostic confidence < 0.85 requires human approval.
    - Actions outside allowlist are strictly REJECTED.
    - Disallowed/destructive actions are strictly REJECTED.
    """
    def __init__(self):
        self.max_blast_radius = settings.AUTO_EXECUTE_MAX_BLAST_RADIUS_PCT
        self.min_confidence = settings.AUTO_EXECUTE_MIN_CONFIDENCE

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

safety_director = SafetyDirector()
