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
async def test_full_e2e_happy_path(test_session: AsyncSession):
    """
    E2E Happy Path Test:
    1. Media stream starts HEALTHY.
    2. Incident is triggered (India vs Australia Final transcode segfault).
    3. Observability Investigator queries Grafana MCP.
    4. Business Impact assesses audience and SLA risk.
    5. Safety Director auto-executes allowlisted traffic shift (blast radius < 25%).
    6. Remediation shifts traffic to transcoder-us-01.
    7. Verification Agent independently samples telemetry and confirms stabilization.
    8. Incident transitions to RESOLVED with state persisted in database.
    """
    media_env.reset()
    assert media_env.state == StreamState.HEALTHY

    # 1. Trigger Incident
    media_env.trigger_incident()
    assert media_env.state == StreamState.DEGRADED

    # 2. Initialize Incident in DB
    repo = IncidentRepository(test_session)
    incident = await repo.create_incident(
        event_title="India vs Australia Final",
        severity="SEV1",
        status="TRIGGERED"
    )

    # 3. Execute Orchestration Engine
    commander = IncidentCommander(test_session)
    outcome = await commander.run_lifecycle(incident.id)

    # 4. Assertions on resolution
    assert outcome["final_state"] == IncidentWorkflowState.RESOLVED.value
    assert outcome["retries"] == 0
    assert outcome["verdict"]["recovered"] is True

    # 5. Assertions on media environment physical state
    assert media_env.state == StreamState.RECOVERED
    assert media_env.routing_weights["transcoder-us-01"] == 1.00

    # 6. Assertions on persistent audit records
    db_incident = await repo.get_incident(incident.id)
    assert db_incident.status == "RESOLVED"
    assert db_incident.resolved_at is not None
