from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Dict, List
from dsrs_common.logging import configure_logging
from dsrs_common.security import get_current_user, AuthSettings

app = FastAPI(title="DSRS Eligibility Service", version="0.1.0")
configure_logging()
from dsrs_common.cors import apply_cors
apply_cors(app)
from dsrs_common.tracing import init_tracing
init_tracing("eligibility", app)
from .startup import setup_background
setup_background(app)

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

