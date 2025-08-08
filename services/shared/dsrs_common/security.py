from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose.exceptions import JWTError

from .jwt import JWKSClient

bearer = HTTPBearer(auto_error=True)

class AuthSettings:
    def __init__(self, issuer: str, audience: str | None = None):
        self.issuer = issuer
        self.audience = audience

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), settings: AuthSettings = Depends()):
    token = creds.credentials
    jwks = JWKSClient(settings.issuer, settings.audience)
    try:
        payload = await jwks.verify(token)
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

