import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.persistence.models import Base
from src.persistence.predictive_repository import PredictiveRepository
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
async def test_end_to_end_predictive_agents_workflow(test_session: AsyncSession):
    # 1. Start from clean nominal state
    media_env.reset()
    assert media_env.state == StreamState.HEALTHY

    # 2. Progress to Step 3: Load Surge / Imminent Risk
    media_env.set_predictive_step(3)

    # 3. Execute predictive cycle under supervisor
    session = test_session
    commander = IncidentCommander(session)
    status_resp = await commander.run_predictive_cycle(force_refresh=True)

    # 4. Verify autonomous evaluation and transition to PREVENTED
    assert status_resp.state == PredictiveWorkflowState.PREVENTED.value
    assert status_resp.risk_score >= 0.80
    assert status_resp.confidence_score >= 0.85

    # 5. Verify simulator environment updated
    # After scale_transcoder_pool, pool size doubled and preventive_scaled set
    assert media_env.transcoder_pool_size >= 16
    assert media_env.preventive_scaled is True

    # 6. Verify database persistence in predictive tables
    pred_repo = PredictiveRepository(session)
    snapshots = await pred_repo.list_recent_snapshots(limit=10)
    assert len(snapshots) >= 1

    decisions = await pred_repo.list_decisions(limit=10)
    assert len(decisions) >= 1
    assert decisions[0].risk_level in ("HIGH_RISK", "IMMINENT_RISK")

    actions = await pred_repo.list_actions(limit=10)
    assert len(actions) >= 1
    assert actions[0].action_type == "scale_transcoder_pool"
    assert actions[0].policy_verdict == "AUTO_EXECUTE"
    assert actions[0].execution_status in ("COMPLETED", "DISPATCHED")

    verifications = await pred_repo.list_verifications(limit=10)
    assert len(verifications) >= 1
    assert verifications[0].verified_successful is True
    assert verifications[0].delta_gpu_utilization <= -20.0

    # Reset simulator
    media_env.reset()
