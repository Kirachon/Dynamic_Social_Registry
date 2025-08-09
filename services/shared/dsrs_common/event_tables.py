from sqlalchemy import text
from sqlalchemy.engine import Engine

def ensure_event_tables(engine: Engine):
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS outbox (
            id VARCHAR(36) PRIMARY KEY,
            aggregate_id VARCHAR(64) NOT NULL,
            type VARCHAR(100) NOT NULL,
            payload TEXT NOT NULL,
            headers TEXT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            published_at TIMESTAMPTZ NULL
        )
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS processed_events (
            id VARCHAR(36) PRIMARY KEY,
            processed_at TIMESTAMPTZ DEFAULT NOW()
        )
        """))

