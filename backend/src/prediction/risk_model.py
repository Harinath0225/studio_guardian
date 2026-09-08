from typing import Dict, List, Any, Tuple
from src.prediction.thresholds import get_signal_weights, classify_risk_tier


SIGNAL_METADATA = {
    "gpu_pressure": {"label": "GPU Utilization Saturation", "raw_key": "gpu_utilization_pct"},
    "queue_growth": {"label": "Transcoder Queue Buildup", "raw_key": "queue_depth"},
    "latency_pressure": {"label": "Segment Fetch Latency", "raw_key": "transcoder_latency_ms"},
    "error_growth": {"label": "Playback Buffer Degradation", "raw_key": "playback_error_rate_pct"},
    "viewer_growth": {"label": "Audience Concurrency Surge", "raw_key": "active_viewers"},
    "deployment_risk": {"label": "Recent Config Deployment Recency", "raw_key": "deployment_recency"},
}


class RiskModel:
    """
    Deterministic risk model evaluating multi-signal pressure on live media infrastructure.
    Calculates weighted composite risk score [0.0, 1.0] and detailed contributing factors.
    """

    def __init__(self, custom_weights: Dict[str, float] = None):
        self.weights = custom_weights or get_signal_weights()

    def calculate_risk(
        self,
        normalized_signals: Dict[str, float],
        raw_metrics: Dict[str, Any],
    ) -> Tuple[float, str, List[Dict[str, Any]]]:
        """
        Calculates composite risk score, tier, and breakdown of contributors.
        Returns (risk_score, risk_tier, contributors_list).
        """
        weights = self.weights
        total_score = 0.0
        contributors = []

        for signal_key, weight in weights.items():
            norm_val = normalized_signals.get(signal_key, 0.0)
            # Contribution points scaled to 100 max
            points = round(norm_val * weight * 100.0, 2)
            total_score += norm_val * weight

            meta = SIGNAL_METADATA.get(signal_key, {"label": signal_key, "raw_key": signal_key})
            raw_val = raw_metrics.get(meta["raw_key"], norm_val)

            contributors.append({
                "name": signal_key,
                "label": meta["label"],
                "raw_value": float(raw_val) if isinstance(raw_val, (int, float)) else 0.0,
                "normalized": round(norm_val, 4),
                "points": points,
            })

        # Leading indicator compound saturation boost:
        # In live streaming, when primary bottleneck indicators (GPU + queue) reach critical saturation (>0.80),
        # playback failure is imminent even before player-side errors spike.
        gpu_norm = normalized_signals.get("gpu_pressure", 0.0)
        queue_norm = normalized_signals.get("queue_growth", 0.0)
        lat_norm = normalized_signals.get("latency_pressure", 0.0)
        if gpu_norm >= 0.85 and queue_norm >= 0.80:
            compound_score = (gpu_norm * 0.40) + (queue_norm * 0.35) + (lat_norm * 0.25)
            if compound_score > total_score:
                scale_factor = compound_score / total_score if total_score > 0 else 1.0
                total_score = compound_score
                for c in contributors:
                    c["points"] = round(c["points"] * scale_factor, 2)

        # Clamp total risk score to [0.0, 1.0]
        risk_score = round(min(1.0, max(0.0, total_score)), 4)
        risk_tier = classify_risk_tier(risk_score)

        # Sort contributors in descending order of points impact
        contributors.sort(key=lambda x: x["points"], reverse=True)

        return risk_score, risk_tier, contributors

    def identify_failure_mode(self, normalized_signals: Dict[str, float]) -> str:
        """Identifies the most probable operational failure mode based on dominant signal cluster."""
        gpu = normalized_signals.get("gpu_pressure", 0.0)
        queue = normalized_signals.get("queue_growth", 0.0)
        latency = normalized_signals.get("latency_pressure", 0.0)
        error = normalized_signals.get("error_growth", 0.0)
        deployment = normalized_signals.get("deployment_risk", 0.0)

        if gpu > 0.75 and queue > 0.70:
            return "transcoder_capacity_exhaustion"
        elif latency > 0.80 and queue > 0.60:
            return "origin_ingest_bottleneck"
        elif error > 0.70 and deployment > 0.50:
            return "regressive_deployment_failure"
        elif gpu > 0.80:
            return "gpu_hardware_saturation"
        elif latency > 0.75:
            return "regional_network_congestion"
        else:
            return "unspecified_resource_saturation"


risk_model = RiskModel()
