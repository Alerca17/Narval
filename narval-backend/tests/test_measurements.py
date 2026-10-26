import uuid

def test_ingest_without_auth(client):
    payload = {
        "device_code": "ESP32-TEST",
        "packet_id": f"pkt-{uuid.uuid4().hex[:8]}",
        "ph": {"raw": 2000, "voltage": 2.1, "value": 7.0, "is_calibrated": True},
        "turbidity": {"raw": 1800, "voltage": 2.5, "value": 1.5, "is_calibrated": True},
        "temperature": {"celsius": 20.0, "is_valid": True}
    }
    response = client.post("/api/v1/measurements", json=payload)
    assert response.status_code == 401
    assert "X-Device-Token" in response.json()["detail"]

def test_ingest_with_invalid_token(client):
    payload = {
        "device_code": "ESP32-TEST",
        "packet_id": f"pkt-{uuid.uuid4().hex[:8]}",
        "ph": {"raw": 2000, "voltage": 2.1, "value": 7.0, "is_calibrated": True},
        "turbidity": {"raw": 1800, "voltage": 2.5, "value": 1.5, "is_calibrated": True},
        "temperature": {"celsius": 20.0, "is_valid": True}
    }
    response = client.post("/api/v1/measurements", json=payload, headers={"X-Device-Token": "bad-token"})
    assert response.status_code == 401

def test_ingest_success_and_deduplication(client, auth_headers):
    unique_packet_id = f"pkt-{uuid.uuid4().hex[:12]}"
    payload = {
        "device_code": "ESP32-NARVAL-TEST-01",
        "packet_id": unique_packet_id,
        "device_timestamp": "2026-10-25T20:30:00Z",
        "ph": {"raw": 2048, "voltage": 1.95, "value": 7.20, "is_calibrated": True},
        "turbidity": {"raw": 1950, "voltage": 2.40, "value": 1.80, "is_calibrated": True},
        "temperature": {"celsius": 19.8, "is_valid": True}
    }

    # First ingestion -> 201 Created
    res1 = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert res1.status_code == 201
    data = res1.json()
    assert data["packet_id"] == unique_packet_id
    assert data["quality_status"] == "VALID"
    assert data["calibration_status"] == "CALIBRATED"

    # Duplicate packet_id -> 409 Conflict
    res2 = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert res2.status_code == 409
    assert "ya fue procesado" in res2.json()["detail"]

def test_get_latest_measurement(client):
    response = client.get("/api/v1/measurements/latest")
    assert response.status_code == 200
    data = response.json()
    assert "measurement" in data
    assert "semaforo" in data
    assert data["semaforo"]["global_status"] in ("GREEN", "YELLOW", "RED", "GRAY")

def test_list_measurements(client):
    response = client.get("/api/v1/measurements?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
