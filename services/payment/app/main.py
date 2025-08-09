from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings
from .db import SessionLocal, Base, engine
from .repository import PaymentRepository

app = FastAPI(title="DSRS Payment Service", version="0.1.0")
configure_logging()
from dsrs_common.cors import apply_cors
apply_cors(app)
Base.metadata.create_all(bind=engine)
from dsrs_common.tracing import init_tracing
init_tracing("payment", app)

async def auth_settings():
    return AuthSettings(issuer="https://auth.local/issuer", audience="dsrs-api")

class PaymentDTO(BaseModel):
    id: str
    beneficiary_id: str
    amount: float
    status: str

@app.get("/health")
async def health():
  return {"status": "ok"}

@app.get("/api/v1/payments", response_model=List[PaymentDTO])
async def list_payments(user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
  db = SessionLocal()
  try:
    repo = PaymentRepository(db)
    rows = repo.list()
    return [PaymentDTO.model_validate(r.__dict__) for r in rows]
  finally:
    db.close()

