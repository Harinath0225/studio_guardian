import pytest
from src.simulator.metrics_generator import MetricsGenerator
from src.api.observability import generate_live_log_lines, get_dashboard_json

def test_prometheus_metrics_generation():
    text = MetricsGenerator.generate_prometheus_text()
    assert "studio_guardian_playback_error_rate" in text
    assert "studio_guardian_transcoder_latency_seconds" in text
    assert "studio_guardian_gpu_utilization_pct" in text
    assert "studio_guardian_transcoder_queue_depth" in text
    assert "studio_guardian_scte_timing_drift_ms" in text
    assert "studio_guardian_splice_alignment_error_ms" in text
    assert "studio_guardian_concurrent_viewers" in text

def test_live_log_generation():
    logs = generate_live_log_lines()
    assert len(logs) > 0
    first_log = logs[0]
    assert "timestamp" in first_log
    assert "level" in first_log
    assert "service" in first_log
    assert "message" in first_log

@pytest.mark.asyncio
async def test_dashboard_json_retrieval():
    data = await get_dashboard_json()
    assert isinstance(data, dict)
    assert "title" in data
    assert "panels" in data
    assert len(data["panels"]) >= 5
