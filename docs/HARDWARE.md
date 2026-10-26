# HARDWARE Y FIRMWARE ESP32 — PROYECTO NARVAL

## 1. Componentes Físicos y Especificación Eléctrica

| Módulo / Sensor | Función | Pines ESP32 Sugeridos | Protocolo / Nivel | Observaciones |
|---|---|---|---|---|
| **ESP32 DevKit V1** | Microcontrolador central | N/A | Wi-Fi 802.11 b/g/n, MicroPython | Procesamiento de lecturas, empaque JSON y envío HTTP. |
| **Módulo Sensor de pH (ej. PH-4502C)** | Medición de acidez/alcalinidad | GPIO 35 (ADC1_CH7) | Analógico 0-3.3V (mediante divisor si el módulo opera a 5V) | Requiere masa común (GND). Medir siempre voltaje antes de convertir. |
| **Sensor de Turbidez (ej. Módulo óptico con placa acondicionadora)** | Medición de partículas en suspensión | GPIO 34 (ADC1_CH6) | Analógico 0-3.3V / 4.5V | Mantener switch en 'A' (Analógico). La conversión a NTU requiere calibración con solución de formazina. |
| **Sensor de Temperatura DS18B20** | Temperatura del agua | GPIO 4 | OneWire (Digital) | Requiere resistencia pull-up de 4.7 kΩ entre DATA y VCC (3.3V). No conectar invertido. |

---

## 2. Precauciones y Buenas Prácticas de Hardware
1. **Pines ADC de entrada:**
   - En el ESP32, usar exclusivamente **ADC1** (GPIOs 32, 33, 34, 35, 36, 39) cuando Wi-Fi esté habilitado. Los pines de ADC2 están compartidos internamente con el subsistema Wi-Fi y generan lecturas corruptas cuando la radio está encendida.
2. **Alimentación y Tierra Común:**
   - Todos los sensores y el ESP32 deben compartir una única referencia de tierra (GND).
   - Los módulos de pH y turbidez que se alimentan a 5V entregan salidas analógicas que pueden superar los 3.3V tolerados por el ADC del ESP32. Se debe calibrar la ganancia/atenuación o usar divisor resistivo adecuado.
3. **Manejo de Errores DS18B20:**
   - El sensor responde con `85.0 °C` si se lee antes de que termine la conversión o `-127.0 °C` si el cable está roto/desconectado. El firmware filtra estos casos y emite `null` con bandera de error, **nunca un cero ficticio**.
