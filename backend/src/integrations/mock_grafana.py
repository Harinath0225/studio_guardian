import time
from typing import Dict, Any, List
from src.simulator.media_env import media_env, StreamState

class MockGrafanaServer:
    """
    High-fidelity deterministic local Grafana MCP provider for offline development
    and reliable hackathon demonstrations.
    Directly reflects current live media simulator state across Prometheus, Loki, Tempo, and Alerts.
    """
    def __init__(self):
        self.started_at = time.time()

    def query_prometheus(self, query: str) -> Dict[str, Any]:
        """Simulates querying Prometheus metrics via Grafana datasource."""
        metrics = media_env.get_telemetry_snapshot()
        now = time.time()

        result_data = []
        if "buffer_ratio" in query or "playback_error" in query:
            result_data.append({
                "metric": {"__name__": "media_playback_buffer_ratio", "channel": "star-sports-hindi", "region": "ap-south-1"},
                "value": [now, str(metrics["playback_error_rate_pct"])]
            })
        elif "rendition_error" in query:
            result_data.append({
                "metric": {"__name__": "media_transcode_rendition_error_rate", "profile": "1080p60_hdr", "pod": "transcoder-worker-7b"},
                "value": [now, str(metrics["gpu_allocation_failure_pct"])]
            })

        elif "gpu" in query or "utilization" in query:
            result_data.append({
                "metric": {"__name__": "media_transcode_gpu_utilization_pct", "pool": "transcoder-worker-pool", "region": "ap-south-1"},
                "value": [now, str(metrics.get("gpu_utilization_pct", 65.0))]
            })
        elif "queue" in query or "depth" in query:
            result_data.append({
                "metric": {"__name__": "media_transcode_queue_depth", "pool": "transcoder-worker-pool", "region": "ap-south-1"},
                "value": [now, str(metrics.get("queue_depth", 6))]
            })
        elif "active_viewers" in query or "concurrent_viewers" in query:
            result_data.append({
                "metric": {"__name__": "media_stream_active_viewers", "event": "ind-vs-aus-final"},
                "value": [now, str(metrics["concurrent_viewers"])]
            })
        elif "segment_fetch_latency" in query or "latency" in query:
            result_data.append({
                "metric": {"__name__": "media_origin_segment_fetch_latency_ms", "origin": "mumbai-primary"},
                "value": [now, str(metrics["transcoder_latency_ms"])]
            })
        else:
            # Default generic response
            result_data.append({
                "metric": {"__name__": "custom_metric", "status": media_env.state.value},
                "value": [now, "1.0"]
            })

        return {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": result_data
            }
        }

    def search_loki(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Simulates querying Loki logs via Grafana MCP."""
        now = time.time()
        logs = []

        if media_env.state == StreamState.DEGRADED:
            logs = [
                f"{now - 45} [ERROR] transcoder-worker-7b: libx265 failed: segmentation fault in SEI message payload insertion (build v2.4.1-rc3)",
                f"{now - 30} [WARN] edge-proxy-mumbai-02: 504 Gateway Timeout fetching segment 1080p60_hdr/seg_192834.ts from origin",
                f"{now - 15} [ERROR] transcoder-worker-7b: OOMKilled or SIGSEGV loop detected in transcode worker pool pod 7b",
                f"{now - 5} [WARN] player-telemetry-collector: Elevated rebuffering reports in Mumbai ASN 55836"
            ]
        elif media_env.state == StreamState.RECOVERED or media_env.predictive_step == 4:
            logs = [
                f"{now - 20} [INFO] transcoder-worker-pool: Scaled to 16 active worker nodes",
                f"{now - 10} [INFO] transcoder-worker-pool: GPU utilization normalized to 61.2%, queue depth stabilized at 12",
                f"{now - 2} [INFO] player-telemetry-collector: Playback buffer ratios normal at 0.38%"
            ]
        elif media_env.predictive_step == 3:
            logs = [
                f"{now - 30} [WARN] transcoder-worker-pool: GPU utilization exceeding 93% on primary worker nodes",
                f"{now - 15} [WARN] transcoder-queue-mgr: Queue depth accelerating (+48 chunks buffered)",
                f"{now - 5} [WARN] origin-ingest: Segment transcode latency 470ms approaching 500ms segment boundary threshold"
            ]
        elif media_env.predictive_step == 2:
            logs = [
                f"{now - 20} [INFO] transcoder-worker-pool: GPU utilization trending upward (81.0%)",
                f"{now - 10} [INFO] transcoder-queue-mgr: Queue depth 28 chunks, rate of change positive",
                f"{now - 2} [INFO] player-telemetry-collector: Playback error rate currently stable at 0.44%"
            ]
        else:
            logs = [
                f"{now - 20} [INFO] transcode-cluster: All 24 transcode pods healthy",
                f"{now - 10} [INFO] edge-proxy-mumbai-01: Segment delivery nominal, cache hit ratio 98.4%",
                f"{now - 2} [INFO] player-telemetry-collector: Buffer ratio stable at 0.42%"
            ]

        return {
            "status": "success",
            "data": {
                "resultType": "streams",
                "result": [
                    {
                        "stream": {"app": "media-pipeline", "cluster": "mumbai-prod"},
                        "values": [[str(int(now * 1e9)), line] for line in logs[:limit]]
                    }
                ]
            }
        }

    def get_tempo_traces(self, trace_id: str) -> Dict[str, Any]:
        """Simulates querying Tempo distributed traces via Grafana MCP."""
        metrics = media_env.get_telemetry_snapshot()
        is_degraded = media_env.state == StreamState.DEGRADED

        return {
            "status": "success",
            "traceID": trace_id or "trace-transcode-mumbai-9921",
            "spans": [
                {
                    "spanID": "span-client-request",
                    "operationName": "GET /live/ind-vs-aus/1080p60_hdr/segment_192834.ts",
                    "duration": 4850 if is_degraded else 42,
                    "tags": {"http.status_code": 504 if is_degraded else 200}
                },
                {
                    "spanID": "span-edge-proxy",
                    "operationName": "proxy.forward_to_origin",
                    "duration": 4800 if is_degraded else 38,
                    "tags": {"upstream": "transcoder-worker-7b", "error": is_degraded}
                },
                {
                    "spanID": "span-transcoder",
                    "operationName": "ffmpeg.encode_frame_sei",
                    "duration": 4790 if is_degraded else 25,
                    "tags": {
                        "error": is_degraded,
                        "error.message": "SIGSEGV in libx265 SEI parser" if is_degraded else "None"
                    }
                }
            ]
        }

    def list_alerts(self) -> List[Dict[str, Any]]:
        """Simulates listing active Grafana Alerting rules."""
        metrics = media_env.get_telemetry_snapshot()
        alerts = []

        if media_env.state == StreamState.DEGRADED:
            alerts.append({
                "fingerprint": "alert-buffer-ratio-critical",
                "ruleName": "HighMediaBufferRatioAlert",
                "state": "firing",
                "labels": {"severity": "critical", "service": "live-stream", "region": "ap-south-1"},
                "annotations": {
                    "summary": f"Media playback buffer ratio is {metrics['playback_error_rate_pct']:.2f}%, exceeding 2.0% SLA threshold"
                }
            })
            alerts.append({
                "fingerprint": "alert-transcode-error-high",
                "ruleName": "TranscoderRenditionFailureRateAlert",
                "state": "firing",
                "labels": {"severity": "critical", "service": "transcoder", "profile": "1080p60_hdr"},
                "annotations": {
                    "summary": f"Rendition error rate {metrics['gpu_allocation_failure_pct']:.2f}% on transcoder worker pod 7b"
                }
            })
        else:
            alerts.append({
                "fingerprint": "alert-buffer-ratio-critical",
                "ruleName": "HighMediaBufferRatioAlert",
                "state": "normal",
                "labels": {"severity": "critical", "service": "live-stream", "region": "ap-south-1"},
                "annotations": {"summary": "Playback buffer ratio normal"}
            })

        return alerts

mock_grafana_server = MockGrafanaServer()
