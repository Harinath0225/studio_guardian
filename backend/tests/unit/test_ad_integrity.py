import pytest
from src.media.ad_integrity import ad_integrity_evaluator
from src.media.perceptual_quality import perceptual_quality_evaluator

def test_ad_integrity_nominal():
    telemetry = {
        "event_title": "star-sports-live",
        "scte_timing_drift_ms": 15.0,
        "splice_alignment_error_ms": 5.0,
        "ad_pod_drop_pct": 0.0,
        "tracking_error_ratio": 0.001
    }
    report = ad_integrity_evaluator.evaluate(telemetry)
    assert not report.is_anomaly
    assert report.severity == "INFO"
    assert report.estimated_ad_exposure_usd == 0.0

def test_ad_integrity_drift_breach():
    telemetry = {
        "event_title": "star-sports-live",
        "scte_timing_drift_ms": 420.0, # Exceeds +-200ms tolerance
        "splice_alignment_error_ms": 120.0,
        "ad_pod_drop_pct": 8.5,
        "tracking_error_ratio": 0.12
    }
    report = ad_integrity_evaluator.evaluate(telemetry, total_viewers=10_000_000)
    assert report.is_anomaly
    assert report.severity == "CRITICAL"
    assert report.estimated_ad_exposure_usd > 0.0
    assert report.recommended_action == "activate_ad_slate"

def test_perceptual_quality_evaluation():
    nominal = {
        "av_sync_drift_ms": 10.0,
        "loudness_lufs": -24.1,
        "frame_drop_ratio_pct": 0.1,
        "black_frame_ratio_pct": 0.0
    }
    rep_nom = perceptual_quality_evaluator.evaluate(nominal)
    assert not rep_nom.is_anomaly
    assert rep_nom.severity == "INFO"

    corrupted = {
        "av_sync_drift_ms": 320.0, # >250ms critical
        "loudness_lufs": -18.0,
        "frame_drop_ratio_pct": 6.2,
        "black_frame_ratio_pct": 3.0
    }
    rep_cor = perceptual_quality_evaluator.evaluate(corrupted)
    assert rep_cor.is_anomaly
    assert rep_cor.severity == "CRITICAL"