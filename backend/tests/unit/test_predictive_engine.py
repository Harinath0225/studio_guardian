import pytest
import time
from src.prediction.feature_normalizer import FeatureNormalizer
from src.prediction.risk_model import RiskModel
from src.prediction.predictor import Predictor
from src.prediction.thresholds import (
    classify_risk_tier,
    RISK_TIER_HEALTHY,
    RISK_TIER_WATCH,
    RISK_TIER_ELEVATED,
    RISK_TIER_HIGH,
    RISK_TIER_IMMINENT,
)

def test_feature_normalizer_comprehensive():
    normalizer = FeatureNormalizer()
    now = time.time()

    # 1. Nominal test
    nominal_sample = {
        "gpu_utilization_pct": 55.0,
        "transcoder_latency_ms": 200.0,
        "queue_depth": 4,
        "playback_error_rate_pct": 0.05,
        "active_viewers": 8500000,
        "recent_deployment": None,
    }
    features = normalizer.normalize(nominal_sample, timestamp=now)
    assert 0.0 <= features["gpu_pressure"] <= 0.50
    assert 0.0 <= features["queue_growth"] <= 0.50
    assert 0.0 <= features["latency_pressure"] <= 0.50

    # 2. Extreme saturation test
    extreme_sample = {
        "gpu_utilization_pct": 98.5,
        "transcoder_latency_ms": 550.0,
        "queue_depth": 65,
        "playback_error_rate_pct": 0.85,
        "active_viewers": 14000000,
        "recent_deployment": 120,
    }
    extreme_features = normalizer.normalize(extreme_sample, timestamp=now + 10)
    assert extreme_features["gpu_pressure"] > 0.90
    assert extreme_features["queue_growth"] > 0.80
    assert extreme_features["latency_pressure"] > 0.80

def test_risk_model_evaluation_and_contributors():
    model = RiskModel()

    # Low risk
    low_signals = {
        "gpu_pressure": 0.2,
        "queue_growth": 0.1,
        "latency_pressure": 0.15,
        "error_growth": 0.05,
        "viewer_growth": 0.1,
        "deployment_risk": 0.0,
    }
    low_raw = {"gpu_utilization_pct": 52.0, "queue_depth": 3, "transcoder_latency_ms": 180.0}
    score, tier, contributors = model.calculate_risk(low_signals, low_raw)
    assert score < 0.35
    assert tier == RISK_TIER_HEALTHY

    # High risk
    high_signals = {
        "gpu_pressure": 0.95,
        "queue_growth": 0.90,
        "latency_pressure": 0.85,
        "error_growth": 0.70,
        "viewer_growth": 0.80,
        "deployment_risk": 0.40,
    }
    high_raw = {"gpu_utilization_pct": 94.0, "queue_depth": 50, "transcoder_latency_ms": 480.0}
    score_h, tier_h, contributors_h = model.calculate_risk(high_signals, high_raw)
    assert score_h >= 0.80
    assert tier_h in (RISK_TIER_HIGH, RISK_TIER_IMMINENT)

    # Contributor breakdown
    assert len(contributors_h) >= 3
    total_points = sum(c["points"] for c in contributors_h)
    assert abs(total_points - (score_h * 100.0)) < 1.0

def test_thresholds_classification():
    assert classify_risk_tier(0.15) == RISK_TIER_HEALTHY
    assert classify_risk_tier(0.45) == RISK_TIER_WATCH
    assert classify_risk_tier(0.68) == RISK_TIER_ELEVATED
    assert classify_risk_tier(0.82) == RISK_TIER_HIGH
    assert classify_risk_tier(0.92) == RISK_TIER_IMMINENT

def test_predictor_time_to_threshold_and_confidence():
    pred = Predictor()
    norm = {"gpu_pressure": 0.94, "queue_growth": 0.91}
    raw = {"gpu_utilization_pct": 94.0, "transcoder_latency_ms": 490.0, "queue_depth": 52}

    # Time to threshold under high risk
    window = pred.estimate_time_to_threshold(0.88, norm, raw)
    assert "min" in window and "max" in window
    assert window["min"] <= window["max"]
    assert window["min"] >= 1

    # High confidence on fresh concordant data
    conf = pred.calculate_confidence(raw, norm, telemetry_age_sec=1.5)
    assert conf >= 0.80

    # Low confidence on stale data
    stale_conf = pred.calculate_confidence(raw, norm, telemetry_age_sec=45.0)
    assert stale_conf < conf
