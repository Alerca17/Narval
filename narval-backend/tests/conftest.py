import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers():
    return {
        "X-Device-Token": settings.DEVICE_INGESTION_SECRET
    }
