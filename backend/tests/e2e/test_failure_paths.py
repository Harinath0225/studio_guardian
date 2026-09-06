import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.persistence.models import Base
from src.persistence.repository import IncidentRepository
from src.simulator.media_env import media_env, StreamState
from src.orchestration.engine import IncidentCommander
from src.orchestration.states import IncidentWorkflowState

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_session():
    test_engine = create_async_engine(TEST_DB_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await test_engine.dispose()

@pytest.mark.asyncio
async def test_failure_path_verification_failure_and_escalation(test_session: AsyncSession):
    """
    E2E Failure Path Test:
    1. Incident triggered.
    2. Simulated recovery failure enabled (standby cluster unable to stabilize).
    3. Verification Agent detects failed recovery.
    4. Orchestrator triggers REINVESTIGATING retry loop.
    5. When retries exceed MAX_REMEDIATION_RETRIES (2), system escalates to ESCALATED_HUMAN_TAKEOVER.
    """
    media_env.reset()
    media_env.trigger_incident()
    media_env.force_recovery_failure = True

    repo = IncidentRepository(test_session)
    incident = await repo.create_incident(
        event_title="India vs Australia Final",
        severity="SEV1",
        status="TRIGGERED"
    )

    commander = IncidentCommander(test_session)
    outcome = await commander.run_lifecycle(incident.id)

    assert outcome["final_state"] == IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER.value
    assert outcome["retries"] > 1

    db_incident = await repo.get_incident(incident.id)
    assert db_incident.status == "ESCALATED_HUMAN_TAKEOVER"

    # Verify that events recorded the reinvestigation attempts
    events = await repo.get_incident_events(incident.id)
    reinvestigate_events = [e for e in events if "REINVESTIGATING" in str(e.payload)]
    assert len(reinvestigate_events) >= 1
