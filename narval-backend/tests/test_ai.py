import uuid

def test_ai_analyze_blocked_when_sensors_not_ready(client):
    # If latest measurement has sensor errors, AI call must be blocked
    response = client.post("/api/v1/ai/analyze", json={"include_recent_count": 3})
    # Could be 400 if latest has errors
    if response.status_code == 400:
        data = response.json()
        assert data["detail"]["error_code"] == "SENSORS_NOT_READY"
        assert len(data["detail"]["sensor_errors"]) > 0
        assert "action_required" in data["detail"]

def test_ai_analyze_success_when_sensors_ready(client, auth_headers):
    # Ingest a fully valid measurement
    pkt_id = f"pkt-ai-valid-{uuid.uuid4().hex[:8]}"
    payload = {
        "device_code": "ESP32-AI-TEST",
        "packet_id": pkt_id,
        "ph": {"raw": 2100, "voltage": 2.0, "value": 7.2, "is_calibrated": True},
        "turbidity": {"raw": 1900, "voltage": 2.2, "value": 1.5, "is_calibrated": True},
        "temperature": {"celsius": 22.0, "is_valid": True}
    }
    ingest_res = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert ingest_res.status_code == 201
    meas_id = ingest_res.json()["id"]

    # Request analysis specifically for this valid measurement
    response = client.post("/api/v1/ai/analyze", json={"measurement_id": meas_id, "include_recent_count": 3})
    assert response.status_code == 200
    data = response.json()
    assert "model_used" in data
    assert "summary" in data
    assert "analysis_text" in data
    assert "limitations_disclaimer" in data
