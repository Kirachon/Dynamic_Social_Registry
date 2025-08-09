import asyncio
from aiokafka import AIOKafkaConsumer
from sqlalchemy import text
from dsrs_common.events import Event
from dsrs_common.kafka import make_consumer
from dsrs_common.events import topic_for
from .db import engine, SessionLocal

from .metrics import ELIGIBILITY_DECISIONS, ELIGIBILITY_PROCESSING_TIME

async def handle_registry_event(evt: Event):
    # simplistic rule: approve if pmt_score <= 0.3, else deny
    data = evt.data
    with ELIGIBILITY_PROCESSING_TIME.time():
        status = "approved" if data.get("pmt_score", 1) <= 0.3 else "denied"
        db = SessionLocal()
        try:
            # idempotency: skip if we've processed this event id
            exists = db.execute(text("SELECT 1 FROM processed_events WHERE id=:id"), {"id": evt.id}).first()
            if exists:
                return
            # record decision
            db.execute(text("INSERT INTO eligibility_decisions (id, household_id, status) VALUES (:id, :hid, :st)"),
                       {"id": evt.id, "hid": data.get("id"), "st": status})
            ELIGIBILITY_DECISIONS.labels(status=status).inc()
            # emit eligibility.assessed.* via outbox
            out_evt = Event(type=f"eligibility.assessed.{status}", source="eligibility", subject=data.get("id"), data={
                "id": data.get("id"),
                "status": status,
            }, traceparent=evt.traceparent)
            db.execute(text("INSERT INTO outbox (id, aggregate_id, type, payload) VALUES (:id, :agg, :type, :payload)"),
                       {"id": out_evt.id, "agg": data.get("id"), "type": out_evt.type, "payload": out_evt.to_json()})
            db.execute(text("INSERT INTO processed_events (id) VALUES (:id)"), {"id": evt.id})
            db.commit()
        except Exception as e:
            db.rollback()
            # DLQ
            try:
                from dsrs_common.kafka import get_producer
                from dsrs_common.dlq import publish_dlq
                prod = await get_producer()
                await publish_dlq(prod, evt, str(e))
            except Exception:
                pass
        finally:
            db.close()

async def consume_registry():
    consumer = await make_consumer("registry.household", group_id="eligibility")
    try:
        while True:
            msg = await consumer.getone()
            evt = Event.from_json(msg.value.decode("utf-8"))
            await handle_registry_event(evt)
            from dsrs_common.metrics import EVENTS_CONSUMED
            EVENTS_CONSUMED.labels(service="eligibility", topic=msg.topic).inc()
            await consumer.commit()
    finally:
        await consumer.stop()

