import uuid
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.models import (
    Incident, IncidentEvent, AgentRun, Observation,
    RootCauseHypothesis, BusinessImpact, RemediationAction,
    VerificationResult, IncidentFingerprint, AuditLog
)

class IncidentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_uuid(self, val: Union[str, uuid.UUID]) -> uuid.UUID:
        if isinstance(val, str):
            return uuid.UUID(val)
        return val

    async def get_incident(self, incident_id: Union[str, uuid.UUID]) -> Optional[Incident]:
        uid = self._to_uuid(incident_id)
        result = await self.session.execute(
            select(Incident).where(Incident.id == uid)
        )
        return result.scalar_one_or_none()

    async def list_incidents(self, limit: int = 50) -> List[Incident]:
        result = await self.session.execute(
            select(Incident).order_by(desc(Incident.started_at)).limit(limit)
        )
        return list(result.scalars().all())

    async def create_incident(
        self,
        event_title: str = "India vs Australia Final",
        title: Optional[str] = None,
        severity: str = "SEV1",
        status: str = "DETECTED",
        affected_regions: Optional[List[str]] = None,
        primary_affected_service: Optional[str] = None
    ) -> Incident:
        resolved_title = title or event_title
        incident = Incident(
            event_title=resolved_title,
            severity=severity,
            status=status,
            affected_regions=affected_regions or ["AU", "SG"],
            primary_affected_service=primary_affected_service or "transcoder-syd-01",
            started_at=datetime.now(timezone.utc)
        )
        self.session.add(incident)
        await self.session.flush()
        return incident

    async def update_incident_status(self, incident_id: Union[str, uuid.UUID], status: str) -> None:
        uid = self._to_uuid(incident_id)
        resolved_at = datetime.now(timezone.utc) if status == "RESOLVED" else None
        update_data = {"status": status, "updated_at": datetime.now(timezone.utc)}
        if resolved_at:
            update_data["resolved_at"] = resolved_at

        await self.session.execute(
            update(Incident).where(Incident.id == uid).values(**update_data)
        )
        await self.session.flush()

    async def update_status(self, incident_id: Union[str, uuid.UUID], status: str) -> None:
        await self.update_incident_status(incident_id, status)

    async def add_event(
        self,
        incident_id: Union[str, uuid.UUID],
        event_type: str,
        summary: Optional[str] = None,
        source_agent: Optional[str] = None,
        payload: Optional[dict] = None
    ) -> IncidentEvent:
        return await self.add_incident_event(
            incident_id=incident_id,
            event_type=event_type,
            summary=summary,
            source_agent=source_agent,
            payload=payload
        )

    async def add_incident_event(
        self,
        incident_id: Union[str, uuid.UUID],
        event_type: str,
        summary: Optional[str] = None,
        source_agent: Optional[str] = None,
        payload: Optional[dict] = None
    ) -> IncidentEvent:
        uid = self._to_uuid(incident_id)
        event = IncidentEvent(
            incident_id=uid,
            event_type=event_type,
            source_agent=source_agent,
            summary=summary or f"Event: {event_type}",
            payload=payload or {},
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_incident_events(self, incident_id: Union[str, uuid.UUID]) -> List[IncidentEvent]:
        uid = self._to_uuid(incident_id)
        result = await self.session.execute(
            select(IncidentEvent).where(IncidentEvent.incident_id == uid).order_by(IncidentEvent.created_at)
        )
        return list(result.scalars().all())

    async def start_agent_run(
        self,
        incident_id: Union[str, uuid.UUID],
        agent_name: str,
        input_context: Optional[dict] = None
    ) -> AgentRun:
        uid = self._to_uuid(incident_id)
        run = AgentRun(
            incident_id=uid,
            agent_name=agent_name,
            status="RUNNING",
            input_context=input_context or {},
            started_at=datetime.now(timezone.utc)
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def complete_agent_run(
        self,
        agent_run_id: Union[str, uuid.UUID],
        output_data: dict,
        status: str = "COMPLETED"
    ) -> None:
        uid = self._to_uuid(agent_run_id)
        await self.session.execute(
            update(AgentRun).where(AgentRun.id == uid).values(
                status=status,
                output_data=output_data,
                completed_at=datetime.now(timezone.utc)
            )
        )
        await self.session.flush()

    async def get_agent_runs(self, incident_id: Union[str, uuid.UUID]) -> List[AgentRun]:
        uid = self._to_uuid(incident_id)
        result = await self.session.execute(
            select(AgentRun).where(AgentRun.incident_id == uid).order_by(AgentRun.started_at)
        )
        return list(result.scalars().all())

    async def record_observation(
        self,
        incident_id: Union[str, uuid.UUID],
        source: str,
        signal_name: str,
        raw_data: dict
    ) -> Observation:
        uid = self._to_uuid(incident_id)
        obs = Observation(
            incident_id=uid,
            source=source,
            metric_name=signal_name,
            observed_value=float(raw_data.get("value", 0.0)) if isinstance(raw_data.get("value"), (int, float)) else 1.0,
            raw_telemetry=raw_data,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(obs)
        await self.session.flush()
        return obs

    async def get_observations(self, incident_id: Union[str, uuid.UUID]) -> List[Observation]:
        uid = self._to_uuid(incident_id)
        result = await self.session.execute(
            select(Observation).where(Observation.incident_id == uid)
        )
        return list(result.scalars().all())

    async def record_hypothesis(
        self,
        incident_id: Union[str, uuid.UUID],
        title: str,
        component: str,
        confidence: float,
        evidence: list
    ) -> RootCauseHypothesis:
        uid = self._to_uuid(incident_id)
        hyp = RootCauseHypothesis(
            incident_id=uid,
            root_cause_title=title,
            confidence=confidence,
            causal_chain=f"Subsystem {component} anomaly",
            supporting_evidence_ids=evidence,
            is_primary=True,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(hyp)
        await self.session.flush()
        return hyp

    async def get_hypotheses(self, incident_id: Union[str, uuid.UUID]) -> List[RootCauseHypothesis]:
        uid = self._to_uuid(incident_id)
        result = await self.session.execute(
            select(RootCauseHypothesis).where(RootCauseHypothesis.incident_id == uid)
        )
        return list(result.scalars().all())

    async def record_business_impact(
        self,
        incident_id: Union[str, uuid.UUID],
        viewers_affected: int,
        vip_viewers_affected: int,
        ad_revenue_at_risk: float,
        sla_exposure: float,
        summary: str
    ) -> BusinessImpact:
        uid = self._to_uuid(incident_id)
        impact = BusinessImpact(
            incident_id=uid,
            affected_viewers=viewers_affected,
            vip_viewers=vip_viewers_affected,
            impact_score=5 if sla_exposure > 20000 else 3,
            estimated_ad_exposure_usd=ad_revenue_at_risk,
            sla_breach_risk="CRITICAL" if sla_exposure > 20000 else "HIGH",
            narrative_summary=summary,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(impact)
        await self.session.flush()
        return impact

    async def get_latest_business_impact(self, incident_id: Union[str, uuid.UUID]) -> Optional[BusinessImpact]:
        uid = self._to_uuid(incident_id)
        result = await self.session.execute(
            select(BusinessImpact).where(BusinessImpact.incident_id == uid).order_by(desc(BusinessImpact.created_at)).limit(1)
        )
        return result.scalar_one_or_none()

    async def record_remediation(
        self,
        incident_id: Union[str, uuid.UUID],
        action_type: str,
        target_component: str,
        parameters: dict,
        status: str
    ) -> RemediationAction:
        uid = self._to_uuid(incident_id)
        rem = RemediationAction(
            incident_id=uid,
            action_type=action_type,
            target_resource=target_component,
            parameters=parameters,
            risk_level="LOW",
            blast_radius_pct=14.7,
            policy_decision="AUTO_EXECUTE",
            execution_status=status,
            executed_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(rem)
        await self.session.flush()
        return rem

    async def get_remediations(self, incident_id: Union[str, uuid.UUID]) -> List[RemediationAction]:
        uid = self._to_uuid(incident_id)
        result = await self.session.execute(
            select(RemediationAction).where(RemediationAction.incident_id == uid)
        )
        return list(result.scalars().all())

    async def record_verification(
        self,
        incident_id: Union[str, uuid.UUID],
        recovered: bool,
        before_telemetry: dict,
        after_telemetry: dict,
        metrics_delta: dict
    ) -> VerificationResult:
        uid = self._to_uuid(incident_id)
        ver = VerificationResult(
            incident_id=uid,
            status="RESOLVED" if recovered else "FAILED",
            recovery_confidence=0.98 if recovered else 0.20,
            before_telemetry=before_telemetry,
            after_telemetry=after_telemetry,
            stability_duration_sec=15,
            verification_summary="Verified healthy stream telemetry recovery." if recovered else "Verification detected persistent degradation.",
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(ver)
        await self.session.flush()
        return ver

    async def get_verifications(self, incident_id: Union[str, uuid.UUID]) -> List[VerificationResult]:
        uid = self._to_uuid(incident_id)
        result = await self.session.execute(
            select(VerificationResult).where(VerificationResult.incident_id == uid)
        )
        return list(result.scalars().all())

    async def log_audit(
        self,
        incident_id: Union[str, uuid.UUID],
        action_type: str,
        actor: str,
        details: dict
    ) -> AuditLog:
        log = AuditLog(
            actor=actor,
            action=action_type,
            resource_id=str(incident_id),
            details=details,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(log)
        await self.session.flush()
        return log
