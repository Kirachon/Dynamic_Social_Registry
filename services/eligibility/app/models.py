from sqlalchemy import String, Integer, Numeric, DateTime, UUID, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from .db import Base
import uuid

class EligibilityAssessment(Base):
    __tablename__ = "eligibility_assessments"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    eligibility_status: Mapped[str] = mapped_column(String(50), nullable=False)  # approved, denied, pending
    eligibility_score: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    assessment_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    assessed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessment_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class EventOutbox(Base):
    __tablename__ = "event_outbox"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aggregate_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[str] = mapped_column(Text, nullable=False)
    headers: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class ProcessedEvent(Base):
    __tablename__ = "processed_events"
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True)  # Event ID from Kafka
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    processed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    consumer_group: Mapped[str] = mapped_column(String(100), nullable=False, default="eligibility")
