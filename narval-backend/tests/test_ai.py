import types
import uuid
from unittest.mock import MagicMock, patch
import pytest
from app.core.config import settings
from app.services.ai_service import AIService


def _ingest(client, auth_headers, **overrides):
    payload = {
        "device_code": "ESP32-AI-TEST",
        "packet_id": f"pkt-ai-{uuid.uuid4().hex[:10]}",
        "ph": {"raw": 2100, "voltage": 2.0, "value": 7.2, "is_calibrated": True},
        "turbidity": {"raw": 1900, "voltage": 2.2, "value": 1.5, "is_calibrated": True},
        "temperature": {"celsius": 22.0, "is_valid": True},
        **overrides,
    }
    res = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert res.status_code == 201
    return res.json()["id"]


def test_ai_analyze_returns_404_when_database_empty(client):
    """Retorna HTTP 404 cuando no existen mediciones almacenadas para analizar."""
    res = client.post("/api/v1/ai/analyze", json={"include_recent_count": 3})
    assert res.status_code == 404


@pytest.mark.parametrize(
    "overrides,expected_substr",
    [
        ({"ph": {"raw": 4095, "voltage": 3.3, "value": None, "is_calibrated": False}}, "pH"),
        ({"ph": {"raw": 5, "voltage": 0.0, "value": None, "is_calibrated": False}}, "ADC <= 5"),
        ({"turbidity": {"raw": 5, "voltage": 0.0, "value": None, "is_calibrated": False}}, "turbidez"),
        ({"temperature": {"celsius": None, "is_valid": False}}, "temperatura"),
        (
            {
                "quality_status": "SENSOR_ERROR",
                "validation_notes": "TEMP_SENSOR_DISCONNECTED, TURBIDITY_SENSOR_DISCONNECTED",
            },
            "GPIO 26",
        ),
    ],
)
def test_ai_analyze_blocked_when_sensors_not_ready(client, auth_headers, overrides, expected_substr):
    """CP-M5-01 / Regresión BUG-007 y BUG-004: Siempre exige HTTP 400 SENSORS_NOT_READY ante fallos físicos."""
    meas_id = _ingest(client, auth_headers, **overrides)
    response = client.post("/api/v1/ai/analyze", json={"measurement_id": meas_id, "include_recent_count": 3})
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["error_code"] == "SENSORS_NOT_READY"
    assert len(detail["sensor_errors"]) > 0
    assert any(expected_substr.lower() in err.lower() for err in detail["sensor_errors"])
    assert "GPIO 34" in detail["action_required"]
    assert "GPIO 36" in detail["action_required"]
    assert "GPIO 26" in detail["action_required"]


def test_ai_analyze_success_fallback_deterministic_engine(client, auth_headers, monkeypatch):
    """CP-M5-03: Con GEMINI_API_KEY vacía se activa el motor determinista local con aviso normativo."""
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    meas_id = _ingest(client, auth_headers)

    response = client.post("/api/v1/ai/analyze", json={"measurement_id": meas_id, "include_recent_count": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["model_used"] == "local-deterministic-engine"
    assert data["measurement_id"] == meas_id
    assert "Resolución 2115 de 2007" in data["limitations_disclaimer"]
    assert data["summary"]
    assert data["analysis_text"]


def test_ai_analyze_success_with_mocked_gemini_sdk(client, auth_headers, monkeypatch):
    """CP-M5-02: Simula respuesta exitosa del SDK google-genai y valida persistencia y disclaimer."""
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "clave-gemini-prueba")
    meas_id = _ingest(client, auth_headers)

    fake_response = types.SimpleNamespace(
        text="El agua monitoreada presenta pH 7.20 y turbidez 1.50 NTU dentro de rangos técnicos.\nRecomendación: continuar monitoreo periódico."
    )
    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = fake_response

    with patch("google.genai.Client", return_value=fake_client):
        response = client.post("/api/v1/ai/analyze", json={"measurement_id": meas_id, "include_recent_count": 3})

    assert response.status_code == 200
    data = response.json()
    assert data["model_used"] == settings.GEMINI_MODEL
    assert "7.20" in data["analysis_text"]
    assert data["limitations_disclaimer"] == AIService.DISCLAIMER


def test_ai_analyze_falls_back_when_gemini_raises(client, auth_headers, monkeypatch):
    """CP-M5-03: Ante fallo del SDK Gemini se degrada de forma controlada al motor determinista local."""
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "clave-gemini-prueba")
    meas_id = _ingest(client, auth_headers)

    with patch("google.genai.Client", side_effect=RuntimeError("Cuota agotada 429")):
        response = client.post("/api/v1/ai/analyze", json={"measurement_id": meas_id, "include_recent_count": 3})

    assert response.status_code == 200
    data = response.json()
    assert data["model_used"] == "local-deterministic-engine"
    assert "no constituye una certificación oficial" in data["limitations_disclaimer"].lower()
