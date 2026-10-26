from typing import List
from fastapi import APIRouter, Depends
from app.schemas.device import DeviceStatusResponse
from app.services.device_service import DeviceService
from app.api.deps import get_device_service

router = APIRouter()

@router.get(
    "/status",
    response_model=List[DeviceStatusResponse],
    summary="Estado de comunicación de dispositivos",
    description="Devuelve el estado operativo de los microcontroladores basado en su última actividad registrada.",
)
def get_devices_status(
    device_service: DeviceService = Depends(get_device_service),
):
    return device_service.get_devices_status()
