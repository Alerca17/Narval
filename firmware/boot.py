# boot.py - Inicialización Automática de Red Wi-Fi y Reloj NTP
import gc
import network
import time
import config

gc.collect()

def obtener_timestamp_iso():
    t = time.gmtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(t[0], t[1], t[2], t[3], t[4], t[5])

def sincronizar_hora_ntp():
    try:
        import ntptime
        ntptime.host = "pool.ntp.org"
        ntptime.settime()
        print("Reloj sincronizado UTC:", obtener_timestamp_iso())
    except Exception as e:
        print("No se pudo sincronizar NTP (usando reloj interno):", e)

def conectar_wifi_inicial():
    print("\n==================================================")
    print(" INICIANDO NODO EDGE: PROYECTO NARVAL MVP")
    print("==================================================")
    
    if not config.CONECTAR_WIFI_PRUEBA:
        print("Modo offline activo (CONECTAR_WIFI_PRUEBA = False).")
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Conectando a Wi-Fi '{config.WIFI_SSID}'...")
        wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
        for _ in range(25):
            if wlan.isconnected():
                break
            print(".", end="")
            time.sleep(0.5)
        print()

    if wlan.isconnected():
        print("¡Wi-Fi Conectado con éxito! IP del ESP32:", wlan.ifconfig()[0])
        sincronizar_hora_ntp()
        return True
    else:
        print("Sin conexión Wi-Fi. Verifica que la red sea 2.4GHz.")
        return False

if __name__ == "__main__":
    conectar_wifi_inicial()
