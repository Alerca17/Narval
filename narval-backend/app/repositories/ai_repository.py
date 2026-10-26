from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models.ai_analysis import AIAnalysis

class AIRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, analysis: AIAnalysis) -> AIAnalysis:
        if not analysis.created_at:
            analysis.created_at = datetime.now(timezone.utc)
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_by_id(self, analysis_id: int) -> Optional[AIAnalysis]:
        return self.db.get(AIAnalysis, analysis_id)

    def get_by_measurement_id(self, measurement_id: int) -> Optional[AIAnalysis]:
        stmt = select(AIAnalysis).where(AIAnalysis.measurement_id == measurement_id).order_by(desc(AIAnalysis.created_at)).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_recent(self, limit: int = 5) -> List[AIAnalysis]:
        stmt = select(AIAnalysis).order_by(desc(AIAnalysis.created_at)).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
