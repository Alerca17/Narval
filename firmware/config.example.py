# config.example.py - Plantilla de Configuración para el ESP32 (MicroPython)
# Copia este archivo como 'config.py' en la raíz de tu ESP32 o en esta carpeta y completa tus credenciales.

# --- MODOS DE OPERACIÓN ---
CONECTAR_WIFI_PRUEBA = True   # Conecta al Wi-Fi y sincroniza reloj NTP al arrancar
ENVIAR_A_BACKEND = True       # Enviar automáticamente al servidor FastAPI

# --- CREDENCIALES WI-FI ---
WIFI_SSID = "TU_RED_WIFI"
WIFI_PASS = "TU_PASSWORD_WIFI"

# --- ENDPOINT DEL BACKEND FASTAPI ---
# IP de tu computador en la red local o dominio del servidor (ej. http://192.168.1.64:8000/api/v1/measurements)
API_URL = "http://192.168.1.64:8000/api/v1/measurements"

# --- IDENTIDAD Y SEGURIDAD DEL DISPOSITIVO ---
DEVICE_ID = "NARVAL-001"
DEVICE_SECRET = "narval_secret_token_2026_xyz"  # Debe coincidir con DEVICE_INGESTION_SECRET del backend
FIRMWARE_VERSION = "1.1.0"
SCHEMA_VERSION = "1.0"

# --- PINES FÍSICOS VALIDADOS (Placa ESP32 D1 R32) ---
PIN_TURBIDEZ = 36     # IO36 (ADC1_0)
PIN_PH = 34           # IO34 (ADC1_6)
PIN_TEMP = 26         # IO26 (Digital 1-Wire DS18B20 con pull-up 4.7k)

# --- CONSTANTES ELECTRÓNICAS Y DE CALIBRACIÓN ---
FACTOR_DIVISOR = 1.5          # Divisor resistivo 10k y 20k -> (10+20)/20 = 1.5
VOLTAJE_BASE_PH = 4.50        # Voltaje base ajustado para PH-4502C
PENDIENTE_PH = -3.50          # Pendiente calibrada
VOLTAJE_BASE_AGUA = 2.34      # Voltaje base calibrado para sensor de turbidez

# --- PARÁMETROS DE OPERACIÓN Y COLA ANTI-PÉRDIDA ---
INTERVALO_SEGUNDOS = 45       # Una lectura completa cada 45 s (ej. 1800 = 30 min en producción)
MAX_COLA = 50
ARCHIVO_SEQ = "seq.txt"
