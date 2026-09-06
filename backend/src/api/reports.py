from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.database import get_db
from src.services.reports import ReportService

router = APIRouter(prefix="/api/v1/incidents", tags=["reports"])

@router.get("/{incident_id}/report")
async def get_incident_report(
    incident_id: str,
    format: str = Query("rca", enum=["rca", "executive"]),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns dynamically generated Engineering RCA or Executive Brief markdown report.
    """
    if format == "rca":
        content = await ReportService.generate_rca_report(db, incident_id)
    else:
        content = await ReportService.generate_executive_brief(db, incident_id)

    return {
        "incident_id": incident_id,
        "format": format,
        "markdown": content
    }
