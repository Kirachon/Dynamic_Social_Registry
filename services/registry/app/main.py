from fastapi import FastAPI, Depends, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings
from .db import SessionLocal, Base, engine
from .repository import HouseholdRepository
from .schemas import HouseholdsSummary, HouseholdCreate, HouseholdUpdate
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

configure_logging()
from dsrs_common.cors import apply_cors
apply_cors(app)
Base.metadata.create_all(bind=engine)
Instrumentator().instrument(app).expose(app)
from dsrs_common.tracing import init_tracing
init_tracing("registry", app)
from .startup import setup_background
setup_background(app)

# DI settings
async def auth_settings():
    return AuthSettings(issuer="https://auth.local/issuer", audience="dsrs-api")

class HouseholdDTO(BaseModel):
    id: str
    household_number: str
    region_code: str
    pmt_score: float
    status: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/v1/households", response_model=List[HouseholdDTO])
async def list_households(user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    db = SessionLocal()
    try:
        repo = HouseholdRepository(db)
        rows = repo.list()
        return [HouseholdDTO.model_validate(r.__dict__) for r in rows]
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

@app.post("/api/v1/households", response_model=HouseholdDTO, status_code=201)
async def create_household(payload: HouseholdCreate, user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    db = SessionLocal()
    try:
        h = Household(id=payload.id, household_number=payload.household_number, region_code=payload.region_code, pmt_score=payload.pmt_score, status=payload.status)
        db.add(h)
        db.commit()
        emit_household_registered(h)
        return HouseholdDTO.model_validate(h.__dict__)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.put("/api/v1/households/{id}", response_model=HouseholdDTO)
async def update_household(id: str = Path(..., min_length=1, max_length=36), payload: HouseholdUpdate = None, user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    db = SessionLocal()
    try:
        h = db.get(Household, id)
        if not h:
            raise HTTPException(status_code=404, detail="Household not found")
        if payload.household_number is not None:
            h.household_number = payload.household_number
        if payload.region_code is not None:
            h.region_code = payload.region_code
        if payload.pmt_score is not None:
            h.pmt_score = payload.pmt_score
        if payload.status is not None:
            h.status = payload.status
        db.commit()
        emit_household_registered(h)
        return HouseholdDTO.model_validate(h.__dict__)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
