from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OFFLINE", nullable=False)  # ONLINE, OFFLINE, ERROR
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    measurements: Mapped[List["Measurement"]] = relationship("Measurement", back_populates="device", cascade="all, delete-orphan")
