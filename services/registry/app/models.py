from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Household(Base):
    __tablename__ = "households"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    household_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    region_code: Mapped[str] = mapped_column(String(10), index=True)
    pmt_score: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20))

