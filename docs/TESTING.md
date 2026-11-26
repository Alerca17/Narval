# Plan y Reporte de Pruebas — Narval

Este documento consolida la verificación técnica automatizada del proyecto Narval (Backend FastAPI, Firmware MicroPython ESP32 y Frontend React/TypeScript) alineada con el Plan de Pruebas `MVP_IEEE829_Narval.docx`.

## 1. Resumen de Última Ejecución Verificada (`25/11/2026`)

| Subsistema | Suite / Herramienta | Resultado | Cobertura Real | Reportes Generados |
| :--- | :--- | :---: | :---: | :--- |
| **Backend (`narval-backend/`)** | `pytest 9.1.1` + `pytest-cov 7.1.0` (BD SQLite aislada en memoria) | **63 aprobadas / 0 fallidas** (`3.29 s`) | **93%** (`95.86%` líneas) | `docs/qa/reports/backend-junit.xml`, `backend-coverage.xml` |
| **Firmware (`firmware/`)** | `pytest 9.1.1` + `pytest-cov 7.1.0` (mocks MicroPython + resiliencia Wi-Fi) | **14 aprobadas / 0 fallidas** (`1.83 s`) | **82.55% `main.py`** (`77.78%` total) | `docs/qa/reports/firmware-junit.xml`, `firmware-coverage.xml` |
| **Frontend (`narval-frontend/`)** | `Vitest 4.1.12` + RTL + `@vitest/coverage-v8` | **16 aprobadas / 0 fallidas** (`5.10 s`) | **89.83%** líneas (`100%` en `AIPanel.tsx`) | `docs/qa/reports/frontend-coverage-summary.json` |
| **Análisis Estático y Build** | `oxlint` + `tsc -b && vite build` | **0 errores** (`0.87 s` build) | N/A | `narval-frontend/dist/` |
| **HIL en Vivo (`ESP32 D1 R32 COM6`)** | `mpremote` + monitor serie (`INTERVALO_SEGUNDOS = 45`) | **20+ ciclos consecutivos `HTTP 201`** | **0 caídas Wi-Fi** | `docs/qa/evidencias/logs/hil_serial_raw.txt`, `api_live_measurements.json` |

## 2. Escenarios Cubiertos por Subsistema

### 2.1. Backend (`narval-backend/tests/`)
- **Seguridad y Middleware (`test_security.py`):** Hash SHA-256, comparación en tiempo constante, encabezado alternativo `X-Device-Secret`, cabeceras OWASP, límite `64 KB` (`413`), cabecera `Content-Length` malformada (`400`), *rate limiting* (`429` + `Retry-After`) y normalización de configuración.
- **Ingesta, Adaptador e Idempotencia (`test_measurements.py`):** Autenticación `401`, ingesta canónica `201`, deduplicación `409`, adaptador de payload del firmware de producción `be9c0c2`, rechazo Pydantic `422`, calibración mixta (`pH` calibrado + turbidez `PENDING`), `/latest` vacío/poblado, paginación, filtros y `404`.
- **Semáforo Virtual (`test_semaforo.py`):** Fronteras exactas de la Resolución 2115 de 2007 (`pH`: `5.99`, `6.0`, `6.49`, `6.5`, `9.0`, `9.01`, `9.5`, `9.51`; `turbidez`: `0.0`, `2.0`, `2.01`, `5.0`, `5.01` NTU; `temperatura`: `4.9`, `5.0`, `9.9`, `10.0`, `30.0`, `30.1`, `38.0`, `38.1 °C` y `None`) y precedencia global.
- **Alertas y Dispositivos (`test_alerts.py`, `test_devices.py`):** Creación automática de `CRITICAL`/`WARNING`, ausencia de alerta en `GRAY`/`GREEN`, filtros de consulta, frontera de latido `300 s` (`ONLINE`/`OFFLINE`) y `DeviceService.authenticate_device`.
- **Integración Google Gemini y Resiliencia (`test_ai.py`):** Bloqueo `400 SENSORS_NOT_READY` (con pines `GPIO 26`, `GPIO 34`, `GPIO 36`), respuesta `404` en BD vacía, mock de `google-genai` con aviso normativo y respaldo determinista local (`local-deterministic-engine`).
- **Salud y Sembrado (`test_health.py`):** `/health` y `/api/v1/health` saludables y degradados, e idempotencia de `app/core/seed.py`.

### 2.2. Firmware ESP32 (`firmware/tests/`)
- Filtrado estadístico por mediana de 11 muestras ADC y guarda `muestras <= 0`.
- Conversión física acotada de pH (`[0.0, 14.0]`) y turbidez (`[0.0, 3000.0]` NTU).
- Filtrado de fallos DS18B20 (`85.0 °C`, `-127.0 °C`, desconexión ROM, excepciones CRC).
- Motor de validación local (`VALID`, `SENSOR_ERROR`, `INVALID`, `SUSPECT`), regla atómica "Todo o Nada", persistencia de secuencia `seq.txt`, reintentos HTTP (`201`/`409`/`500`) y cola FIFO anti-pérdida.

### 2.3. Frontend (`narval-frontend/`)
- `ApiService` (`src/services/__tests__/api.test.ts`) y hooks `useMeasurements`, `useDeviceStatus`, `useAIAnalysis` (`src/hooks/__tests__/hooks.test.tsx`).
- Componentes `ChartsView` (rango térmico `0 – 45 °C` sin recorte SVG), `AIPanel` (`SENSORS_NOT_READY` y aviso Res. 2115) e integración de `App` (regresión de unidad `pH` en detalle de alerta y banner `Error de conexión`).
- Especificación E2E con Playwright lista en `narval-frontend/e2e/narval.spec.ts`.

## 3. Comandos de Ejecución Local

### Backend
```bash
cd narval-backend
.\.venv\Scripts\pytest.exe -v --cov=app --cov-report=term-missing
```

### Firmware (con mocks MicroPython)
```bash
cd firmware
..\narval-backend\.venv\Scripts\pytest.exe -v --cov=main --cov=boot --cov-report=term-missing
```

### Frontend
```bash
cd narval-frontend
npm run lint
npm run build
npm run test:coverage
```

## 4. Documentación Complementaria de QA

- [Especificación de Casos de Prueba (IEEE 829)](./qa/TEST_CASES.md)
- [Registro de Defectos / Bug Tracker](./qa/BUG_TRACKER.md) y [bug_tracker.csv](./qa/bug_tracker.csv)
- [Bitácora de Evidencias HIL y Calibración Metrológica](./qa/HIL_CALIBRATION_CHECKLIST.md)
- [Informe Final de Resultados y Acta UAT](./qa/FINAL_TEST_REPORT_AND_UAT.md)
- Pipeline CI automático: `.github/workflows/ci.yml`
