from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from src.persistence.database import get_db
from src.persistence.models import Incident
from src.persistence.repository import IncidentRepository

router = APIRouter(prefix="/api/v1/incidents", tags=["Incidents"])

@router.get("")
async def list_incidents(db: AsyncSession = Depends(get_db)):
    repo = IncidentRepository(db)
    incidents = await repo.list_incidents()
    return [
        {
            "id": str(inc.id),
            "event_title": inc.event_title,
            "status": inc.status,
            "severity": inc.severity,
            "primary_affected_service": inc.primary_affected_service,
            "affected_regions": inc.affected_regions,
            "retry_count": inc.retry_count,
            "started_at": inc.started_at.isoformat() if inc.started_at else None,
            "resolved_at": inc.resolved_at.isoformat() if inc.resolved_at else None,
        }
        for inc in incidents
    ]

@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    try:
        inc_uuid = uuid.UUID(incident_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid incident UUID format")

    repo = IncidentRepository(db)
    incident = await repo.get_incident(inc_uuid)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "id": str(incident.id),
        "event_title": incident.event_title,
        "status": incident.status,
        "severity": incident.severity,
        "primary_affected_service": incident.primary_affected_service,
        "affected_regions": incident.affected_regions,
        "retry_count": incident.retry_count,
        "started_at": incident.started_at.isoformat() if incident.started_at else None,
        "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
    }
