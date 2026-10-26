from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DeviceBase(BaseModel):
    code: str
    name: str
    firmware_version: Optional[str] = None

class DeviceCreate(DeviceBase):
    api_key: Optional[str] = None

class DeviceResponse(DeviceBase):
    id: int
    status: str
    last_seen_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DeviceStatusResponse(BaseModel):
    code: str
    name: str
    status: str  # ONLINE, OFFLINE, ERROR
    last_seen_at: Optional[datetime] = None
    seconds_since_last_ping: Optional[int] = None
    firmware_version: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
