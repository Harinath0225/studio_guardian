import os
import json
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, Response
from src.simulator.media_env import media_env, StreamState

router = APIRouter(prefix="/api/v1/observability", tags=["Observability & Grafana"])

POSSIBLE_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "grafana", "studio-guardian-dashboard.json"),
    os.path.join(os.path.dirname(__file__), "..", "..", "grafana", "studio-guardian-dashboard.json"),
]

def _get_dashboard_file_path() -> Optional[str]:
    for p in POSSIBLE_PATHS:
        norm = os.path.normpath(p)
        if os.path.exists(norm):
            return norm
    return None

def generate_live_log_lines() -> List[Dict[str, Any]]:
    """Generates realistic live Loki log entries based on current media pipeline state."""
    now = time.time()
    iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    telemetry = media_env.get_telemetry_snapshot()
    
    logs = []
    
    if media_env.scte_timing_drift_ms > 200.0 or media_env.ad_pod_drop_pct > 2.0:
        logs.append({
            "timestamp": iso,
            "level": "ERROR",
            "service": "scte35-sentinel",
            "message": f"SCTE-35 cue timing drift {telemetry['scte_timing_drift_ms']:.1f}ms exceeds operational envelope (±200.0ms). Splice alignment error: {telemetry['splice_alignment_error_ms']:.1f}ms"
        })
        logs.append({
            "timestamp": iso,
            "level": "WARN",
            "service": "ad-pod-engine",
            "message": f"Ad pod drop rate at {telemetry['ad_pod_drop_pct']:.1f}%. Downstream client manifest ad stitch failure risk elevated."
        })
    
    if media_env.state == StreamState.DEGRADED:
        logs.append({
            "timestamp": iso,
            "level": "CRITICAL",
            "service": "transcoder-worker-7b",
            "message": f"SIGSEGV or OOMKilled loop detected in libx265 SEI message parser. GPU allocation failure: {telemetry['gpu_allocation_failure_pct']:.1f}%"
        })
        logs.append({
            "timestamp": iso,
            "level": "ERROR",
            "service": "origin-ingest",
            "message": f"Segment latency spiked to {telemetry['transcoder_latency_ms']:.1f}ms (threshold 500ms). Downstream buffer starvation in regions: {', '.join(telemetry.get('affected_regions', ['AU', 'SG']))}"
        })
        logs.append({
            "timestamp": iso,
            "level": "WARN",
            "service": "edge-proxy-mumbai-02",
            "message": f"504 Gateway Timeout fetching segment 1080p60_hdr/seg_192834.ts from origin. Playback buffer error: {telemetry['playback_error_rate_pct']:.2f}%"
        })
    elif media_env.state == StreamState.LOAD_SURGE or media_env.predictive_step == 3:
        logs.append({
            "timestamp": iso,
            "level": "WARN",
            "service": "transcoder-worker-pool",
            "message": f"GPU compute saturation at {telemetry.get('gpu_utilization_pct', 93.4):.1f}%. Approaching hard quota on primary transcode nodes."
        })
        logs.append({
            "timestamp": iso,
            "level": "WARN",
            "service": "transcoder-queue-mgr",
            "message": f"Transcode worker queue depth accelerating (+{telemetry.get('queue_depth', 48)} chunks buffered). Encoding latency: {telemetry['transcoder_latency_ms']:.1f}ms"
        })
        logs.append({
            "timestamp": iso,
            "level": "INFO",
            "service": "predictive-risk-agent",
            "message": f"Grafana MCP sweep detected leading indicator anomaly in ap-south-1. Calculating risk trajectory score: 0.82"
        })
    elif media_env.state == StreamState.RECOVERED or media_env.predictive_step == 4:
        logs.append({
            "timestamp": iso,
            "level": "INFO",
            "service": "transcoder-worker-pool",
            "message": f"Preventive scale applied: pool size {telemetry.get('transcoder_pool_size', 16)} active nodes. GPU load normalized to {telemetry.get('gpu_utilization_pct', 61.2):.1f}%"
        })
        logs.append({
            "timestamp": iso,
            "level": "INFO",
            "service": "video-proxy",
            "message": f"Traffic routed successfully to healthy cluster {telemetry.get('active_cluster', 'transcoder-us-01')}. Playback error rate: {telemetry['playback_error_rate_pct']:.2f}%"
        })
    else:
        logs.append({
            "timestamp": iso,
            "level": "INFO",
            "service": "origin-ingest",
            "message": f"Live manifest publishing nominal. Concurrency: {telemetry['concurrent_viewers']:,} viewers. Segment duration: 2000ms"
        })
        logs.append({
            "timestamp": iso,
            "level": "INFO",
            "service": "scte35-sentinel",
            "message": f"SCTE-35 cue timing drift nominal at {telemetry.get('scte_timing_drift_ms', 12.0):.1f}ms. Splice alignment error: {telemetry.get('splice_alignment_error_ms', 8.0):.1f}ms"
        })
        logs.append({
            "timestamp": iso,
            "level": "INFO",
            "service": "perceptual-sentinel",
            "message": f"Perceptual telemetry within bounds: A/V sync drift {telemetry.get('av_sync_drift_ms', 15.0):.1f}ms, loudness deviation {telemetry.get('loudness_deviation_lufs', 0.2):.1f} LUFS"
        })
        
    return logs


@router.get("/logs")
async def get_live_logs(
    limit: int = Query(50, ge=1, le=200),
    level: Optional[str] = Query(None, description="Filter by INFO, WARN, ERROR, CRITICAL"),
    service: Optional[str] = Query(None, description="Filter by service name")
):
    """Returns recent live operational Loki-style logs for the streaming console."""
    lines = generate_live_log_lines()
    if level:
        lines = [l for l in lines if l["level"].upper() == level.upper()]
    if service:
        lines = [l for l in lines if service.lower() in l["service"].lower()]
    return {
        "status": "success",
        "total": len(lines),
        "logs": lines[:limit]
    }


@router.get("/dashboard-json")
async def get_dashboard_json():
    """Returns the ready-to-import Grafana Cloud Dashboard JSON specification."""
    file_path = _get_dashboard_file_path()
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    return {"error": "Dashboard JSON specification file not found."}


@router.get("/loki/status")
async def get_loki_status():
    """Returns current Grafana Cloud Loki configuration and diagnostic info."""
    from src.config import settings
    token = settings.GRAFANA_LOKI_TOKEN or settings.GRAFANA_SERVICE_ACCOUNT_TOKEN
    is_cloud_access_token = token.startswith("glc_")
    is_sa_token = token.startswith("glsa_")
    
    return {
        "loki_url": settings.GRAFANA_LOKI_URL,
        "loki_user_id": settings.GRAFANA_LOKI_USER_ID,
        "token_configured": bool(token),
        "token_type": "CLOUD_ACCESS_POLICY" if is_cloud_access_token else ("SERVICE_ACCOUNT" if is_sa_token else "CUSTOM"),
        "can_push_to_loki": is_cloud_access_token,
        "note": "Grafana Cloud Loki requires a Cloud Access Policy Token (glc_...) with 'logs:write' scope to accept pushed logs. Service Account tokens (glsa_...) only grant dashboard API access."
    }


@router.post("/loki/test-push")
async def test_loki_push():
    """Triggers an active probe push to Grafana Cloud Loki to verify connectivity."""
    from src.simulator.loki_shipper import loki_shipper
    result = await loki_shipper.test_connection()
    return result


@router.get("/vertex/reasoning-engine")
async def get_vertex_reasoning_engine_status():
    """Returns status and registration metadata for the Vertex AI Reasoning Engine."""
    from src.config import settings
    manifest_path = os.path.join(os.path.dirname(__file__), "..", "..", "vertex_reasoning_engine_manifest.json")
    manifest = None
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            pass

    return {
        "status": "ONLINE",
        "platform": "Gemini Enterprise Agent Platform (Google Cloud)",
        "project": settings.GOOGLE_CLOUD_PROJECT,
        "location": settings.GOOGLE_CLOUD_LOCATION,
        "model": settings.GEMINI_MODEL,
        "reasoning_engine_class": "StudioGuardianReasoningEngine",
        "manifest": manifest
    }


class ReasoningEngineQueryRequest(BaseModel if 'BaseModel' in globals() else object):
    pass

@router.post("/vertex/reasoning-engine/query")
async def query_vertex_reasoning_engine(payload: Dict[str, Any]):
    """Executes a query or operational reasoning task through StudioGuardianReasoningEngine."""
    from src.integrations.vertex_reasoning_engine import StudioGuardianReasoningEngine
    from src.config import settings

    engine = StudioGuardianReasoningEngine(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.GOOGLE_CLOUD_LOCATION,
        model=settings.GEMINI_MODEL
    )
    engine.set_up()
    prompt = payload.get("prompt", "Assess live broadcast stability and capacity risk")
    kwargs = {k: v for k, v in payload.items() if k != "prompt"}
    result = engine.query(prompt, **kwargs)
    return {
        "status": "success",
        "prompt": prompt,
        "result": result
    }
