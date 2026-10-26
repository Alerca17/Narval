from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("measurements.id", ondelete="SET NULL"), nullable=True, index=True)
    parameter_name: Mapped[str] = mapped_column(String(30), nullable=False)  # ph, turbidity, temperature, device
    observed_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold_reference: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="WARNING", nullable=False)  # INFO, WARNING, CRITICAL
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationship
    measurement: Mapped[Optional["Measurement"]] = relationship("Measurement", back_populates="alerts")
