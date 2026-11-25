# Informe Final de Resultados de Pruebas y Acta de Aceptación (UAT) — Narval

> **Proyecto:** Narval — Monitoreo de Calidad del Agua para Acueductos Veredales
> **Institución:** Politécnico Colombiano Jaime Isaza Cadavid — Ingeniería Informática (`ING01207 Proyecto Integrador`)
> **Plan de Pruebas Base:** `MVP_IEEE829_Narval.docx`
> **Fecha de emisión de resultados:** `24/11/2026`

---

## 1. Resumen Ejecutivo de Ejecución Automatizada (Resultados Reales)

| Subsistema | Herramienta / Entorno | Pruebas Ejecutadas | Aprobadas | Fallidas | Cobertura Obtenida | Umbral del Plan | Cumplimiento |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Backend API y Servicios** | `pytest 9.2.0` + `pytest-cov 7.1.0` (`Python 3.14.7`, BD SQLite aislada en memoria) | **63** | **63** | **0** | **96%** total (`servicios 87%–100%`, `seguridad 94%–100%`, `API 100%`, `repos 86%–100%`) | Servicios/Seg. `>= 85%`; API/Repos `>= 75%` | **CUMPLE** |
| **Firmware IoT ESP32** | `pytest 9.2.0` + `pytest-cov 7.1.0` (mocks MicroPython `machine`, `onewire`, `ds18x20`, `network`, `urequests`) | **8** | **8** | **0** | **82%** total (`main.py 84%`, `boot.py 69%`) | Drivers/lógica `>= 70%` | **CUMPLE** |
| **Frontend Semáforo Virtual** | `Vitest 4.1.12` + `@vitest/coverage-v8` + React Testing Library (`Node v26.12.0`) | **15** | **15** | **0** | **86.3%** sentencias / **88.61%** líneas (`hooks 90%`, `services 87.75%`, `presentation 94.11%`, `App.tsx 77.27%`) | Hooks/Servicios `>= 70%` | **CUMPLE** |
| **Análisis Estático y Build Frontend** | `oxlint 1.88+`, `tsc -b`, `vite build` (`vite 8.3.5`) | Verificación completa | **OK** | **0 errores** | `0` errores (`5` advertencias preexistentes en código legado/hooks); bundle `dist/` generado en `1.83 s` | `0` errores de compilación/lint | **CUMPLE** |
| **TOTAL AUTOMATIZADO** | **3 suites + pipeline CI (`.github/workflows/ci.yml`)** | **86** | **86 (100%)** | **0** | **82% – 96% según capa** | `>= 95%` aprobación global | **CUMPLE** |

### Artefactos de Evidencia Generados en el Repositorio

- Reportes JUnit y Cobertura XML (Backend): `docs/qa/reports/backend-junit.xml`, `docs/qa/reports/backend-coverage.xml`
- Reportes JUnit y Cobertura XML (Firmware): `docs/qa/reports/firmware-junit.xml`, `docs/qa/reports/firmware-coverage.xml`
- Reporte de Cobertura JSON (Frontend): `docs/qa/reports/frontend-coverage-summary.json`
- Especificación de Casos de Prueba: `docs/qa/TEST_CASES.md`
- Registro de Defectos: `docs/qa/BUG_TRACKER.md` y `docs/qa/bug_tracker.csv`
- Bitácora HIL y Calibración: `docs/qa/HIL_CALIBRATION_CHECKLIST.md`
- Pipeline de Integración Continua: `.github/workflows/ci.yml`
- Especificación E2E Playwright: `narval-frontend/playwright.config.ts` y `narval-frontend/e2e/narval.spec.ts`

---

## 2. Balance de Defectos (`BUG-001` a `BUG-009`)

- **Defectos Críticos / Bloqueantes abiertos:** `0` (**Cumple criterio de salida**).
- **Defectos Altos (`P1`) corregidos y verificados en regresión:** `3 / 3` (`BUG-003`, `BUG-005`, `BUG-006`).
- **Defectos Medios corregidos y verificados en regresión:** `4 / 5` (`BUG-001`, `BUG-002`, `BUG-004`, `BUG-007`).
- **Defectos diferidos / excluidos del MVP con mitigación documentada:** `1` Medio (`BUG-009`: autenticación por dispositivo individual `api_key_hash`, fuera de alcance MVP) y `1` Bajo parcial (`BUG-008`: limpieza de 6 componentes UI legados no montados).

---

## 3. Actividades Pendientes de Entorno Físico / Externo

Las siguientes verificaciones requieren infraestructura externa o hardware de laboratorio que no forma parte de la ejecución automatizada local:

1. **Pruebas Físicas HIL y Calibración Metrológica:** Ejecución en banco con ESP32 D1 R32, soluciones buffer `pH 4.01 / 7.00` y patrones de formazina según `docs/qa/HIL_CALIBRATION_CHECKLIST.md`.
2. **Migración DDL en PostgreSQL / Supabase real:** Ejecución de `alembic upgrade head` apuntando a `DIRECT_URL` (`:5432`) y validación de pooler transaccional (`:6543`).
3. **Ejecución E2E con navegadores reales (Playwright):** Instalar binarios (`npx playwright install`) y ejecutar `npm run test:e2e` contra el servidor local activo.
4. **Firma del Acta de Aceptación de Usuario (UAT)** tras demostración piloto.

---

## 4. Acta de Aceptación de Usuario (UAT)

> **Alcance Normativo:** El firmante declara comprender que Narval monitorea de manera técnica e informativa pH, turbidez y temperatura tomando como referencia la Resolución 2115 de 2007, y **no constituye una certificación oficial de potabilidad ni reemplaza análisis microbiológicos de laboratorio acreditados**.

| Criterio de Aceptación UAT | Cumple | Observaciones |
| :--- | :---: | :--- |
| Legibilidad del Semáforo Virtual y tarjetas en móvil y escritorio | `[ ] Sí / [ ] No` | |
| Claridad de alertas críticas/preventivas y unidades (`pH`, `NTU`, `°C`) | `[ ] Sí / [ ] No` | |
| Visualización del aviso normativo de no certificación de potabilidad en informes IA | `[ ] Sí / [ ] No` | |
| Bloqueo comprensible del análisis IA ante desconexión de sensores físicos | `[ ] Sí / [ ] No` | |

| Nombre y Apellido | Rol | Organización | Fecha | Firma |
| :--- | :--- | :--- | :---: | :---: |
| Alejandro Correa Arias | Líder Técnico / Arquitecto de Software | Politécnico Jaime Isaza Cadavid | `[Pendiente]` | |
| Juan Chavarria Restrepo | Ingeniero de QA | Politécnico Jaime Isaza Cadavid | `[Pendiente]` | |
| Juan Cardona | Representante de Equipo | Politécnico Jaime Isaza Cadavid | `[Pendiente]` | |
| `[PENDIENTE DE CONFIRMACIÓN]` | Operador Piloto / Cliente | Acueducto Veredal Piloto | `[Pendiente]` | |
