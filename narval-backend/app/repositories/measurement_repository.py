from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, desc
from app.models.measurement import Measurement
from app.models.device import Device

class MeasurementRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, measurement_id: int) -> Optional[Measurement]:
        stmt = (
            select(Measurement)
            .options(joinedload(Measurement.device), joinedload(Measurement.alerts))
            .where(Measurement.id == measurement_id)
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_by_packet_id(self, packet_id: str) -> Optional[Measurement]:
        stmt = select(Measurement).where(Measurement.packet_id == packet_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_latest(self, device_code: Optional[str] = None) -> Optional[Measurement]:
        stmt = (
            select(Measurement)
            .join(Device, Measurement.device_id == Device.id)
            .options(joinedload(Measurement.device))
        )
        if device_code:
            stmt = stmt.where(Device.code == device_code)
        stmt = stmt.order_by(desc(Measurement.received_at)).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_recent(self, limit: int = 10, device_code: Optional[str] = None) -> List[Measurement]:
        stmt = (
            select(Measurement)
            .join(Device, Measurement.device_id == Device.id)
            .options(joinedload(Measurement.device))
        )
        if device_code:
            stmt = stmt.where(Device.code == device_code)
        stmt = stmt.order_by(desc(Measurement.received_at)).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def list_measurements(
        self,
        limit: int = 50,
        offset: int = 0,
        device_code: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[Measurement], int]:
        # Base query
        stmt = (
            select(Measurement)
            .join(Device, Measurement.device_id == Device.id)
            .options(joinedload(Measurement.device))
        )
        count_stmt = select(func.count(Measurement.id)).join(Device, Measurement.device_id == Device.id)

        if device_code:
            stmt = stmt.where(Device.code == device_code)
            count_stmt = count_stmt.where(Device.code == device_code)
        if start_date:
            stmt = stmt.where(Measurement.received_at >= start_date)
            count_stmt = count_stmt.where(Measurement.received_at >= start_date)
        if end_date:
            stmt = stmt.where(Measurement.received_at <= end_date)
            count_stmt = count_stmt.where(Measurement.received_at <= end_date)

        total = self.db.execute(count_stmt).scalar() or 0
        items = list(
            self.db.execute(
                stmt.order_by(desc(Measurement.received_at)).offset(offset).limit(limit)
            ).scalars().all()
        )
        return items, total

    def create(self, measurement: Measurement) -> Measurement:
        if not measurement.received_at:
            measurement.received_at = datetime.now(timezone.utc)
        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)
        return measurement
