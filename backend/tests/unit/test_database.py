import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.persistence.models import Base, Incident, IncidentEvent, IncidentFingerprint
from src.persistence.repository import IncidentRepository

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_session():
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await test_engine.dispose()

@pytest.mark.asyncio
async def test_create_and_query_incident(db_session: AsyncSession):
    repo = IncidentRepository(db_session)
    incident = await repo.create_incident(
        event_title="India vs Australia Final",
        severity="SEV1",
        affected_regions=["AU", "SG"],
        primary_affected_service="transcoder-syd-01"
    )
    assert incident.id is not None
    assert incident.event_title == "India vs Australia Final"
    assert incident.status == "DETECTED"
    assert incident.affected_regions == ["AU", "SG"]

    # Query incident
    fetched = await repo.get_incident(incident.id)
    assert fetched is not None
    assert fetched.primary_affected_service == "transcoder-syd-01"

    # Add event
    event = await repo.add_event(
        incident_id=incident.id,
        event_type="agent_started",
        summary="Observability Investigator started",
        source_agent="incident_commander",
        payload={"task": "inspect_telemetry"}
    )
    assert event.id is not None
    assert event.incident_id == incident.id

    # Update status
    await repo.update_status(incident.id, "RESOLVED")
    updated = await repo.get_incident(incident.id)
    assert updated.status == "RESOLVED"
    assert updated.resolved_at is not None
