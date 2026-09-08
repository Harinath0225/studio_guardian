import time
from typing import Dict, List, Tuple, Any, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)


class FeatureNormalizer:
    """
    Deterministic telemetry normalizer for live media SRE operations.
    Converts multi-dimensional operational metrics into dimensionless [0.0, 1.0] features.
    
    1. Static Gauges: Min-max clamped against strict operational SLO boundaries.
    2. Dynamic Velocity: Computes 60-second sliding regression slope (dy/dt) and acceleration (d²y/dt²).
    3. Baseline Deviation: Normalizes distance from expected nominal operating parameters.
    """

    def __init__(self, history_window_sec: float = 60.0, max_history_points: int = 12):
        self.history_window_sec = history_window_sec
        self.max_history_points = max_history_points
        # In-memory circular history buffer: timestamp -> metric dict
        self._history: deque[Tuple[float, Dict[str, float]]] = deque(maxlen=max_history_points)

        # Operational SLO Baselines (Nominal Floor, Critical Ceiling)
        self.slo_bounds = {
            "gpu_utilization_pct": {"floor": 50.0, "ceil": 95.0},
            "transcoder_latency_ms": {"floor": 150.0, "ceil": 500.0},
            "queue_depth": {"floor": 5.0, "ceil": 50.0},
            "playback_error_rate_pct": {"floor": 0.30, "ceil": 1.50},
            "regional_saturation": {"floor": 60.0, "ceil": 95.0},
            "active_viewers": {"floor": 5_000_000.0, "ceil": 15_000_000.0},
        }

        # Max acceptable rate-of-change per minute for slope normalization
        self.max_slope_per_min = {
            "queue_growth": 40.0,       # +40 chunks/min is 1.0 max velocity
            "error_growth": 0.50,       # +0.50% error growth/min is 1.0
            "latency_growth": 150.0,    # +150ms/min is 1.0
            "viewer_growth": 2_000_000.0 # +2M viewers/min is 1.0
        }

    def record_sample(self, raw_metrics: Dict[str, Any], timestamp: Optional[float] = None) -> None:
        """Appends a new telemetry sample to the sliding window buffer."""
        ts = timestamp or time.time()
        point = {
            "gpu_utilization_pct": float(raw_metrics.get("gpu_utilization_pct", 0.0)),
            "transcoder_latency_ms": float(raw_metrics.get("transcoder_latency_ms", 0.0)),
            "queue_depth": float(raw_metrics.get("queue_depth", 0.0)),
            "playback_error_rate_pct": float(raw_metrics.get("playback_error_rate_pct", 0.0)),
            "active_viewers": float(raw_metrics.get("active_viewers", 0.0)),
        }
        self._history.append((ts, point))
        self._prune_history(ts)

    def _prune_history(self, current_ts: float) -> None:
        """Drops samples older than history_window_sec."""
        cutoff = current_ts - self.history_window_sec
        while self._history and self._history[0][0] < cutoff:
            self._history.popleft()

    def clamp_min_max(self, value: float, floor: float, ceil: float) -> float:
        """Min-max clamping to [0.0, 1.0]."""
        if ceil <= floor:
            return 0.0
        clamped = max(floor, min(ceil, value))
        return round((clamped - floor) / (ceil - floor), 4)

    def calculate_linear_slope(self, metric_name: str) -> float:
        """
        Calculates the linear regression slope (dy/dt per minute) over the historical sample window.
        Returns units-per-minute rate of change.
        """
        if len(self._history) < 2:
            return 0.0

        ts_list = [p[0] for p in self._history]
        val_list = [p[1].get(metric_name, 0.0) for p in self._history]

        t0 = ts_list[0]
        # Convert seconds to minutes for clean rates
        times_min = [(t - t0) / 60.0 for t in ts_list]
        n = len(times_min)
        mean_t = sum(times_min) / n
        mean_y = sum(val_list) / n

        denom = sum((t - mean_t) ** 2 for t in times_min)
        if denom == 0:
            return 0.0

        numer = sum((times_min[i] - mean_t) * (val_list[i] - mean_y) for i in range(n))
        slope = numer / denom
        return slope

    def calculate_acceleration(self, metric_name: str) -> float:
        """Calculates 2nd derivative (change in slope between first half and second half of window)."""
        if len(self._history) < 4:
            return 0.0

        mid = len(self._history) // 2
        first_half = list(self._history)[:mid]
        second_half = list(self._history)[mid:]

        def _half_slope(half: List[Tuple[float, Dict[str, float]]]) -> float:
            if len(half) < 2:
                return 0.0
            t_span = (half[-1][0] - half[0][0]) / 60.0
            if t_span <= 0:
                return 0.0
            return (half[-1][1].get(metric_name, 0.0) - half[0][1].get(metric_name, 0.0)) / t_span

        slope1 = _half_slope(first_half)
        slope2 = _half_slope(second_half)
        return slope2 - slope1

    def normalize(self, raw_metrics: Dict[str, Any], timestamp: Optional[float] = None) -> Dict[str, float]:
        """
        Executes complete deterministic normalization pipeline for a snapshot.
        Returns a dictionary of normalized signals, each bounded strictly within [0.0, 1.0].
        """
        self.record_sample(raw_metrics, timestamp)


        gpu_raw = float(raw_metrics.get("gpu_utilization_pct", 0.0))
        lat_raw = float(raw_metrics.get("transcoder_latency_ms", 0.0))
        regional_sat_raw = float(raw_metrics.get("regional_saturation", gpu_raw))

        # 1. Static SLO normalizations
        gpu_pressure = self.clamp_min_max(
            gpu_raw,
            self.slo_bounds["gpu_utilization_pct"]["floor"],
            self.slo_bounds["gpu_utilization_pct"]["ceil"]
        )

        latency_pressure = self.clamp_min_max(
            lat_raw,
            self.slo_bounds["transcoder_latency_ms"]["floor"],
            self.slo_bounds["transcoder_latency_ms"]["ceil"]
        )

        regional_saturation = self.clamp_min_max(
            regional_sat_raw,
            self.slo_bounds["regional_saturation"]["floor"],
            self.slo_bounds["regional_saturation"]["ceil"]
        )

        # 2. Dynamic growth slopes & static pressure floors
        queue_slope = self.calculate_linear_slope("queue_depth")
        error_slope = self.calculate_linear_slope("playback_error_rate_pct")
        viewer_slope = self.calculate_linear_slope("active_viewers")

        queue_static = self.clamp_min_max(
            float(raw_metrics.get("queue_depth", 0.0)),
            self.slo_bounds["queue_depth"]["floor"],
            self.slo_bounds["queue_depth"]["ceil"]
        )
        error_static = self.clamp_min_max(
            float(raw_metrics.get("playback_error_rate_pct", 0.0)),
            self.slo_bounds["playback_error_rate_pct"]["floor"],
            self.slo_bounds["playback_error_rate_pct"]["ceil"]
        )
        viewer_static = self.clamp_min_max(
            float(raw_metrics.get("active_viewers", 0.0)),
            self.slo_bounds["active_viewers"]["floor"],
            self.slo_bounds["active_viewers"]["ceil"]
        )

        # Positive velocity clamped to [0.0, 1.0], with static saturation floor
        queue_growth = max(queue_static, min(1.0, max(0.0, queue_slope / self.max_slope_per_min["queue_growth"])))
        error_growth = max(error_static, min(1.0, max(0.0, error_slope / self.max_slope_per_min["error_growth"])))
        viewer_growth = max(viewer_static * 0.7, min(1.0, max(0.0, viewer_slope / self.max_slope_per_min["viewer_growth"])))

        # Acceleration booster: If queue is accelerating, apply up to 15% acceleration penalty
        queue_accel = self.calculate_acceleration("queue_depth")
        if queue_accel > 0:
            queue_growth = min(1.0, queue_growth + min(0.15, queue_accel / 100.0))

        # 3. Deployment recency penalty (if a deployment occurred within 300s)
        recent_deployment = raw_metrics.get("recent_deployment")
        deployment_risk = 0.0
        if recent_deployment:
            deployment_risk = 0.60 # Static 0.60 recency penalty if recent deployment is active


        return {
            "gpu_pressure": round(gpu_pressure, 4),
            "queue_growth": round(queue_growth, 4),
            "latency_pressure": round(latency_pressure, 4),
            "error_growth": round(error_growth, 4),
            "viewer_growth": round(viewer_growth, 4),
            "regional_saturation": round(regional_saturation, 4),
            "deployment_risk": round(deployment_risk, 4),
        }

    def normalize_features(self, raw_metrics: Dict[str, Any], timestamp: Optional[float] = None) -> Dict[str, float]:
        """Convenience alias for normalize."""
        return self.normalize(raw_metrics, timestamp)


# Singleton normalizer instance
feature_normalizer = FeatureNormalizer()

