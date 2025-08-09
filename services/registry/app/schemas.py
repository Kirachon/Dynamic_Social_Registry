from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, Optional
from datetime import datetime
import uuid

class HouseholdsSummary(BaseModel):
    total: int

class HouseholdCreate(BaseModel):
    head_of_household_name: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    address: Annotated[str, StringConstraints(min_length=1)]
    phone_number: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    household_size: int = Field(default=1, ge=1)
    monthly_income: Optional[float] = Field(default=None, ge=0)

class HouseholdUpdate(BaseModel):
    head_of_household_name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=255)]] = None
    address: Optional[Annotated[str, StringConstraints(min_length=1)]] = None
    phone_number: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    household_size: Optional[int] = Field(default=None, ge=1)
    monthly_income: Optional[float] = Field(default=None, ge=0)

class HouseholdResponse(BaseModel):
    id: uuid.UUID
    head_of_household_name: str
    address: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    household_size: int
    monthly_income: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
