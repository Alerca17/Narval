# NARVAL SOURCE OF TRUTH (SOT) — ESPECIFICACIÓN MAESTRA

## 1. Identidad y Propósito del Proyecto
- **Nombre Oficial:** Narval MVP.
- **Nombre de Interfaz Web:** Semáforo Virtual.
- **Propósito:** Sistema IoT de monitoreo de parámetros seleccionados de calidad del agua (pH, turbidez y temperatura), orientado al contexto de acueductos rurales en Colombia.
- **Objetivo Técnico:** Adquirir mediciones mediante un microcontrolador ESP32 con sensores físicos, validarlas y transmitirlas a un backend FastAPI, persistirlas en PostgreSQL (Supabase) mediante SQLAlchemy 2, visualizarlas en un Semáforo Virtual (React/TypeScript) y ofrecer análisis explicativo complementario mediante Google Gemini.
- **Límite Normativo y Científico Crucial:** Narval **NO** es un sistema de certificación de potabilidad ni diagnóstico sanitario oficial. Tres parámetros fisicoquímicos no bastan para certificar agua potable según la Resolución 2115 de 2007 (falta microbiología, cloro residual, metales, etc.). El sistema clasifica el comportamiento de los parámetros medidos contra umbrales técnicos documentados, no la potabilidad total.

---

## 2. Alcance Aprobado vs. Funcionalidades Excluidas

### 2.1. Alcance Aprobado (MVP)
1. **Hardware & Firmware:** ESP32 ejecutando MicroPython, lectura de pH (módulo analógico), turbidez (módulo analógico) y temperatura (DS18B20 en protocolo OneWire). Conexión Wi-Fi y transmisión HTTP/HTTPS a la API.
2. **Backend API:** FastAPI (Python 3.14 / 3.11+), arquitectura en capas limpia (API -> Service -> Repository -> Domain/DB).
3. **Persistencia:** PostgreSQL alojado en Supabase, utilizando SQLAlchemy 2 como ORM determinista y Alembic para migraciones.
4. **Semáforo Virtual (Reglas Deterministas):** Clasificación por estados (Verde/Óptimo, Amarillo/Advertencia, Rojo/Crítico, Gris/Sin Calibrar o Error) según umbrales de referencia basados en rangos de la Resolución 2115 de 2007 de Colombia.
5. **Inteligencia Artificial:** Google Gemini vía `google-genai` SDK oficial en el backend. Análisis cualitativo y contextual sobre mediciones reales persistidas. No inventa números, no cambia el estado del semáforo, no certifica potabilidad.
6. **Frontend:** React + TypeScript con Vite, arquitectura en capas (Presentation/Components -> Custom Hooks -> Services/API -> Types/Contracts).

### 2.2. Funcionalidades Expresamente Fuera de Alcance (NO INVENTAR)
- Registro, login y roles multiempresa.
- Facturación, pagos, suscripciones y módulos comerciales.
- Geolocalización satelital y mapas interactivos pesados.
- Notificaciones externas por SMS, WhatsApp o Email.
- Sensores no incluidos (ej. conductividad, cloro, oxígeno disuelto, etc.).
- Chatbot conversacional abierto de propósito general.
- Algoritmos predictivos de Machine Learning no solicitados.
- Microservicios distribuidos, colas Redis/Kafka innecesarias.
- Datos simulados ficticios presentados como mediciones reales.

---

## 3. Arquitectura del Sistema y Flujo de Datos

```
[ ESP32 + Sensores ]
  - pH (ADC)
  - Turbidez (ADC)
  - DS18B20 (OneWire)
       │
       ▼ (MicroPython HTTP Client - JSON payload con device_token)
[ Backend FastAPI ]
  ├── Layer 1: API / Routers (/api/v1/measurements, /devices, /alerts, /ai, /health)
  ├── Layer 2: Services (MeasurementService, VirtualSemaforoEngine, AIService)
  ├── Layer 3: Repositories (Data Access Layer - SQLAlchemy 2.0)
  └── Layer 4: Domain & Database (PostgreSQL / Supabase via Pooler/Direct)
       │
       ├───► [ Google Gemini API ] (Análisis descriptivo contextual backend-to-backend)
       │
       ▼ (REST API JSON Responses)
[ Frontend React + TypeScript ]
  ├── Presentation: Dashboard, Semáforo Virtual, Tarjetas, Histórico, Gráficos, Panel IA
  ├── State & Hooks: useMeasurements, useDeviceStatus, useAIAnalysis
  └── API Client / Services Layer
```

---

## 4. Hardware y Especificación de Sensores

| Sensor | Interfaz Eléctrica | Señal Cruda | Unidades Físicas | Manejo de Calibración |
|---|---|---|---|---|
| **pH (Módulo Analógico)** | Pin ADC ESP32 (ej. GPIO 34 / 35) | ADC raw (0-4095), Voltaje (V) | pH (0.0 - 14.0) | Requiere calibración en 2 puntos (pH 4.01 y 6.86/7.00). Si no hay calibración, se reporta crudo y se marca `calibration_status='PENDING'`. |
| **Turbidez (Sensor Óptico)** | Pin ADC ESP32 (ej. GPIO 32 / 33) | ADC raw (0-4095), Voltaje (V) | NTU | Sin curva empírica validada, reporta Voltaje y se marca `calibration_status='PENDING'`. No se inventan fórmulas de NTU. |
| **Temperatura (DS18B20)** | Bus OneWire (GPIO 4 / GPIO 2) + Resistencia Pull-up 4.7kΩ | Código digital 64-bit ROM | Grados Celsius (°C) | Protocolo digital con checksum. En caso de fallo o desconexión se reporta `null` y flag de error (NUNCA 0.0 °C). |

---

## 5. Modelo de Datos Relacional (PostgreSQL)

1. **`devices`**:
   - `id` (UUID / Integer PK), `code` (VARCHAR unique, ej. 'ESP32-NARVAL-01'), `name`, `status` ('ONLINE', 'OFFLINE', 'ERROR'), `api_key_hash`, `firmware_version`, `last_seen_at`, `created_at`.
2. **`measurements`**:
   - `id` (UUID / Integer PK), `device_id` (FK), `packet_id` (VARCHAR unique para deduplicación), `ph_raw`, `ph_voltage`, `ph_value`, `turbidity_raw`, `turbidity_voltage`, `turbidity_value`, `temperature_celsius`, `device_timestamp`, `received_at`, `quality_status` ('VALID', 'PARTIAL', 'INVALID'), `calibration_status` ('CALIBRATED', 'PENDING', 'UNAVAILABLE'), `validation_notes`.
3. **`reference_rules`**:
   - `id`, `parameter_name` ('ph', 'turbidity', 'temperature'), `source` ('Resolución 2115 de 2007', etc.), `min_value`, `max_value`, `unit`, `is_active`, `version`.
4. **`alerts`**:
   - `id`, `measurement_id` (FK), `parameter_name`, `observed_value`, `threshold_reference`, `severity` ('INFO', 'WARNING', 'CRITICAL'), `message`, `created_at`.
5. **`ai_analyses`**:
   - `id`, `measurement_id` (FK nullable), `query_scope` ('SINGLE', 'INTERVAL'), `model_used`, `analysis_text`, `summary`, `limitations_disclaimer`, `created_at`.
6. **`sensor_calibrations`**:
   - `id`, `sensor_type`, `calibration_date`, `parameters_json`, `notes`, `is_active`.

---

## 6. Reglas Deterministas del Semáforo Virtual

Basadas en la normativa colombiana de referencia técnica (Resolución 2115 de 2007):
- **pH:**
  - *Óptimo (Verde):* 6.5 a 9.0 (con sensor calibrado).
  - *Alerta (Amarillo):* 6.0 a 6.49 ó 9.01 a 9.5.
  - *Crítico (Rojo):* < 6.0 ó > 9.5.
  - *Pendiente (Gris/Azul):* Lectura cruda disponible pero sin calibrar (`PENDING`).
- **Turbidez:**
  - *Óptimo (Verde):* ≤ 2.0 NTU (con curva de calibración confirmada).
  - *Alerta (Amarillo):* 2.1 a 5.0 NTU.
  - *Crítico (Rojo):* > 5.0 NTU.
  - *Pendiente (Gris/Azul):* Sin curva calibrada (reporta voltaje crudo).
- **Temperatura:**
  - *Referencia ambiental/aceptable:* 10.0 °C a 30.0 °C (variable climática, no tiene límite directo de riesgo en potabilidad pero afecta cinéticas químicas y pH).
  - *Anómalo:* < 0 °C ó > 45 °C (posible fallo o condición extrema).
- **Semáforo Global:**
  - Verde sólo si **todos** los sensores calibrados están en rango óptimo.
  - Si falta calibración, el semáforo global indica "Datos Parciales / Calibración Pendiente" (Amarillo/Gris con etiqueta explicativa), nunca verde total engañoso.

---

## 7. Directrices de Integración de Gemini
- Ejecución exclusivamente en el backend mediante `google-genai`.
- Clave de API `GEMINI_API_KEY` almacenada en `.env` (nunca expuesta al frontend).
- Prompt del sistema estrictamente delimitado: describe variaciones, destaca alertas, contextualiza según rangos colombianos, pero **declara explícitamente que no reemplaza análisis de laboratorio ni certifica potabilidad**.

---

## 8. Matriz de Estado de Implementación

| Componente | Estado | Verificación |
|---|---|---|
| **Estructura Base Workspace** | Implementado | Configurado con capas limpias |
| **Entorno Virtual & Dependencias** | Implementado | Python 3.14 + FastAPI + SQLAlchemy 2 + psycopg + google-genai instalados |
| **Conexión Supabase (PostgreSQL)** | Verificado | Conectividad probada en puertos 5432 y 6543 |
| **Modelos SQLAlchemy 2 & Alembic** | En progreso | Diseñado según especificación maestra |
| **Capa de Servicios y Repositorios** | En progreso | Implementación de lógica determinista |
| **Endpoints FastAPI (v1)** | En progreso | Ingestión, consultas, semáforo, salud, IA |
| **Firmware MicroPython ESP32** | Diseñado | Código modular para sensores y Wi-Fi |
| **Frontend React + Vite** | En progreso | Arquitectura en capas para Semáforo Virtual |
| **Integración Gemini Backend** | En progreso | Servicio seguro con fallback |
