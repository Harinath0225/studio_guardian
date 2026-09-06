from fastapi import APIRouter, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from src.persistence.database import get_db
from src.persistence.repository import IncidentRepository
from src.simulator.injector import IncidentInjector
from src.simulator.metrics_generator import MetricsGenerator
from src.simulator.video_proxy import VideoRoutingProxy
from src.simulator.media_env import media_env

router = APIRouter(tags=["Demo & Simulator"])

class TriggerIncidentRequest(BaseModel):
    scenario: str = "india_vs_australia_final"

class RouteShiftRequest(BaseModel):
    target_cluster: str = "transcoder-us-01"
    shift_pct: float = 100.0

@router.post("/api/v1/demo/incident")
async def trigger_incident(req: Optional[TriggerIncidentRequest] = None, db: AsyncSession = Depends(get_db)):
    scenario = req.scenario if req else "india_vs_australia_final"
    injection_res = IncidentInjector.inject_incident(scenario)

    repo = IncidentRepository(db)
    incident = await repo.create_incident(
        event_title=media_env.event_title,
        severity="SEV1",
        affected_regions=["AU", "SG"],
        primary_affected_service="transcoder-syd-01"
    )
    await repo.add_event(
        incident_id=incident.id,
        event_type="incident_detected",
        summary="Automated telemetry breach: playback error rate spiked to 8.7% in Australia and Singapore.",
        source_agent="incident_commander",
        payload=injection_res["telemetry"]
    )
    await db.commit()

    # Launch background IncidentCommander orchestration lifecycle
    from src.orchestration.engine import IncidentCommander
    import asyncio
    
    async def run_orchestration_bg(inc_id: str):
        from src.persistence.database import AsyncSessionLocal
        async with AsyncSessionLocal() as bg_session:
            commander = IncidentCommander(bg_session)
            await commander.run_lifecycle(inc_id)

    asyncio.create_task(run_orchestration_bg(str(incident.id)))

    return {
        "incident_id": str(incident.id),
        "event_title": incident.event_title,
        "status": incident.status,
        "telemetry": injection_res["telemetry"],
        "message": injection_res["message"]
    }

@router.post("/api/v1/demo/reset")
async def reset_demo():
    res = IncidentInjector.reset_incident()
    return res

@router.post("/api/v1/demo/force-failure")
async def force_failure(enable: bool = True):
    res = IncidentInjector.force_failure(enable)
    return res

@router.post("/api/v1/simulator/route")
async def shift_route(req: RouteShiftRequest):
    result = VideoRoutingProxy.shift_traffic(
        target_cluster=req.target_cluster,
        shift_pct=req.shift_pct
    )
    return result

@router.get("/api/v1/simulator/telemetry")
async def get_telemetry():
    return MetricsGenerator.get_current_metrics()

@router.get("/metrics", response_class=Response)
async def get_prometheus_metrics():
    """Prometheus exposition format scrape endpoint for Grafana."""
    metrics_text = MetricsGenerator.generate_prometheus_text()
    return Response(content=metrics_text, media_type="text/plain; version=0.0.4")
