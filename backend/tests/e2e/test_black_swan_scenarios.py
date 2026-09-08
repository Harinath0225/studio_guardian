import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.mark.asyncio
async def test_black_swan_scenarios_e2e():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Inject Transcoder Surge
        res_surge = await ac.post("/api/v1/demo/black-swan/transcoder-surge")
        assert res_surge.status_code == 200
        data_surge = res_surge.json()
        assert data_surge["scenario"] == "TRANSCODER_SURGE"
        assert data_surge["telemetry"]["gpu_utilization_pct"] >= 90.0

        # 2. Inject SCTE-35 Corruption
        res_scte = await ac.post("/api/v1/demo/black-swan/scte35-corruption")
        assert res_scte.status_code == 200
        data_scte = res_scte.json()
        assert data_scte["scenario"] == "SCTE35_CORRUPTION"
        assert data_scte["telemetry"]["scte_timing_drift_ms"] > 200.0

        # 3. Reset Baseline
        res_reset = await ac.post("/api/v1/demo/black-swan/reset")
        assert res_reset.status_code == 200
        data_reset = res_reset.json()
        assert data_reset["scenario"] == "BASELINE_RESET"
        assert data_reset["telemetry"]["scte_timing_drift_ms"] < 100.0