import os
os.environ["TESTING"] = "1"
os.environ["OTEL_ENABLE"] = "0"

from httpx import AsyncClient
from services.registry.app.main import app
import pytest

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

