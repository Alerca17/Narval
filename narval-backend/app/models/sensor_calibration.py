from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Integer, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class SensorCalibration(Base):
    __tablename__ = "sensor_calibrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_type: Mapped[str] = mapped_column(String(30), nullable=False)  # ph, turbidity, temperature
    calibration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    parameters_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
