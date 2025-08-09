import asyncio
import os
from fastapi import FastAPI, Depends
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings
from pymongo import MongoClient
from .schemas import AnalyticsSummary
from .consumer import consume_analytics

app = FastAPI(title="DSRS Analytics Service", version="0.1.0")

def init_app():
    """Initialize application components - called on startup, not import"""
    configure_logging()
    from dsrs_common.cors import apply_cors
    apply_cors(app)
    from dsrs_common.tracing import init_tracing
    init_tracing("analytics", app)
    from dsrs_common.health import router as health_router, set_liveness_checker, set_readiness_checker
    from .health_checks import liveness_check, readiness_check
    app.include_router(health_router)
    set_liveness_checker(liveness_check)
    set_readiness_checker(readiness_check)

# Background consumer

_tasks = []
@app.on_event("startup")
async def _start():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    _tasks.append(asyncio.create_task(consume_analytics(mongo_url)))

@app.on_event("shutdown")
async def _stop():
    for t in _tasks:
        t.cancel()

async def auth_settings():
    return AuthSettings(issuer="https://auth.local/issuer", audience="dsrs-api")

# Only initialize if running as main application, not during testing
if os.getenv("TESTING") != "1":
    init_app()

@app.get("/api/v1/analytics/summary", response_model=AnalyticsSummary)
async def summary(user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    # Read live counters from MongoDB
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = MongoClient(mongo_url)
    col = client.get_database().get_collection("metrics")
    doc = col.find_one({"_id":"summary"}) or {}
    return AnalyticsSummary(
        assessed_total=int(doc.get("assessed", 0)),
        approved_total=int(doc.get("approved", 0)),
        payments_scheduled_total=int(doc.get("payments_scheduled", 0)),
        payments_completed_total=int(doc.get("payments_completed", 0)),
    )

