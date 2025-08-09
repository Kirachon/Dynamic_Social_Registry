from sqlalchemy import text
from .db import SessionLocal
from dsrs_common.events import Event
from dsrs_common.trace import current_traceparent


def emit_household_registered(h, db=None):
    evt = Event(type="registry.household.registered", source="registry", subject=h.id, data={
        "id": h.id,
        "household_number": getattr(h, 'household_number', None),
        "region_code": getattr(h, 'region_code', None),
        "pmt_score": getattr(h, 'pmt_score', None),
    }, traceparent=current_traceparent())
    if db is not None:
        # Use caller's transaction/session for atomicity; caller controls commit
        db.execute(text("INSERT INTO outbox (id, aggregate_id, type, payload) VALUES (:id, :agg, :type, :payload)"),
                   {"id": evt.id, "agg": h.id, "type": evt.type, "payload": evt.to_json()})
        return evt.id
    # Fallback: own session (non-atomic with business write)
    _db = SessionLocal()
    try:
        _db.execute(text("INSERT INTO outbox (id, aggregate_id, type, payload) VALUES (:id, :agg, :type, :payload)"),
                   {"id": evt.id, "agg": h.id, "type": evt.type, "payload": evt.to_json()})
        _db.commit()
        return evt.id
    except Exception:
        _db.rollback()
        raise
    finally:
        _db.close()

