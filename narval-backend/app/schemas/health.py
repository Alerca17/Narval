from typing import Optional
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    gemini_api: str
    environment: str
