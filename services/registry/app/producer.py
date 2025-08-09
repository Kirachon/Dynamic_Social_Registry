from sqlalchemy import text
from .db import SessionLocal
from dsrs_common.events import Event


def emit_household_registered(h):
    evt = Event(type="registry.household.registered", source="registry", subject=h.id, data={
        "id": h.id,
        "household_number": getattr(h, 'household_number', None),
        "region_code": getattr(h, 'region_code', None),
        "pmt_score": getattr(h, 'pmt_score', None),
    })
    db = SessionLocal()
    try:
        db.execute(text("INSERT INTO outbox (id, aggregate_id, type, payload) VALUES (:id, :agg, :type, :payload)"),
                   {"id": evt.id, "agg": h.id, "type": evt.type, "payload": evt.to_json()})
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

