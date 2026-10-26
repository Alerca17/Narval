# firmware/main.py
# Ciclo principal de adquisición y transmisión de datos de calidad del agua
import time
import gc

try:
    import config
except ImportError:
    print("[Error] No se encontró 'config.py'.")
    print("[Ayuda] Copia 'config.example.py' a 'config.py' y configura tus credenciales.")
    raise SystemExit

from net.wifi import connect_wifi
from net.http_client import send_measurement
from sensors.ph import PHSensor
from sensors.turbidity import TurbiditySensor
from sensors.temperature import TemperatureSensor

def format_iso_timestamp(epoch_time: int) -> str:
    """Convierte tiempo en segundos a formato ISO 8601 UTC básico."""
    tm = time.gmtime(epoch_time)
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
        tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]
    )

def main():
    print("=========================================")
    print("      NARVAL ESP32 - FIRMWARE v1.0       ")
    print("=========================================")
    
    # 1. Conectar a Wi-Fi
    if not connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD):
        print("[Alerta] Sin conexión Wi-Fi inicial. Reintentando en bucle...")

    # 2. Inicializar Sensores en ADC1 y OneWire
    ph_sensor = PHSensor(
        pin_num=config.PIN_PH,
        is_calibrated=getattr(config, "PH_CALIBRATED", False),
        slope=getattr(config, "PH_SLOPE", -5.70),
        intercept=getattr(config, "PH_INTERCEPT", 21.34)
    )
    
    turbidity_sensor = TurbiditySensor(
        pin_num=config.PIN_TURBIDITY,
        is_calibrated=getattr(config, "TURBIDITY_CALIBRATED", False),
        slope=getattr(config, "TURBIDITY_SLOPE", -1120.4),
        intercept=getattr(config, "TURBIDITY_INTERCEPT", 5742.3)
    )
    
    temp_sensor = TemperatureSensor(pin_num=config.PIN_ONEWIRE)
    
    packet_seq = 1
    
    while True:
        try:
            # Reconexión Wi-Fi preventiva
            connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD, timeout_seconds=5)

            now_epoch = time.time()
            packet_id = f"pkt-{config.DEVICE_CODE}-{now_epoch}-{packet_seq:04d}"
            device_timestamp = format_iso_timestamp(now_epoch)

            # Lectura de los 3 parámetros
            ph_data = ph_sensor.read(samples=10)
            turbidity_data = turbidity_sensor.read(samples=10)
            temp_data = temp_sensor.read()

            payload = {
                "device_code": config.DEVICE_CODE,
                "packet_id": packet_id,
                "device_timestamp": device_timestamp,
                "ph": ph_data,
                "turbidity": turbidity_data,
                "temperature": temp_data
            }

            # Enviar al backend FastAPI
            send_measurement(config.BACKEND_URL, config.DEVICE_TOKEN, payload)
            packet_seq += 1

        except Exception as err:
            print("[Loop Error] Excepción no controlada en ciclo:", err)

        # Liberar memoria y esperar siguiente intervalo
        gc.collect()
        time.sleep(getattr(config, "MEASUREMENT_INTERVAL_SECONDS", 10))

if __name__ == "__main__":
    main()
