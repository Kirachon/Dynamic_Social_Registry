import json
import time
from functools import lru_cache
from typing import Optional

import httpx
from jose import jwt
from jose.exceptions import JWTError

class JWKSClient:
    def __init__(self, issuer: str, audience: Optional[str] = None, jwks_url: Optional[str] = None):
        self.issuer = issuer.rstrip('/')
        self.audience = audience
        self.jwks_url = jwks_url or f"{self.issuer}/.well-known/jwks.json"
        self._cache: Optional[dict] = None
        self._cache_exp = 0

    async def _get_jwks(self) -> dict:
        now = time.time()
        if self._cache and now < self._cache_exp:
            return self._cache
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(self.jwks_url)
            r.raise_for_status()
            self._cache = r.json()
            self._cache_exp = now + 300
            return self._cache

    async def verify(self, token: str) -> dict:
        jwks = await self._get_jwks()
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get('kid')
        key = None
        for k in jwks.get('keys', []):
            if k.get('kid') == kid:
                key = k
                break
        if not key:
            raise JWTError('Signing key not found')
        options = {"verify_aud": bool(self.audience)}
        return jwt.decode(token, key, algorithms=[key.get('alg', 'RS256')], audience=self.audience, issuer=self.issuer, options=options)

