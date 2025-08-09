import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings
from .db import SessionLocal, Base, engine
from .repository import HouseholdRepository
from .schemas import HouseholdsSummary, HouseholdCreate, HouseholdUpdate, HouseholdResponse
from .models import Household
from .producer import emit_household_registered
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="DSRS Registry Service", version="0.1.0")

# CORS for local dev (do not use wildcard in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_app():
    """Initialize application components - called on startup, not import"""
    configure_logging()
    from dsrs_common.cors import apply_cors
    apply_cors(app)
    Base.metadata.create_all(bind=engine)
    Instrumentator().instrument(app).expose(app)
    from dsrs_common.tracing import init_tracing
    init_tracing("registry", app)
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

# DI settings
async def auth_settings():
    return AuthSettings(issuer="https://auth.local/issuer", audience="dsrs-api")

# Remove the old HouseholdDTO - we'll use HouseholdResponse from schemas

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/v1/households", response_model=List[HouseholdResponse])
async def list_households(user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    db = SessionLocal()
    try:
        repo = HouseholdRepository(db)
        rows = repo.list()
        return [HouseholdResponse.model_validate(r) for r in rows]
    finally:
        db.close()

@app.get("/api/v1/households/summary", response_model=HouseholdsSummary)
async def households_summary(user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    db = SessionLocal()
    try:
        total = db.execute("SELECT COUNT(*) FROM households").scalar_one()
        return HouseholdsSummary(total=total)
    finally:
        db.close()

@app.post("/api/v1/households", response_model=HouseholdResponse, status_code=201)
async def create_household(payload: HouseholdCreate, user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    db = SessionLocal()
    try:
        h = Household(
            head_of_household_name=payload.head_of_household_name,
            address=payload.address,
            phone_number=payload.phone_number,
            email=payload.email,
            household_size=payload.household_size,
            monthly_income=payload.monthly_income
        )
        db.add(h)
        db.flush()  # Flush to get the generated ID without committing
        # atomic outbox: insert within the same transaction before commit
        emit_household_registered(h, db=db)
        db.commit()
        db.refresh(h)  # Refresh to get the timestamps
        return HouseholdResponse.model_validate(h)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.put("/api/v1/households/{id}", response_model=HouseholdResponse)
async def update_household(id: uuid.UUID, payload: HouseholdUpdate = None, user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    db = SessionLocal()
    try:
        h = db.get(Household, id)
        if not h:
            raise HTTPException(status_code=404, detail="Household not found")
        if payload.head_of_household_name is not None:
            h.head_of_household_name = payload.head_of_household_name
        if payload.address is not None:
            h.address = payload.address
        if payload.phone_number is not None:
            h.phone_number = payload.phone_number
        if payload.email is not None:
            h.email = payload.email
        if payload.household_size is not None:
            h.household_size = payload.household_size
        if payload.monthly_income is not None:
            h.monthly_income = payload.monthly_income
        # atomic outbox: insert within same transaction
        emit_household_registered(h, db=db)
        db.commit()
        db.refresh(h)  # Refresh to get updated timestamps
        return HouseholdResponse.model_validate(h)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
