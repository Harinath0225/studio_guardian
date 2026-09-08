import time
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.prediction.feature_normalizer import feature_normalizer
from src.prediction.risk_model import risk_model
from src.prediction.predictor import predictor
from src.prediction.thresholds import (
    classify_risk_tier,
    determine_predictive_state,
    PREDICTIVE_STATES,
)
from src.prediction.schemas import (
    SignalContributor,
    FailureWindow,
    RuntimeMetadata,
    PreventionProposalResponse,
    PredictiveStatusResponse,
)
from src.integrations.mcp_tools import query_predictive_telemetry
from src.config import settings


class PredictiveHypothesisOutput(BaseModel):
    failure_mode: str = Field(..., description="High-level category of impending failure")
    failure_hypothesis: str = Field(..., description="Detailed causal narrative explaining the leading signals")
    reasoning_summary: str = Field(..., description="Concise SRE operational rationale")
    recommended_action: str = Field(..., description="Recommended preventive action")
    uncertainty_factors: List[str] = Field(default_factory=list, description="Caveats or factors affecting projection certainty")


class PredictiveRiskAgent(BaseAgent):
    """
    Predictive Risk Agent.
    Responsibilities:
    1. Query leading operational signals via Grafana MCP (Prometheus, Loki, Tempo, Alerts).
    2. Normalize multi-dimensional metrics deterministically using operational SLO baselines.
    3. Compute composite risk score, tier, and signal contributor breakdown.
    4. Estimate failure horizon window and data confidence independently.
    5. Formulate structured causal hypothesis and prevention proposal using Gemini reasoning.
    6. Maintain execution frames and Vertex AI session runtime metadata.
    """

    def __init__(self):
        super().__init__(
            name="PredictiveRiskAgent",
            role_description="Continuous operational risk forecasting and preventive hypothesis agent in Vertex AI Agent Engine"
        )
        self.session_id = f"session-pred-{uuid.uuid4().hex[:8]}"
        self.execution_frames: List[Dict[str, Any]] = []

    def get_system_instruction(self) -> str:
        return (
            "You are the Studio Guardian Predictive Risk Agent running within Google Cloud Vertex AI Agent Engine. "
            "Your mission is PREDICTIVE PREVENTION: identify emerging system failure conditions BEFORE viewer playback degradation begins. "
            "You evaluate leading telemetry signals: GPU utilization saturation, worker queue depth growth, segment fetch latency, and viewer surge. "
            "Never invent or hallucinate metrics; all facts must stem directly from observed telemetry and deterministic normalization. "
            "Formulate an authoritative failure hypothesis, articulate uncertainty factors, and recommend allowlisted preventive actions."
        )

    def _record_frame(self, stage: str, details: Dict[str, Any]) -> None:
        """Records an execution frame for Vertex AI Agent Engine tracing."""
        frame = {
            "timestamp": time.time(),
            "stage": stage,
            "session_id": self.session_id,
            "details": details,
        }
        self.execution_frames.append(frame)

    async def evaluate_operational_risk(
        self,
        repository: Optional[Any] = None,
        snapshot_id: Optional[str] = None,
    ) -> PredictiveStatusResponse:
        t0 = time.time()
        self._record_frame("START_EVALUATION", {"snapshot_id": snapshot_id})

        # 1. Fetch live or mock Grafana MCP telemetry
        raw_metrics = await query_predictive_telemetry(
            repository=repository,
            snapshot_id=snapshot_id
        )
        self._record_frame("TELEMETRY_INGESTION", {
            "provider_source": raw_metrics.get("provider_source"),
            "gpu": raw_metrics.get("gpu_utilization_pct"),
            "queue": raw_metrics.get("queue_depth"),
            "latency": raw_metrics.get("transcoder_latency_ms"),
            "errors": raw_metrics.get("playback_error_rate_pct"),
            "viewers": raw_metrics.get("active_viewers"),
        })

        # 2. Deterministic feature normalization
        normalized_signals = feature_normalizer.normalize_features(raw_metrics)
        self._record_frame("FEATURE_NORMALIZATION", {"normalized": normalized_signals})

        # 3. Deterministic risk calculation
        risk_score, risk_tier, contributors_raw = risk_model.calculate_risk(normalized_signals, raw_metrics)
        contributors = [
            SignalContributor(
                name=c["name"],
                label=c["label"],
                raw_value=c["raw_value"],
                normalized=c["normalized"],
                points=c["points"]
            )
            for c in contributors_raw
        ]

        # 4. Predictor estimation: failure window & confidence
        window_dict = predictor.estimate_time_to_threshold(risk_score, normalized_signals, raw_metrics)
        failure_window = FailureWindow(min=window_dict["min"], max=window_dict["max"])
        confidence = predictor.calculate_confidence(raw_metrics, normalized_signals)

        # 5. Operating state mapping
        state = determine_predictive_state(risk_score)
        self._record_frame("RISK_ASSESSMENT", {
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "state": state,
            "confidence": confidence,
            "window": window_dict,
        })

        # 6. Gemini reasoning for structured causal narrative
        is_high_risk = risk_score >= 0.60
        prompt = (
            f"Operational Telemetry Risk Assessment:\n"
            f"- Composite Risk Score: {risk_score:.3f} (Tier: {risk_tier}, State: {state})\n"
            f"- Data Confidence: {confidence:.2f}\n"
            f"- Estimated Failure Window: {failure_window.min} to {failure_window.max} minutes\n"
            f"- Telemetry Values:\n"
            f"  * GPU Utilization: {raw_metrics.get('gpu_utilization_pct', 0.0):.1f}%\n"
            f"  * Transcoder Queue Depth: {raw_metrics.get('queue_depth', 0)}\n"
            f"  * Segment Fetch Latency: {raw_metrics.get('transcoder_latency_ms', 0.0):.1f} ms\n"
            f"  * Playback Error Rate: {raw_metrics.get('playback_error_rate_pct', 0.0):.2f}%\n"
            f"  * Active Viewers: {raw_metrics.get('active_viewers', 0):,}\n"
            f"- Top Contributing Signals:\n"
            + "\n".join([f"  * {c.label}: +{c.points} pts (raw: {c.raw_value})" for c in contributors[:3]]) +
            "\n\nProvide the failure mode, causal failure hypothesis, reasoning summary, and recommended action."
        )

        fallback_hypothesis = {
            "failure_mode": (
                "Transcoder Worker Pool Capacity Saturation"
                if is_high_risk
                else "Nominal Operating State"
            ),
            "failure_hypothesis": (
                f"Surge in high-bitrate viewer concurrency has driven transcoder worker GPU utilization to "
                f"{raw_metrics.get('gpu_utilization_pct', 0):.1f}% with worker queue depth accumulating at "
                f"{raw_metrics.get('queue_depth', 0)} chunks. Linear projection indicates buffer starvation and "
                f"playback stalling will manifest in {failure_window.min}-{failure_window.max} minutes."
            ) if is_high_risk else "All media pipeline metrics operating well within designated SLO safety bounds.",
            "reasoning_summary": (
                f"Prometheus GPU pressure and Loki queue warnings confirm approaching bottleneck. "
                f"Immediate horizontal capacity expansion recommended before degradation reaches viewer players."
            ) if is_high_risk else "Continuous leading telemetry sweep reports stable transcode pipelines.",
            "recommended_action": "scale_transcoder_pool" if is_high_risk else "CONTINUE_MONITORING",
            "uncertainty_factors": [
                "Burstiness of viewer incoming stream connection rate",
                "Downstream CDN cache hit ratio variance"
            ] if is_high_risk else ["Telemetry signals nominal"]
        }

        reasoning = await self.execute_structured(
            prompt=prompt,
            response_schema=PredictiveHypothesisOutput,
            fallback_data=fallback_hypothesis
        )
        self._record_frame("GEMINI_REASONING", reasoning.model_dump())

        # 7. Build Prevention Proposal if risk >= 0.75
        active_proposal: Optional[PreventionProposalResponse] = None
        if risk_score >= 0.75:
            # Check policy criteria
            requires_approval = False
            policy_verdict = "AUTO_APPROVED"
            blast_radius = 15.0 # default scale_transcoder_pool blast radius

            if blast_radius > settings.PREDICTIVE_BLAST_RADIUS_MAX_AUTO_PREVENT:
                requires_approval = True
                policy_verdict = "WAITING_HUMAN_APPROVAL"
            elif confidence < settings.PREDICTIVE_CONFIDENCE_THRESHOLD_AUTO_PREVENT:
                requires_approval = True
                policy_verdict = "WAITING_HUMAN_APPROVAL"
            elif risk_score < settings.PREDICTIVE_RISK_THRESHOLD_AUTO_PREVENT:
                requires_approval = True
                policy_verdict = "WAITING_HUMAN_APPROVAL"

            active_proposal = PreventionProposalResponse(
                id=f"prop-{uuid.uuid4().hex[:8]}",
                action_type="scale_transcoder_pool",
                target_service="transcoder-pool",
                blast_radius_pct=blast_radius,
                expected_loss_without_action=18000.0,
                cost_of_prevention=450.0,
                expected_avoided_exposure=17550.0,
                policy_verdict=policy_verdict,
                status="DISPATCHED" if policy_verdict == "AUTO_APPROVED" else "PENDING_APPROVAL",
                requires_approval=requires_approval,
            )

        ai_info = self.ai_client.get_runtime_info()
        runtime_metadata = RuntimeMetadata(
            agent_engine=f"Vertex AI ({ai_info.get('model', settings.GEMINI_MODEL)})",
            agent_runtime=ai_info.get("agent_runtime", "Vertex AI Agent Engine"),
            active_agent="PredictiveRiskAgent",
            current_specialist="PredictiveRiskAgent",
            session_id=self.session_id,
            agent_state="EVALUATED",
            telemetry_source=raw_metrics.get("provider_source", "LIVE_GRAFANA_MCP"),
            execution_frames=self.execution_frames,
        )

        response = PredictiveStatusResponse(
            state=state,
            risk_score=risk_score,
            risk_level=risk_tier,
            confidence_score=confidence,
            predicted_failure_mode=reasoning.failure_mode,
            estimated_window_minutes=failure_window,
            contributors=contributors,
            failure_hypothesis=reasoning.failure_hypothesis,
            reasoning_summary=reasoning.reasoning_summary,
            active_proposal=active_proposal,
            runtime_metadata=runtime_metadata,
        )

        self._record_frame("COMPLETE_EVALUATION", {
            "duration_ms": (time.time() - t0) * 1000.0,
            "state": response.state
        })
        return response
