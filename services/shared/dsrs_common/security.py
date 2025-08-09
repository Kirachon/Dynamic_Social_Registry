import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose.exceptions import JWTError

from .jwt import JWKSClient

bearer = HTTPBearer(auto_error=True)

class AuthSettings:
    def __init__(self, issuer: str | None = None, audience: str | None = None):
        self.issuer = issuer or os.getenv("ISSUER")
        self.audience = audience or os.getenv("AUDIENCE")
        self.allow_insecure_local = os.getenv("ALLOW_INSECURE_LOCAL") == "1"

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), settings: AuthSettings = Depends()):
    if settings.allow_insecure_local:
        # Local dev bypass (no token verification). DO NOT USE IN PROD.
        return {"sub": "local-dev"}
    token = creds.credentials
    jwks = JWKSClient(settings.issuer, settings.audience)
    try:
        payload = await jwks.verify(token)
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

