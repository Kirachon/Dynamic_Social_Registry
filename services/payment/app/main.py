from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings

app = FastAPI(title="DSRS Payment Service", version="0.1.0")
configure_logging()

async def auth_settings():
    return AuthSettings(issuer="https://auth.local/issuer", audience="dsrs-api")

class Payment(BaseModel):
    id: str
    beneficiary_id: str
    amount: float
    status: str

MOCK_PAYMENTS: List[Payment] = [
    Payment(id="P1", beneficiary_id="B1", amount=3000.0, status="Completed"),
]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/v1/payments", response_model=List[Payment])
async def list_payments(user=Depends(get_current_user), settings: AuthSettings = Depends(auth_settings)):
    return MOCK_PAYMENTS

