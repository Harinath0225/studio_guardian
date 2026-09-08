import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.persistence.models import Base
from src.persistence.database import get_db
from src.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def override_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async def _get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()
    await engine.dispose()

@pytest.mark.asyncio
async def test_predictive_prevention_workflow_e2e(override_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Step 1: Query mathematical provenance
        res_prov = await ac.get("/api/v1/predictive/provenance")
        assert res_prov.status_code == 200
        prov_data = res_prov.json()
        assert "provenance" in prov_data
        assert "composite_formula" in prov_data["provenance"]

        # Step 2: Inject capacity surge leading indicator
        res_inj = await ac.post("/api/v1/demo/black-swan/transcoder-surge")
        assert res_inj.status_code == 200

        # Step 3: Evaluate operational risk via /api/v1/prediction/evaluate
        res_risk = await ac.post("/api/v1/prediction/evaluate", json={"force_telemetry_refresh": True})
        assert res_risk.status_code == 200
        risk_data = res_risk.json()
        assert "risk_score" in risk_data
        assert "confidence_score" in risk_data
        assert len(risk_data["contributors"]) > 0

        # Step 4: Reset environment
        res_reset = await ac.post("/api/v1/demo/black-swan/reset")
        assert res_reset.status_code == 200