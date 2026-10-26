from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class AIAnalyzeRequest(BaseModel):
    measurement_id: Optional[int] = Field(None, description="ID de medición específica a analizar. Si se omite, analiza la más reciente.")
    include_recent_count: int = Field(5, ge=1, le=20, description="Cantidad de mediciones históricas previas para comparación contextual.")

class AIAnalysisResponse(BaseModel):
    id: Optional[int] = None
    measurement_id: Optional[int] = None
    model_used: str
    summary: str
    analysis_text: str
    limitations_disclaimer: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
