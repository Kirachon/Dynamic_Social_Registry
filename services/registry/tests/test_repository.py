import os
import time
import pytest
from testcontainers.postgres import PostgresContainer

# Ensure SQLAlchemy uses psycopg3 driver

def to_psycopg_url(url: str) -> str:
    return url.replace("postgresql://", "postgresql+psycopg://")

@pytest.fixture(scope="session")
def pg_url():
    with PostgresContainer("postgres:15") as pg:
        url = to_psycopg_url(pg.get_connection_url())
        yield url

@pytest.fixture()
def db_session(pg_url):
    os.environ["DATABASE_URL"] = pg_url
    # Import after env is set so engine binds to container
    from app.db import Base, engine, SessionLocal
    from app.models import Household

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed
    s = SessionLocal()
    try:
        s.add(Household(id="H1", household_number="HH-0001", region_code="NCR", pmt_score=0.12, status="Active"))
        s.add(Household(id="H2", household_number="HH-0002", region_code="III", pmt_score=0.35, status="Active"))
        s.commit()
        yield s
    finally:
        s.close()


def test_household_repository_list(db_session):
    from app.repository import HouseholdRepository
    repo = HouseholdRepository(db_session)
    rows = repo.list()
    ids = sorted([r.id for r in rows])
    assert ids == ["H1", "H2"]

