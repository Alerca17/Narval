from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.schemas.semaforo import VirtualSemaforoResponse
from app.schemas.ai_analysis import AIAnalysisResponse

class PhInput(BaseModel):
    raw: Optional[float] = Field(None, description="Valor analógico bruto del ADC (0-4095)")
    voltage: Optional[float] = Field(None, description="Voltaje calculado en voltios")
    value: Optional[float] = Field(None, ge=0.0, le=14.0, description="pH convertido si existe calibración")
    is_calibrated: bool = False

class TurbidityInput(BaseModel):
    raw: Optional[float] = Field(None, description="Valor analógico bruto del ADC")
    voltage: Optional[float] = Field(None, description="Voltaje calculado en voltios")
    value: Optional[float] = Field(None, ge=0.0, description="Turbidez en NTU si existe calibración")
    is_calibrated: bool = False

class TemperatureInput(BaseModel):
    celsius: Optional[float] = Field(None, ge=-10.0, le=80.0, description="Temperatura en grados Celsius")
    is_valid: bool = True

class MeasurementCreate(BaseModel):
    device_code: str = Field(..., min_length=3, max_length=50)
    packet_id: str = Field(..., min_length=5, max_length=100, description="ID único para deduplicación idempotente")
    device_timestamp: Optional[datetime] = None
    ph: PhInput
    turbidity: TurbidityInput
    temperature: TemperatureInput
    quality_status: Optional[str] = None
    validation_notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def adapt_esp32_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Detect ESP32 format: {device_id, sequence_number, captured_at, measurements: {...}}
        if "device_id" in data and "measurements" in data:
            device_id = str(data["device_id"])
            seq = data.get("sequence_number", int(datetime.utcnow().timestamp()))
            packet_id = f"{device_id}-seq-{seq}"
            
            m = data.get("measurements", {})
            q_status = data.get("quality_status", "VALID")
            q_flags = data.get("quality_flags", [])
            flags_str = ", ".join(q_flags) if isinstance(q_flags, list) else str(q_flags)

            ph_val = m.get("ph")
            turb_val = m.get("turbidity_ntu")
            temp_val = m.get("temperature_c")

            return {
                "device_code": device_id,
                "packet_id": packet_id,
                "device_timestamp": data.get("captured_at"),
                "quality_status": q_status,
                "validation_notes": flags_str if flags_str else None,
                "ph": {
                    "raw": m.get("ph_raw"),
                    "voltage": None,
                    "value": ph_val,
                    "is_calibrated": ph_val is not None,
                },
                "turbidity": {
                    "raw": m.get("turbidity_raw"),
                    "voltage": None,
                    "value": turb_val,
                    "is_calibrated": turb_val is not None,
                },
                "temperature": {
                    "celsius": temp_val,
                    "is_valid": temp_val is not None,
                }
            }
        return data

class MeasurementResponse(BaseModel):
    id: int
    device_id: int
    device_code: str
    packet_id: str
    ph_raw: Optional[float] = None
    ph_voltage: Optional[float] = None
    ph_value: Optional[float] = None
    turbidity_raw: Optional[float] = None
    turbidity_voltage: Optional[float] = None
    turbidity_value: Optional[float] = None
    temperature_celsius: Optional[float] = None
    device_timestamp: Optional[datetime] = None
    received_at: datetime
    quality_status: str
    calibration_status: str
    validation_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LatestMeasurementResponse(BaseModel):
    measurement: Optional[MeasurementResponse] = None
    semaforo: VirtualSemaforoResponse
    ai_analysis: Optional[AIAnalysisResponse] = None

class MeasurementListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[MeasurementResponse]
