from typing import Optional, List, Tuple
from app.models.measurement import Measurement
from app.schemas.semaforo import (
    SemaforoColor,
    ParameterEvaluation,
    VirtualSemaforoResponse,
)

class VirtualSemaforoEngine:
    """
    Motor determinista de evaluación de calidad de parámetros del agua.
    Basado en los límites técnicos de referencia de la Resolución 2115 de 2007 (Colombia).
    """

    @classmethod
    def evaluate_ph(cls, value: Optional[float], voltage: Optional[float], is_calibrated: bool) -> ParameterEvaluation:
        if value is None:
            if voltage is not None:
                return ParameterEvaluation(
                    parameter="pH",
                    color=SemaforoColor.GRAY,
                    value=None,
                    voltage=round(voltage, 3),
                    unit="pH",
                    status_label="Calibración Pendiente",
                    message="Lectura analógica recibida pero sin calibración confirmada. Voltaje: {:.2f}V".format(voltage),
                    is_calibrated=False,
                )
            return ParameterEvaluation(
                parameter="pH",
                color=SemaforoColor.GRAY,
                value=None,
                voltage=None,
                unit="pH",
                status_label="Sin Lectura",
                message="No se recibió valor del sensor de pH.",
                is_calibrated=False,
            )

        if not is_calibrated:
            return ParameterEvaluation(
                parameter="pH",
                color=SemaforoColor.GRAY,
                value=round(value, 2),
                voltage=round(voltage, 3) if voltage is not None else None,
                unit="pH",
                status_label="Calibración Pendiente",
                message="Valor estimado pendiente de verificación con soluciones buffer pH 4 y 7.",
                is_calibrated=False,
            )

        # Reglas normativas Resolución 2115 de 2007: 6.5 a 9.0
        if 6.5 <= value <= 9.0:
            return ParameterEvaluation(
                parameter="pH",
                color=SemaforoColor.GREEN,
                value=round(value, 2),
                voltage=round(voltage, 3) if voltage is not None else None,
                unit="pH",
                status_label="Óptimo",
                message="Dentro del rango admisible (6.5 - 9.0 Res. 2115/2007).",
                is_calibrated=True,
            )
        elif (6.0 <= value < 6.5) or (9.0 < value <= 9.5):
            return ParameterEvaluation(
                parameter="pH",
                color=SemaforoColor.YELLOW,
                value=round(value, 2),
                voltage=round(voltage, 3) if voltage is not None else None,
                unit="pH",
                status_label="Alerta",
                message=f"Leve desviación del rango admisible ({value:.2f} pH).",
                is_calibrated=True,
            )
        else:
            return ParameterEvaluation(
                parameter="pH",
                color=SemaforoColor.RED,
                value=round(value, 2),
                voltage=round(voltage, 3) if voltage is not None else None,
                unit="pH",
                status_label="Crítico",
                message=f"Fuera de rango seguro normativo ({value:.2f} pH). Posible acidificación o alcalinidad extrema.",
                is_calibrated=True,
            )

    @classmethod
    def evaluate_turbidity(cls, value: Optional[float], voltage: Optional[float], is_calibrated: bool) -> ParameterEvaluation:
        if value is None or not is_calibrated:
            if voltage is not None:
                return ParameterEvaluation(
                    parameter="Turbidez",
                    color=SemaforoColor.GRAY,
                    value=None,
                    voltage=round(voltage, 3),
                    unit="NTU",
                    status_label="Calibración Pendiente",
                    message="Sensor óptico en operación ({:.2f}V). Pendiente curva de calibración con formazina.".format(voltage),
                    is_calibrated=False,
                )
            return ParameterEvaluation(
                parameter="Turbidez",
                color=SemaforoColor.GRAY,
                value=None,
                voltage=None,
                unit="NTU",
                status_label="Sin Lectura",
                message="No se recibió lectura del sensor de turbidez.",
                is_calibrated=False,
            )

        # Reglas normativas Resolución 2115 de 2007: hasta 2.0 NTU aceptable
        if value <= 2.0:
            return ParameterEvaluation(
                parameter="Turbidez",
                color=SemaforoColor.GREEN,
                value=round(value, 2),
                voltage=round(voltage, 3) if voltage is not None else None,
                unit="NTU",
                status_label="Óptimo",
                message="Turbidez baja y admisible (≤ 2.0 NTU Res. 2115/2007).",
                is_calibrated=True,
            )
        elif 2.0 < value <= 5.0:
            return ParameterEvaluation(
                parameter="Turbidez",
                color=SemaforoColor.YELLOW,
                value=round(value, 2),
                voltage=round(voltage, 3) if voltage is not None else None,
                unit="NTU",
                status_label="Alerta",
                message=f"Turbidez moderada ({value:.2f} NTU). Supera el valor recomendado de 2.0 NTU.",
                is_calibrated=True,
            )
        else:
            return ParameterEvaluation(
                parameter="Turbidez",
                color=SemaforoColor.RED,
                value=round(value, 2),
                voltage=round(voltage, 3) if voltage is not None else None,
                unit="NTU",
                status_label="Crítico",
                message=f"Turbidez elevada ({value:.2f} NTU). Agua con alta presencia de partículas en suspensión.",
                is_calibrated=True,
            )

    @classmethod
    def evaluate_temperature(cls, celsius: Optional[float]) -> ParameterEvaluation:
        if celsius is None:
            return ParameterEvaluation(
                parameter="Temperatura",
                color=SemaforoColor.GRAY,
                value=None,
                voltage=None,
                unit="°C",
                status_label="Error Sensor",
                message="Fallo de comunicación OneWire con el sensor DS18B20.",
                is_calibrated=False,
            )

        if 10.0 <= celsius <= 30.0:
            return ParameterEvaluation(
                parameter="Temperatura",
                color=SemaforoColor.GREEN,
                value=round(celsius, 1),
                voltage=None,
                unit="°C",
                status_label="Aceptable",
                message=f"Temperatura ambiental de agua normal ({celsius:.1f} °C).",
                is_calibrated=True,
            )
        elif (5.0 <= celsius < 10.0) or (30.0 < celsius <= 38.0):
            return ParameterEvaluation(
                parameter="Temperatura",
                color=SemaforoColor.YELLOW,
                value=round(celsius, 1),
                voltage=None,
                unit="°C",
                status_label="Advertencia",
                message=f"Temperatura atípica para acueducto rural ({celsius:.1f} °C).",
                is_calibrated=True,
            )
        else:
            return ParameterEvaluation(
                parameter="Temperatura",
                color=SemaforoColor.RED,
                value=round(celsius, 1),
                voltage=None,
                unit="°C",
                status_label="Crítico",
                message=f"Temperatura anómala o extremo físico ({celsius:.1f} °C).",
                is_calibrated=True,
            )

    @classmethod
    def evaluate_measurement(cls, measurement: Optional[Measurement]) -> VirtualSemaforoResponse:
        if not measurement:
            return VirtualSemaforoResponse(
                global_status=SemaforoColor.GRAY,
                global_label="Sin Mediciones",
                global_summary="No hay registros almacenados para evaluar el estado.",
                ph=cls.evaluate_ph(None, None, False),
                turbidity=cls.evaluate_turbidity(None, None, False),
                temperature=cls.evaluate_temperature(None),
                notes="Esperando primera transmisión de datos del dispositivo ESP32."
            )

        is_ph_calibrated = measurement.calibration_status == "CALIBRATED" and measurement.ph_value is not None
        is_turbidity_calibrated = measurement.calibration_status == "CALIBRATED" and measurement.turbidity_value is not None

        ph_eval = cls.evaluate_ph(measurement.ph_value, measurement.ph_voltage, is_ph_calibrated)
        turb_eval = cls.evaluate_turbidity(measurement.turbidity_value, measurement.turbidity_voltage, is_turbidity_calibrated)
        temp_eval = cls.evaluate_temperature(measurement.temperature_celsius)

        colors = [ph_eval.color, turb_eval.color, temp_eval.color]

        # Determinación del estado global:
        if SemaforoColor.RED in colors:
            global_status = SemaforoColor.RED
            global_label = "Estado Crítico"
            global_summary = "Uno o más parámetros superan los límites de seguridad normativos."
        elif SemaforoColor.YELLOW in colors:
            global_status = SemaforoColor.YELLOW
            global_label = "Estado de Alerta"
            global_summary = "Parámetros fuera del rango óptimo recomendados."
        elif SemaforoColor.GRAY in colors:
            # Hay datos pero alguno está pendiente de calibración o sin lectura
            global_status = SemaforoColor.YELLOW
            global_label = "Datos Parciales / Calibración Pendiente"
            global_summary = "El sistema recibe señales pero no todos los sensores cuentan con calibración validada."
        else:
            # Todos verdes
            global_status = SemaforoColor.GREEN
            global_label = "Parámetros Óptimos"
            global_summary = "Todos los parámetros monitorizados se encuentran dentro de los rangos de referencia."

        notes = []
        if not is_ph_calibrated and measurement.ph_voltage is not None:
            notes.append("pH: pendiente calibración en 2 puntos.")
        if not is_turbidity_calibrated and measurement.turbidity_voltage is not None:
            notes.append("Turbidez: sin curva de calibración de formazina.")
        if measurement.validation_notes:
            notes.append(measurement.validation_notes)

        return VirtualSemaforoResponse(
            global_status=global_status,
            global_label=global_label,
            global_summary=global_summary,
            ph=ph_eval,
            turbidity=turb_eval,
            temperature=temp_eval,
            notes=" | ".join(notes) if notes else None
        )
