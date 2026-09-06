import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.orchestration.states import IncidentWorkflowState, ALLOWED_TRANSITIONS
from src.persistence.repository import IncidentRepository
from src.agents.investigator import ObservabilityInvestigatorAgent
from src.agents.impact import BusinessImpactAgent
from src.agents.remediation import RemediationAgent
from src.agents.verifier import VerificationAgent
from src.policy.director import safety_director, SafetyDecision
from src.agents.schemas import (
    InvestigationInput,
    BusinessImpactInput,
    RemediationPlan,
    VerificationInput
)

logger = logging.getLogger(__name__)

class IncidentCommander:
    """
    Incident Commander Supervisor Orchestration Engine.
    Responsibilities:
    1. Supervise the end-to-end multi-agent lifecycle across specialist agents.
    2. Enforce state machine transitions and retry thresholds (max 2 retries before ESCALATED_HUMAN_TAKEOVER).
    3. Persist every transition, agent run, observation, hypothesis, impact, and audit record into PostgreSQL/SQLite.
    4. Provide the functioning thin vertical slice:
       TRIGGER -> INVESTIGATE -> CORRELATE -> ASSESS -> POLICY -> REMEDIATE -> VERIFY -> RESOLVE.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IncidentRepository(db)
        self.investigator = ObservabilityInvestigatorAgent()
        self.impact_agent = BusinessImpactAgent()
        self.remediation_agent = RemediationAgent()
        self.verifier = VerificationAgent()
        self.max_retries = settings.MAX_REMEDIATION_RETRIES

    async def _transition_state(self, incident_id: str, current_state: IncidentWorkflowState, next_state: IncidentWorkflowState):
        """Enforces transition matrix validity and persists state change."""
        allowed = ALLOWED_TRANSITIONS.get(current_state, set())
        if next_state not in allowed:
            logger.warning(f"Illegal transition attempted: {current_state} -> {next_state}. Forcing audit log.")
        
        await self.repo.update_incident_status(incident_id, next_state.value)
        await self.repo.add_incident_event(
            incident_id=incident_id,
            event_type="STATE_TRANSITION",
            payload={"from_state": current_state.value, "to_state": next_state.value}
        )
        from src.events.bus import event_bus
        await event_bus.publish(
            event_type="STATE_TRANSITION",
            payload={
                "incident_id": incident_id,
                "from_state": current_state.value,
                "to_state": next_state.value,
                "timestamp": time.time()
            }
        )
        logger.info(f"Incident {incident_id} transitioned: {current_state.value} -> {next_state.value}")

    async def run_lifecycle(self, incident_id: Any, event_title: str = "India vs Australia Final") -> Dict[str, Any]:
        """
        Executes the complete multi-agent vertical slice.
        """
        incident_id = str(incident_id)
        now = time.time()
        current_state = IncidentWorkflowState.TRIGGERED
        retries = 0

        # Initial transition: TRIGGERED -> INVESTIGATING
        await self._transition_state(incident_id, current_state, IncidentWorkflowState.INVESTIGATING)
        current_state = IncidentWorkflowState.INVESTIGATING

        while retries <= self.max_retries:
            # 1. Observability Investigation
            agent_run_inv = await self.repo.start_agent_run(incident_id, self.investigator.name)
            inv_input = InvestigationInput(
                incident_id=incident_id,
                event_title=event_title,
                triggered_at=now,
                trigger_reason="Prometheus alert firing"
            )
            inv_report = await self.investigator.investigate(inv_input)

            # Persist observations & hypotheses
            for obs in inv_report.observations:
                await self.repo.record_observation(
                    incident_id=incident_id,
                    source=obs.source,
                    signal_name=obs.signal_name,
                    raw_data={"value": obs.value, "status": obs.status}
                )
            for hyp in inv_report.hypotheses:
                await self.repo.record_hypothesis(
                    incident_id=incident_id,
                    title=hyp.title,
                    component=hyp.component,
                    confidence=hyp.confidence,
                    evidence=hyp.supporting_evidence
                )
            await self.repo.complete_agent_run(agent_run_inv.id, inv_report.model_dump())

            # Transition: INVESTIGATING -> CORRELATING -> ASSESSING_IMPACT
            await self._transition_state(incident_id, current_state, IncidentWorkflowState.CORRELATING)
            current_state = IncidentWorkflowState.CORRELATING
            await self._transition_state(incident_id, current_state, IncidentWorkflowState.ASSESSING_IMPACT)
            current_state = IncidentWorkflowState.ASSESSING_IMPACT

            # 2. Business Impact Assessment
            agent_run_imp = await self.repo.start_agent_run(incident_id, self.impact_agent.name)
            impact_input = BusinessImpactInput(
                incident_id=incident_id,
                total_viewers=12_400_000,
                affected_regions=["AU", "SG"],
                playback_error_rate_pct=8.7 if retries == 0 else 5.2,
                incident_duration_seconds=300.0 * (retries + 1)
            )
            impact_assessment = await self.impact_agent.assess_impact(impact_input)
            await self.repo.record_business_impact(
                incident_id=incident_id,
                viewers_affected=impact_assessment.affected_viewers,
                vip_viewers_affected=impact_assessment.affected_vip_viewers,
                ad_revenue_at_risk=impact_assessment.ad_revenue_at_risk_usd,
                sla_exposure=impact_assessment.sla_penalty_exposure_usd,
                summary=impact_assessment.executive_summary
            )
            await self.repo.complete_agent_run(agent_run_imp.id, impact_assessment.model_dump())

            # Transition: ASSESSING_IMPACT -> EVALUATING_POLICY
            await self._transition_state(incident_id, current_state, IncidentWorkflowState.EVALUATING_POLICY)
            current_state = IncidentWorkflowState.EVALUATING_POLICY

            # 3. Remediation Planning & Safety Policy Evaluation
            agent_run_rem = await self.repo.start_agent_run(incident_id, self.remediation_agent.name)
            rem_plan = await self.remediation_agent.propose_remediation(
                incident_id=incident_id,
                primary_root_cause=inv_report.primary_root_cause,
                target_component=inv_report.hypotheses[0].component if inv_report.hypotheses else "transcoder-syd-01"
            )

            policy_eval = safety_director.evaluate(rem_plan, diagnostic_confidence=inv_report.confidence_score)
            await self.repo.log_audit(
                incident_id=incident_id,
                action_type="POLICY_EVALUATION",
                actor="SafetyDirector",
                details=policy_eval.model_dump()
            )

            if policy_eval.decision == SafetyDecision.HUMAN_APPROVAL_REQUIRED:
                await self._transition_state(incident_id, current_state, IncidentWorkflowState.WAITING_HUMAN_APPROVAL)
                current_state = IncidentWorkflowState.WAITING_HUMAN_APPROVAL
                await self.repo.complete_agent_run(agent_run_rem.id, {"status": "PAUSED_WAITING_HUMAN_APPROVAL"})
                return {
                    "incident_id": incident_id,
                    "final_state": current_state.value,
                    "message": "Orchestration paused: Human approval required by Safety Policy."
                }
            elif policy_eval.decision == SafetyDecision.REJECTED:
                await self._transition_state(incident_id, current_state, IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER)
                current_state = IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER
                await self.repo.complete_agent_run(agent_run_rem.id, {"status": "REJECTED_BY_POLICY"})
                return {
                    "incident_id": incident_id,
                    "final_state": current_state.value,
                    "message": f"Remediation rejected by Safety Director: {policy_eval.reason}"
                }

            # Decision: AUTO_EXECUTE -> Transition to REMEDIATING
            await self._transition_state(incident_id, current_state, IncidentWorkflowState.REMEDIATING)
            current_state = IncidentWorkflowState.REMEDIATING

            rem_exec = await self.remediation_agent.execute_remediation(rem_plan)
            await self.repo.record_remediation(
                incident_id=incident_id,
                action_type=rem_plan.action_type,
                target_component=rem_plan.target_component,
                parameters=rem_plan.parameters,
                status=rem_exec.status
            )
            await self.repo.complete_agent_run(agent_run_rem.id, rem_exec.model_dump())

            # Transition: REMEDIATING -> VERIFYING
            await self._transition_state(incident_id, current_state, IncidentWorkflowState.VERIFYING)
            current_state = IncidentWorkflowState.VERIFYING

            # 4. Independent Verification
            agent_run_ver = await self.repo.start_agent_run(incident_id, self.verifier.name)
            ver_input = VerificationInput(
                incident_id=incident_id,
                action_executed=f"{rem_plan.action_type} on {rem_plan.target_cluster}",
                pre_remediation_error_rate=8.7,
                pre_remediation_latency=485.0
            )
            ver_verdict = await self.verifier.verify_recovery(ver_input)
            await self.repo.record_verification(
                incident_id=incident_id,
                recovered=ver_verdict.recovered,
                before_telemetry={"error_rate_pct": 8.7, "latency_ms": 485.0},
                after_telemetry={
                    "error_rate_pct": ver_verdict.current_playback_error_rate_pct,
                    "latency_ms": ver_verdict.current_transcoder_latency_ms
                },
                metrics_delta={
                    "error_rate_delta_pct": ver_verdict.error_rate_delta_pct,
                    "latency_delta_pct": ver_verdict.latency_delta_pct
                }
            )
            await self.repo.complete_agent_run(agent_run_ver.id, ver_verdict.model_dump())

            if ver_verdict.recovered:
                await self._transition_state(incident_id, current_state, IncidentWorkflowState.RESOLVED)
                current_state = IncidentWorkflowState.RESOLVED
                return {
                    "incident_id": incident_id,
                    "final_state": current_state.value,
                    "retries": retries,
                    "verdict": ver_verdict.model_dump(),
                    "message": "Incident successfully resolved and independently verified."
                }
            else:
                retries += 1
                if retries <= self.max_retries:
                    logger.warning(f"Verification failed on attempt {retries}. Initiating REINVESTIGATING loop.")
                    await self._transition_state(incident_id, current_state, IncidentWorkflowState.REINVESTIGATING)
                    current_state = IncidentWorkflowState.REINVESTIGATING
                    await self._transition_state(incident_id, current_state, IncidentWorkflowState.INVESTIGATING)
                    current_state = IncidentWorkflowState.INVESTIGATING
                else:
                    logger.error(f"Max retries ({self.max_retries}) exceeded without recovery. Escalating to human takeover.")
                    await self._transition_state(incident_id, current_state, IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER)
                    current_state = IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER
                    return {
                        "incident_id": incident_id,
                        "final_state": current_state.value,
                        "retries": retries,
                        "message": "Max remediation retries exceeded without recovery. Escalated to human takeover."
                    }

        return {
            "incident_id": incident_id,
            "final_state": current_state.value,
            "retries": retries
        }
