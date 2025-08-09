import os
import pytest
from testcontainers.postgres import PostgresContainer


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
    from app.db import Base, engine, SessionLocal
    from app.models import Payment
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    s = SessionLocal()
    try:
        s.add(Payment(id="P1", beneficiary_id="B1", amount=3000, status="Completed"))
        s.add(Payment(id="P2", beneficiary_id="B1", amount=3000, status="Completed"))
        s.commit()
        yield s
    finally:
        s.close()


def test_payment_repository_list(db_session):
    from app.repository import PaymentRepository
    repo = PaymentRepository(db_session)
    rows = repo.list()
    ids = sorted([r.id for r in rows])
    assert ids == ["P1", "P2"]

