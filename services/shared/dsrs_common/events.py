from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Any, Optional
import os, json, uuid

EVENT_VERSION = "1.0"

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    source: str
    subject: Optional[str] = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    traceparent: Optional[str] = None
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = EVENT_VERSION
    data: dict[str, Any]

    def to_json(self) -> str:
        return self.model_dump_json()

    @staticmethod
    def from_json(s: str) -> "Event":
        return Event.model_validate_json(s)


def topic_for(event_type: str) -> str:
    # Map event types to topics
    if event_type.startswith("registry.household."):
        return "registry.household"
    if event_type.startswith("eligibility.assessed"):
        return "eligibility.assessed"
    if event_type.startswith("payment."):
        return "payment.events"
    return "dsrs.events"


def kafka_bootstrap() -> str:
    return os.getenv("KAFKA_BROKERS", "localhost:9092")

