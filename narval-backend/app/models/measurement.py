from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    packet_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    # pH sensor readings
    ph_raw: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ph_voltage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ph_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Turbidity sensor readings
    turbidity_raw: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    turbidity_voltage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    turbidity_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Temperature DS18B20 reading
    temperature_celsius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamps
    device_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    
    # Metrological quality & validation
    quality_status: Mapped[str] = mapped_column(String(20), default="VALID", nullable=False)  # VALID, PARTIAL, INVALID
    calibration_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)  # CALIBRATED, PENDING, UNAVAILABLE
    validation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="measurements")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="measurement", cascade="all, delete-orphan")
    ai_analyses: Mapped[List["AIAnalysis"]] = relationship("AIAnalysis", back_populates="measurement")
