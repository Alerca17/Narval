from fastapi import APIRouter
from app.api.v1.endpoints import measurements, devices, alerts, ai, health

api_v1_router = APIRouter()

api_v1_router.include_router(measurements.router, prefix="/measurements", tags=["Mediciones"])
api_v1_router.include_router(devices.router, prefix="/devices", tags=["Dispositivos"])
api_v1_router.include_router(alerts.router, prefix="/alerts", tags=["Alertas"])
api_v1_router.include_router(ai.router, prefix="/ai", tags=["Inteligencia Artificial"])
api_v1_router.include_router(health.router, prefix="/health", tags=["Salud"])
