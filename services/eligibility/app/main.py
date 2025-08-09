import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Dict, List
from sqlalchemy import text
from .db import SessionLocal
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings

app = FastAPI(title="DSRS Eligibility Service", version="0.1.0")

def init_app():
    """Initialize application components - called on startup, not import"""
    configure_logging()
    from dsrs_common.cors import apply_cors
    apply_cors(app)
    from dsrs_common.tracing import init_tracing
    init_tracing("eligibility", app)
    from dsrs_common.health import router as health_router, set_liveness_checker, set_readiness_checker
    from .health_checks import liveness_check, readiness_check
    app.include_router(health_router)
    set_liveness_checker(liveness_check)
    set_readiness_checker(readiness_check)
    from .startup import setup_background
    setup_background(app)

# Only initialize if running as main application, not during testing
if os.getenv("TESTING") != "1":
    init_app()

async def auth_settings():
    return AuthSettings(issuer="https://auth.local/issuer", audience="dsrs-api")

class EligibilityRequest(BaseModel):
    household_id: str
    programs: List[str]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/v1/eligibility/check")
async def check_eligibility(req: EligibilityRequest, user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)) -> Dict[str, bool]:
    return {p: True for p in req.programs}

@app.get("/api/v1/eligibility/summary")
async def eligibility_summary(user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    """Return basic eligibility statistics from the database.
    approved: count of approved assessments
    denied: count of denied assessments
    pending: count of pending assessments (if used)
    """
    db = SessionLocal()
    try:
        approved = db.execute(text("SELECT COUNT(*) FROM eligibility_assessments WHERE eligibility_status='approved'" )).scalar_one()
        denied = db.execute(text("SELECT COUNT(*) FROM eligibility_assessments WHERE eligibility_status='denied'" )).scalar_one()
        pending = db.execute(text("SELECT COUNT(*) FROM eligibility_assessments WHERE eligibility_status='pending'" )).scalar_one()
        return {"approved": int(approved), "rejected": int(denied), "pending": int(pending)}
    finally:
        db.close()

