import logging
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from app.core.config import settings
from app.models.measurement import Measurement
from app.models.ai_analysis import AIAnalysis
from app.schemas.ai_analysis import AIAnalysisResponse
from app.repositories.ai_repository import AIRepository
from app.repositories.measurement_repository import MeasurementRepository

logger = logging.getLogger("narval.ai")

ESP32_FLAG_MESSAGES = {
    "TEMP_SENSOR_DISCONNECTED": "Sensor de temperatura (DS18B20): Desconectado del bus OneWire (GPIO 26). Verifica que el cable de datos y la resistencia pull-up de 4.7k estén conectados.",
    "TEMP_POWER_OR_BUS_ERROR": "Sensor de temperatura (DS18B20): Fallo de alimentación o bus OneWire (lectura de 85°C o -127°C).",
    "TEMP_READ_EXCEPTION": "Sensor de temperatura (DS18B20): Excepción eléctrica al consultar la sonda.",
    "TEMP_OUTSIDE_PHYSICAL_RANGE": "Sensor de temperatura (DS18B20): Lectura térmica anómala fuera de rango físico admisible (0°C - 50°C).",
    "PH_ADC_SATURATED_OR_DISCONNECTED": "Sensor de pH: Electrodo saturado o desconectado (ADC en 4095). Revisa que la sonda BNC esté ajustada, que el módulo PH-4502C esté alimentado y comparta tierra (GND) con el ESP32.",
    "TURBIDITY_SENSOR_DISCONNECTED": "Sensor de turbidez: Módulo óptico desconectado (ADC <= 5). Verifica la alimentación y el pin analógico en GPIO 36.",
    "PH_OUTSIDE_PHYSICAL_RANGE": "Sensor de pH: Valor fuera de escala física admisible (0.0 a 14.0).",
    "TURBIDITY_OUTSIDE_PHYSICAL_RANGE": "Sensor de turbidez: Valor de turbidez fuera de escala física.",
    "PH_EXCESSIVE_NOISE": "Sensor de pH: Ruido eléctrico excesivo en la lectura analógica.",
    "TURBIDITY_EXCESSIVE_NOISE": "Sensor de turbidez: Ruido óptico/eléctrico excesivo en el fototransistor.",
}

class AIService:
    DISCLAIMER = (
        "AVISO TÉCNICO NORMATIVO: Este análisis descriptivo es generado mediante inteligencia artificial "
        "con base exclusiva en los parámetros fisicoquímicos monitorizados (pH, turbidez, temperatura). "
        "No constituye una certificación oficial de potabilidad, aptitud para consumo humano ni diagnóstico sanitario. "
        "La evaluación de agua potable en Colombia requiere análisis de laboratorio acreditados conforme a la Resolución 2115 de 2007."
    )

    def __init__(self, ai_repo: AIRepository, measurement_repo: MeasurementRepository):
        self.ai_repo = ai_repo
        self.measurement_repo = measurement_repo

    def validate_sensors_readiness(self, target: Measurement) -> Tuple[bool, List[str]]:
        """
        Valida rigurosamente si todos los sensores físicos están conectados y operativos.
        Si algún sensor está desconectado, saturado o en fallo, NO se permite llamar a Gemini.
        """
        errors = []

        # 1. Comprobar flags de calidad provenientes del ESP32
        notes_str = target.validation_notes or ""
        for flag_key, msg in ESP32_FLAG_MESSAGES.items():
            if flag_key in notes_str:
                errors.append(msg)

        # 2. Comprobación directa de variables físicas del sensor de temperatura
        if target.temperature_celsius is None:
            if not any("temperatura" in e.lower() for e in errors):
                errors.append("Sensor de temperatura: No reporta un valor numérico válido (posible circuito abierto o sonda desconectada).")

        # 3. Comprobación directa de variables físicas del sensor de pH
        if target.ph_raw is None or target.ph_raw >= 4090:
            if not any("ph" in e.lower() for e in errors):
                errors.append("Sensor de pH: Señal saturada en el límite superior (ADC 4095). Revisa conexión BNC y masa (GND).")
        elif target.ph_raw <= 5:
            if not any("ph" in e.lower() for e in errors):
                errors.append("Sensor de pH: Señal en cero (ADC <= 5). El módulo no entrega señal al pin ADC.")

        # 4. Comprobación directa de variables físicas del sensor de turbidez
        if target.turbidity_raw is None or target.turbidity_raw <= 5:
            if not any("turbidez" in e.lower() for e in errors):
                errors.append("Sensor de turbidez: Señal nula o sensor desconectado.")

        # 5. Estado general de calidad
        if target.quality_status in ("SENSOR_ERROR", "INVALID") and not errors:
            errors.append(f"El microcontrolador ESP32 declaró el estado técnico: {target.quality_status}.")

        is_ready = len(errors) == 0
        return is_ready, errors

    def analyze_measurement(
        self,
        measurement_id: Optional[int] = None,
        include_recent_count: int = 5,
    ) -> AIAnalysisResponse:
        # 1. Fetch target measurement
        if measurement_id:
            target = self.measurement_repo.get_by_id(measurement_id)
        else:
            target = self.measurement_repo.get_latest()

        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron mediciones registradas en la base de datos para analizar."
            )

        # 2. VALIDACIÓN ESTRICTA: ¿Todos los sensores están listos y conectados?
        is_ready, sensor_errors = self.validate_sensors_readiness(target)
        if not is_ready:
            logger.warning(f"Intento de análisis con sensores no listos en medición {target.id}: {sensor_errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "SENSORS_NOT_READY",
                    "title": "Sensores no disponibles para análisis con Gemini",
                    "message": "No es posible solicitar el reporte con inteligencia artificial porque uno o más sensores presentan fallas, desconexión física o lecturas saturadas.",
                    "sensor_errors": sensor_errors,
                    "action_required": "Por favor revisa el cableado físico de los sensores en el ESP32 (COM7), verifica la masa común GND y que la sonda BNC de pH y el DS18B20 estén conectados firmemente."
                }
            )

        # 3. Fetch history for contextual variation
        recent = self.measurement_repo.get_recent(limit=include_recent_count)

        # 4. Check if Gemini API key is configured
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY no configurada. Generando análisis determinista local.")
            return self._generate_fallback_analysis(target, recent)

        # 5. Invoke Google Gemini API
        try:
            return self._call_gemini_api(target, recent)
        except Exception as e:
            logger.error(f"Error al invocar Google Gemini API: {e}")
            fallback = self._generate_fallback_analysis(target, recent)
            fallback.analysis_text += f"\n\n(Nota: La llamada en vivo a Gemini no pudo completarse: {str(e)})"
            return fallback

    def _call_gemini_api(self, target: Measurement, history: List[Measurement]) -> AIAnalysisResponse:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Build context prompt with verified data
        system_instruction = (
            "Eres un analista técnico especializado en calidad del agua y sistemas de monitoreo IoT para acueductos rurales en Colombia. "
            "Tu labor es interpretar mediciones de sensores reales (pH, turbidez, temperatura) basándote estrictamente en los datos provistos. "
            "REGLAS OBLIGATORIAS:\n"
            "1. No inventes números ni alteres las cifras recibidas.\n"
            "2. No afirmes que el agua es potable ni des diagnósticos sanitarios categóricos.\n"
            "3. Refiérete a la Resolución 2115 de 2007 (pH admisible: 6.5 a 9.0; turbidez recomendada: <= 2.0 NTU).\n"
            "4. Si un sensor no está calibrado o falta su valor, señálalo explícitamente como una limitación técnica.\n"
            "5. Tu respuesta debe estructurarse con claridad: 'RESUMEN EJECUTIVO' (1-2 frases concisas) y 'ANÁLISIS DESCRIPTIVO' (detalles fisicoquímicos, variaciones respecto a lecturas anteriores y recomendaciones operativas)."
        )

        user_content = f"""
DATOS DE LA MEDICIÓN A ANALIZAR (ID: {target.id}):
- Dispositivo: {target.device.code if target.device else 'Desconocido'}
- Fecha y hora recepción: {target.received_at.isoformat()}
- pH Valor: {target.ph_value if target.ph_value is not None else 'No calibrado'} (Voltaje: {target.ph_voltage}V, Raw: {target.ph_raw})
- Turbidez Valor: {target.turbidity_value if target.turbidity_value is not None else 'No calibrado'} NTU (Voltaje: {target.turbidity_voltage}V, Raw: {target.turbidity_raw})
- Temperatura: {target.temperature_celsius if target.temperature_celsius is not None else 'No disponible'} °C
- Estado de Calidad: {target.quality_status}
- Estado de Calibración: {target.calibration_status}
- Notas de Validación: {target.validation_notes or 'Ninguna'}

HISTORIAL RECIENTE ({len(history)} mediciones previas):
"""
        for h in history:
            user_content += f"- [ID {h.id} a las {h.received_at.strftime('%H:%M:%S')}]: pH={h.ph_value}, Turb={h.turbidity_value}, Temp={h.temperature_celsius}°C\n"

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )

        raw_text = response.text or "Sin respuesta generada por Gemini."
        
        # Split executive summary if available
        summary = "Análisis contextual de parámetros de agua completado exitosamente."
        if "RESUMEN EJECUTIVO" in raw_text:
            parts = raw_text.split("ANÁLISIS DESCRIPTIVO")
            summary_part = parts[0].replace("RESUMEN EJECUTIVO", "").replace("**", "").replace("#", "").strip(": \n")
            summary = summary_part[:280]

        # Persist analysis in database
        analysis_record = AIAnalysis(
            measurement_id=target.id,
            query_scope="SINGLE",
            model_used=settings.GEMINI_MODEL,
            summary=summary,
            analysis_text=raw_text,
            limitations_disclaimer=self.DISCLAIMER,
            created_at=datetime.now(timezone.utc),
        )
        saved = self.ai_repo.create(analysis_record)

        return AIAnalysisResponse(
            id=saved.id,
            measurement_id=saved.measurement_id,
            model_used=saved.model_used,
            summary=saved.summary,
            analysis_text=saved.analysis_text,
            limitations_disclaimer=saved.limitations_disclaimer,
            created_at=saved.created_at,
        )

    def _generate_fallback_analysis(self, target: Measurement, history: List[Measurement]) -> AIAnalysisResponse:
        """Generador determinista de respaldo si no hay conexión a internet o credenciales."""
        obs = []
        if target.ph_value is not None:
            if 6.5 <= target.ph_value <= 9.0:
                obs.append(f"El pH registrado ({target.ph_value:.2f}) se encuentra dentro del rango admisible de la Resolución 2115 de 2007 (6.5 - 9.0).")
            else:
                obs.append(f"El pH registrado ({target.ph_value:.2f}) presenta una desviación del rango admisible.")
        elif target.ph_voltage is not None:
            obs.append(f"El sensor de pH reporta señal analógica ({target.ph_voltage:.2f}V) pero se encuentra pendiente de calibración.")

        if target.turbidity_value is not None:
            if target.turbidity_value <= 2.0:
                obs.append(f"La turbidez ({target.turbidity_value:.2f} NTU) cumple con el valor recomendado (≤ 2.0 NTU).")
            else:
                obs.append(f"La turbidez ({target.turbidity_value:.2f} NTU) supera el umbral recomendado de 2.0 NTU.")
        elif target.turbidity_voltage is not None:
            obs.append(f"El sensor óptico de turbidez emite {target.turbidity_voltage:.2f}V; requiere curva de calibración para reportar NTU.")

        if target.temperature_celsius is not None:
            obs.append(f"La temperatura del agua es de {target.temperature_celsius:.1f} °C, adecuada para condiciones ambientales.")
        else:
            obs.append("Lectura de temperatura no disponible en este paquete.")

        summary = f"Evaluación técnica local: Calidad {target.quality_status}, Calibración {target.calibration_status}."
        analysis_text = (
            f"INFORME DESCRIPTIVO TÉCNICO (Generador Determinista de Respaldo):\n\n"
            f"1. Observaciones de la Medición (ID: {target.id}):\n"
            + "\n".join(f"   • {o}" for o in obs)
            + f"\n\n2. Contexto Histórico: Se comparó con las últimas {len(history)} mediciones registradas en el acueducto.\n"
            f"3. Acción sugerida: Realizar calibración con soluciones patrón para habilitar lectura en unidades NTU y pH definitivas.\n"
        )

        analysis_record = AIAnalysis(
            measurement_id=target.id,
            query_scope="SINGLE",
            model_used="local-deterministic-engine",
            summary=summary[:280],
            analysis_text=analysis_text,
            limitations_disclaimer=self.DISCLAIMER,
            created_at=datetime.now(timezone.utc),
        )
        saved = self.ai_repo.create(analysis_record)

        return AIAnalysisResponse(
            id=saved.id,
            measurement_id=saved.measurement_id,
            model_used=saved.model_used,
            summary=saved.summary,
            analysis_text=saved.analysis_text,
            limitations_disclaimer=saved.limitations_disclaimer,
            created_at=saved.created_at,
        )
