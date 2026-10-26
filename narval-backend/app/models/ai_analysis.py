from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("measurements.id", ondelete="SET NULL"), nullable=True, index=True)
    query_scope: Mapped[str] = mapped_column(String(30), default="SINGLE", nullable=False)  # SINGLE, RECENT_BATCH
    model_used: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[str] = mapped_column(String(300), nullable=False)
    analysis_text: Mapped[str] = mapped_column(Text, nullable=False)
    limitations_disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationship
    measurement: Mapped[Optional["Measurement"]] = relationship("Measurement", back_populates="ai_analyses")
