from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.schemas.measurement import (
    MeasurementCreate,
    MeasurementResponse,
    LatestMeasurementResponse,
    MeasurementListResponse,
)
from app.services.measurement_service import MeasurementService
from app.repositories.measurement_repository import MeasurementRepository
from app.api.deps import (
    get_measurement_service,
    get_measurement_repo,
    verify_device_ingestion_auth,
)

router = APIRouter()

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=MeasurementResponse,
    summary="Ingesta de medición IoT",
    description="Recibe mediciones emitidas por el firmware MicroPython del microcontrolador ESP32.",
)
def ingest_measurement(
    payload: MeasurementCreate,
    authorized: bool = Depends(verify_device_ingestion_auth),
    measurement_service: MeasurementService = Depends(get_measurement_service),
):
    saved_measurement, _ = measurement_service.process_and_store_measurement(payload)
    return MeasurementResponse(
        id=saved_measurement.id,
        device_id=saved_measurement.device_id,
        device_code=payload.device_code,
        packet_id=saved_measurement.packet_id,
        ph_raw=saved_measurement.ph_raw,
        ph_voltage=saved_measurement.ph_voltage,
        ph_value=saved_measurement.ph_value,
        turbidity_raw=saved_measurement.turbidity_raw,
        turbidity_voltage=saved_measurement.turbidity_voltage,
        turbidity_value=saved_measurement.turbidity_value,
        temperature_celsius=saved_measurement.temperature_celsius,
        device_timestamp=saved_measurement.device_timestamp,
        received_at=saved_measurement.received_at,
        quality_status=saved_measurement.quality_status,
        calibration_status=saved_measurement.calibration_status,
        validation_notes=saved_measurement.validation_notes,
    )

@router.get(
    "/latest",
    response_model=LatestMeasurementResponse,
    summary="Última medición y Semáforo Virtual",
    description="Obtiene el registro más reciente y la evaluación determinista del Semáforo Virtual.",
)
def get_latest_measurement(
    device_code: Optional[str] = Query(None, description="Filtrar por código de dispositivo"),
    measurement_service: MeasurementService = Depends(get_measurement_service),
):
    return measurement_service.get_latest_with_semaforo(device_code=device_code)

@router.get(
    "",
    response_model=MeasurementListResponse,
    summary="Historial de mediciones",
    description="Consulta paginada del historial de mediciones con filtros de fecha y dispositivo.",
)
def list_measurements(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    device_code: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    measurement_repo: MeasurementRepository = Depends(get_measurement_repo),
):
    items, total = measurement_repo.list_measurements(
        limit=limit,
        offset=offset,
        device_code=device_code,
        start_date=start_date,
        end_date=end_date,
    )
    result_items = [
        MeasurementResponse(
            id=m.id,
            device_id=m.device_id,
            device_code=m.device.code if m.device else "UNKNOWN",
            packet_id=m.packet_id,
            ph_raw=m.ph_raw,
            ph_voltage=m.ph_voltage,
            ph_value=m.ph_value,
            turbidity_raw=m.turbidity_raw,
            turbidity_voltage=m.turbidity_voltage,
            turbidity_value=m.turbidity_value,
            temperature_celsius=m.temperature_celsius,
            device_timestamp=m.device_timestamp,
            received_at=m.received_at,
            quality_status=m.quality_status,
            calibration_status=m.calibration_status,
            validation_notes=m.validation_notes,
        )
        for m in items
    ]
    return MeasurementListResponse(total=total, limit=limit, offset=offset, items=result_items)

@router.get(
    "/{measurement_id}",
    response_model=MeasurementResponse,
    summary="Detalle de una medición",
)
def get_measurement_by_id(
    measurement_id: int,
    measurement_repo: MeasurementRepository = Depends(get_measurement_repo),
):
    m = measurement_repo.get_by_id(measurement_id)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medición no encontrada")
    return MeasurementResponse(
        id=m.id,
        device_id=m.device_id,
        device_code=m.device.code if m.device else "UNKNOWN",
        packet_id=m.packet_id,
        ph_raw=m.ph_raw,
        ph_voltage=m.ph_voltage,
        ph_value=m.ph_value,
        turbidity_raw=m.turbidity_raw,
        turbidity_voltage=m.turbidity_voltage,
        turbidity_value=m.turbidity_value,
        temperature_celsius=m.temperature_celsius,
        device_timestamp=m.device_timestamp,
        received_at=m.received_at,
        quality_status=m.quality_status,
        calibration_status=m.calibration_status,
        validation_notes=m.validation_notes,
    )
