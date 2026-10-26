from datetime import datetime, timezone
from typing import List, Optional
from app.models.device import Device
from app.schemas.device import DeviceStatusResponse
from app.repositories.device_repository import DeviceRepository
from app.core.security import verify_device_token, hash_token

class DeviceService:
    def __init__(self, device_repo: DeviceRepository):
        self.device_repo = device_repo

    def get_or_create_device(self, code: str, default_name: Optional[str] = None) -> Device:
        device = self.device_repo.get_by_code(code)
        if not device:
            name = default_name or f"Dispositivo {code}"
            device = self.device_repo.create(code=code, name=name)
        return device

    def authenticate_device(self, code: str, token: str) -> bool:
        device = self.device_repo.get_by_code(code)
        if not device:
            return False
        # If device has an individual api_key_hash
        if device.api_key_hash:
            return verify_device_token(token, device.api_key_hash)
        return False

    def get_devices_status(self, offline_threshold_seconds: int = 300) -> List[DeviceStatusResponse]:
        devices = self.device_repo.get_all()
        now = datetime.now(timezone.utc)
        results = []

        for dev in devices:
            seconds_diff = None
            status = "OFFLINE"
            if dev.last_seen_at:
                diff = (now - dev.last_seen_at).total_seconds()
                seconds_diff = int(diff)
                if seconds_diff <= offline_threshold_seconds:
                    status = "ONLINE"
                else:
                    status = "OFFLINE"
            
            results.append(
                DeviceStatusResponse(
                    code=dev.code,
                    name=dev.name,
                    status=status,
                    last_seen_at=dev.last_seen_at,
                    seconds_since_last_ping=seconds_diff,
                    firmware_version=dev.firmware_version,
                )
            )
        return results
