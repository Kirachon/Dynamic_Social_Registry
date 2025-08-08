from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    beneficiary_id: Mapped[str] = mapped_column(String(36), index=True)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20))

