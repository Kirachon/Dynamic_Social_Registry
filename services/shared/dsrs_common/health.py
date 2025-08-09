from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter()

@router.get("/healthz/liveness")
async def liveness():
    return {"status": "alive"}

@router.get("/healthz/readiness")
async def readiness():
    # Placeholder: in real env, check DB/Kafka; here return ok
    return {"status": "ready"}

