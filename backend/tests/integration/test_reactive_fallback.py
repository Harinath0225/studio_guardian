import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.persistence.models import Base
from src.persistence.repository import IncidentRepository
from src.simulator.media_env import media_env, StreamState
from src.agents.incident_commander import IncidentCommander
from src.orchestration.states import PredictiveWorkflowState

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
async def test_predictive_to_reactive_context_inheritance(test_session: AsyncSession):
    # 1. Trigger acute stream degradation in media simulator
    media_env.trigger_incident()
    assert media_env.state == StreamState.DEGRADED

    # 2. Run predictive cycle under acute failure
    session = test_session
    commander = IncidentCommander(session)
    status_resp = await commander.run_predictive_cycle()

    # 3. Assert seamless fallback state
    assert commander.predictive_state == PredictiveWorkflowState.FALLBACK_REACTIVE

    # 4. Verify reactive incident created with inherited context
    repo = IncidentRepository(session)
    incidents = await repo.list_incidents()
    assert len(incidents) >= 1
    fallback_incident = incidents[0]
    assert "Reactive Escalation" in fallback_incident.event_title or "Playback" in fallback_incident.event_title

    # Reset media env
    media_env.reset()

