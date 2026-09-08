from typing import Dict
from src.config import settings

# Operational Risk Tiers
RISK_TIER_HEALTHY = "HEALTHY"       # < 0.30
RISK_TIER_WATCH = "WATCH"           # 0.30 - 0.59
RISK_TIER_ELEVATED = "ELEVATED_RISK" # 0.60 - 0.79
RISK_TIER_HIGH = "HIGH_RISK"         # 0.80 - 0.89
RISK_TIER_IMMINENT = "IMMINENT_RISK" # >= 0.90

TIER_BOUNDS = [
    (0.90, RISK_TIER_IMMINENT),
    (0.80, RISK_TIER_HIGH),
    (0.60, RISK_TIER_ELEVATED),
    (0.30, RISK_TIER_WATCH),
    (0.00, RISK_TIER_HEALTHY),
]

def classify_risk_tier(risk_score: float) -> str:
    """Classifies a composite risk score into its corresponding operational tier."""
    for threshold, tier in TIER_BOUNDS:
        if risk_score >= threshold:
            return tier
    return RISK_TIER_HEALTHY

def get_signal_weights() -> Dict[str, float]:
    """Returns configurable signal weights from environment settings."""
    return {
        "gpu_pressure": settings.PREDICTIVE_WEIGHT_GPU,
        "queue_growth": settings.PREDICTIVE_WEIGHT_QUEUE,
        "latency_pressure": settings.PREDICTIVE_WEIGHT_LATENCY,
        "error_growth": settings.PREDICTIVE_WEIGHT_ERROR,
        "viewer_growth": settings.PREDICTIVE_WEIGHT_VIEWER,
        "deployment_risk": settings.PREDICTIVE_WEIGHT_DEPLOYMENT,
    }

PREDICTIVE_STATES = [
    RISK_TIER_HEALTHY,
    RISK_TIER_WATCH,
    RISK_TIER_ELEVATED,
    RISK_TIER_HIGH,
    RISK_TIER_IMMINENT,
    "PREVENTED",
]

def determine_predictive_state(risk_score: float) -> str:
    """Maps composite risk score to operational predictive state."""
    return classify_risk_tier(risk_score)

