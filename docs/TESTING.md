# PLAN Y REPORTE DE PRUEBAS — PROYECTO NARVAL

## 1. Alcance de las Pruebas
Se implementó y ejecutó una suite automatizada completa de 17 pruebas unitarias e integración en el backend con `pytest`, así como pruebas de compilación estricta en el frontend con TypeScript y Vite.

---

## 2. Resumen de Ejecución de Pruebas

### 2.1. Backend (FastAPI + SQLAlchemy 2 + Supabase)
- **Herramienta:** `pytest 9.1.1` sobre `Python 3.14.3`
- **Resultados:** `17 passed` (100% de éxito).
- **Módulos verificados:**
  1. `tests/test_health.py`:
     - Verificación de disponibilidad de FastAPI (`/health` y `/api/v1/health`).
     - Verificación de conexión en vivo con PostgreSQL 17.11 en Supabase (`status: connected`).
  2. `tests/test_measurements.py`:
     - Ingesta rechazada sin token (`401 Unauthorized`).
     - Ingesta rechazada con token falso (`401 Unauthorized`).
     - Ingesta exitosa con token legítimo (`201 Created`).
     - Prevención de duplicados (`409 Conflict` cuando se retransmite el mismo `packet_id`).
     - Consulta de última medición persistida y cálculo del Semáforo Virtual.
     - Consulta paginada del historial de mediciones.
  3. `tests/test_semaforo.py`:
     - pH en rango 6.5 a 9.0 $\rightarrow$ `GREEN` (Óptimo, Res. 2115/2007).
     - pH en 6.0 a 6.49 $\rightarrow$ `YELLOW` (Alerta).
     - pH < 6.0 $\rightarrow$ `RED` (Crítico).
     - pH sin calibrar $\rightarrow$ `GRAY` (Calibración Pendiente).
     - Turbidez $\le$ 2.0 NTU $\rightarrow$ `GREEN` (Óptimo).
     - Turbidez entre 2.0 y 5.0 NTU $\rightarrow$ `YELLOW` (Alerta).
     - Turbidez > 5.0 NTU $\rightarrow$ `RED` (Crítico).
     - Turbidez sin calibrar $\rightarrow$ `GRAY` (Calibración Pendiente).
     - Temperatura normal 10 - 30 °C $\rightarrow$ `GREEN` (Aceptable).
     - Temperatura atípica > 30 °C $\rightarrow$ `YELLOW` (Advertencia).
     - Temperatura extrema > 40 °C $\rightarrow$ `RED` (Crítico).
     - Fallo en sonda OneWire $\rightarrow$ `GRAY` (Error de Sensor, sin generar ceros ficticios).
  4. `tests/test_ai.py`:
     - Invocación de `POST /api/v1/ai/analyze`.
     - Estructura DTO con `model_used`, `summary`, `analysis_text` y `limitations_disclaimer`.

### 2.2. Frontend (React 19 + TypeScript + Vite)
- **Herramienta:** `tsc -b && vite build`
- **Resultados:** Compilación limpia sin errores de tipos ni advertencias bloqueantes.

---

## 3. Instrucciones para Re-ejecutar las Pruebas

### Pruebas del Backend
```bash
cd narval-backend
.\.venv\Scripts\python -m pytest -v
```

### Pruebas del Frontend
```bash
cd narval-frontend
npm run build
```
