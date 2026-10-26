# CONTRATO DE API REST — PROYECTO NARVAL

**Versión:** 1.0.0  
**Prefijo Base:** `/api/v1`  
**Formato de Intercambio:** `application/json`

---

## 1. Autenticación y Seguridad
- **Ingesta IoT (`POST /api/v1/measurements`):** Header `X-Device-Token: <token_secreto_dispositivo>`.
- **Consultas Web (Lectura):** Acceso directo para el Semáforo Virtual (sin login en este MVP según alcance de la sección 3).
- **IA (`POST /api/v1/ai/analyze`):** Solicita análisis de mediciones ya persistidas.

---

## 2. Endpoints

### 2.1. Ingesta de Mediciones
- **Ruta:** `POST /api/v1/measurements`
- **Headers:** `X-Device-Token: <token>`
- **Request Body:**
```json
{
  "device_code": "ESP32-NARVAL-001",
  "packet_id": "pkt-20261025-0001",
  "device_timestamp": "2026-10-25T20:30:00Z",
  "ph": {
    "raw": 2450,
    "voltage": 1.98,
    "value": 7.15,
    "is_calibrated": true
  },
  "turbidity": {
    "raw": 1820,
    "voltage": 2.45,
    "value": 1.80,
    "is_calibrated": false
  },
  "temperature": {
    "celsius": 19.5,
    "is_valid": true
  }
}
```
- **Responses:**
  - `201 Created`: Medición validada y persistida.
  - `400 Bad Request`: Payload con formato inválido o valores físicamente imposibles.
  - `401 Unauthorized`: Token de dispositivo inválido o no suministrado.
  - `409 Conflict`: Paquete duplicado (`packet_id` ya registrado).

---

### 2.2. Última Medición y Semáforo Virtual
- **Ruta:** `GET /api/v1/measurements/latest`
- **Response `200 OK`:**
```json
{
  "measurement": {
    "id": 105,
    "device_id": 1,
    "device_code": "ESP32-NARVAL-001",
    "received_at": "2026-10-25T20:30:02Z",
    "ph_raw": 2450,
    "ph_voltage": 1.98,
    "ph_value": 7.15,
    "turbidity_raw": 1820,
    "turbidity_voltage": 2.45,
    "turbidity_value": null,
    "temperature_celsius": 19.5,
    "quality_status": "PARTIAL",
    "calibration_status": "PENDING"
  },
  "semaforo": {
    "global_status": "YELLOW",
    "label": "Parcial / Calibración Pendiente",
    "ph_status": "GREEN",
    "turbidity_status": "GRAY",
    "temperature_status": "GREEN",
    "notes": "Turbidez sin curva de calibración confirmada. Se reporta voltaje."
  }
}
```

---

### 2.3. Historial de Mediciones
- **Ruta:** `GET /api/v1/measurements`
- **Query Params:**
  - `limit`: int (default: 50, max: 200)
  - `offset`: int (default: 0)
  - `start_date`: ISO datetime opcional
  - `end_date`: ISO datetime opcional
  - `device_code`: string opcional
- **Response `200 OK`:**
```json
{
  "total": 150,
  "limit": 50,
  "offset": 0,
  "items": [ ... ]
}
```

---

### 2.4. Detalle de una Medición
- **Ruta:** `GET /api/v1/measurements/{id}`
- **Response:** Detalle completo, alertas generadas y análisis asociados.

---

### 2.5. Estado de Comunicación de Dispositivos
- **Ruta:** `GET /api/v1/devices/status`
- **Response `200 OK`:**
```json
[
  {
    "code": "ESP32-NARVAL-001",
    "name": "Estación Rural Quebrada Alta",
    "status": "ONLINE",
    "last_seen_at": "2026-10-25T20:30:02Z",
    "seconds_since_last_ping": 15,
    "firmware_version": "1.0.0-mp"
  }
]
```

---

### 2.6. Alertas
- **Ruta:** `GET /api/v1/alerts`
- **Query Params:** `severity`, `limit`, `offset`
- **Response `200 OK`:** Lista de alertas activas e históricas.

---

### 2.7. Análisis Descriptivo con Gemini
- **Ruta:** `POST /api/v1/ai/analyze`
- **Request Body:**
```json
{
  "measurement_id": 105,
  "include_recent_history_count": 5
}
```
- **Response `200 OK`:**
```json
{
  "analysis_id": 12,
  "measurement_id": 105,
  "model_used": "gemini-2.5-flash",
  "created_at": "2026-10-25T20:30:05Z",
  "summary": "Parámetros de pH y temperatura estables en rangos óptimos. Turbidez pendiente de curva de calibración.",
  "analysis_text": "Análisis contextual detallado basado en datos reales...",
  "disclaimer": "Este análisis es de carácter técnico-descriptivo y no certifica potabilidad del agua ni reemplaza pruebas de laboratorio acreditadas según la Resolución 2115 de 2007."
}
```

---

### 2.8. Chequeo de Salud (Health Check)
- **Ruta:** `GET /health`
- **Response `200 OK`:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "gemini_api": "configured"
}
```
