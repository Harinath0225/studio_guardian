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
async def test_end_to_end_orchestration_successful_resolution(test_session: AsyncSession):
    # 1. Reset media environment and trigger incident
    media_env.reset()
    media_env.trigger_incident()
    assert media_env.state == StreamState.DEGRADED

    # 2. Initialize database session and incident record
    session = test_session
    repo = IncidentRepository(session)
    incident = await repo.create_incident(
        title="P1 - Playback Stalling on India vs Australia Final",
        severity="SEV-1",
        status="TRIGGERED"
    )
    incident_id = incident.id

    commander = IncidentCommander(session)
    result = await commander.run_lifecycle(incident_id)

    # 3. Validate overall workflow outcome
    assert result["final_state"] == IncidentWorkflowState.RESOLVED.value
    assert result["retries"] == 0
    assert result["verdict"]["recovered"] is True

    # 4. Validate database persistence across all tables
    # Check incident final status
    db_incident = await repo.get_incident(incident_id)
    assert db_incident.status == IncidentWorkflowState.RESOLVED.value

    # Check state transitions and audit logs
    events = await repo.get_incident_events(incident_id)
    state_events = [e for e in events if e.event_type == "STATE_TRANSITION"]
    assert len(state_events) >= 6

    # Check agent runs
    runs = await repo.get_agent_runs(incident_id)
    agent_names = [r.agent_name for r in runs]
    assert "ObservabilityInvestigator" in agent_names
    assert "BusinessImpactAgent" in agent_names
    assert "RemediationAgent" in agent_names
    assert "VerificationAgent" in agent_names

    # Check observations persisted
    observations = await repo.get_observations(incident_id)
    assert len(observations) >= 4

    # Check hypotheses persisted
    hypotheses = await repo.get_hypotheses(incident_id)
    assert len(hypotheses) >= 1

    # Check business impact persisted
    impact = await repo.get_latest_business_impact(incident_id)
    assert impact is not None
    assert impact.affected_viewers > 0

    # Check remediation action persisted
    remediations = await repo.get_remediations(incident_id)
    assert len(remediations) >= 1
    assert remediations[0].execution_status == "EXECUTED"

    # Check verification persisted
    verifications = await repo.get_verifications(incident_id)
    assert len(verifications) >= 1
    assert verifications[0].status == "RESOLVED"

@pytest.mark.asyncio
async def test_orchestration_escalates_on_forced_recovery_failure(test_session: AsyncSession):
    # Setup media environment with forced failure
    media_env.reset()
    media_env.trigger_incident()
    media_env.force_recovery_failure = True

    session = test_session
    repo = IncidentRepository(session)
    incident = await repo.create_incident(
        title="P1 - Stubborn Degraded Transcode Pod",
        severity="SEV-1",
        status="TRIGGERED"
    )
    incident_id = incident.id

    commander = IncidentCommander(session)
    result = await commander.run_lifecycle(incident_id)

    # Should exceed max retries and escalate to human takeover
    assert result["final_state"] == IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER.value
    assert result["retries"] > 1

    db_incident = await repo.get_incident(incident_id)
    assert db_incident.status == IncidentWorkflowState.ESCALATED_HUMAN_TAKEOVER.value
