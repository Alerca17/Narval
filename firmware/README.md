# Firmware MicroPython para ESP32 — Narval

Este directorio contiene el firmware modular para el microcontrolador **ESP32 DevKit V1**, encargado de adquirir las señales de los sensores físicos, filtrar anomalías y transmitirlas mediante HTTP al backend de Narval.

## Estructura

```
firmware/
├── boot.py              # Inicialización del microcontrolador y memoria
├── main.py              # Bucle de muestreo, empaque JSON y envío periódico
├── config.example.py    # Plantilla de configuración (Wi-Fi, URL, pines, calibración)
├── sensors/
│   ├── ph.py            # Lectura del electrodo de pH sobre ADC1 (GPIO 35)
│   ├── turbidity.py     # Lectura del sensor óptico sobre ADC1 (GPIO 34)
│   └── temperature.py   # Lectura de la sonda digital DS18B20 OneWire (GPIO 4)
└── net/
    ├── wifi.py          # Gestor de conexión Wi-Fi con auto-reconexión
    └── http_client.py   # Envío seguro con header 'X-Device-Token'
```

## Preparación y Puesta en Marcha

1. **Instalar MicroPython en el ESP32:**
   Descarga el firmware oficial desde [micropython.org](https://micropython.org/download/ESP32_GENERIC/) y flashea tu placa con `esptool`:
   ```bash
   esptool.py --chip esp32 --port COM3 erase_flash
   esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 ESP32_GENERIC-*.bin
   ```

2. **Configurar Credenciales:**
   Copia `config.example.py` a `config.py` y ajusta tus valores:
   ```python
   WIFI_SSID = "TuWiFi"
   WIFI_PASSWORD = "TuPassword"
   BACKEND_URL = "http://<IP-DE-TU-SERVIDOR>:8000/api/v1/measurements"
   DEVICE_TOKEN = "narval_secret_token_2026_xyz"
   ```

3. **Subir los Archivos al ESP32:**
   Puedes usar [Thonny IDE](https://thonny.org/) o la herramienta `mpremote`:
   ```bash
   pip install mpremote
   mpremote connect COM3 cp -r . :
   ```

4. **Ejecutar:**
   Reinicia el ESP32. En la consola serie observarás el proceso de conexión Wi-Fi y los envíos HTTP periódicos `201 Created`.
