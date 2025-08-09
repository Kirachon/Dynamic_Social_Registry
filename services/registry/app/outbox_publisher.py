import asyncio
import json
from sqlalchemy import text
from .db import SessionLocal
from dsrs_common.events import Event, topic_for
from dsrs_common.kafka import get_producer

async def publish_loop(poll_interval: float = 1.0):
    while True:
        await asyncio.sleep(poll_interval)
        db = SessionLocal()
        try:
            rows = db.execute(text("SELECT id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY created_at LIMIT 50")).fetchall()
            if not rows:
                continue
            producer = await get_producer()
            for r in rows:
                evt = Event.from_json(r.payload)
                from dsrs_common.kafka import send_event
                await send_event(producer, topic_for(evt.type), evt.to_json().encode("utf-8"), evt.traceparent)
                db.execute(text("UPDATE outbox SET published_at = NOW() WHERE id = :id"), {"id": r.id})
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

