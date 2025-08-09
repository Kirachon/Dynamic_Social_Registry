from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, Optional

class HouseholdsSummary(BaseModel):
    total: int

HouseholdID = Annotated[str, StringConstraints(min_length=1, max_length=36)]
RegionCode = Annotated[str, StringConstraints(min_length=2, max_length=10)]

class HouseholdCreate(BaseModel):
    id: HouseholdID
    household_number: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    region_code: RegionCode
    pmt_score: float = Field(ge=0, le=1)
    status: Annotated[str, StringConstraints(min_length=3, max_length=20)]

class HouseholdUpdate(BaseModel):
    household_number: Annotated[Optional[str], StringConstraints(min_length=3, max_length=20)] = None
    region_code: Optional[RegionCode] = None
    pmt_score: Optional[float] = Field(default=None, ge=0, le=1)
    status: Annotated[Optional[str], StringConstraints(min_length=3, max_length=20)] = None
