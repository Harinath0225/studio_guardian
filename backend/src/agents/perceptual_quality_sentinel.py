"""
Perceptual Quality Sentinel Agent.
Monitors AV synchronization drift, loudness deviations from -24 LUFS, video frame drops,
and black frame percentage as lightweight operational signals.
"""

from typing import Dict, Any
from pydantic import BaseModel
from src.agents.base import BaseAgent
from src.media.perceptual_quality import perceptual_quality_evaluator, PerceptualQualityReport

class PerceptualQualityAgentResponse(BaseModel):
    agent_name: str = "PerceptualQualitySentinel"
    report: PerceptualQualityReport
    sentinel_narrative: str
    recommended_action: str

class PerceptualQualitySentinel(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PerceptualQualitySentinel",
            role_description="Monitors AV sync offset, loudness deviation (-24 LUFS), frame drops, and black frame ratios"
        )

    def get_system_instruction(self) -> str:
        return (
            "You are the Perceptual Quality Sentinel for Studio Guardian. "
            "You evaluate lightweight, measurable perceptual broadcast signals: "
            "audio/video synchronization drift, audio loudness deviation against target -24 LUFS, "
            "video frame drop percentages, and black-frame anomalies. "
            "Do NOT claim to be a full broadcast hardware QC platform. "
            "Provide succinct operational alerts on perceptible user impairments."
        )

    async def evaluate_stream(self, telemetry: Dict[str, Any]) -> PerceptualQualityAgentResponse:
        report = perceptual_quality_evaluator.evaluate(telemetry)

        prompt = (
            f"Evaluate perceptual media quality for stream '{report.stream_id}':\n"
            f"- AV Sync Drift: {report.av_sync_drift_ms:+.1f}ms\n"
            f"- Audio Loudness: {report.loudness_lufs:.1f} LUFS (Target: -24.0 LUFS, Deviation: {report.loudness_deviation_lufs:.1f})\n"
            f"- Video Frame Drop: {report.frame_drop_ratio_pct:.2f}%\n"
            f"- Black Frame Ratio: {report.black_frame_ratio_pct:.2f}%\n"
            f"- Status: {report.severity}, Primary Defect: {report.primary_defect}\n"
            f"Deliver an operational summary and suggested engineering action."
        )

        fallback_action = "NONE"
        if report.primary_defect == "CRITICAL_AV_DESYNC":
            fallback_action = "reset_pts_clock_sync"
        elif report.primary_defect == "BLACK_FRAME_OUTAGE":
            fallback_action = "switch_packager_backup"
        elif report.is_anomaly:
            fallback_action = "adjust_transcoder_bitrate_profile"

        fallback_data = {
            "agent_name": "PerceptualQualitySentinel",
            "report": report.model_dump(),
            "sentinel_narrative": (
                f"Stream quality is {report.severity}. Primary defect: {report.primary_defect}. "
                f"AV sync offset is {report.av_sync_drift_ms:+.1f}ms, loudness is {report.loudness_lufs:.1f} LUFS. "
                + ("Immediate intervention recommended." if report.is_anomaly else "Stream perceptual metrics are nominal.")
            ),
            "recommended_action": fallback_action
        }

        try:
            res = await self.execute_structured(
                prompt=prompt,
                response_schema=PerceptualQualityAgentResponse,
                fallback_data=fallback_data
            )
            res.report = report
            return res
        except Exception:
            return PerceptualQualityAgentResponse(**fallback_data)