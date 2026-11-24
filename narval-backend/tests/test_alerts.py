import uuid


def test_alerts_generated_and_filtered_correctly(client, auth_headers):
    """CP-M4-05: Genera CRITICAL para RED, WARNING para YELLOW, ninguna para GRAY, y valida filtros."""
    payload = {
        "device_code": "ESP32-ALERTS",
        "packet_id": f"pkt-alert-{uuid.uuid4().hex[:8]}",
        "ph": {"raw": 2100, "voltage": 2.0, "value": 5.2, "is_calibrated": True},          # RED -> CRITICAL
        "turbidity": {"raw": 1900, "voltage": 2.2, "value": 3.5, "is_calibrated": True},   # YELLOW -> WARNING
        "temperature": {"celsius": None, "is_valid": False},                               # GRAY -> sin alerta
    }
    res = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert res.status_code == 201

    all_alerts = client.get("/api/v1/alerts")
    assert all_alerts.status_code == 200
    items = all_alerts.json()["items"]
    assert all_alerts.json()["total"] == 2
    assert len(items) == 2

    by_param = {a["parameter_name"]: a for a in items}
    assert set(by_param.keys()) == {"ph", "turbidity"}
    assert by_param["ph"]["severity"] == "CRITICAL"
    assert by_param["turbidity"]["severity"] == "WARNING"

    # Filtro combinado por severidad y parámetro
    crit_ph = client.get("/api/v1/alerts?severity=CRITICAL&parameter_name=ph")
    assert crit_ph.status_code == 200
    crit_items = crit_ph.json()["items"]
    assert len(crit_items) == 1
    assert crit_items[0]["parameter_name"] == "ph"
    assert crit_items[0]["severity"] == "CRITICAL"


def test_no_alerts_generated_for_optimal_readings(client, auth_headers):
    """Valida que lecturas dentro de rango óptimo no creen alertas."""
    payload = {
        "device_code": "ESP32-OK",
        "packet_id": f"pkt-ok-{uuid.uuid4().hex[:8]}",
        "ph": {"raw": 2100, "voltage": 2.0, "value": 7.1, "is_calibrated": True},
        "turbidity": {"raw": 1900, "voltage": 2.2, "value": 0.8, "is_calibrated": True},
        "temperature": {"celsius": 21.0, "is_valid": True},
    }
    res = client.post("/api/v1/measurements", json=payload, headers=auth_headers)
    assert res.status_code == 201

    alerts = client.get("/api/v1/alerts")
    assert alerts.status_code == 200
    assert alerts.json()["items"] == []
    assert alerts.json()["total"] == 0
