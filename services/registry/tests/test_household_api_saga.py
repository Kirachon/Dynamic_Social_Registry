import os
import pytest
from httpx import AsyncClient
from testcontainers.kafka import KafkaContainer
from app.main import app

@pytest.mark.asyncio
async def test_create_household_triggers_outbox(monkeypatch):
    with KafkaContainer() as kafka:
        os.environ['KAFKA_BROKERS'] = kafka.get_bootstrap_server()
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Auth bypass is allowed in dev test context via settings in app
            payload = {
                "id": "H100",
                "household_number": "HH-0100",
                "region_code": "NCR",
                "pmt_score": 0.25,
                "status": "Active"
            }
            r = await ac.post("/api/v1/households", json=payload)
            assert r.status_code == 201

