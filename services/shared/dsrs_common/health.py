from fastapi import APIRouter
from typing import Awaitable, Callable, Optional

router = APIRouter()

_liveness_checker: Optional[Callable[[], Awaitable[None]]] = None
_readiness_checker: Optional[Callable[[], Awaitable[None]]] = None

def set_liveness_checker(checker: Callable[[], Awaitable[None]]):
    global _liveness_checker
    _liveness_checker = checker

def set_readiness_checker(checker: Callable[[], Awaitable[None]]):
    global _readiness_checker
    _readiness_checker = checker

@router.get("/healthz/liveness")
async def liveness():
    if _liveness_checker:
        await _liveness_checker()
    return {"status": "alive"}

@router.get("/healthz/readiness")
async def readiness():
    if _readiness_checker:
        await _readiness_checker()
    return {"status": "ready"}

