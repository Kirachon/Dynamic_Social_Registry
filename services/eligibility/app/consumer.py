import asyncio
from aiokafka import AIOKafkaConsumer
from sqlalchemy import text
from dsrs_common.events import Event
from dsrs_common.kafka import make_consumer
from dsrs_common.events import topic_for
from .db import engine, SessionLocal

async def handle_registry_event(evt: Event):
    # simplistic rule: approve if pmt_score <= 0.3, else deny
    data = evt.data
    status = "approved" if data.get("pmt_score", 1) <= 0.3 else "denied"
    db = SessionLocal()
    try:
        # record decision
        db.execute(text("INSERT INTO eligibility_decisions (id, household_id, status) VALUES (:id, :hid, :st)"),
                   {"id": evt.id, "hid": data.get("id"), "st": status})
        db.commit()
        # TODO: produce eligibility.assessed.* outbox event in eligibility service when DB/model exists
    except Exception:
        db.rollback()
    finally:
        db.close()

async def consume_registry():
    consumer = await make_consumer("registry.household", group_id="eligibility")
    try:
        while True:
            msg = await consumer.getone()
            evt = Event.from_json(msg.value.decode("utf-8"))
            await handle_registry_event(evt)
            await consumer.commit()
    finally:
        await consumer.stop()

