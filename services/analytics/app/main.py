from fastapi import FastAPI, Depends
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings
from .schemas import AnalyticsSummary

app = FastAPI(title="DSRS Analytics Service", version="0.1.0")
configure_logging()
from dsrs_common.cors import apply_cors
apply_cors(app)
from dsrs_common.tracing import init_tracing
init_tracing("analytics", app)

# Background consumer
import os
from .consumer import consume_analytics
import asyncio

_tasks = []
@app.on_event("startup")
async def _start():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    _tasks.append(asyncio.create_task(consume_analytics(mongo_url)))

@app.on_event("shutdown")
async def _stop():
    for t in _tasks:
        t.cancel()

async def auth_settings():
    return AuthSettings(issuer="https://auth.local/issuer", audience="dsrs-api")

from dsrs_common.health import router as health_router, set_liveness_checker, set_readiness_checker
from .health_checks import liveness_check, readiness_check
app.include_router(health_router)
set_liveness_checker(liveness_check)
set_readiness_checker(readiness_check)

@app.get("/api/v1/analytics/summary", response_model=AnalyticsSummary)
async def summary(user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    return AnalyticsSummary(
        risk_model_accuracy=0.87,
        beneficiaries_total=18500000,
        coverage_rate=0.945,
        non_compliance_rate=0.078,
    )

