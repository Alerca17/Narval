from sqlalchemy import String, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ReferenceRule(Base):
    __tablename__ = "reference_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parameter_name: Mapped[str] = mapped_column(String(30), nullable=False)  # ph, turbidity, temperature
    source: Mapped[str] = mapped_column(String(100), default="Resolución 2115 de 2007", nullable=False)
    min_value: Mapped[float] = mapped_column(Float, nullable=True)
    max_value: Mapped[float] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
