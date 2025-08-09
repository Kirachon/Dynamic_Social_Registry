import logging
import json
from sqlalchemy import text
from dsrs_common.events import Event
from dsrs_common.kafka import make_consumer
from .db import SessionLocal

from .metrics import ELIGIBILITY_DECISIONS, ELIGIBILITY_PROCESSING_TIME

logger = logging.getLogger(__name__)

async def handle_registry_event(evt: Event):
    logger.info(f"Processing registry event {evt.id} of type {evt.type}")
    # simplistic rule: approve if monthly_income <= 3000, else deny
    data = evt.data
    with ELIGIBILITY_PROCESSING_TIME.time():
        monthly_income = data.get("monthly_income", 0) or 0
        status = "approved" if monthly_income <= 3000 else "denied"
        db = SessionLocal()
        try:
            # idempotency: skip if we've processed this event id
            exists = db.execute(text("SELECT 1 FROM processed_events WHERE id=:id"), {"id": evt.id}).first()
            if exists:
                logger.info(f"Event {evt.id} already processed, skipping")
                return
            # record assessment in eligibility_assessments table
            criteria = {"monthly_income": monthly_income, "threshold": 3000}
            db.execute(text("""
                INSERT INTO eligibility_assessments (household_id, eligibility_status, eligibility_score, assessment_criteria, assessed_by, notes)
                VALUES (:hid, :status, :score, :criteria, :assessed_by, :notes)
            """), {
                "hid": data.get("id"),
                "status": status,
                "score": monthly_income / 100,  # Simple scoring based on income
                "criteria": json.dumps(criteria),  # Convert dict to JSON string
                "assessed_by": "automated_system",
                "notes": f"Automated assessment based on monthly income: ${monthly_income}"
            })
            ELIGIBILITY_DECISIONS.labels(status=status).inc()
            # emit eligibility.assessed.* via outbox
            out_evt = Event(type=f"eligibility.assessed.{status}", source="eligibility", subject=data.get("id"), data={
                "household_id": data.get("id"),
                "status": status,
                "monthly_income": monthly_income,
                "assessment_date": evt.ts
            }, traceparent=evt.traceparent)
            db.execute(text("INSERT INTO event_outbox (id, aggregate_id, event_type, event_data) VALUES (:id, :agg, :type, :payload)"),
                       {"id": out_evt.id, "agg": data.get("id"), "type": out_evt.type, "payload": out_evt.to_json()})
            db.execute(text("INSERT INTO processed_events (id) VALUES (:id)"), {"id": evt.id})
            db.commit()
            logger.info(f"Successfully processed event {evt.id}, status: {status}")
        except Exception as e:
            logger.error(f"Error processing event {evt.id}: {e}")
            db.rollback()
            # DLQ
            try:
                from dsrs_common.kafka import get_producer
                from dsrs_common.dlq import publish_dlq
                prod = await get_producer()
                await publish_dlq(prod, evt, str(e))
                logger.info(f"Published event {evt.id} to DLQ due to error: {e}")
            except Exception as dlq_error:
                logger.error(f"Failed to publish to DLQ: {dlq_error}")
                pass
        finally:
            db.close()

async def consume_registry():
    logger.info("Starting registry event consumer")
    consumer = await make_consumer("registry.household", group_id="eligibility")
    try:
        while True:
            try:
                logger.debug("Waiting for next message...")
                msg = await consumer.getone()
                logger.info(f"Received message from topic {msg.topic}, partition {msg.partition}, offset {msg.offset}")
                evt = Event.from_json(msg.value.decode("utf-8"))
                await handle_registry_event(evt)
                from dsrs_common.metrics import EVENTS_CONSUMED
                EVENTS_CONSUMED.labels(service="eligibility", topic=msg.topic).inc()
                await consumer.commit()
                logger.info(f"Successfully committed message offset {msg.offset}")
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                # Continue processing other messages
    finally:
        await consumer.stop()

