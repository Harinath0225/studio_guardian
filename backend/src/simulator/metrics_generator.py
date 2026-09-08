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

        gpu_util = telemetry.get("gpu_utilization_pct", 65.0)
        queue_depth = telemetry.get("queue_depth", 6)
        scte_drift = telemetry.get("scte_timing_drift_ms", 12.0)
        splice_error = telemetry.get("splice_alignment_error_ms", 8.0)
        ad_drop = telemetry.get("ad_pod_drop_pct", 0.0)
        av_sync = telemetry.get("av_sync_drift_ms", 15.0)
        loudness_dev = telemetry.get("loudness_deviation_lufs", 0.2)
        frame_drop = telemetry.get("frame_drop_ratio_pct", 0.1)

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
            "# HELP studio_guardian_gpu_utilization_pct GPU compute utilization percentage",
            "# TYPE studio_guardian_gpu_utilization_pct gauge",
            f'studio_guardian_gpu_utilization_pct{{cluster="{telemetry["active_cluster"]}"}} {gpu_util:.2f}',
            "",
            "# HELP studio_guardian_transcoder_queue_depth Pending video chunks buffered in worker queue",
            "# TYPE studio_guardian_transcoder_queue_depth gauge",
            f'studio_guardian_transcoder_queue_depth{{cluster="{telemetry["active_cluster"]}"}} {queue_depth}',
            "",
            "# HELP studio_guardian_concurrent_viewers Total live stream viewers",
            "# TYPE studio_guardian_concurrent_viewers gauge",
            f'studio_guardian_concurrent_viewers{{event="{telemetry["event_title"]}"}} {viewers}',
            "",
            "# HELP studio_guardian_affected_viewers Degraded live stream viewers",
            "# TYPE studio_guardian_affected_viewers gauge",
            f'studio_guardian_affected_viewers{{event="{telemetry["event_title"]}"}} {affected}',
            "",
            "# HELP studio_guardian_scte_timing_drift_ms SCTE-35 cue timing drift relative to PTS in milliseconds",
            "# TYPE studio_guardian_scte_timing_drift_ms gauge",
            f'studio_guardian_scte_timing_drift_ms{{event="{telemetry["event_title"]}"}} {scte_drift:.2f}',
            "",
            "# HELP studio_guardian_splice_alignment_error_ms SCTE-35 splice insert alignment error in milliseconds",
            "# TYPE studio_guardian_splice_alignment_error_ms gauge",
            f'studio_guardian_splice_alignment_error_ms{{event="{telemetry["event_title"]}"}} {splice_error:.2f}',
            "",
            "# HELP studio_guardian_ad_pod_drop_pct Ad pod drop percentage",
            "# TYPE studio_guardian_ad_pod_drop_pct gauge",
            f'studio_guardian_ad_pod_drop_pct{{event="{telemetry["event_title"]}"}} {ad_drop:.2f}',
            "",
            "# HELP studio_guardian_av_sync_drift_ms Audio-video lip sync drift in milliseconds",
            "# TYPE studio_guardian_av_sync_drift_ms gauge",
            f'studio_guardian_av_sync_drift_ms{{event="{telemetry["event_title"]}"}} {av_sync:.2f}',
            "",
            "# HELP studio_guardian_loudness_deviation_lufs Audio loudness deviation from -24.0 LUFS target",
            "# TYPE studio_guardian_loudness_deviation_lufs gauge",
            f'studio_guardian_loudness_deviation_lufs{{event="{telemetry["event_title"]}"}} {loudness_dev:.2f}',
            "",
            "# HELP studio_guardian_frame_drop_ratio_pct Video frame drop percentage",
            "# TYPE studio_guardian_frame_drop_ratio_pct gauge",
            f'studio_guardian_frame_drop_ratio_pct{{event="{telemetry["event_title"]}"}} {frame_drop:.2f}',
            ""
        ]
        return "\n".join(lines)
