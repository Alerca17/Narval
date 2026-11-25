import uuid


def test_ingest_without_auth(client):
    """CP-M2-01: Rechaza ingesta sin encabezado de autenticación con HTTP 401."""
    payload = {
        "device_code": "ESP32-TEST",
        "packet_id": f"pkt-{uuid.uuid4().hex[:8]}",
        "ph": {"raw": 2000, "voltage": 2.1, "value": 7.0, "is_calibrated": True},
        "turbidity": {"raw": 1800, "voltage": 2.5, "value": 1.5, "is_calibrated": True},
        "temperature": {"celsius": 20.0, "is_valid": True},
    }
    response = client.post("/api/v1/measurements", json=payload)
    assert response.status_code == 401
    assert "X-Device-Token" in response.json()["detail"]


def test_ingest_with_invalid_token(client):
    """CP-M2-01: Rechaza ingesta con token inválido con HTTP 401."""
    payload = {
        "device_code": "ESP32-TEST",
        "packet_id": f"pkt-{uuid.uuid4().hex[:8]}",
        "ph": {"raw": 2000, "voltage": 2.1, "value": 7.0, "is_calibrated": True},
        "turbidity": {"raw": 1800, "voltage": 2.5, "value": 1.5, "is_calibrated": True},
        "temperature": {"celsius": 20.0, "is_valid": True},
    }
    response = client.post("/api/v1/measurements", json=payload, headers={"X-Device-Token": "token-invalido"})
    assert response.status_code == 401


def test_ingest_success_and_deduplication(client, auth_headers):
    """CP-M3-01: Ingesta canónica exitosa (201) y rechazo por duplicidad de packet_id (409)."""
    unique_packet_id = f"pkt-{uuid.uuid4().hex[:12]}"
    payload = {
        "device_code": "ESP32-NARVAL-TEST-01",
        "packet_id": unique_packet_id,
        "device_timestamp": "2026-10-25T20:30:00Z",
        "ph": {"raw": 2048, "voltage": 1.95, "value": 7.20, "is_calibrated": True},
        "turbidity": {"raw": 1950, "voltage": 2.40, "value": 1.80, "is_calibrated": True},
        "temperature": {"celsius": 19.8, "is_valid": True},
    }

    res1 = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert res1.status_code == 201
    data = res1.json()
    assert data["packet_id"] == unique_packet_id
    assert data["quality_status"] == "VALID"
    assert data["calibration_status"] == "CALIBRATED"

    res2 = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert res2.status_code == 409
    assert "ya fue procesado" in res2.json()["detail"]


def test_ingest_esp32_production_payload_adapter(client, auth_headers):
    """CP-M3-02: Valida el adaptador adapt_esp32_payload para el esquema real del firmware ESP32."""
    payload = {
        "schema_version": "1.0",
        "device_id": "NARVAL-001",
        "sequence_number": 42,
        "firmware_version": "1.0.0",
        "captured_at": "2026-11-24T10:00:00Z",
        "quality_status": "VALID",
        "quality_flags": [],
        "measurements": {
            "ph": 7.1,
            "turbidity_ntu": 1.2,
            "temperature_c": 20.5,
            "ph_raw": 2100,
            "turbidity_raw": 1900,
        },
    }
    res = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["packet_id"] == "NARVAL-001-seq-42"
    assert data["ph_value"] == 7.1
    assert data["turbidity_value"] == 1.2
    assert data["temperature_celsius"] == 20.5
    assert data["ph_raw"] == 2100
    assert data["turbidity_raw"] == 1900


def test_ingest_pydantic_rejects_impossible_physical_ranges(client, auth_headers):
    """CP-M3-03: Rechaza pH, turbidez y temperatura fuera de rango físico con HTTP 422."""
    bad_cases = [
        {"ph": {"raw": 2000, "voltage": 2.0, "value": 14.5, "is_calibrated": True}},
        {"turbidity": {"raw": 1800, "voltage": 2.0, "value": -0.5, "is_calibrated": True}},
        {"temperature": {"celsius": 85.0, "is_valid": True}},
    ]
    for override in bad_cases:
        payload = {
            "device_code": "ESP32-VAL",
            "packet_id": f"pkt-val-{uuid.uuid4().hex[:8]}",
            "ph": {"raw": 2000, "voltage": 2.0, "value": 7.0, "is_calibrated": True},
            "turbidity": {"raw": 1800, "voltage": 2.0, "value": 1.0, "is_calibrated": True},
            "temperature": {"celsius": 20.0, "is_valid": True},
            **override,
        }
        res = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
        assert res.status_code == 422


def test_ingest_mixed_calibration_preserves_calibrated_ph(client, auth_headers):
    """CP-M3-04 / Regresión BUG-003: El pH calibrado conserva color GREEN aunque turbidez esté PENDING."""
    payload = {
        "device_code": "ESP32-MIX",
        "packet_id": f"pkt-mix-{uuid.uuid4().hex[:8]}",
        "ph": {"raw": 2450, "voltage": 1.98, "value": 7.15, "is_calibrated": True},
        "turbidity": {"raw": 1820, "voltage": 2.45, "value": None, "is_calibrated": False},
        "temperature": {"celsius": 19.5, "is_valid": True},
    }
    res = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()["quality_status"] == "PARTIAL"
    assert res.json()["calibration_status"] == "PENDING"

    latest = client.get("/api/v1/measurements/latest").json()
    assert latest["semaforo"]["ph"]["color"] == "GREEN"
    assert latest["semaforo"]["ph"]["is_calibrated"] is True
    assert latest["semaforo"]["turbidity"]["color"] == "GRAY"
    assert latest["semaforo"]["global_status"] == "YELLOW"


def test_get_latest_measurement_empty_and_populated(client, auth_headers):
    """CP-M3-05: Verifica /latest con base de datos vacía (GRAY) y con medición óptima (GREEN)."""
    # Base de datos vacía -> GRAY
    empty_res = client.get("/api/v1/measurements/latest")
    assert empty_res.status_code == 200
    empty_data = empty_res.json()
    assert empty_data["measurement"] is None
    assert empty_data["semaforo"]["global_status"] == "GRAY"

    # Base de datos poblada -> GREEN
    payload = {
        "device_code": "ESP32-LATEST",
        "packet_id": f"pkt-lat-{uuid.uuid4().hex[:8]}",
        "ph": {"raw": 2100, "voltage": 2.0, "value": 7.2, "is_calibrated": True},
        "turbidity": {"raw": 1900, "voltage": 2.3, "value": 1.1, "is_calibrated": True},
        "temperature": {"celsius": 21.0, "is_valid": True},
    }
    client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    response = client.get("/api/v1/measurements/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["measurement"] is not None
    assert data["semaforo"]["global_status"] == "GREEN"


def test_list_measurements_pagination_filters_and_get_by_id(client, auth_headers):
    """CP-M3-05: Valida paginación, filtro por dispositivo, consulta por ID y HTTP 404."""
    created_ids = []
    for i, dev in enumerate(["DEV-A", "DEV-A", "DEV-B"]):
        res = client.post(
            "/api/v1/measurements",
            json={
                "device_code": dev,
                "packet_id": f"pkt-list-{i}-{uuid.uuid4().hex[:6]}",
                "ph": {"raw": 2100, "voltage": 2.0, "value": 7.0, "is_calibrated": True},
                "turbidity": {"raw": 1900, "voltage": 2.2, "value": 1.0, "is_calibrated": True},
                "temperature": {"celsius": 20.0, "is_valid": True},
            },
            headers=auth_headers,
        )
        assert res.status_code == 201
        created_ids.append(res.json()["id"])

    # Paginación
    res_page = client.get("/api/v1/measurements?limit=2&offset=0")
    assert res_page.status_code == 200
    assert res_page.json()["total"] == 3
    assert len(res_page.json()["items"]) == 2

    # Filtro por código de dispositivo
    res_dev = client.get("/api/v1/measurements?device_code=DEV-A")
    assert res_dev.status_code == 200
    assert res_dev.json()["total"] == 2

    # Consulta por ID existente
    res_id = client.get(f"/api/v1/measurements/{created_ids[0]}")
    assert res_id.status_code == 200
    assert res_id.json()["id"] == created_ids[0]

    # Consulta por ID inexistente -> HTTP 404
    res_404 = client.get("/api/v1/measurements/999999")
    assert res_404.status_code == 404
