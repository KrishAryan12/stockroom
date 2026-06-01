from __future__ import annotations

import os
from pathlib import Path
import uuid

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/stockroom_test",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
PROJECT_ROOT = Path(__file__).resolve().parents[2]

from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402


def ensure_database(url: str) -> None:
    url_obj = make_url(url)
    admin_url = url_obj.set(database="postgres")
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    with engine.connect() as connection:
        exists = connection.execute(
            text("select 1 from pg_database where datname = :name"),
            {"name": url_obj.database},
        ).scalar_one_or_none()
        if not exists:
            connection.exec_driver_sql(f'CREATE DATABASE "{url_obj.database}"')


def run_migrations(url: str) -> None:
    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")


ensure_database(TEST_DATABASE_URL)
run_migrations(TEST_DATABASE_URL)

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def reset_database():
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE audit_logs, idempotency_records, order_items, orders, customers, products, users RESTART IDENTITY CASCADE"
            )
        )
    yield


@pytest.fixture()
def client():
    def override_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Avery Stone", "email": f"avery-{uuid.uuid4().hex[:8]}@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
