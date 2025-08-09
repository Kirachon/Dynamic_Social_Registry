import os
import pytest
from httpx import AsyncClient

os.environ["TESTING"] = "1"
os.environ["OTEL_ENABLE"] = "0"

from services.registry.app.main import app

@pytest.mark.asyncio
async def test_kafka_topics_health():
    # placeholder to ensure kafka container can run
    # full E2E tests will publish/consume in a follow-up
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200

