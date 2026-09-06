import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.persistence.models import Base, IncidentFingerprint
from src.agents.memory import incident_memory_engine
from src.integrations.vertex_memory import VertexMemoryAdapter

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_session():
    test_engine = create_async_engine(TEST_DB_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        # Seed test fingerprint
        fp = IncidentFingerprint(
            symptom_signature={"failing_component": "transcoder-syd-01", "error_rate": "CRITICAL"},
            root_cause_summary="SIGSEGV in libx265 SEI insertion on transcoder worker pool",
            successful_action_type="TRAFFIC_SHIFT",
            tags=["transcoder", "sei", "libx265", "sydney"]
        )
        session.add(fp)
        await session.commit()
        yield session

    await test_engine.dispose()

@pytest.mark.asyncio
async def test_incident_memory_extraction_and_recall(test_session: AsyncSession):
    signature = incident_memory_engine.extract_signature(
        error_rate_pct=8.7,
        latency_ms=485.0,
        failing_component="transcoder-syd-01",
        recent_deployment="v4.2.1-transcoder-patch"
    )

    assert signature["error_rate_category"] == "CRITICAL"
    assert signature["failing_component"] == "transcoder-syd-01"
    assert signature["has_recent_deployment"] is True

    adapter = VertexMemoryAdapter(test_session)
    matches = await adapter.search_similar_past_incidents(signature)
    assert len(matches) >= 1
    top_match = matches[0]
    assert top_match["successful_action_type"] == "TRAFFIC_SHIFT"
    assert "libx265" in top_match["root_cause_summary"]
    assert top_match["similarity_score"] >= 0.80
