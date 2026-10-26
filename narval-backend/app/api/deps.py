from typing import Generator, Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_device_token
from app.repositories.device_repository import DeviceRepository
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.ai_repository import AIRepository
from app.services.device_service import DeviceService
from app.services.alert_service import AlertService
from app.services.measurement_service import MeasurementService
from app.services.ai_service import AIService

# Repositories
def get_device_repo(db: Session = Depends(get_db)) -> DeviceRepository:
    return DeviceRepository(db)

def get_measurement_repo(db: Session = Depends(get_db)) -> MeasurementRepository:
    return MeasurementRepository(db)

def get_alert_repo(db: Session = Depends(get_db)) -> AlertRepository:
    return AlertRepository(db)

def get_ai_repo(db: Session = Depends(get_db)) -> AIRepository:
    return AIRepository(db)

# Services
def get_device_service(
    device_repo: DeviceRepository = Depends(get_device_repo),
) -> DeviceService:
    return DeviceService(device_repo)

def get_alert_service(
    alert_repo: AlertRepository = Depends(get_alert_repo),
) -> AlertService:
    return AlertService(alert_repo)

def get_ai_service(
    ai_repo: AIRepository = Depends(get_ai_repo),
    measurement_repo: MeasurementRepository = Depends(get_measurement_repo),
) -> AIService:
    return AIService(ai_repo, measurement_repo)

def get_measurement_service(
    measurement_repo: MeasurementRepository = Depends(get_measurement_repo),
    device_repo: DeviceRepository = Depends(get_device_repo),
    alert_service: AlertService = Depends(get_alert_service),
    ai_service: AIService = Depends(get_ai_service),
) -> MeasurementService:
    return MeasurementService(measurement_repo, device_repo, alert_service, ai_service)

# Device Authentication for Ingestion (supports both X-Device-Token and X-Device-Secret from ESP32)
def verify_device_ingestion_auth(
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
    x_device_secret: Optional[str] = Header(None, alias="X-Device-Secret"),
) -> bool:
    token = x_device_token or x_device_secret
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header 'X-Device-Token' o 'X-Device-Secret' requerido para la ingesta de mediciones.",
        )
    # Compare with configured secret
    if not verify_device_token(token, settings.DEVICE_INGESTION_SECRET):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de dispositivo inválido o no autorizado.",
        )
    return True
