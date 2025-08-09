import asyncio
from sqlalchemy import text
from .db import SessionLocal
from dsrs_common.events import Event
from .metrics import PAYMENTS_COMPLETED

async def completion_loop(interval: float = 5.0):
    while True:
        await asyncio.sleep(interval)
        db = SessionLocal()
        try:
            # transition a few scheduled payments to completed
            rows = db.execute(text("SELECT id, beneficiary_id, amount FROM payments WHERE status='Scheduled' LIMIT 10")).fetchall()
            for r in rows:
                db.execute(text("UPDATE payments SET status='Completed' WHERE id=:id"), {"id": r.id})
                PAYMENTS_COMPLETED.inc()
                out_evt = Event(type="payment.completed", source="payment", subject=r.id, data={
                    "id": r.id, "beneficiary_id": r.beneficiary_id, "amount": r.amount, "status": "Completed"
                })
                db.execute(text("INSERT INTO outbox (id, aggregate_id, type, payload) VALUES (:id, :agg, :type, :payload)"),
                           {"id": out_evt.id, "agg": r.id, "type": out_evt.type, "payload": out_evt.to_json()})
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

