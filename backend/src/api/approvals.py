from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.database import get_db
from src.persistence.repository import IncidentRepository
from src.agents.schemas import RemediationPlan
from src.agents.remediation import RemediationAgent
from src.agents.verifier import VerificationAgent
from src.agents.schemas import VerificationInput

router = APIRouter(prefix="/api/v1/incidents", tags=["approvals"])

class ApprovalDecisionRequest(BaseModel):
    approved: bool = Field(description="True to approve execution, False to reject")
    operator_notes: Optional[str] = Field(default="", description="Operator rationale or notes")

@router.post("/{incident_id}/approve")
async def approve_incident_remediation(
    incident_id: str,
    payload: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Operator endpoint to manually approve or reject pending remediation actions.
    """
    repo = IncidentRepository(db)
    incident = await repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status != "WAITING_HUMAN_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Incident is in status '{incident.status}', not waiting for human approval.")

    if not payload.approved:
        await repo.update_incident_status(incident_id, "REJECTED_BY_OPERATOR")
        await repo.log_audit(
            incident_id=incident_id,
            action_type="OPERATOR_REJECTION",
            actor="human_operator",
            details={"notes": payload.operator_notes}
        )
        return {"status": "REJECTED", "message": "Remediation plan rejected by operator."}

    # If approved, dispatch remediation
    await repo.update_incident_status(incident_id, "REMEDIATING")
    await repo.log_audit(
        incident_id=incident_id,
        action_type="OPERATOR_APPROVAL",
        actor="human_operator",
        details={"notes": payload.operator_notes}
    )

    remediation_agent = RemediationAgent()
    plan = RemediationPlan(
        incident_id=incident_id,
        action_type="TRAFFIC_SHIFT",
        target_component="transcoder-syd-01",
        target_cluster="transcoder-us-01",
        parameters={"target_cluster": "transcoder-us-01", "shift_pct": 100.0},
        estimated_blast_radius_pct=14.7,
        risk_level="LOW",
        rationale="Operator approved emergency traffic shift to warm standby."
    )

    result = await remediation_agent.execute_remediation(plan)
    await repo.record_remediation(
        incident_id=incident_id,
        action_type=plan.action_type,
        target_component=plan.target_component,
        parameters=plan.parameters,
        status=result.status
    )

    return {
        "status": "APPROVED_AND_EXECUTED",
        "remediation_result": result.model_dump()
    }

@router.post("/{incident_id}/takeover")
async def takeover_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Emergency operator takeover of a specific active incident.
    """
    import time
    from src.events.bus import event_bus

    repo = IncidentRepository(db)
    incident = await repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    old_state = incident.status
    await repo.update_incident_status(incident_id, "ESCALATED_HUMAN_TAKEOVER")
    await repo.log_audit(
        incident_id=incident_id,
        action_type="EMERGENCY_OPERATOR_TAKEOVER",
        actor="human_operator",
        details={"reason": "Manual operator intervention initiated from Command Center."}
    )
    await event_bus.publish(
        event_type="STATE_TRANSITION",
        payload={
            "incident_id": incident_id,
            "from_state": old_state,
            "to_state": "ESCALATED_HUMAN_TAKEOVER",
            "timestamp": time.time()
        }
    )

    return {
        "status": "ESCALATED_HUMAN_TAKEOVER",
        "message": f"Incident {incident_id} successfully escalated to human takeover."
    }

@router.post("/emergency-takeover")
async def emergency_takeover_global(
    db: AsyncSession = Depends(get_db)
):
    """
    Global emergency takeover: escalates the latest active incident to human takeover.
    """
    import time
    from src.events.bus import event_bus

    repo = IncidentRepository(db)
    incidents = await repo.list_incidents(limit=1)
    if not incidents:
        return {"status": "NO_ACTIVE_INCIDENT", "message": "No active incident found."}

    incident = incidents[0]
    old_state = incident.status
    await repo.update_incident_status(str(incident.id), "ESCALATED_HUMAN_TAKEOVER")
    await repo.log_audit(
        incident_id=str(incident.id),
        action_type="EMERGENCY_OPERATOR_TAKEOVER",
        actor="human_operator",
        details={"reason": "Global manual operator intervention from Command Center."}
    )
    await event_bus.publish(
        event_type="STATE_TRANSITION",
        payload={
            "incident_id": str(incident.id),
            "from_state": old_state,
            "to_state": "ESCALATED_HUMAN_TAKEOVER",
            "timestamp": time.time()
        }
    )

    return {
        "status": "ESCALATED_HUMAN_TAKEOVER",
        "incident_id": str(incident.id),
        "message": "Emergency takeover activated successfully."
    }

