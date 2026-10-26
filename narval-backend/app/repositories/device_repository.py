from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.device import Device

class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, device_id: int) -> Optional[Device]:
        return self.db.get(Device, device_id)

    def get_by_code(self, code: str) -> Optional[Device]:
        stmt = select(Device).where(Device.code == code)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(self) -> List[Device]:
        stmt = select(Device).order_by(Device.code)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, code: str, name: str, api_key_hash: Optional[str] = None, firmware_version: Optional[str] = None) -> Device:
        device = Device(
            code=code,
            name=name,
            status="OFFLINE",
            api_key_hash=api_key_hash,
            firmware_version=firmware_version,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def update_heartbeat(self, device: Device, status: str = "ONLINE", firmware_version: Optional[str] = None) -> Device:
        device.last_seen_at = datetime.now(timezone.utc)
        device.status = status
        if firmware_version:
            device.firmware_version = firmware_version
        self.db.commit()
        self.db.refresh(device)
        return device
