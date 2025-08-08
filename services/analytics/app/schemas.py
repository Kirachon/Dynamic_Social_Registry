from pydantic import BaseModel

class AnalyticsSummary(BaseModel):
  risk_model_accuracy: float
  beneficiaries_total: int
  coverage_rate: float
  non_compliance_rate: float

