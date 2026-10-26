from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.health import HealthResponse
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get(
    "",
    response_model=HealthResponse,
    summary="Chequeo de salud del servicio",
    description="Comprueba la operatividad de FastAPI y la conectividad con PostgreSQL/Supabase.",
)
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1;"))
    except Exception as e:
        db_status = f"disconnected ({str(e)})"

    gemini_status = "configured" if bool(settings.GEMINI_API_KEY) else "unconfigured (using fallback)"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version="1.0.0",
        database=db_status,
        gemini_api=gemini_status,
        environment=settings.ENVIRONMENT,
    )
