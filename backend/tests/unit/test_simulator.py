import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.persistence.models import Base
from src.persistence.database import get_db
from src.simulator.media_env import media_env, StreamState
from src.simulator.metrics_generator import MetricsGenerator
from src.simulator.injector import IncidentInjector
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
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await test_engine.dispose()

def test_media_environment_lifecycle():
    media_env.reset()
    assert media_env.state == StreamState.HEALTHY
    initial = media_env.get_telemetry_snapshot()
    assert initial["playback_error_rate_pct"] < 1.0

    # Trigger incident
    media_env.trigger_incident()
    assert media_env.state == StreamState.DEGRADED
    degraded = media_env.get_telemetry_snapshot()
    assert degraded["playback_error_rate_pct"] > 8.0
    assert degraded["transcoder_latency_ms"] > 400.0
    assert "AU" in degraded["affected_regions"]

    # Apply remediation
    shift_res = media_env.apply_traffic_shift(target_cluster="transcoder-us-01")
    assert shift_res["status"] == "COMPLETED"
    assert media_env.state == StreamState.RECOVERED
    recovered = media_env.get_telemetry_snapshot()
    assert recovered["playback_error_rate_pct"] < 1.0
    assert recovered["routing_weights"]["transcoder-us-01"] == 1.0

@pytest.mark.asyncio
async def test_demo_api_endpoints(client: AsyncClient):
    # 1. Trigger incident
    res = await client.post("/api/v1/demo/incident", json={"scenario": "india_vs_australia_final"})
    assert res.status_code == 200
    data = res.json()
    assert "incident_id" in data
    assert data["status"] == "DETECTED"
    assert data["telemetry"]["playback_error_rate_pct"] > 8.0

    # 2. Prometheus scrape endpoint
    metrics_res = await client.get("/metrics")
    assert metrics_res.status_code == 200
    metrics_text = metrics_res.text
    assert "studio_guardian_playback_error_rate" in metrics_text
    assert "studio_guardian_transcoder_latency_seconds" in metrics_text

    # 3. Route shift
    route_res = await client.post("/api/v1/simulator/route", json={"target_cluster": "transcoder-us-01", "shift_pct": 100.0})
    assert route_res.status_code == 200
    assert route_res.json()["status"] == "COMPLETED"

    # 4. Reset demo
    reset_res = await client.post("/api/v1/demo/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "RESET_COMPLETE"
