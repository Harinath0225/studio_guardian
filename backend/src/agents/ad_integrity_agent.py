"""
Ad Integrity Specialist Agent.
Analyzes SCTE-35 ad splice timing drift against configured operational tolerances (default +-200ms)
and quantifies ad revenue burn risk without altering server CPU/Memory health.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from src.agents.base import BaseAgent
from src.media.ad_integrity import ad_integrity_evaluator, AdIntegrityReport

class AdIntegrityAgentResponse(BaseModel):
    agent_name: str = "AdIntegrityAgent"
    report: AdIntegrityReport
    executive_narrative: str
    action_proposal: str

class AdIntegrityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AdIntegrityAgent",
            role_description="Monitors SCTE-35 splice timing drift, ad pod drops, and ad tracking health against configured operational tolerance"
        )

    def get_system_instruction(self) -> str:
        return (
            "You are the Ad Integrity Specialist Agent for Studio Guardian. "
            "Your role is to detect SCTE-35 splice timing drift and ad pod corruption in live streaming broadcasts. "
            "Evaluate metrics strictly against the configured operational tolerance (+-200ms). "
            "Do NOT make unsupported claims about international compliance standards. "
            "Explain the business risk and propose mitigations (such as activating the emergency backup ad slate)."
        )

    async def inspect_stream(self, telemetry: Dict[str, Any], total_viewers: int = 12_400_000) -> AdIntegrityAgentResponse:
        # Deterministic evaluation first
        report = ad_integrity_evaluator.evaluate(telemetry, total_viewers=total_viewers)

        prompt = (
            f"Analyze SCTE-35 ad splice status for stream '{report.stream_id}':\n"
            f"- SCTE-35 Cue Timing Drift: {report.scte_timing_drift_ms:+.1f}ms (Operational tolerance: +-{report.operational_tolerance_ms:.0f}ms)\n"
            f"- Splice Alignment Error: {report.splice_alignment_error_ms:.1f}ms\n"
            f"- Ad Pod Drop Rate: {report.ad_pod_drop_pct:.1f}%\n"
            f"- Estimated Ad Revenue Exposure: ${report.estimated_ad_exposure_usd:,.2f}\n"
            f"- Anomaly Detected: {report.is_anomaly} (Severity: {report.severity})\n"
            f"Provide a concise executive explanation and recommend immediate action."
        )

        fallback_data = {
            "agent_name": "AdIntegrityAgent",
            "report": report.model_dump(),
            "executive_narrative": (
                f"SCTE-35 cue timing drift is {report.scte_timing_drift_ms:+.1f}ms against the configured operational tolerance of "
                f"+-{report.operational_tolerance_ms:.0f}ms. "
                + (f"Ad pod drop stands at {report.ad_pod_drop_pct:.1f}% putting ${report.estimated_ad_exposure_usd:,.2f} in ad revenue at risk." if report.is_anomaly else "Ad insertion timing is currently within tolerance.")
            ),
            "action_proposal": report.recommended_action
        }

        try:
            res = await self.execute_structured(
                prompt=prompt,
                response_schema=AdIntegrityAgentResponse,
                fallback_data=fallback_data
            )
            # Ensure deterministic figures cannot be altered
            res.report = report
            return res
        except Exception:
            return AdIntegrityAgentResponse(**fallback_data)