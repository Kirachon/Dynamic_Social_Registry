import os
import asyncio
from sqlalchemy import text
from .db import engine
from aiokafka import AIOKafkaProducer
from dsrs_common.events import kafka_bootstrap

async def liveness_check():
    # simple DB ping
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

async def readiness_check():
    # DB
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    # Kafka metadata
    prod = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap())
    await prod.start()
    try:
        # fetch cluster metadata
        md = await prod.client.fetch_all_metadata()
        if not md.brokers:
            raise RuntimeError("No Kafka brokers in metadata")
    finally:
        await prod.stop()

