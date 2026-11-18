import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import text

BACKEND_DIR = Path(__file__).resolve().parents[1]

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL") or dotenv_values(BACKEND_DIR / ".env").get(
    "TEST_DATABASE_URL"
)
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL must be set in backend/.env or the environment.")

# Point the application at the test database before the app modules read settings.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.database import get_engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def clean_database():
    engine = get_engine()
    if not engine.url.database or not engine.url.database.endswith("_test"):
        raise RuntimeError(f"Refusing to run tests against non-test database '{engine.url.database}'.")
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE maintenance_requests, technicians RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def make_technician(client):
    def _make(**overrides):
        payload = {
            "name": "Alex Tech",
            "email": "alex.tech@example.com",
            "specialization": "Electrical",
            "availability": "Available",
        }
        payload.update(overrides)
        response = client.post("/api/v1/technicians", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture
def make_request(client):
    def _make(**overrides):
        payload = {
            "employee_name": "Sam Employee",
            "employee_email": "sam@example.com",
            "title": "Desk lamp flickering",
            "description": "The lamp flickers when switched on.",
            "category": "Electrical",
            "location": "Floor 3, Desk 12",
            "priority": "Medium",
        }
        payload.update(overrides)
        response = client.post("/api/v1/requests", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make
