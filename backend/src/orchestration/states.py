from enum import Enum
from typing import Dict, Set

class IncidentWorkflowState(str, Enum):
    TRIGGERED = "TRIGGERED"
    INVESTIGATING = "INVESTIGATING"
    CORRELATING = "CORRELATING"
    ASSESSING_IMPACT = "ASSESSING_IMPACT"
    EVALUATING_POLICY = "EVALUATING_POLICY"
    WAITING_HUMAN_APPROVAL = "WAITING_HUMAN_APPROVAL"
    REMEDIATING = "REMEDIATING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    REINVESTIGATING = "REINVESTIGATING"
    ESCALATED_HUMAN_TAKEOVER = "ESCALATED_HUMAN_TAKEOVER"

# State transition matrix enforcing strict workflow progression
ALLOWED_TRANSITIONS: Dict[IncidentWorkflowState, Set[IncidentWorkflowState]] = {
    IncidentWorkflowState.TRIGGERED: {IncidentWorkflowState.INVESTIGATING},
    IncidentWorkflowState.INVESTIGATING: {IncidentWorkflowState.CORRELATING, IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER},
    IncidentWorkflowState.CORRELATING: {IncidentWorkflowState.ASSESSING_IMPACT},
    IncidentWorkflowState.ASSESSING_IMPACT: {IncidentWorkflowState.EVALUATING_POLICY},
    IncidentWorkflowState.EVALUATING_POLICY: {
        IncidentWorkflowState.REMEDIATING,
        IncidentWorkflowState.WAITING_HUMAN_APPROVAL,
        IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER
    },
    IncidentWorkflowState.WAITING_HUMAN_APPROVAL: {
        IncidentWorkflowState.REMEDIATING,
        IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER
    },
    IncidentWorkflowState.REMEDIATING: {IncidentWorkflowState.VERIFYING},
    IncidentWorkflowState.VERIFYING: {
        IncidentWorkflowState.RESOLVED,
        IncidentWorkflowState.REINVESTIGATING,
        IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER
    },
    IncidentWorkflowState.REINVESTIGATING: {
        IncidentWorkflowState.INVESTIGATING,
        IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER
    },
    IncidentWorkflowState.RESOLVED: set(),
    IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER: set(),
}

class PredictiveWorkflowState(str, Enum):

    MONITORING = "MONITORING"
    RISK_DETECTED = "RISK_DETECTED"
    PREDICTING = "PREDICTING"
    POLICY_CHECK = "POLICY_CHECK"
    WAITING_HUMAN_APPROVAL = "WAITING_HUMAN_APPROVAL"
    PREVENTING = "PREVENTING"
    VERIFYING = "VERIFYING"
    PREVENTED = "PREVENTED"
    FALLBACK_REACTIVE = "FALLBACK_REACTIVE"

# Predictive state transitions
PREDICTIVE_ALLOWED_TRANSITIONS: Dict[PredictiveWorkflowState, Set[PredictiveWorkflowState]] = {
    PredictiveWorkflowState.MONITORING: {PredictiveWorkflowState.RISK_DETECTED, PredictiveWorkflowState.FALLBACK_REACTIVE},
    PredictiveWorkflowState.RISK_DETECTED: {PredictiveWorkflowState.PREDICTING, PredictiveWorkflowState.MONITORING, PredictiveWorkflowState.FALLBACK_REACTIVE},
    PredictiveWorkflowState.PREDICTING: {PredictiveWorkflowState.POLICY_CHECK, PredictiveWorkflowState.FALLBACK_REACTIVE},
    PredictiveWorkflowState.POLICY_CHECK: {
        PredictiveWorkflowState.PREVENTING,
        PredictiveWorkflowState.WAITING_HUMAN_APPROVAL,
        PredictiveWorkflowState.MONITORING,
        PredictiveWorkflowState.FALLBACK_REACTIVE
    },
    PredictiveWorkflowState.WAITING_HUMAN_APPROVAL: {
        PredictiveWorkflowState.PREVENTING,
        PredictiveWorkflowState.MONITORING,
        PredictiveWorkflowState.FALLBACK_REACTIVE
    },
    PredictiveWorkflowState.PREVENTING: {PredictiveWorkflowState.VERIFYING, PredictiveWorkflowState.FALLBACK_REACTIVE},
    PredictiveWorkflowState.VERIFYING: {PredictiveWorkflowState.PREVENTED, PredictiveWorkflowState.FALLBACK_REACTIVE},
    PredictiveWorkflowState.PREVENTED: {PredictiveWorkflowState.MONITORING},
    PredictiveWorkflowState.FALLBACK_REACTIVE: set(),
}

