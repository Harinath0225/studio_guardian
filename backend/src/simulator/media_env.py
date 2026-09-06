import time
from typing import Dict, Any, List
from enum import Enum

class StreamState(str, Enum):
    HEALTHY = "HEALTHY"
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

        # Failure injection overrides
        self.force_recovery_failure: bool = False

    def set_state(self, new_state: StreamState) -> None:
        self.state = new_state
        self.last_state_change = time.time()

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
        self.last_state_change = time.time()

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
            return {
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
                "recent_deployment": self.recent_deployment
            }
        elif self.state == StreamState.RECOVERED:
            return {
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
                "recent_deployment": self.recent_deployment
            }
        else: # HEALTHY
            return {
                "event_title": self.event_title,
                "status": self.state.value,
                "playback_error_rate_pct": 0.41,
                "transcoder_latency_ms": 18.2,
                "gpu_allocation_failure_pct": 0.0,
                "concurrent_viewers": self.total_viewers,
                "affected_viewers": 0,
                "affected_regions": [],
                "active_cluster": "transcoder-syd-01",
                "routing_weights": self.routing_weights,
                "recent_deployment": None
            }

media_env = MediaEnvironment()
