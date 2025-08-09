import os
from fastapi import FastAPI
from pydantic import BaseModel
from dsrs_common.logging import configure_logging

app = FastAPI(title="DSRS Identity Service", version="0.1.0")

def init_app():
    """Initialize application components - called on startup, not import"""
    configure_logging()
    from dsrs_common.cors import apply_cors
    apply_cors(app)
    from dsrs_common.tracing import init_tracing
    init_tracing("identity", app)

# Only initialize if running as main application, not during testing
if os.getenv("TESTING") != "1":
    init_app()

class AuthRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/v1/identity/authenticate", response_model=TokenResponse)
async def authenticate(req: AuthRequest):
    # Placeholder implementation; in production integrate with Keycloak or IdP
    return TokenResponse(access_token="dummy.jwt.token")

