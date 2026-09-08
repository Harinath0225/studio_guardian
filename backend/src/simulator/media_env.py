import time
from typing import Dict, Any, List
from enum import Enum

class StreamState(str, Enum):
    HEALTHY = "HEALTHY"
    LOAD_SURGE = "LOAD_SURGE"
    DEGRADED = "DEGRADED"
    RECOVERED = "RECOVERED"

class MediaEnvironment:
    def __init__(self):
        self.event_title: str = "India vs Australia Final"
        self.total_viewers: int = 12_400_000
        self.state: StreamState = StreamState.HEALTHY
        self.last_state_change: float = time.time()
        self.recent_deployment: str = "v4.2.1-transcoder-patch"
        self.deployment_time_offset_sec: int = 180 # Deployed 3 minutes before incident

        # Active transcoders and traffic allocation
        self.routing_weights: Dict[str, float] = {
            "transcoder-syd-01": 0.50,
            "transcoder-sin-01": 0.50,
            "transcoder-us-01": 0.00 # Standby healthy backup cluster
        }

        # Predictive prevention state
        self.predictive_step: int = 0
        self.transcoder_pool_size: int = 8
        self.preventive_scaled: bool = False

        # Failure injection overrides
        self.force_recovery_failure: bool = False

        # SCTE-35 Ad Integrity state (FR-007)
        self.scte_timing_drift_ms: float = 12.0
        self.splice_alignment_error_ms: float = 8.0
        self.ad_pod_drop_pct: float = 0.0
        self.tracking_error_ratio: float = 0.001

        # Perceptual Quality state (FR-007)
        self.av_sync_drift_ms: float = 15.0
        self.loudness_lufs: float = -24.0
        self.loudness_deviation_lufs: float = 0.2
        self.frame_drop_ratio_pct: float = 0.1
        self.black_frame_ratio_pct: float = 0.0

    def set_state(self, new_state: StreamState) -> None:
        self.state = new_state
        self.last_state_change = time.time()
        if new_state == StreamState.LOAD_SURGE:
            self.predictive_step = 3
        elif new_state == StreamState.HEALTHY:
            self.predictive_step = 1


    def trigger_incident(self) -> None:
        self.state = StreamState.DEGRADED
        self.last_state_change = time.time()

    def reset(self) -> None:
        self.state = StreamState.HEALTHY
        self.routing_weights = {
            "transcoder-syd-01": 0.50,
            "transcoder-sin-01": 0.50,
            "transcoder-us-01": 0.00
        }
        self.force_recovery_failure = False
        self.predictive_step = 0
        self.transcoder_pool_size = 8
        self.preventive_scaled = False
        self.scte_timing_drift_ms = 12.0
        self.splice_alignment_error_ms = 8.0
        self.ad_pod_drop_pct = 0.0
        self.tracking_error_ratio = 0.001
        self.av_sync_drift_ms = 15.0
        self.loudness_lufs = -24.0
        self.loudness_deviation_lufs = 0.2
        self.frame_drop_ratio_pct = 0.1
        self.black_frame_ratio_pct = 0.0
        self.last_state_change = time.time()

    def set_predictive_step(self, step: int) -> None:
        """Sets the current step in the predictive load-surge progression."""
        self.predictive_step = step
        if step == 4:
            self.scale_transcoder_pool()

    def scale_transcoder_pool(self, scale_factor: float = 2.0) -> Dict[str, Any]:
        """Executes controlled preventive capacity scaling for transcoder pool."""
        self.transcoder_pool_size = int(self.transcoder_pool_size * scale_factor)
        self.preventive_scaled = True
        self.predictive_step = 4
        return {
            "status": "COMPLETED",
            "action": "scale_transcoder_pool",
            "previous_pool_size": int(self.transcoder_pool_size / scale_factor),
            "new_pool_size": self.transcoder_pool_size,
            "target_service": "transcoder-worker-pool",
            "message": f"Successfully scaled transcoder worker pool to {self.transcoder_pool_size} active nodes."
        }

    def apply_traffic_shift(self, target_cluster: str = "transcoder-us-01", shift_pct: float = 100.0) -> Dict[str, Any]:
        """Performs authentic controlled traffic shifting on the simulated video routing proxy."""
        if self.force_recovery_failure:
            # Simulated failure path
            return {
                "status": "APPLIED_WITH_ERRORS",
                "message": f"Traffic shifted to {target_cluster}, but standby node failed to allocate transcode slots.",
                "active_weights": self.routing_weights
            }

        # Shift traffic to healthy standby cluster
        self.routing_weights = {
            "transcoder-syd-01": 0.00,
            "transcoder-sin-01": 0.00,
            target_cluster: 1.00
        }
        self.state = StreamState.RECOVERED
        self.last_state_change = time.time()
        return {
            "status": "COMPLETED",
            "message": f"Successfully diverted 100% of AU/SG traffic to {target_cluster}.",
            "active_weights": self.routing_weights
        }

    def get_telemetry_snapshot(self) -> Dict[str, Any]:
        """Calculates instantaneous telemetry values based on active state and routing weights."""
        if self.state == StreamState.DEGRADED:
            return self._attach_media_signals({
                "event_title": self.event_title,
                "status": self.state.value,
                "playback_error_rate_pct": 8.7,
                "transcoder_latency_ms": 485.0,
                "gpu_allocation_failure_pct": 14.2,
                "concurrent_viewers": self.total_viewers,
                "affected_viewers": 1_820_000,
                "affected_regions": ["AU", "SG"],
                "active_cluster": "transcoder-syd-01",
                "routing_weights": self.routing_weights,
                "recent_deployment": self.recent_deployment,
                "transcoder_pool_size": self.transcoder_pool_size,
                "queue_depth": 140,
                "gpu_utilization_pct": 98.5
            })
        elif self.state == StreamState.RECOVERED:
            return self._attach_media_signals({
                "event_title": self.event_title,
                "status": self.state.value,
                "playback_error_rate_pct": 0.38,
                "transcoder_latency_ms": 19.5,
                "gpu_allocation_failure_pct": 0.0,
                "concurrent_viewers": self.total_viewers,
                "affected_viewers": 0,
                "affected_regions": [],
                "active_cluster": "transcoder-us-01",
                "routing_weights": self.routing_weights,
                "recent_deployment": self.recent_deployment,
                "transcoder_pool_size": self.transcoder_pool_size,
                "queue_depth": 8,
                "gpu_utilization_pct": 52.0
            })
        else: # HEALTHY / PREDICTIVE MODES
            # Step 1: Normal healthy
            # Step 2: Elevated risk
            # Step 3: Imminent risk (still normal playback error, but resources saturated!)
            # Step 4: Prevented/Scaled (resources recovered)
            if self.predictive_step == 2:
                return self._attach_media_signals({
                    "event_title": self.event_title,
                    "status": "WATCH",
                    "playback_error_rate_pct": 0.44,
                    "transcoder_latency_ms": 340.0,
                    "gpu_allocation_failure_pct": 0.0,
                    "concurrent_viewers": 11_200_000,
                    "affected_viewers": 0,
                    "affected_regions": [],
                    "active_cluster": "transcoder-syd-01",
                    "routing_weights": self.routing_weights,
                    "recent_deployment": None,
                    "transcoder_pool_size": self.transcoder_pool_size,
                    "queue_depth": 28,
                    "gpu_utilization_pct": 81.0
                })
            elif self.predictive_step == 3:
                return self._attach_media_signals({
                    "event_title": self.event_title,
                    "status": "IMMINENT_RISK",
                    "playback_error_rate_pct": 0.48,
                    "transcoder_latency_ms": 470.0,
                    "gpu_allocation_failure_pct": 0.0,
                    "concurrent_viewers": 11_800_000,
                    "affected_viewers": 0,
                    "affected_regions": [],
                    "active_cluster": "transcoder-syd-01",
                    "routing_weights": self.routing_weights,
                    "recent_deployment": self.recent_deployment,
                    "transcoder_pool_size": self.transcoder_pool_size,
                    "queue_depth": 48,
                    "gpu_utilization_pct": 93.4
                })

            elif self.predictive_step == 4 or self.preventive_scaled:
                return self._attach_media_signals({
                    "event_title": self.event_title,
                    "status": "PREVENTED",
                    "playback_error_rate_pct": 0.38,
                    "transcoder_latency_ms": 260.0,
                    "gpu_allocation_failure_pct": 0.0,
                    "concurrent_viewers": 12_400_000,
                    "affected_viewers": 0,
                    "affected_regions": [],
                    "active_cluster": "transcoder-syd-01",
                    "routing_weights": self.routing_weights,
                    "recent_deployment": None,
                    "transcoder_pool_size": self.transcoder_pool_size,
                    "queue_depth": 12,
                    "gpu_utilization_pct": 61.2
                })
            else:
                data = {
                    "event_title": self.event_title,
                    "status": "HEALTHY",
                    "playback_error_rate_pct": 0.41,
                    "transcoder_latency_ms": 220.0,
                    "gpu_allocation_failure_pct": 0.0,
                    "concurrent_viewers": 10_800_000,
                    "affected_viewers": 0,
                    "affected_regions": [],
                    "active_cluster": "transcoder-syd-01",
                    "routing_weights": self.routing_weights,
                    "recent_deployment": None,
                    "transcoder_pool_size": self.transcoder_pool_size,
                    "queue_depth": 6,
                    "gpu_utilization_pct": 65.0
                }
                return self._attach_media_signals(data)

    def _attach_media_signals(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        snapshot.update({
            "scte_timing_drift_ms": self.scte_timing_drift_ms,
            "splice_alignment_error_ms": self.splice_alignment_error_ms,
            "ad_pod_drop_pct": self.ad_pod_drop_pct,
            "tracking_error_ratio": self.tracking_error_ratio,
            "av_sync_drift_ms": self.av_sync_drift_ms,
            "loudness_lufs": self.loudness_lufs,
            "loudness_deviation_lufs": self.loudness_deviation_lufs,
            "frame_drop_ratio_pct": self.frame_drop_ratio_pct,
            "black_frame_ratio_pct": self.black_frame_ratio_pct,
        })
        return snapshot

media_env = MediaEnvironment()
