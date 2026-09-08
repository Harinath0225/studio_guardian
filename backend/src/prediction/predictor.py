from typing import Dict, Any, Tuple
from src.prediction.feature_normalizer import feature_normalizer
from src.prediction.risk_model import risk_model


class Predictor:
    """
    Predictive engine estimating:
    1. Deterministic failure time horizon window (minutes to degradation).
    2. Independent data and signal confidence score [0.0, 1.0].
    """

    def __init__(self):
        pass

    def estimate_time_to_threshold(
        self,
        risk_score: float,
        normalized_signals: Dict[str, float],
        raw_metrics: Dict[str, Any],
    ) -> Dict[str, int]:
        """
        Estimates time until service degradation threshold based on distance and positive rate of change.
        Returns {'min': min_minutes, 'max': max_minutes} bounded between 3 and 15 minutes.
        """
        # Degradation threshold defined at risk_score = 0.90
        critical_threshold = 0.90
        distance = max(0.01, critical_threshold - risk_score)

        # Use queue and latency growth rates as primary velocity proxy
        queue_growth = normalized_signals.get("queue_growth", 0.1)
        gpu_pressure = normalized_signals.get("gpu_pressure", 0.5)

        # Composite velocity per minute (0.01 to 0.15)
        rate = max(0.02, (queue_growth * 0.08) + (gpu_pressure * 0.04))

        estimated_minutes = distance / rate

        # Build uncertainty bounds: [0.8x, 1.3x]
        window_min = int(max(3, round(estimated_minutes * 0.8)))
        window_max = int(max(window_min + 2, min(15, round(estimated_minutes * 1.3))))

        # If already at IMMINENT risk, collapse window to immediate 3-7 mins
        if risk_score >= 0.85:
            window_min = max(3, min(window_min, 6))
            window_max = max(window_min + 2, min(window_max, 10))

        return {"min": window_min, "max": window_max}

    def calculate_confidence(
        self,
        raw_metrics: Dict[str, Any],
        normalized_signals: Dict[str, float],
        telemetry_age_sec: float = 2.0,
    ) -> float:
        """
        Calculates independent confidence score [0.0, 1.0] based on:
        1. Telemetry freshness (<15 seconds old)
        2. Expected sample completeness
        3. Multi-signal directional concordance (at least 2 leading signals trending in unison)
        """
        # 1. Freshness factor (1.0 if <5s, down to 0.5 at 15s)
        if telemetry_age_sec <= 5.0:
            freshness_factor = 1.0
        elif telemetry_age_sec <= 15.0:
            freshness_factor = 1.0 - ((telemetry_age_sec - 5.0) / 20.0)
        else:
            freshness_factor = 0.40

        # 2. Completeness factor (required sensor keys present)
        required_keys = ["gpu_utilization_pct", "transcoder_latency_ms", "queue_depth"]
        present_count = sum(1 for k in required_keys if k in raw_metrics)
        completeness_factor = present_count / len(required_keys)

        # 3. Multi-signal concordance: count signals above normal baseline (0.50)
        elevated_signals = sum(
            1 for k in ["gpu_pressure", "queue_growth", "latency_pressure"]
            if normalized_signals.get(k, 0.0) >= 0.50
        )
        if elevated_signals >= 2:
            concordance_factor = 1.0
        elif elevated_signals == 1:
            concordance_factor = 0.80
        else:
            concordance_factor = 0.65

        # Weighted composite confidence
        composite_confidence = (
            (freshness_factor * 0.35) +
            (completeness_factor * 0.35) +
            (concordance_factor * 0.30)
        )
        return round(min(1.0, max(0.0, composite_confidence)), 2)


predictor = Predictor()
