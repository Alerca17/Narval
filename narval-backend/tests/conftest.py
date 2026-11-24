import os

# Fuerza base de datos SQLite en memoria ANTES de importar la aplicación (evita afectar producción/Supabase - R-01)
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["GEMINI_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 - Registra los 6 modelos ORM en Base.metadata
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.security_middleware import ai_rate_limiter
from app.main import app
from app.models.base import Base


@pytest.fixture(autouse=True)
def reset_db_and_state():
    """Recrea las 6 tablas y limpia el limitador de tasa en memoria antes de cada prueba (R-01 / R-06)."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ai_rate_limiter.history.clear()
    yield
    ai_rate_limiter.history.clear()


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers():
    return {
        "X-Device-Token": settings.DEVICE_INGESTION_SECRET
    }
