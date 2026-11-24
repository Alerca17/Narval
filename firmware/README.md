# Firmware MicroPython para ESP32 — Narval (Producción)

Firmware de adquisición, filtrado estadístico y transmisión para microcontrolador **ESP32 (Placa D1 R32)** en acueductos rurales.

## Estructura

```
firmware/
├── boot.py              # Inicialización de hardware, conexión Wi-Fi inicial y sincronización horaria NTP
├── config.example.py    # Plantilla de configuración (Wi-Fi, URL del backend, pines y calibración)
├── config.py            # Configuración real activa (ignorado en Git por seguridad)
├── main.py              # Bucle continuo: filtrado de mediana (11 muestras), validación atómica y cola FIFO
└── seq.txt              # Contador de persistencia de secuencia de paquetes (generado automáticamente)
```

## Pines y Hardware Validado (ESP32 D1 R32)

| Sensor / Periférico | Pin ESP32 | Modo / Protocolo | Observaciones |
|---|---|---|---|
| **Turbidez Óptica** | IO36 (ADC1_0) | Analógico 0-3.3V (ADC 12-bit) | Atenuación 11dB, divisor resistivo 10k/20k (factor 1.5) |
| **Electrodo de pH** | IO34 (ADC1_6) | Analógico 0-3.3V (ADC 12-bit) | Atenuación 11dB, PH-4502C |
| **DS18B20 Temperatura** | IO26 | Digital 1-Wire | Resistencia pull-up 4.7 kΩ a 3.3V |

## Características del Firmware

1. **Filtrado Estadístico por Mediana:** Se toman 11 muestras consecutivas por cada canal analógico, ordenándolas para extraer la mediana y calcular la dispersión (detección de ruido/picos espurios).
2. **Validación Atómica de Calidad ("Todo o Nada"):**
   - Si un sensor presenta desconexión, saturación o lecturas físicas imposibles, se asigna estado `SENSOR_ERROR` o `INVALID` y se emiten banderas (`quality_flags`), bloqueando el paso de datos corruptos al dashboard.
3. **Cola Local Anti-Pérdida (FIFO):**
   - Si se interrumpe la conexión Wi-Fi o el backend no responde, las lecturas se acumulan en memoria (hasta 50 paquetes) y se retransmiten en orden cronológico en cuanto se restablece la comunicación.
4. **Sincronización NTP:** Marcas de tiempo en formato ISO 8601 UTC sincronizadas con `pool.ntp.org`.
5. **Autenticación en Ingesta:** Encabezados HTTP `X-Device-ID` y `X-Device-Secret` validados contra el backend de FastAPI.

## Puesta en Marcha

1. Copiar `config.example.py` a `config.py` y configurar la red Wi-Fi y la URL del backend:
   ```python
   WIFI_SSID = "TuWiFi"
   WIFI_PASS = "TuPassword"
   API_URL = "http://192.168.1.100:8000/api/v1/measurements"
   DEVICE_SECRET = "narval_secret_token_2026_xyz"
   ```
2. Cargar los archivos `boot.py`, `config.py` y `main.py` al ESP32 usando Thonny IDE o `mpremote`.
