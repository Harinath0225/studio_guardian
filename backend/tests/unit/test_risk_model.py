import pytest
from src.prediction.risk_model import RiskModel
from src.prediction.thresholds import classify_risk_tier
from src.prediction.predictor import Predictor


def test_weighted_risk_scoring():
    model = RiskModel()
    norm_signals = {
        "gpu_pressure": 0.95,
        "queue_growth": 0.95,
        "latency_pressure": 0.90,
        "error_growth": 0.80,
        "viewer_growth": 0.85,
        "deployment_risk": 0.50,
    }
    raw_metrics = {
        "gpu_utilization_pct": 93.4,
        "queue_depth": 48,
        "transcoder_latency_ms": 470.0,
        "playback_error_rate_pct": 0.48,
        "active_viewers": 11800000,
        "deployment_recency": 180,
    }

    score, tier, contributors = model.calculate_risk(norm_signals, raw_metrics)
    assert 0.80 <= score <= 0.95
    assert tier in ("HIGH_RISK", "IMMINENT_RISK")

    # Verify contributors sum equals risk score * 100 approx
    total_points = sum(c["points"] for c in contributors)
    assert abs(total_points - (score * 100.0)) < 1.0

    # Primary contributor should be GPU pressure
    assert contributors[0]["name"] == "gpu_pressure"


def test_tier_classification():
    assert classify_risk_tier(0.15) == "HEALTHY"
    assert classify_risk_tier(0.45) == "WATCH"
    assert classify_risk_tier(0.68) == "ELEVATED_RISK"
    assert classify_risk_tier(0.85) == "HIGH_RISK"
    assert classify_risk_tier(0.94) == "IMMINENT_RISK"


def test_failure_mode_identification():
    model = RiskModel()
    # High GPU + high queue = transcoder capacity exhaustion
    mode = model.identify_failure_mode({"gpu_pressure": 0.90, "queue_growth": 0.85})
    assert mode == "transcoder_capacity_exhaustion"


def test_time_to_threshold_and_confidence():
    pred = Predictor()
    norm = {"gpu_pressure": 0.92, "queue_growth": 0.88}
    raw = {"gpu_utilization_pct": 92.0, "transcoder_latency_ms": 450.0, "queue_depth": 40}

    window = pred.estimate_time_to_threshold(0.86, norm, raw)
    assert 3 <= window["min"] <= 10
    assert window["min"] <= window["max"] <= 15

    confidence = pred.calculate_confidence(raw, norm, telemetry_age_sec=2.0)
    assert 0.80 <= confidence <= 1.0
