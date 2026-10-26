# firmware/net/wifi.py
import network
import time

def connect_wifi(ssid: str, password: str, timeout_seconds: int = 20) -> bool:
    """Conecta el ESP32 a la red Wi-Fi configurada."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("[WiFi] Ya conectado. IP:", wlan.ifconfig()[0])
        return True

    print(f"[WiFi] Conectando a {ssid}...")
    wlan.connect(ssid, password)

    start = time.time()
    while not wlan.isconnected():
        time.sleep_ms(500)
        print(".", end="")
        if time.time() - start > timeout_seconds:
            print("\n[WiFi] Tiempo de espera agotado al conectar.")
            return False

    print("\n[WiFi] Conexión establecida con éxito!")
    print("[WiFi] Configuración de red:", wlan.ifconfig())
    return True
