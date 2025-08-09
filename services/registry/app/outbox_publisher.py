import asyncio
import logging
from sqlalchemy import text
from .db import SessionLocal
from dsrs_common.events import Event, topic_for
from dsrs_common.kafka import get_producer

logger = logging.getLogger(__name__)

async def publish_loop(poll_interval: float = 1.0):
    logger.info(f"Starting outbox publisher with poll interval {poll_interval}s")
    while True:
        await asyncio.sleep(poll_interval)
        db = SessionLocal()
        try:
            rows = db.execute(text("SELECT id, event_type, event_data FROM event_outbox WHERE processed_at IS NULL ORDER BY created_at LIMIT 50")).fetchall()
            if not rows:
                logger.debug("No unprocessed events in outbox")
                continue

            logger.info(f"Found {len(rows)} unprocessed events in outbox")
            producer = await get_producer()

            for r in rows:
                try:
                    # Handle both JSON string and dict from JSONB column
                    if isinstance(r.event_data, dict):
                        evt = Event.model_validate(r.event_data)
                    else:
                        evt = Event.from_json(r.event_data)
                    topic = topic_for(evt.type)
                    logger.info(f"Publishing event {r.id} of type {evt.type} to topic {topic}")

                    from dsrs_common.kafka import send_event
                    await send_event(producer, topic, evt.to_json().encode("utf-8"), evt.traceparent)

                    db.execute(text("UPDATE event_outbox SET processed_at = NOW() WHERE id = :id"), {"id": r.id})
                    logger.info(f"Successfully published and marked event {r.id} as processed")

                except Exception as e:
                    logger.error(f"Failed to publish event {r.id}: {e}")
                    # Continue with other events, don't break the loop

            db.commit()
            logger.info(f"Committed {len(rows)} event updates")

        except Exception as e:
            logger.error(f"Error in publish loop: {e}")
            db.rollback()
        finally:
            db.close()

