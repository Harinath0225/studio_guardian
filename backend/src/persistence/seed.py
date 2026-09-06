import asyncio
import uuid
from datetime import datetime, timezone
from src.persistence.database import AsyncSessionLocal
from src.persistence.models import Incident, IncidentFingerprint

async def seed_historical_incidents():
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        # Seed historical incident: "Global Music Awards 2025 - Transcoder Out of Memory"
        historical_incident = Incident(
            id=uuid.uuid4(),
            event_title="Global Music Awards 2025",
            status="RESOLVED",
            severity="SEV1",
            primary_affected_service="transcoder-eu-02",
            affected_regions=["GB", "DE", "FR"],
            started_at=datetime.now(timezone.utc),
            resolved_at=datetime.now(timezone.utc)
        )
        session.add(historical_incident)
        await session.flush()

        fingerprint = IncidentFingerprint(
            incident_id=historical_incident.id,
            symptom_signature={
                "error_rate_pct": 7.4,
                "transcoder_latency_ms": 420,
                "gpu_allocation_failure_pct": 12.5,
                "affected_regions": ["GB", "DE", "FR"]
            },
            root_cause_summary="Memory leak in GPU encoder driver post-update v4.1.9",
            successful_action_type="TRAFFIC_SHIFT",
            tags=["transcoder", "gpu-memory", "traffic-shift", "live-awards"]
        )
        session.add(fingerprint)
        await session.commit()
        print("Historical incident seed data created successfully!")

if __name__ == "__main__":
    asyncio.run(seed_historical_incidents())
