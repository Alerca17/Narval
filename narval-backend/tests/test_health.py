from unittest.mock import MagicMock
from app.api.v1.endpoints.health import health_check
from app.core.seed import seed
from app.models.reference_rule import ReferenceRule


def test_root_health_check(client):
    """CP-M6-02: Verifica respuesta saludable en GET /health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["database"] == "connected"


def test_api_v1_health_check(client):
    """CP-M6-02: Verifica respuesta saludable en GET /api/v1/health."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_health_check_reports_degraded_when_db_fails():
    """CP-M6-02: Reporta estado degradado cuando la base de datos no responde."""
    broken_db = MagicMock()
    broken_db.execute.side_effect = RuntimeError("Conexión rechazada")

    res = health_check(db=broken_db)
    assert res.status == "degraded"
    assert res.database.startswith("disconnected")


def test_seed_reference_rules_is_idempotent(db_session):
    """CP-M6-01: Ejecutar seed() dos veces mantiene exactamente 3 reglas activas de Res. 2115."""
    seed()
    seed()

    rules = db_session.query(ReferenceRule).filter(ReferenceRule.is_active.is_(True)).all()
    assert len(rules) == 3
    params = {r.parameter_name for r in rules}
    assert params == {"ph", "turbidity", "temperature"}
