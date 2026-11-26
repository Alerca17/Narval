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
        ntptime.timeout = 5
        ntptime.settime()
        print("[NTP] Reloj sincronizado UTC:", obtener_timestamp_iso())
        return True
    except Exception as e:
        print("[NTP] Aviso: No se pudo sincronizar con pool.ntp.org (se mantiene RTC interno):", e)
        return False

def conectar_wifi_inicial():
    print("\n==================================================")
    print(" INICIANDO NODO EDGE: PROYECTO NARVAL MVP v1.1   ")
    print("==================================================")
    
    if not getattr(config, "CONECTAR_WIFI_PRUEBA", True):
        print("[Wi-Fi] Modo offline activo.")
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Optimización de estabilidad Wi-Fi en ESP32:
    # 1. Desactivar modo de ahorro de energía (evita desconexiones por inactividad)
    try:
        wlan.config(pm=0)
    except Exception:
        pass

    # 2. Potencia de transmisión máxima (20 dBm) para mejorar cobertura
    try:
        wlan.config(txpower=20)
    except Exception:
        pass
    
    if not wlan.isconnected():
        print(f"[Wi-Fi] Conectando a red '{config.WIFI_SSID}'...")
        try:
            wlan.disconnect()
            time.sleep_ms(150)
        except Exception:
            pass
        wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
        for i in range(30):
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
        print("[Wi-Fi] Aviso: No se pudo conectar de inmediato. El ciclo principal reintentará.")
        return False

if __name__ == "__main__":
    conectar_wifi_inicial()
