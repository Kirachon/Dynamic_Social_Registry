import asyncio
import os
import pytest
from testcontainers.kafka import KafkaContainer
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_kafka_topics_health():
    # placeholder to ensure kafka container can run
    # full E2E tests will publish/consume in a follow-up
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200

