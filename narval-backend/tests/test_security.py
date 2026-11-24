import uuid
from app.core.config import Settings, settings
from app.core.security import hash_token, verify_device_token
from app.core.security_middleware import RateLimiter


def _sample_payload(packet_id: str | None = None):
    return {
        "device_code": "ESP32-SEC-01",
        "packet_id": packet_id or f"pkt-sec-{uuid.uuid4().hex[:10]}",
        "ph": {"raw": 2100, "voltage": 2.0, "value": 7.1, "is_calibrated": True},
        "turbidity": {"raw": 1900, "voltage": 2.4, "value": 1.2, "is_calibrated": True},
        "temperature": {"celsius": 20.5, "is_valid": True},
    }


def test_hash_and_verify_device_token():
    """CP-M2-02: Verifica hash SHA-256 y comparación en tiempo constante."""
    raw = "narval-secret-device-token"
    hashed = hash_token(raw)
    assert len(hashed) == 64
    assert verify_device_token(raw, hashed) is True
    assert verify_device_token(raw, raw) is True
    assert verify_device_token("token-incorrecto", hashed) is False
    assert verify_device_token("", hashed) is False
    assert verify_device_token(raw, "") is False


def test_ingest_accepts_x_device_secret_header(client):
    """CP-M2-02: Acepta el encabezado alternativo X-Device-Secret enviado por el ESP32."""
    res = client.post(
        "/api/v1/measurements",
        json=_sample_payload(),
        headers={"X-Device-Secret": settings.DEVICE_INGESTION_SECRET},
    )
    assert res.status_code == 201


def test_owasp_security_headers_present(client):
    """CP-M2-03: Verifica la presencia de cabeceras de seguridad OWASP en las respuestas."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["X-XSS-Protection"] == "1; mode=block"
    assert res.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "geolocation=()" in res.headers["Permissions-Policy"]


def test_payload_size_limit_64kb_and_malformed_content_length(client, auth_headers):
    """CP-M2-03 / Regresión BUG-005: Controla el límite de 64 KB y cabeceras Content-Length inválidas."""
    # Carga útil superior a 65536 bytes -> HTTP 413
    oversized = _sample_payload()
    oversized["validation_notes"] = "X" * 70000
    res_big = client.post("/api/v1/measurements", json=oversized, headers=auth_headers)
    assert res_big.status_code == 413
    assert "64 KB" in res_big.json()["detail"]

    # Content-Length no numérico -> HTTP 400 (regresión BUG-005)
    res_bad = client.post(
        "/api/v1/measurements",
        content=b"{}",
        headers={**auth_headers, "Content-Type": "application/json", "Content-Length": "abc"},
    )
    assert res_bad.status_code == 400
    assert "Content-Length" in res_bad.json()["detail"]

    # Content-Length negativo -> HTTP 400
    res_neg = client.post(
        "/api/v1/measurements",
        content=b"{}",
        headers={**auth_headers, "Content-Type": "application/json", "Content-Length": "-5"},
    )
    assert res_neg.status_code == 400


def test_rate_limiter_unit_and_ai_endpoint_429(client, auth_headers):
    """CP-M2-04: Valida límite unitario y respuesta HTTP 429 en la sexta petición al endpoint de IA."""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.is_allowed("10.0.0.1") == (True, 0)
    assert limiter.is_allowed("10.0.0.1") == (True, 0)
    allowed, retry_after = limiter.is_allowed("10.0.0.1")
    assert allowed is False
    assert retry_after >= 1

    # Registra una medición válida para que las 5 primeras peticiones respondan 200 y la 6ta retorne 429
    ingest = client.post("/api/v1/measurements", json=_sample_payload(), headers=auth_headers)
    assert ingest.status_code == 201
    mid = ingest.json()["id"]

    for _ in range(5):
        r = client.post("/api/v1/ai/analyze", json={"measurement_id": mid, "include_recent_count": 2})
        assert r.status_code == 200

    r6 = client.post("/api/v1/ai/analyze", json={"measurement_id": mid, "include_recent_count": 2})
    assert r6.status_code == 429
    assert r6.json()["error_code"] == "RATE_LIMIT_EXCEEDED"
    assert int(r6.headers["Retry-After"]) >= 1


def test_settings_database_url_normalization_and_cors():
    """Valida normalización de URLs PostgreSQL, lista CORS y modelo Gemini por defecto (R-04)."""
    s = Settings(
        DATABASE_URL="postgresql://user:pass@host:5432/db",
        DIRECT_URL="postgresql://user:pass@host:5432/db",
        ALLOWED_ORIGINS="http://localhost:5173, https://narval.example.com ",
    )
    assert s.DATABASE_URL.startswith("postgresql+psycopg://")
    assert s.DIRECT_URL.startswith("postgresql+psycopg://")
    assert s.cors_origins == ["http://localhost:5173", "https://narval.example.com"]
    assert s.GEMINI_MODEL == "gemini-2.5-flash"
