import os
import pytest
from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer
from sqlalchemy import text

os.environ["TESTING"] = "1"
os.environ["OTEL_ENABLE"] = "0"

from services.registry.app.db import SessionLocal
from services.registry.app.models import Household
from services.registry.app.producer import emit_household_registered

@pytest.mark.asyncio
async def test_registry_to_payment_saga(monkeypatch):
    # Start Kafka and Postgres containers for the test
    with KafkaContainer() as kafka, PostgresContainer("postgres:15") as pg:
        os.environ['KAFKA_BROKERS'] = kafka.get_bootstrap_server()
        os.environ['DATABASE_URL'] = pg.get_connection_url().replace('postgresql://', 'postgresql+psycopg://')
        os.environ['ALLOW_INSECURE_LOCAL'] = '1'  # Allow auth bypass for tests

        # Import after environment is set
        from services.registry.app.db import Base, engine

        # Prepare DB
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        # Insert a household and emit event
        db = SessionLocal()
        try:
            h = Household(id="H_TEST", household_number="HH-TEST", region_code="NCR", pmt_score=0.2, status="Active")
            db.add(h)
            db.commit()
            emit_household_registered(h)
        finally:
            db.close()
        # There is no running service loop here; this test asserts producer enqueues into outbox successfully
        # Full e2e with service loops would be done in a higher-level integration test suite
        outbox_count = SessionLocal().execute(text("SELECT COUNT(*) FROM outbox")).scalar_one()
        assert outbox_count == 1

