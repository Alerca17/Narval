from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class AlertResponse(BaseModel):
    id: int
    measurement_id: Optional[int] = None
    parameter_name: str
    observed_value: Optional[float] = None
    threshold_reference: Optional[str] = None
    severity: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[AlertResponse]
