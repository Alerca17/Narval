from datetime import datetime, timezone
from typing import Optional, Tuple, List, Any
from fastapi import HTTPException, status
from app.models.measurement import Measurement
from app.models.device import Device
from app.schemas.measurement import MeasurementCreate, MeasurementResponse, LatestMeasurementResponse
from app.schemas.semaforo import VirtualSemaforoResponse
from app.schemas.ai_analysis import AIAnalysisResponse
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.device_repository import DeviceRepository
from app.services.semaforo_service import VirtualSemaforoEngine
from app.services.alert_service import AlertService

class MeasurementService:
    def __init__(
        self,
        measurement_repo: MeasurementRepository,
        device_repo: DeviceRepository,
        alert_service: AlertService,
        ai_service: Optional[Any] = None,
    ):
        self.measurement_repo = measurement_repo
        self.device_repo = device_repo
        self.alert_service = alert_service
        self.ai_service = ai_service

    def process_and_store_measurement(self, payload: MeasurementCreate) -> Tuple[Measurement, VirtualSemaforoResponse]:
        # 1. Deduplication Check
        existing = self.measurement_repo.get_by_packet_id(payload.packet_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Paquete con packet_id '{payload.packet_id}' ya fue procesado anteriormente."
            )

        # 2. Get or create Device
        device = self.device_repo.get_by_code(payload.device_code)
        if not device:
            device = self.device_repo.create(
                code=payload.device_code,
                name=f"Estación {payload.device_code}"
            )

        # Update device heartbeat
        self.device_repo.update_heartbeat(device, status="ONLINE")

        # 3. Assess Quality & Calibration Status
        notes = []
        is_partial = False
        is_calibrated_ph = payload.ph.is_calibrated and payload.ph.value is not None
        is_calibrated_turb = payload.turbidity.is_calibrated and payload.turbidity.value is not None

        if not is_calibrated_ph:
            is_partial = True
            notes.append("pH no calibrado")
        if not is_calibrated_turb:
            is_partial = True
            notes.append("Turbidez no calibrada")
        if payload.temperature.celsius is None or not payload.temperature.is_valid:
            is_partial = True
            notes.append("Temperatura no disponible o con error")

        quality_status = payload.quality_status or ("PARTIAL" if is_partial else "VALID")
        calibration_status = "CALIBRATED" if (is_calibrated_ph and is_calibrated_turb) else "PENDING"

        if payload.validation_notes:
            notes.append(payload.validation_notes)

        # 4. Create Measurement Entity
        measurement = Measurement(
            device_id=device.id,
            packet_id=payload.packet_id,
            ph_raw=payload.ph.raw,
            ph_voltage=payload.ph.voltage,
            ph_value=payload.ph.value if is_calibrated_ph else None,
            turbidity_raw=payload.turbidity.raw,
            turbidity_voltage=payload.turbidity.voltage,
            turbidity_value=payload.turbidity.value if is_calibrated_turb else None,
            temperature_celsius=payload.temperature.celsius if payload.temperature.is_valid else None,
            device_timestamp=payload.device_timestamp,
            received_at=datetime.now(timezone.utc),
            quality_status=quality_status,
            calibration_status=calibration_status,
            validation_notes=", ".join(notes) if notes else None,
        )

        saved_measurement = self.measurement_repo.create(measurement)

        # 5. Evaluate Semaforo
        semaforo = VirtualSemaforoEngine.evaluate_measurement(saved_measurement)

        # 6. Evaluate and persist alerts if out of bounds
        self.alert_service.evaluate_and_generate_alerts(saved_measurement, semaforo)

        return saved_measurement, semaforo

    def get_latest_with_semaforo(self, device_code: Optional[str] = None) -> LatestMeasurementResponse:
        measurement = self.measurement_repo.get_latest(device_code=device_code)
        semaforo = VirtualSemaforoEngine.evaluate_measurement(measurement)

        meas_resp = None
        ai_resp = None

        if measurement:
            meas_resp = MeasurementResponse(
                id=measurement.id,
                device_id=measurement.device_id,
                device_code=measurement.device.code if measurement.device else "UNKNOWN",
                packet_id=measurement.packet_id,
                ph_raw=measurement.ph_raw,
                ph_voltage=measurement.ph_voltage,
                ph_value=measurement.ph_value,
                turbidity_raw=measurement.turbidity_raw,
                turbidity_voltage=measurement.turbidity_voltage,
                turbidity_value=measurement.turbidity_value,
                temperature_celsius=measurement.temperature_celsius,
                device_timestamp=measurement.device_timestamp,
                received_at=measurement.received_at,
                quality_status=measurement.quality_status,
                calibration_status=measurement.calibration_status,
                validation_notes=measurement.validation_notes,
            )

            # Retrieve latest AI analysis for this measurement if exists
            if self.ai_service and hasattr(self.ai_service, 'ai_repo'):
                analysis_rec = self.ai_service.ai_repo.get_by_measurement_id(measurement.id)
                if not analysis_rec:
                    recent = self.ai_service.ai_repo.get_recent(limit=1)
                    if recent:
                        analysis_rec = recent[0]
                if analysis_rec:
                    ai_resp = AIAnalysisResponse(
                        id=analysis_rec.id,
                        measurement_id=analysis_rec.measurement_id,
                        model_used=analysis_rec.model_used,
                        summary=analysis_rec.summary,
                        analysis_text=analysis_rec.analysis_text,
                        limitations_disclaimer=analysis_rec.limitations_disclaimer,
                        created_at=analysis_rec.created_at,
                    )

        return LatestMeasurementResponse(
            measurement=meas_resp,
            semaforo=semaforo,
            ai_analysis=ai_resp,
        )
