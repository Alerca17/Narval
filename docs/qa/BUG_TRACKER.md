# Registro de Defectos / Bug Tracker — Proyecto Narval

> **Trazabilidad:** Asociado directamente a los casos de prueba de `docs/qa/TEST_CASES.md`, los riesgos `R-01`–`R-08` de `MVP_IEEE829_Narval.docx` y el archivo tabular exportable [bug_tracker.csv](./bug_tracker.csv).
> **Fecha de actualización:** `24/11/2026`.

---

## 1. Matriz de Defectos y Estado de Verificación

| ID | Severidad | Prioridad | Módulo / Caso | Ubicación en Código | Descripción del Defecto | Estado Actual | Verificación en Regresión |
| :---: | :---: | :---: | :--- | :--- | :--- | :---: | :--- |
| **BUG-001** | Media | `P2` | M7 Frontend (`CP-M7-03`) | `narval-frontend/src/App.tsx:231` | Comparación sensible a mayúsculas (`parameter_name === 'pH'`) mostraba unidad `°C` en alertas de pH (`"ph"`). | **Cerrado (Verificado)** | Normalizado con `.toLowerCase() === 'ph'`; verificado por `src/__tests__/App.test.tsx`. |
| **BUG-002** | Media | `P3` | M7 Frontend (`CP-M7-04`) | `narval-frontend/src/presentation/ChartsView.tsx:43,150-159` | Escala Y fija (`10.0 – 35.0 °C`) recortaba lecturas válidas en alerta/crítico (`5.0 – 9.9 °C` y `> 35.0 °C`). | **Cerrado (Verificado)** | Rango ampliado a `0.0 – 45.0 °C` con acotación SVG segura; verificado por `ChartsView.test.tsx`. |
| **BUG-003** | Alta | `P1` | M3 / M4 Backend (`CP-M3-04`) | `narval-backend/app/services/semaforo_service.py:208-209` | Acoplamiento global de `calibration_status` marcaba el pH sí calibrado como `GRAY` si la turbidez estaba `PENDING`. | **Cerrado (Verificado)** | Desacoplada calibración por parámetro (`ph_value is not None`, `turbidity_value is not None`); verificado en `test_measurements.py` y `test_semaforo.py`. |
| **BUG-004** | Media | `P2` | M5 IA / M1 Firmware (`CP-M5-01`) | `narval-backend/app/services/ai_service.py:15-20,105` | Mensaje `action_required` citaba puerto fijo `COM7` y faltaba referencia explícita al pin validado de pH (`GPIO 34`) del firmware `be9c0c2` (`ESP32 D1 R32`: `GPIO 34` pH, `GPIO 36` turbidez, `GPIO 26` DS18B20). | **Cerrado (Verificado)** | Mensajes alineados con el pinout real de `firmware/config.example.py` (`be9c0c2`); verificado por `test_ai.py`. |
| **BUG-005** | Alta | `P1` | M2 Seguridad (`CP-M2-03`) | `narval-backend/app/core/security_middleware.py:47-72` | `int(content_length)` sin `try/except` lanzaba `ValueError` ante cabeceras malformadas y omitía límite `64 KB` sin `Content-Length` (*chunked*). | **Cerrado (Verificado)** | Validación segura con retorno `HTTP 400` y control de longitud de cuerpo sin cabecera (`HTTP 413`); verificado por `test_security.py`. |
| **BUG-006** | Alta | `P1` | M1 Firmware (`CP-M1-01/05`) | `firmware/main.py:66-68,188-208` | Falta de guarda `muestras <= 0` en `leer_adc_con_calidad`, cierre `res.close()` fuera de `finally` y bucle infinito sin guarda `__name__ == "__main__"` (nota: persistencia `seq.txt` y NTP ya incorporados en commit `be9c0c2`). | **Cerrado (Verificado)** | Guarda `ValueError`, cierre en `finally` y ciclo extraído en `ejecutar_ciclo()`; verificado por `firmware/tests/test_firmware.py`. |
| **BUG-007** | Media | `P2` | M5 / QA Backend (`CP-M5-01`) | `narval-backend/tests/conftest.py`, `tests/test_ai.py` | Falso positivo condicional (`if response.status_code == 400:`) en `test_ai.py` y ausencia de aislamiento de BD en `conftest.py`. | **Cerrado (Verificado)** | `conftest.py` aislado en SQLite en memoria con limpieza por prueba y aserción obligatoria `assert response.status_code == 400` en `test_ai.py`. |
| **BUG-008** | Baja | `P3` | M6 / M7 Config y Docs (`CP-M6 / CP-M7`) | `app/core/config.py:17`, `docs/TESTING.md`, `src/presentation/*.tsx` | `GEMINI_MODEL` por defecto (`gemini-3.5-flash-lite`) difería de `.env.example` (`gemini-2.5-flash`), `docs/TESTING.md` estaba desactualizado y persisten 6 archivos UI legados sin montar. | **Parcialmente Cerrado** | `GEMINI_MODEL` unificado a `gemini-2.5-flash` y `docs/TESTING.md` actualizado; limpieza de componentes UI legados queda diferida (`P4`, fuera de alcance MVP). |
| **BUG-009** | Media | `P2` | M2 / M3 Seguridad (`CP-M2-02`) | `app/api/deps.py:55-71` vs `app/services/device_service.py:19-26` | Autenticación individual por dispositivo (`Device.api_key_hash`) no está conectada al endpoint HTTP de ingesta (usa secreto compartido global `DEVICE_INGESTION_SECRET`). | **Abierto (Mitigado / Diferido)** | Documentado explícitamente en *Elementos a No Probar* del Plan; `DeviceService.authenticate_device` probado unitariamente en `test_devices.py`. |

---

## 2. Convención Operativa en GitHub Issues

Para el seguimiento continuo en `https://github.com/Alerca17/Narval/issues`:
- **Severidad:** `severity:critical`, `severity:high`, `severity:medium`, `severity:low`.
- **Estado:** `status:triage`, `status:in-progress`, `status:qa-verified`.
- **Módulo:** `module:firmware`, `module:backend`, `module:database`, `module:ai-gemini`, `module:frontend`, `type:bug`.
