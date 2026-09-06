import pytest
from src.simulator.media_env import media_env, StreamState
from src.integrations.mcp_client import mcp_client
from src.integrations.mcp_tools import (
    query_prometheus_metrics,
    search_loki_logs,
    get_tempo_traces,
    list_grafana_alerts
)

@pytest.mark.asyncio
async def test_mcp_prometheus_query_healthy_and_degraded():
    # 1. Healthy state
    media_env.set_state(StreamState.HEALTHY)
    res_healthy = await query_prometheus_metrics("media_playback_buffer_ratio")
    assert res_healthy["status"] == "success"
    val = float(res_healthy["data"]["result"][0]["value"][1])
    assert val < 1.0

    # 2. Degraded state
    media_env.set_state(StreamState.DEGRADED)
    res_degraded = await query_prometheus_metrics("media_playback_buffer_ratio")
    assert res_degraded["status"] == "success"
    val_deg = float(res_degraded["data"]["result"][0]["value"][1])
    assert val_deg >= 5.0

@pytest.mark.asyncio
async def test_mcp_loki_logs_search():
    media_env.set_state(StreamState.DEGRADED)
    res = await search_loki_logs("{app=\"media-pipeline\"}", limit=5)
    assert res["status"] == "success"
    streams = res["data"]["result"]
    assert len(streams) > 0
    raw_logs = [entry[1] for entry in streams[0]["values"]]
    assert any("segmentation fault" in log or "504" in log for log in raw_logs)

@pytest.mark.asyncio
async def test_mcp_tempo_traces():
    media_env.set_state(StreamState.DEGRADED)
    trace = await get_tempo_traces("trace-101")
    assert trace["status"] == "success"
    spans = trace["spans"]
    assert len(spans) >= 3
    transcoder_span = next(s for s in spans if s["operationName"] == "ffmpeg.encode_frame_sei")
    assert transcoder_span["tags"]["error"] is True

@pytest.mark.asyncio
async def test_mcp_grafana_alerts():
    media_env.set_state(StreamState.DEGRADED)
    alerts = await list_grafana_alerts()
    assert len(alerts) >= 2
    firing = [a for a in alerts if a["state"] == "firing"]
    assert len(firing) >= 2

    # Reset
    media_env.set_state(StreamState.HEALTHY)
    alerts_healthy = await list_grafana_alerts()
    firing_healthy = [a for a in alerts_healthy if a["state"] == "firing"]
    assert len(firing_healthy) == 0
