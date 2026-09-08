import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.mark.asyncio
async def test_review_start_options_cors():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/api/v1/review/start",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"

@pytest.mark.asyncio
async def test_review_start_post():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/review/start",
            json={"review_type": "automated_evaluation", "evaluator": "test_runner"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "session_id" in data
        assert data["evaluator"] == "test_runner"
        assert "capabilities" in data

@pytest.mark.asyncio
async def test_review_status_get():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/review/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert "system_status" in data
