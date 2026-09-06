import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.persistence.models import Base
from src.persistence.repository import IncidentRepository
from src.services.reports import ReportService

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
async def test_generate_rca_and_executive_brief(test_session: AsyncSession):
    repo = IncidentRepository(test_session)
    incident = await repo.create_incident(
        title="India vs Australia Final",
        severity="SEV1",
        status="RESOLVED"
    )
    inc_id = str(incident.id)

    rca_text = await ReportService.generate_rca_report(test_session, inc_id)
    assert "# Engineering Root Cause Analysis" in rca_text
    assert inc_id in rca_text
    assert "India vs Australia Final" in rca_text

    exec_text = await ReportService.generate_executive_brief(test_session, inc_id)
    assert "# Executive Brief" in exec_text
    assert inc_id in exec_text
