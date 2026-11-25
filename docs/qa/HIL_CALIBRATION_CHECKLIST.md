# Bitácora de Evidencias HIL y Calibración Metrológica — Narval

> **Entregable del Plan de Pruebas (`MVP_IEEE829_Narval.docx`):** Evidencias *Hardware-in-the-Loop* (HIL) y validación metrológica en laboratorio / campo.
> **Normativa de referencia:** Resolución 2115 de 2007 (pH `6.5 – 9.0`, turbidez `<= 2.0 NTU`). *Este protocolo valida el comportamiento técnico del instrumento y no sustituye ensayos de laboratorio acreditados para certificación de potabilidad.*

---

## 1. Configuración Física Verificada (ESP32 D1 R32 — Producción)

| Componente | Pin ESP32 | Protocolo / Acondicionamiento | Verificado |
| :--- | :---: | :--- | :---: |
| **Sensor Óptico de Turbidez** | `IO36` (`ADC1_0`) | Analógico `0 – 3.3 V`, ADC 12 bits (`ATTN_11DB`), divisor resistivo `10k / 20k` (`FACTOR_DIVISOR = 1.5`) | `[ ]` |
| **Módulo de pH (PH-4502C + BNC)** | `IO34` (`ADC1_6`) | Analógico `0 – 3.3 V`, ADC 12 bits (`ATTN_11DB`), masa común `GND` | `[ ]` |
| **Sonda Digital DS18B20** | `IO26` | Bus digital `1-Wire` con resistencia *pull-up* externa de `4.7 kΩ` entre `DATA` y `3.3 V` | `[ ]` |
| **Conectividad Red / Reloj** | Wi-Fi 2.4 GHz | Sincronización `ntptime` (`pool.ntp.org`) y cabeceras `X-Device-ID` / `X-Device-Secret` | `[ ]` |

---

## 2. Protocolo de Calibración en 2 Puntos (pH y Turbidez)

### 2.1. Calibración de pH (Buffers Estándar a 25 °C)

1. Enjuagar la sonda BNC con agua destilada y secar suavemente sin frotar la membrana de vidrio.
2. Sumergir en **Buffer pH `7.00`** y esperar estabilización (`>= 60 s`). Registrar `mediana_raw`, `voltaje_pin` y `voltaje_sensor` desde el monitor serial:
   - `V_buffer_7.00` = `[PENDIENTE DE MEDICIÓN EN LABORATORIO]` V
3. Enjuagar con agua destilada, sumergir en **Buffer pH `4.01`** y esperar estabilización (`>= 60 s`):
   - `V_buffer_4.01` = `[PENDIENTE DE MEDICIÓN EN LABORATORIO]` V
4. Calcular e ingresar en `firmware/config.py`:
   - `VOLTAJE_BASE_PH` = `V_buffer_7.00`
   - `PENDIENTE_PH` = `(4.01 - 7.00) / (V_buffer_4.01 - V_buffer_7.00)`
5. Verificación cruzada: volver a medir en buffer `7.00` y confirmar error absoluto `<= ±0.15 pH`.

### 2.2. Calibración de Turbidez (Referencia Agua Destilada y Formazina)

1. Sumergir la sonda óptica en **agua destilada (`0 NTU`)** evitando burbujas o luz ambiental directa.
2. Registrar el voltaje estabilizado como `VOLTAJE_BASE_AGUA` en `firmware/config.py`:
   - `VOLTAJE_BASE_AGUA` = `[PENDIENTE DE MEDICIÓN EN LABORATORIO]` V
3. Validar respuesta ascendente en patrones conocidos de formazina (`2 NTU`, `5 NTU`, `> 10 NTU`) registrando la tabla de contraste:

| Patrón Certificado (NTU) | Mediana ADC (`raw`) | Voltaje Sensor (V) | Lectura Firmware (NTU) | Color Semáforo Esperado | Resultado |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `0.0 NTU` (Agua destilada) | `[Pendiente]` | `[Pendiente]` | `[Pendiente]` | `GREEN` | `[ ]` |
| `2.0 NTU` (Límite óptimo) | `[Pendiente]` | `[Pendiente]` | `[Pendiente]` | `GREEN` | `[ ]` |
| `5.0 NTU` (Límite alerta) | `[Pendiente]` | `[Pendiente]` | `[Pendiente]` | `YELLOW` | `[ ]` |
| `> 5.0 NTU` (Crítico) | `[Pendiente]` | `[Pendiente]` | `[Pendiente]` | `RED` | `[ ]` |

---

## 3. Lista de Verificación de Pruebas Físicas (HIL)

| ID Prueba HIL | Escenario Físico en Banco | Evidencia Esperada en Monitor Serial y Backend | Estado | Ruta de Captura / Log |
| :--- | :--- | :--- | :---: | :--- |
| **HIL-01** | Arranque en frío con Wi-Fi 2.4 GHz activo | `boot.py` conecta, imprime IP y sincroniza reloj UTC (`pool.ntp.org`). | `[ ] Pendiente` | `docs/qa/evidencias/hil_01_boot.txt` |
| **HIL-02** | Ingesta normal hacia FastAPI (`POST /api/v1/measurements`) | Consola muestra `Entregado al Backend (HTTP 201)` y registro aparece en tablero web. | `[ ] Pendiente` | `docs/qa/evidencias/hil_02_ingesta.png` |
| **HIL-03** | Desconexión física de sonda DS18B20 (`IO26`) | Firmware marca `TEMP_SENSOR_DISCONNECTED` y `quality_status="SENSOR_ERROR"`; valores numéricos se enmascaran a `null` (nunca `0.0 °C`) y Gemini bloquea con `HTTP 400 SENSORS_NOT_READY`. | `[ ] Pendiente` | `docs/qa/evidencias/hil_03_ds18b20.png` |
| **HIL-04** | Desconexión de sonda BNC de pH (`IO34`) o turbidez (`IO36`) | Firmware detecta saturación (`>= 4090`) o caída (`<= 5`), emite bandera física y bloquea consumo de cuota Gemini. | `[ ] Pendiente` | `docs/qa/evidencias/hil_04_bnc.png` |
| **HIL-05** | Corte temporal de Wi-Fi (`30 s`) y reconexión | Lecturas se almacenan en `cola_pendientes` (FIFO hasta `50` paquetes) y se vacían en orden al volver la red (`Recuperado de cola Seq #...`). | `[ ] Pendiente` | `docs/qa/evidencias/hil_05_cola_fifo.txt` |

---

## 4. Registro de Responsables de Ejecución en Laboratorio

| Campo | Valor |
| :--- | :--- |
| **Fecha de ejecución en laboratorio** | `[PENDIENTE DE EJECUCIÓN FÍSICA]` |
| **Responsable Hardware / IoT** | `[PENDIENTE DE CONFIRMACIÓN]` |
| **Responsable QA** | Juan Chavarria Restrepo |
| **Observaciones técnicas** | `[Completar al finalizar las pruebas físicas con soluciones buffer y formazina]` |
