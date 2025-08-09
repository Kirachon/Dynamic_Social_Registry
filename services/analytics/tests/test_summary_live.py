import os
import pytest
from httpx import AsyncClient
from pymongo import MongoClient
from app.main import app

@pytest.mark.asyncio
async def test_summary_returns_live_counters(monkeypatch):
    # Use a local Mongo instance if available
    os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
    client = MongoClient(os.environ['MONGO_URL'])
    col = client.get_database().get_collection('metrics')
    col.delete_many({})
    col.insert_one({"_id":"summary", "assessed": 5, "approved": 3, "payments_scheduled": 2, "payments_completed": 1})

    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/v1/analytics/summary")
        assert r.status_code == 200
        data = r.json()
        assert data['assessed_total'] == 5
        assert data['approved_total'] == 3
        assert data['payments_scheduled_total'] == 2
        assert data['payments_completed_total'] == 1

