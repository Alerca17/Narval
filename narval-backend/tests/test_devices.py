from datetime import datetime, timedelta, timezone
from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from app.services.device_service import DeviceService
from app.core.security import hash_token


def test_devices_status_online_offline_boundaries(client, db_session):
    """CP-M3-06: Frontera de latido 300s (ONLINE) vs >300s (OFFLINE) vs sin ping (OFFLINE)."""
    now = datetime.now(timezone.utc)
    d_online = Device(
        code="ESP32-ON",
        name="Estación Online",
        status="ONLINE",
        last_seen_at=now - timedelta(seconds=295),
    )
    d_offline = Device(
        code="ESP32-OFF",
        name="Estación Offline",
        status="ONLINE",
        last_seen_at=now - timedelta(seconds=305),
    )
    d_never = Device(
        code="ESP32-NEVER",
        name="Estación Sin Ping",
        status="OFFLINE",
        last_seen_at=None,
    )
    db_session.add_all([d_online, d_offline, d_never])
    db_session.commit()

    res = client.get("/api/v1/devices/status")
    assert res.status_code == 200
    by_code = {d["code"]: d for d in res.json()}
    assert by_code["ESP32-ON"]["status"] == "ONLINE"
    assert by_code["ESP32-ON"]["seconds_since_last_ping"] <= 300
    assert by_code["ESP32-OFF"]["status"] == "OFFLINE"
    assert by_code["ESP32-OFF"]["seconds_since_last_ping"] > 300
    assert by_code["ESP32-NEVER"]["status"] == "OFFLINE"
    assert by_code["ESP32-NEVER"]["seconds_since_last_ping"] is None


def test_device_service_get_or_create_and_authenticate(db_session):
    """Valida creación idempotente de estación y autenticación por api_key_hash."""
    repo = DeviceRepository(db_session)
    svc = DeviceService(repo)

    dev = svc.get_or_create_device("ESP32-NEW")
    assert dev.code == "ESP32-NEW"
    assert svc.get_or_create_device("ESP32-NEW").id == dev.id

    # Sin api_key_hash configurado -> False
    assert svc.authenticate_device("ESP32-NEW", "cualquier-token") is False
    assert svc.authenticate_device("INEXISTENTE", "cualquier-token") is False

    # Con api_key_hash individual -> True solo para el token válido
    dev.api_key_hash = hash_token("clave-individual-secreta")
    db_session.commit()
    assert svc.authenticate_device("ESP32-NEW", "clave-individual-secreta") is True
    assert svc.authenticate_device("ESP32-NEW", "clave-erronea") is False
