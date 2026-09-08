import pytest
import time
from src.prediction.feature_normalizer import FeatureNormalizer


def test_static_gauge_clamping():
    normalizer = FeatureNormalizer()

    # Below floor (50%) -> 0.0
    assert normalizer.clamp_min_max(40.0, 50.0, 95.0) == 0.0
    # At floor -> 0.0
    assert normalizer.clamp_min_max(50.0, 50.0, 95.0) == 0.0
    # Midpoint (72.5%) -> 0.5
    assert normalizer.clamp_min_max(72.5, 50.0, 95.0) == 0.5
    # At ceiling (95%) -> 1.0
    assert normalizer.clamp_min_max(95.0, 50.0, 95.0) == 1.0
    # Above ceiling (100%) -> 1.0
    assert normalizer.clamp_min_max(100.0, 50.0, 95.0) == 1.0


def test_linear_slope_and_growth_rate():
    normalizer = FeatureNormalizer(history_window_sec=60.0)
    now = time.time()

    # Feed 3 samples with queue growing by 10 chunks every 15 seconds (= +40 chunks/minute)
    normalizer.record_sample({"queue_depth": 10}, timestamp=now - 30)
    normalizer.record_sample({"queue_depth": 20}, timestamp=now - 15)
    normalizer.record_sample({"queue_depth": 30}, timestamp=now)

    slope = normalizer.calculate_linear_slope("queue_depth")
    # Slope should be approx 40.0 chunks/min
    assert abs(slope - 40.0) < 1.0


def test_normalization_vector_bounds():
    normalizer = FeatureNormalizer()
    now = time.time()

    # Feed emerging high-load telemetry
    raw_sample = {
        "gpu_utilization_pct": 93.4,
        "transcoder_latency_ms": 470.0,
        "queue_depth": 48,
        "playback_error_rate_pct": 0.45,
        "active_viewers": 11800000,
        "recent_deployment": None,
    }

    norm = normalizer.normalize(raw_sample, timestamp=now)
    for signal_name, val in norm.items():
        assert 0.0 <= val <= 1.0, f"Signal {signal_name} ({val}) out of [0.0, 1.0] bounds"

    assert norm["gpu_pressure"] > 0.90
    assert norm["latency_pressure"] > 0.80
