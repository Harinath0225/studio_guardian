import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.persistence.models import Base
from src.persistence.database import get_db
from src.persistence.repository import IncidentRepository
from src.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def client():
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Seed an incident
    async with async_session() as session:
        repo = IncidentRepository(session)
        incident = await repo.create_incident(
            event_title="India vs Australia Final",
            severity="SEV1",
            affected_regions=["AU", "SG"],
            primary_affected_service="transcoder-syd-01"
        )
        await session.commit()
        inc_id = str(incident.id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, inc_id

    app.dependency_overrides.clear()
    await test_engine.dispose()

@pytest.mark.asyncio
async def test_list_and_get_incidents(client):
    ac, inc_id = client
    # List incidents
    res = await ac.get("/api/v1/incidents")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["event_title"] == "India vs Australia Final"

    # Get single incident
    res_single = await ac.get(f"/api/v1/incidents/{inc_id}")
    assert res_single.status_code == 200
    single_data = res_single.json()
    assert single_data["id"] == inc_id
    assert single_data["primary_affected_service"] == "transcoder-syd-01"

@pytest.mark.asyncio
async def test_emergency_takeover_endpoints(client):
    ac, inc_id = client
    # Test specific incident takeover
    res = await ac.post(f"/api/v1/incidents/{inc_id}/takeover")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ESCALATED_HUMAN_TAKEOVER"

    # Test global emergency takeover
    res_global = await ac.post("/api/v1/incidents/emergency-takeover")
    assert res_global.status_code == 200
    global_data = res_global.json()
    assert global_data["status"] == "ESCALATED_HUMAN_TAKEOVER"

