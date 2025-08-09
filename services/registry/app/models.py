from sqlalchemy import String, Integer, Numeric, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from .db import Base
import uuid

class Household(Base):
    __tablename__ = "households"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    head_of_household_name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    household_size: Mapped[int] = mapped_column(Integer, default=1)
    monthly_income: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

