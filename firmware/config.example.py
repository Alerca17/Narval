# ========================================================
# CONFIGURACIÓN DEL FIRMWARE ESP32 (MICROPYTHON)
# Copia este archivo como 'config.py' y completa tus valores.
# ========================================================

# Red Wi-Fi
WIFI_SSID = "TuNombreDeRedWiFi"
WIFI_PASSWORD = "TuPasswordWiFi"

# Backend FastAPI (IP de la máquina anfitriona o dominio del servidor)
BACKEND_URL = "http://192.168.1.100:8000/api/v1/measurements"

# Identificación y autenticación del dispositivo
DEVICE_CODE = "ESP32-NARVAL-001"
DEVICE_TOKEN = "tu-token-secreto-esp32-cambiar-en-produccion"

# Pines ADC (Usar exclusivamente ADC1 para convivir con Wi-Fi en ESP32)
PIN_PH = 35          # ADC1_CH7
PIN_TURBIDITY = 34   # ADC1_CH6
PIN_ONEWIRE = 4      # GPIO con pull-up 4.7k a 3.3V

# Parámetros de calibración inicial (ajustar según CALIBRATION.md)
PH_CALIBRATED = False
PH_SLOPE = -5.70
PH_INTERCEPT = 21.34

TURBIDITY_CALIBRATED = False
TURBIDITY_SLOPE = -1120.4
TURBIDITY_INTERCEPT = 5742.3

# Intervalo entre envíos (segundos)
MEASUREMENT_INTERVAL_SECONDS = 10
