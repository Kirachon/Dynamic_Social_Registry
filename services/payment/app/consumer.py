import logging
from dsrs_common.events import Event
from dsrs_common.kafka import make_consumer
from .db import SessionLocal
from sqlalchemy import text

from .metrics import PAYMENTS_SCHEDULED, PAYMENT_SCHEDULE_TIME

logger = logging.getLogger(__name__)

async def handle_eligibility_event(evt: Event):
    logger.info(f"Processing eligibility event {evt.id} of type {evt.type}")
    if evt.type != "eligibility.assessed.approved":
        logger.info(f"Skipping event {evt.id} - not an approved eligibility assessment")
        return
    db = SessionLocal()
    try:
        # idempotency
        exists = db.execute(text("SELECT 1 FROM processed_events WHERE id=:id"), {"id": evt.id}).first()
        if exists:
            logger.info(f"Event {evt.id} already processed, skipping")
            return
        # schedule a payment for this household
        hid = evt.data.get("household_id")
        pid = evt.id
        with PAYMENT_SCHEDULE_TIME.time():
            db.execute(text("INSERT INTO payments (id, beneficiary_id, amount, status) VALUES (:id, :bid, :amt, :st)"),
                       {"id": pid, "bid": hid, "amt": 3000, "st": "Scheduled"})
        PAYMENTS_SCHEDULED.inc()
        # outbox: payment.scheduled
        out_evt = Event(type="payment.scheduled", source="payment", subject=pid, data={"id": pid, "beneficiary_id": hid, "amount": 3000, "status": "Scheduled"}, traceparent=evt.traceparent)
        db.execute(text("INSERT INTO event_outbox (id, aggregate_id, event_type, event_data) VALUES (:id, :agg, :type, :payload)"),
                   {"id": out_evt.id, "agg": pid, "type": out_evt.type, "payload": out_evt.to_json()})
        db.execute(text("INSERT INTO processed_events (id) VALUES (:id)"), {"id": evt.id})
        db.commit()
        logger.info(f"Successfully processed event {evt.id}, scheduled payment for household {hid}")
    except Exception as e:
        logger.error(f"Error processing event {evt.id}: {e}")
        db.rollback()
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

async def consume_eligibility():
    logger.info("Starting eligibility event consumer")
    consumer = await make_consumer("eligibility.assessed", group_id="payment")
    try:
        while True:
            try:
                logger.debug("Waiting for next message...")
                msg = await consumer.getone()
                logger.info(f"Received message from topic {msg.topic}, partition {msg.partition}, offset {msg.offset}")
                evt = Event.from_json(msg.value.decode("utf-8"))
                await handle_eligibility_event(evt)
                await consumer.commit()
                logger.info(f"Successfully committed message offset {msg.offset}")
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                # Continue processing other messages
    finally:
        await consumer.stop()

