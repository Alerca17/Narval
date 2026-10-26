from fastapi import APIRouter, Depends
from app.schemas.ai_analysis import AIAnalyzeRequest, AIAnalysisResponse
from app.services.ai_service import AIService
from app.api.deps import get_ai_service

router = APIRouter()

@router.post(
    "/analyze",
    response_model=AIAnalysisResponse,
    summary="Análisis descriptivo contextual con Gemini",
    description="Solicita a Google Gemini una interpretación técnica de mediciones reales persistidas.",
)
def request_ai_analysis(
    payload: AIAnalyzeRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    return ai_service.analyze_measurement(
        measurement_id=payload.measurement_id,
        include_recent_count=payload.include_recent_count,
    )
