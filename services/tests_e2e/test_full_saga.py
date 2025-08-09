import asyncio
import os
import time
import pytest
from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer
from httpx import AsyncClient

from services.registry.app.main import app as registry_app
from services.eligibility.app.main import app as eligibility_app
from services.payment.app.main import app as payment_app

@pytest.mark.asyncio
async def test_full_saga_end_to_end(monkeypatch):
    # Spin up Kafka and Postgres containers
    with KafkaContainer() as kafka, PostgresContainer("postgres:15") as pg:
        os.environ['KAFKA_BROKERS'] = kafka.get_bootstrap_server()
        os.environ['DATABASE_URL'] = pg.get_connection_url().replace('postgresql://', 'postgresql+psycopg://')
        # Launch service apps in-process and hit Registry API
        async with AsyncClient(app=registry_app, base_url="http://test") as reg:
            # Create household
            payload = {"id":"H200","household_number":"HH-0200","region_code":"NCR","pmt_score":0.2,"status":"Active"}
            r = await reg.post("/api/v1/households", json=payload)
            assert r.status_code == 201
        # Poll payment service DB via API to see completion
        deadline = time.time() + 30
        success_scheduled = False
        success_completed = False
        while time.time() < deadline:
            async with AsyncClient(app=payment_app, base_url="http://test") as pay:
                pr = await pay.get("/api/v1/payments")
                if pr.status_code == 200:
                    items = pr.json()
                    if any(p.get('id') == 'H200' and p.get('status') == 'Scheduled' for p in items):
                        success_scheduled = True
                    if any(p.get('id') == 'H200' and p.get('status') == 'Completed' for p in items):
                        success_completed = True
                        break
            await asyncio.sleep(1)
        assert success_scheduled, "Payment did not get scheduled"
        assert success_completed, "Payment did not complete"

