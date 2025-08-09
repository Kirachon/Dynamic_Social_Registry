from sqlalchemy import text
from .db import SessionLocal
from dsrs_common.events import Event
from dsrs_common.trace import current_traceparent


def emit_household_registered(h, db=None):
    evt = Event(type="registry.household.registered", source="registry", subject=str(h.id), data={
        "id": str(h.id),
        "head_of_household_name": h.head_of_household_name,
        "address": h.address,
        "phone_number": h.phone_number,
        "email": h.email,
        "household_size": h.household_size,
        "monthly_income": float(h.monthly_income) if h.monthly_income else None,
    }, traceparent=current_traceparent())
    if db is not None:
        # Use caller's transaction/session for atomicity; caller controls commit
        db.execute(text("INSERT INTO event_outbox (id, aggregate_id, event_type, event_data) VALUES (:id, :agg, :type, :payload)"),
                   {"id": evt.id, "agg": h.id, "type": evt.type, "payload": evt.to_json()})
        return evt.id
    # Fallback: own session (non-atomic with business write)
    _db = SessionLocal()
    try:
        _db.execute(text("INSERT INTO event_outbox (id, aggregate_id, event_type, event_data) VALUES (:id, :agg, :type, :payload)"),
                   {"id": evt.id, "agg": h.id, "type": evt.type, "payload": evt.to_json()})
        _db.commit()
        return evt.id
    except Exception:
        _db.rollback()
        raise
    finally:
        _db.close()

