from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings
from .db import SessionLocal, Base, engine
from .repository import HouseholdRepository
from .schemas import HouseholdsSummary
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
Base.metadata.create_all(bind=engine)
Instrumentator().instrument(app).expose(app)

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

