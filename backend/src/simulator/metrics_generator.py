from typing import Dict, Any
from src.simulator.media_env import media_env

class MetricsGenerator:
    @staticmethod
    def get_current_metrics() -> Dict[str, Any]:
        return media_env.get_telemetry_snapshot()

    @staticmethod
    def generate_prometheus_text() -> str:
        """Outputs standard Prometheus exposition text format for Grafana scraping."""
        telemetry = media_env.get_telemetry_snapshot()
        error_rate = telemetry["playback_error_rate_pct"] / 100.0
        latency = telemetry["transcoder_latency_ms"] / 1000.0
        gpu_fail = telemetry["gpu_allocation_failure_pct"] / 100.0
        viewers = telemetry["concurrent_viewers"]
        affected = telemetry["affected_viewers"]

        lines = [
            "# HELP studio_guardian_playback_error_rate Ratio of failed playback sessions",
            "# TYPE studio_guardian_playback_error_rate gauge",
            f'studio_guardian_playback_error_rate{{event="{telemetry["event_title"]}"}} {error_rate:.4f}',
            "",
            "# HELP studio_guardian_transcoder_latency_seconds Latency of live segment encoding",
            "# TYPE studio_guardian_transcoder_latency_seconds gauge",
            f'studio_guardian_transcoder_latency_seconds{{event="{telemetry["event_title"]}",cluster="{telemetry["active_cluster"]}"}} {latency:.4f}',
            "",
            "# HELP studio_guardian_gpu_allocation_failure_ratio Ratio of failed GPU transcoding memory allocations",
            "# TYPE studio_guardian_gpu_allocation_failure_ratio gauge",
            f'studio_guardian_gpu_allocation_failure_ratio{{cluster="{telemetry["active_cluster"]}"}} {gpu_fail:.4f}',
            "",
            "# HELP studio_guardian_concurrent_viewers Total live stream viewers",
            "# TYPE studio_guardian_concurrent_viewers gauge",
            f'studio_guardian_concurrent_viewers{{event="{telemetry["event_title"]}"}} {viewers}',
            "",
            "# HELP studio_guardian_affected_viewers Degraded live stream viewers",
            "# TYPE studio_guardian_affected_viewers gauge",
            f'studio_guardian_affected_viewers{{event="{telemetry["event_title"]}"}} {affected}',
            ""
        ]
        return "\n".join(lines)
