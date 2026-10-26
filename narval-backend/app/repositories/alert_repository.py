from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from app.models.alert import Alert

class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, alert: Alert) -> Alert:
        if not alert.created_at:
            alert.created_at = datetime.now(timezone.utc)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def list_alerts(
        self,
        severity: Optional[str] = None,
        parameter_name: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Alert], int]:
        stmt = select(Alert)
        count_stmt = select(func.count(Alert.id))

        if severity:
            stmt = stmt.where(Alert.severity == severity)
            count_stmt = count_stmt.where(Alert.severity == severity)
        if parameter_name:
            stmt = stmt.where(Alert.parameter_name == parameter_name)
            count_stmt = count_stmt.where(Alert.parameter_name == parameter_name)

        total = self.db.execute(count_stmt).scalar() or 0
        items = list(
            self.db.execute(
                stmt.order_by(desc(Alert.created_at)).offset(offset).limit(limit)
            ).scalars().all()
        )
        return items, total
