import asyncio
from aiokafka import AIOKafkaConsumer
from dsrs_common.events import Event
from dsrs_common.kafka import make_consumer
from .db import SessionLocal
from sqlalchemy import text

from .metrics import PAYMENTS_SCHEDULED, PAYMENT_SCHEDULE_TIME

async def handle_eligibility_event(evt: Event):
    if evt.type != "eligibility.assessed.approved":
        return
    db = SessionLocal()
    try:
        # idempotency
        exists = db.execute(text("SELECT 1 FROM processed_events WHERE id=:id"), {"id": evt.id}).first()
        if exists:
            return
        # schedule a payment for this household
        hid = evt.data.get("id")
        pid = evt.id
        with PAYMENT_SCHEDULE_TIME.time():
            db.execute(text("INSERT INTO payments (id, beneficiary_id, amount, status) VALUES (:id, :bid, :amt, :st)"),
                       {"id": pid, "bid": hid, "amt": 3000, "st": "Scheduled"})
        PAYMENTS_SCHEDULED.inc()
        # outbox: payment.scheduled
        out_evt = Event(type="payment.scheduled", source="payment", subject=pid, data={"id": pid, "beneficiary_id": hid, "amount": 3000, "status": "Scheduled"}, traceparent=evt.traceparent)
        db.execute(text("INSERT INTO outbox (id, aggregate_id, type, payload) VALUES (:id, :agg, :type, :payload)"),
                   {"id": out_evt.id, "agg": pid, "type": out_evt.type, "payload": out_evt.to_json()})
        db.execute(text("INSERT INTO processed_events (id) VALUES (:id)"), {"id": evt.id})
        db.commit()
    except Exception as e:
        db.rollback()
        try:
            from dsrs_common.kafka import get_producer
            from dsrs_common.dlq import publish_dlq
            prod = await get_producer()
            await publish_dlq(prod, evt, str(e))
        except Exception:
            pass
    finally:
        db.close()

async def consume_eligibility():
    consumer = await make_consumer("eligibility.assessed", group_id="payment")
    try:
        while True:
            msg = await consumer.getone()
            evt = Event.from_json(msg.value.decode("utf-8"))
            await handle_eligibility_event(evt)
            await consumer.commit()
    finally:
        await consumer.stop()

