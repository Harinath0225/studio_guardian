import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.persistence.models import (
    PredictiveSnapshot,
    PredictionEvidence,
    PredictionDecision,
    PreventionAction,
    PreventionVerification,
    PredictionFingerprint,
)

logger = logging.getLogger(__name__)


class PredictiveRepository:
    """Repository handling persistence and queries for the Predictive Prevention lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_snapshot(
        self,
        raw_metrics: Optional[Dict[str, Any]] = None,
        normalized_metrics: Optional[Dict[str, float]] = None,
        channel_id: str = "star-sports-hindi",
        region: str = "ap-south-1",
        **kwargs
    ) -> PredictiveSnapshot:
        raw_metrics = dict(raw_metrics) if raw_metrics else {}
        normalized_metrics = dict(normalized_metrics) if normalized_metrics else {}

        # If contributors passed, extract metrics
        if "contributors" in kwargs:
            for c in kwargs["contributors"]:
                name = c.get("name") if isinstance(c, dict) else getattr(c, "name", "")
                val = c.get("raw_value") if isinstance(c, dict) else getattr(c, "raw_value", 0.0)
                norm = c.get("normalized") if isinstance(c, dict) else getattr(c, "normalized", 0.0)
                if "gpu" in name:
                    raw_metrics.setdefault("gpu_utilization_pct", val)
                    normalized_metrics.setdefault("gpu_pressure", norm)
                elif "queue" in name:
                    raw_metrics.setdefault("queue_depth", val)
                    normalized_metrics.setdefault("queue_growth", norm)
                elif "latency" in name:
                    raw_metrics.setdefault("transcoder_latency_ms", val)
                    normalized_metrics.setdefault("latency_pressure", norm)
                elif "error" in name:
                    raw_metrics.setdefault("playback_error_rate_pct", val)
                    normalized_metrics.setdefault("error_growth", norm)
                elif "viewer" in name:
                    raw_metrics.setdefault("active_viewers", val)
                    normalized_metrics.setdefault("viewer_growth", norm)

        snapshot = PredictiveSnapshot(
            sampled_at=datetime.now(timezone.utc),
            channel_id=channel_id,
            region=region,
            gpu_utilization_raw=float(raw_metrics.get("gpu_utilization_pct", 0.0)),
            transcoder_latency_raw=float(raw_metrics.get("transcoder_latency_ms", 0.0)),
            queue_depth_raw=int(raw_metrics.get("queue_depth", 0)),
            playback_error_rate_raw=float(raw_metrics.get("playback_error_rate_pct", 0.0)),
            active_viewers_raw=int(raw_metrics.get("active_viewers", 0)),
            gpu_utilization_norm=float(normalized_metrics.get("gpu_pressure", 0.0)),
            transcoder_latency_norm=float(normalized_metrics.get("latency_pressure", 0.0)),
            queue_growth_slope=float(normalized_metrics.get("queue_growth", 0.0)),
            error_growth_slope=float(normalized_metrics.get("error_growth", 0.0)),
            viewer_growth_slope=float(normalized_metrics.get("viewer_growth", 0.0)),
            regional_saturation_norm=float(normalized_metrics.get("regional_saturation", 0.0)),
            deployment_risk_norm=float(normalized_metrics.get("deployment_risk", 0.0)),
        )
        self.session.add(snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)

        if "risk_score" in kwargs:
            await self.create_decision(
                snapshot_id=snapshot.id,
                risk_score=float(kwargs.get("risk_score", 0.0)),
                risk_level=str(kwargs.get("risk_tier", "HEALTHY")),
                confidence_score=float(kwargs.get("confidence_score", 0.0)),
                risk_contributors=kwargs.get("contributors", []),
                predicted_failure_mode=kwargs.get("predicted_failure_mode"),
                window_minutes_min=kwargs.get("window_min_minutes"),
                window_minutes_max=kwargs.get("window_max_minutes"),
                failure_hypothesis=kwargs.get("failure_hypothesis"),
                reasoning_summary=kwargs.get("reasoning_summary"),
                agent_session_id=kwargs.get("agent_session_id"),
                runtime_metadata=kwargs.get("runtime_metadata"),
            )

        return snapshot

    async def record_evidence(
        self,
        snapshot_id: Any,
        tool_name: str,
        query_expression: str,
        raw_response: Dict[str, Any],
        duration_ms: float,
        provider_source: str = "LIVE_GRAFANA_MCP",
    ) -> PredictionEvidence:
        evidence = PredictionEvidence(
            snapshot_id=snapshot_id,
            queried_at=datetime.now(timezone.utc),
            tool_name=tool_name,
            query_expression=query_expression,
            raw_response=raw_response,
            query_duration_ms=duration_ms,
            provider_source=provider_source,
        )
        self.session.add(evidence)
        await self.session.commit()
        await self.session.refresh(evidence)
        return evidence

    async def create_decision(
        self,
        snapshot_id: Any,
        risk_score: float,
        risk_level: str,
        confidence_score: float,
        risk_contributors: List[Dict[str, Any]],
        predicted_failure_mode: Optional[str] = None,
        window_minutes_min: Optional[int] = None,
        window_minutes_max: Optional[int] = None,
        failure_hypothesis: Optional[str] = None,
        reasoning_summary: Optional[str] = None,
        agent_session_id: Optional[str] = None,
        runtime_metadata: Optional[Dict[str, Any]] = None,
    ) -> PredictionDecision:
        decision = PredictionDecision(
            snapshot_id=snapshot_id,
            decided_at=datetime.now(timezone.utc),
            risk_score=risk_score,
            risk_level=risk_level,
            confidence_score=confidence_score,
            risk_contributors=risk_contributors,
            predicted_failure_mode=predicted_failure_mode,
            window_minutes_min=window_minutes_min,
            window_minutes_max=window_minutes_max,
            failure_hypothesis=failure_hypothesis,
            reasoning_summary=reasoning_summary,
            agent_session_id=agent_session_id,
            runtime_metadata=runtime_metadata or {},
        )
        self.session.add(decision)
        await self.session.commit()
        await self.session.refresh(decision)
        return decision

    async def create_action(
        self,
        decision_id: Any,
        action_type: str,
        target_service: str,
        action_parameters: Dict[str, Any],
        blast_radius_pct: float,
        expected_loss_without_action: float,
        cost_of_prevention: float,
        expected_avoided_exposure: float,
        policy_verdict: str = "AUTO_EXECUTE",
        authorization_tier: str = "AUTONOMOUS",
        operator_id: Optional[str] = None,
        execution_status: str = "PENDING",
    ) -> PreventionAction:
        action = PreventionAction(
            decision_id=decision_id,
            dispatched_at=datetime.now(timezone.utc),
            action_type=action_type,
            target_service=target_service,
            action_parameters=action_parameters,
            blast_radius_pct=blast_radius_pct,
            expected_loss_without_action=expected_loss_without_action,
            cost_of_prevention=cost_of_prevention,
            expected_avoided_exposure=expected_avoided_exposure,
            policy_verdict=policy_verdict,
            authorization_tier=authorization_tier,
            operator_id=operator_id,
            execution_status=execution_status,
        )
        self.session.add(action)
        await self.session.commit()
        await self.session.refresh(action)
        return action

    async def update_action_status(
        self,
        action_id: Any,
        status: str,
        operator_id: Optional[str] = None,
    ) -> Optional[PreventionAction]:
        stmt = select(PreventionAction).where(PreventionAction.id == action_id)
        result = await self.session.execute(stmt)
        action = result.scalar_one_or_none()
        if action:
            action.execution_status = status
            if operator_id:
                action.operator_id = operator_id
                action.authorization_tier = "HUMAN_APPROVED"
            if status in ("COMPLETED", "FAILED"):
                action.completed_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(action)
        return action

    async def create_verification(
        self,
        action_id: Any,
        risk_score_before: float,
        risk_score_after: float,
        gpu_before: float,
        gpu_after: float,
        latency_before: float,
        latency_after: float,
        error_rate_before: float,
        error_rate_after: float,
        verification_verdict: str = "PREVENTION_VERIFIED",
        net_avoided_loss: float = 0.0,
        estimated_viewers_protected: int = 0,
    ) -> PreventionVerification:
        verification = PreventionVerification(
            action_id=action_id,
            verified_at=datetime.now(timezone.utc),
            risk_score_before=risk_score_before,
            risk_score_after=risk_score_after,
            gpu_before=gpu_before,
            gpu_after=gpu_after,
            latency_before=latency_before,
            latency_after=latency_after,
            error_rate_before=error_rate_before,
            error_rate_after=error_rate_after,
            verification_verdict=verification_verdict,
            net_avoided_loss=net_avoided_loss,
            estimated_viewers_protected=estimated_viewers_protected,
        )
        self.session.add(verification)
        await self.session.commit()
        await self.session.refresh(verification)
        return verification

    async def get_latest_decision(self) -> Optional[PredictionDecision]:
        stmt = select(PredictionDecision).order_by(desc(PredictionDecision.decided_at)).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_decision_history(self, limit: int = 20) -> List[PredictionDecision]:
        stmt = select(PredictionDecision).order_by(desc(PredictionDecision.decided_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent_snapshots(self, limit: int = 15) -> List[PredictiveSnapshot]:
        stmt = select(PredictiveSnapshot).order_by(desc(PredictiveSnapshot.sampled_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_decisions(self, limit: int = 20) -> List[PredictionDecision]:
        stmt = select(PredictionDecision).order_by(desc(PredictionDecision.decided_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_actions(self, limit: int = 20) -> List[PreventionAction]:
        stmt = select(PreventionAction).order_by(desc(PreventionAction.dispatched_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_verifications(self, limit: int = 20) -> List[PreventionVerification]:
        stmt = select(PreventionVerification).order_by(desc(PreventionVerification.verified_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

