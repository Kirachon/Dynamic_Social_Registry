from fastapi import FastAPI, Depends
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings
from .schemas import AnalyticsSummary

app = FastAPI(title="DSRS Analytics Service", version="0.1.0")
configure_logging()

async def auth_settings():
    return AuthSettings(issuer="https://auth.local/issuer", audience="dsrs-api")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/v1/analytics/summary", response_model=AnalyticsSummary)
async def summary(user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    return AnalyticsSummary(
        risk_model_accuracy=0.87,
        beneficiaries_total=18500000,
        coverage_rate=0.945,
        non_compliance_rate=0.078,
    )

