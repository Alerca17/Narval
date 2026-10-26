from app.schemas.device import DeviceCreate, DeviceResponse, DeviceStatusResponse
from app.schemas.measurement import (
    PhInput,
    TurbidityInput,
    TemperatureInput,
    MeasurementCreate,
    MeasurementResponse,
    LatestMeasurementResponse,
    MeasurementListResponse,
)
from app.schemas.alert import AlertResponse, AlertListResponse
from app.schemas.ai_analysis import AIAnalyzeRequest, AIAnalysisResponse
from app.schemas.semaforo import (
    SemaforoColor,
    ParameterEvaluation,
    VirtualSemaforoResponse,
)
from app.schemas.health import HealthResponse

__all__ = [
    "DeviceCreate",
    "DeviceResponse",
    "DeviceStatusResponse",
    "PhInput",
    "TurbidityInput",
    "TemperatureInput",
    "MeasurementCreate",
    "MeasurementResponse",
    "LatestMeasurementResponse",
    "MeasurementListResponse",
    "AlertResponse",
    "AlertListResponse",
    "AIAnalyzeRequest",
    "AIAnalysisResponse",
    "SemaforoColor",
    "ParameterEvaluation",
    "VirtualSemaforoResponse",
    "HealthResponse",
]
