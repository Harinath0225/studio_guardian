"""
Perceptual Quality Evaluator.
Strictly conforms to Constitution Principle 10:
- Intentionally lightweight measurable signals only:
  1. AV sync offset (ms)
  2. Integrated loudness deviation from -24.0 LUFS
  3. Video frame drop ratio (%)
  4. Black-frame ratio (%)
- Does NOT emulate a full broadcast QC platform.
"""

from typing import Dict, Any
from pydantic import BaseModel

class PerceptualQualityReport(BaseModel):
    stream_id: str = "star-sports-live"
    av_sync_drift_ms: float
    loudness_lufs: float
    loudness_deviation_lufs: float
    frame_drop_ratio_pct: float
    black_frame_ratio_pct: float
    is_anomaly: bool = False
    severity: str = "INFO"
    primary_defect: str = "NONE"
    summary: str = ""

class PerceptualQualityEvaluator:
    TARGET_LOUDNESS_LUFS: float = -24.0
    NOMINAL_AV_SYNC_TOLERANCE_MS: float = 25.0
    CRITICAL_AV_SYNC_TOLERANCE_MS: float = 250.0

    def evaluate(self, telemetry: Dict[str, Any]) -> PerceptualQualityReport:
        av_sync = float(telemetry.get("av_sync_drift_ms", 15.0))
        loudness = float(telemetry.get("loudness_lufs", -24.0))
        loudness_dev = abs(loudness - self.TARGET_LOUDNESS_LUFS)
        frame_drop = float(telemetry.get("frame_drop_ratio_pct", 0.1))
        black_frame = float(telemetry.get("black_frame_ratio_pct", 0.0))

        is_anomaly = False
        severity = "INFO"
        primary_defect = "NONE"

        if abs(av_sync) > self.CRITICAL_AV_SYNC_TOLERANCE_MS or frame_drop > 5.0 or black_frame > 2.0 or loudness_dev > 4.0:
            is_anomaly = True
            severity = "CRITICAL"
            if abs(av_sync) > self.CRITICAL_AV_SYNC_TOLERANCE_MS:
                primary_defect = "CRITICAL_AV_DESYNC"
            elif black_frame > 2.0:
                primary_defect = "BLACK_FRAME_OUTAGE"
            elif frame_drop > 5.0:
                primary_defect = "SEVERE_VIDEO_STUTTER"
            else:
                primary_defect = "AUDIO_LOUDNESS_VIOLATION"
        elif abs(av_sync) > 100.0 or frame_drop > 2.0 or black_frame > 0.5 or loudness_dev > 2.0:
            is_anomaly = True
            severity = "WARNING"
            if abs(av_sync) > 100.0:
                primary_defect = "ELEVATED_AV_SYNC_DRIFT"
            elif frame_drop > 2.0:
                primary_defect = "ELEVATED_FRAME_DROPS"
            else:
                primary_defect = "LOUDNESS_DRIFT"

        summary = (
            f"Perceptual telemetry: AV sync {av_sync:+.1f}ms, Loudness {loudness:.1f} LUFS "
            f"(deviation {loudness_dev:.1f}), Dropped frames {frame_drop:.2f}%, Black frames {black_frame:.2f}%. "
            f"Status: {severity}."
        )

        return PerceptualQualityReport(
            stream_id=telemetry.get("event_title", "star-sports-live"),
            av_sync_drift_ms=av_sync,
            loudness_lufs=loudness,
            loudness_deviation_lufs=loudness_dev,
            frame_drop_ratio_pct=frame_drop,
            black_frame_ratio_pct=black_frame,
            is_anomaly=is_anomaly,
            severity=severity,
            primary_defect=primary_defect,
            summary=summary
        )

perceptual_quality_evaluator = PerceptualQualityEvaluator()