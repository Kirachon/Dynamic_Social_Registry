import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose.exceptions import JWTError

from .jwt import JWKSClient

logger = logging.getLogger(__name__)
bearer = HTTPBearer(auto_error=False)

class AuthSettings:
    def __init__(self, issuer: str | None = None, audience: str | None = None):
        self.issuer = issuer or os.getenv("ISSUER")
        self.audience = audience or os.getenv("AUDIENCE")
        self.environment = os.getenv("ENVIRONMENT", "production").lower()

        # Only allow insecure bypass in local/development environments
        bypass_allowed = os.getenv("ALLOW_INSECURE_LOCAL") == "1"
        local_env = self.environment in ["local", "development", "dev"]

        self.allow_insecure_local = bypass_allowed and local_env

        # Log security configuration on startup
        if self.allow_insecure_local:
            logger.warning(f"🚨 SECURITY: Authentication bypass ENABLED for environment '{self.environment}'. This should NEVER be used in production!")
        else:
            logger.info(f"🔒 SECURITY: JWT authentication ENFORCED for environment '{self.environment}'")

        # Validate required settings for production environments
        if not local_env and (not self.issuer or not self.audience):
            raise ValueError(f"ISSUER and AUDIENCE must be set for environment '{self.environment}'")

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), settings: AuthSettings = Depends()):
    # Development bypass with strict environment checking
    if settings.allow_insecure_local:
        logger.debug("Using development authentication bypass")
        return {"sub": "local-dev", "environment": settings.environment}

    # Production JWT verification
    if not creds:
        logger.warning("Authentication failed: No credentials provided")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = creds.credentials
    jwks = JWKSClient(settings.issuer, settings.audience)
    try:
        payload = await jwks.verify(token)
        logger.debug(f"JWT verification successful for subject: {payload.get('sub', 'unknown')}")
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

