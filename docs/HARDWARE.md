# HARDWARE Y FIRMWARE ESP32 — PROYECTO NARVAL

## 1. Componentes Físicos y Especificación Eléctrica (Placa ESP32 D1 R32)

| Módulo / Sensor | Función | Pin Validado ESP32 | Protocolo / Nivel | Observaciones |
|---|---|---|---|---|
| **ESP32 D1 R32 (WROOM)** | Microcontrolador central | N/A | Wi-Fi 802.11 b/g/n, MicroPython | Procesamiento en el borde, filtrado por mediana, empaque JSON y envío HTTP. |
| **Sensor de Turbidez Óptico** | Medición de partículas en suspensión | **IO36 (ADC1_0)** | Analógico 0-3.3V | Con divisor resistivo 10k/20k (factor divisor 1.5). Calibrado con voltaje base de agua limpia. |
| **Sensor de pH (PH-4502C)** | Medición de acidez/alcalinidad | **IO34 (ADC1_6)** | Analógico 0-3.3V | Con divisor resistivo 10k/20k (factor divisor 1.5). Calibrado con pendiente y voltaje base. |
| **Sensor de Temperatura DS18B20** | Temperatura del agua | **IO26** | Digital 1-Wire | Resistencia pull-up de 4.7 kΩ a 3.3V. |

---

## 2. Precauciones y Buenas Prácticas de Hardware
1. **Pines ADC de entrada:**
   - En el ESP32, se usa exclusivamente **ADC1** (IO36 y IO34) para garantizar convivencia con la radio Wi-Fi activa sin corrupción de lectura.
2. **Divisor de Tensión y Referencia de Tierra:**
   - Sensores alimentados a 5V utilizan divisor de tensión 10kΩ / 20kΩ para entregar un máximo de 3.3V al ADC.
   - Todos los sensores y el ESP32 comparten la misma masa común (GND).
3. **Manejo de Errores y Filtrado Estadístico:**
   - Se toman 11 muestras por canal para calcular la mediana y descartar ruido transitorio.
   - Si la sonda DS18B20 responde con `85.0 °C` (lectura apresurada) o `-127.0 °C` (cable desconectado), el firmware emite bandera de error y no valores cero engañosos.
