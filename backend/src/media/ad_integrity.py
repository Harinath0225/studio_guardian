"""
Ad Integrity Evaluator.
Evaluates SCTE-35 cue timing drift against configured operational tolerances.
Strictly conforms to Constitution Principle 9:
- Uses configured operational tolerance (default: +-200ms)
- Does NOT claim universal standards compliance without verified profile
- Calculates deterministic ad revenue exposure
"""

from typing import Dict, Any
from pydantic import BaseModel, Field

class AdIntegrityReport(BaseModel):
    stream_id: str = "star-sports-live"
    scte_timing_drift_ms: float
    splice_alignment_error_ms: float
    ad_pod_drop_pct: float
    tracking_error_ratio: float
    operational_tolerance_ms: float = 200.0
    is_anomaly: bool = False
    severity: str = "INFO"
    estimated_ad_exposure_usd: float = 0.0
    recommended_action: str = "NONE"
    summary: str = ""

class AdIntegrityEvaluator:
    def __init__(self, operational_tolerance_ms: float = 200.0, cpm_usd: float = 28.50):
        self.operational_tolerance_ms = operational_tolerance_ms
        self.cpm_usd = cpm_usd

    def evaluate(self, telemetry: Dict[str, Any], total_viewers: int = 12_400_000) -> AdIntegrityReport:
        drift = float(telemetry.get("scte_timing_drift_ms", 0.0))
        splice_err = float(telemetry.get("splice_alignment_error_ms", 0.0))
        pod_drop = float(telemetry.get("ad_pod_drop_pct", 0.0))
        tracking_err = float(telemetry.get("tracking_error_ratio", 0.0))

        is_anomaly = False
        severity = "INFO"
        recommended_action = "NONE"
        
        # Check against configured operational tolerance
        if abs(drift) > 350.0 or pod_drop > 5.0:
            is_anomaly = True
            severity = "CRITICAL"
            recommended_action = "activate_ad_slate"
        elif abs(drift) > self.operational_tolerance_ms or pod_drop > 1.0 or tracking_err > 0.05:
            is_anomaly = True
            severity = "WARNING"
            recommended_action = "resync_scte_cue_stream"

        # Deterministic ad revenue exposure calculation:
        # If pod drops or timing is corrupted, lost impressions across affected viewers
        affected_viewers = int(total_viewers * (pod_drop / 100.0 if pod_drop > 0 else (0.15 if is_anomaly else 0.0)))
        # 12 ads/hour, 5-minute break exposure window
        lost_impressions = affected_viewers * (12.0 * (5.0 / 60.0))
        exposure_usd = round((lost_impressions / 1000.0) * self.cpm_usd, 2)

        summary = (
            f"SCTE-35 cue timing drift observed at {drift:+.1f}ms against configured tolerance of "
            f"+-{self.operational_tolerance_ms:.0f}ms. Ad pod drop: {pod_drop:.1f}%. "
            f"Severity: {severity}."
        )

        return AdIntegrityReport(
            stream_id=telemetry.get("event_title", "star-sports-live"),
            scte_timing_drift_ms=drift,
            splice_alignment_error_ms=splice_err,
            ad_pod_drop_pct=pod_drop,
            tracking_error_ratio=tracking_err,
            operational_tolerance_ms=self.operational_tolerance_ms,
            is_anomaly=is_anomaly,
            severity=severity,
            estimated_ad_exposure_usd=exposure_usd,
            recommended_action=recommended_action,
            summary=summary
        )

ad_integrity_evaluator = AdIntegrityEvaluator()