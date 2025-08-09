from pydantic import BaseModel, Field
from typing import Optional

class AnalyticsSummary(BaseModel):
  # Event-driven live counters
  assessed_total: int = Field(0, description="Total eligibility assessments processed")
  approved_total: int = Field(0, description="Total approved eligibility decisions")
  payments_scheduled_total: int = Field(0, description="Total payments scheduled")
  payments_completed_total: int = Field(0, description="Total payments completed")
  # Optional legacy/sample fields retained for compatibility (may be None)
  risk_model_accuracy: Optional[float] = None
  beneficiaries_total: Optional[int] = None
  coverage_rate: Optional[float] = None
  non_compliance_rate: Optional[float] = None

