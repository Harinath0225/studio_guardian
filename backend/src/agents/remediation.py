import time
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
from src.agents.schemas import RemediationPlan, RemediationExecutionResult
from src.simulator.video_proxy import VideoRoutingProxy

class RemediationAgent(BaseAgent):
    """
    Remediation Specialist Agent.
    Responsibilities:
    1. Formulate actionable operational candidate plans (traffic shift to standby, container restart, scaling).
    2. Estimate blast radius and risk level.
    3. Dispatch authentic controlled remediation via VideoRoutingProxy.
    """
    def __init__(self):
        super().__init__(
            name="RemediationAgent",
            role_description="Synthesizes candidate operational fixes and dispatches controlled routing/container commands"
        )

    def get_system_instruction(self) -> str:
        return (
            "You are the Studio Guardian Remediation Agent. "
            "Your objective is to evaluate operational options to restore a degraded live stream. "
            "Select the least destructive, lowest blast-radius action (e.g., regional traffic shift to a standby cluster). "
            "Never perform uncontrolled mutations. Adhere strictly to the allowlisted actions: TRAFFIC_SHIFT, CONTAINER_RESTART, SCALE_REPLICAS."
        )

    async def propose_remediation(
        self,
        incident_id: str,
        primary_root_cause: str,
        target_component: str = "transcoder-syd-01"
    ) -> RemediationPlan:
        prompt = (
            f"Propose an operational remediation plan for incident {incident_id}.\n"
            f"Diagnosed Root Cause: {primary_root_cause}\n"
            f"Failing Subsystem: {target_component}\n"
            f"Formulate a minimal-blast-radius plan."
        )

        fallback = {
            "incident_id": incident_id,
            "action_type": "TRAFFIC_SHIFT",
            "target_component": target_component,
            "target_cluster": "transcoder-us-01",
            "parameters": {"target_cluster": "transcoder-us-01", "shift_pct": 100.0},
            "estimated_blast_radius_pct": 14.7, # 14.7% of viewers in degraded region
            "risk_level": "LOW",
            "rationale": (
                "Diverting 100% of affected AU/SG ingest and transcode traffic away from "
                "degraded transcoder-syd-01 to healthy warm-standby cluster transcoder-us-01."
            )
        }

        return await self.execute_structured(
            prompt=prompt,
            response_schema=RemediationPlan,
            fallback_data=fallback
        )

    async def execute_remediation(self, plan: RemediationPlan) -> RemediationExecutionResult:
        """
        Dispatches the remediation plan against the controlled media routing environment.
        """
        now = time.time()
        if plan.action_type == "TRAFFIC_SHIFT":
            target = plan.target_cluster or plan.parameters.get("target_cluster", "transcoder-us-01")
            shift_pct = plan.parameters.get("shift_pct", 100.0)
            res = VideoRoutingProxy.shift_traffic(target_cluster=target, shift_pct=shift_pct)

            status = "EXECUTED" if res.get("status") == "COMPLETED" else "FAILED"
            return RemediationExecutionResult(
                incident_id=plan.incident_id,
                action_type=plan.action_type,
                status=status,
                details=res,
                executed_at=now
            )
        else:
            return RemediationExecutionResult(
                incident_id=plan.incident_id,
                action_type=plan.action_type,
                status="FAILED",
                details={"error": f"Unsupported or disallowed action type: {plan.action_type}"},
                executed_at=now
            )
