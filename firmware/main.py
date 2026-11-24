# main.py - Firmware Principal Proyecto Narval MVP (Producción)
import machine
import onewire
import ds18x20
import time
import network
import ujson
import gc
import config

try:
    import urequests
    import ntptime
except ImportError:
    print("Aviso: Librerías de red no disponibles en este entorno.")

# ==========================================
# 1. INICIALIZACIÓN DE HARDWARE
# ==========================================
adc_turbidez = machine.ADC(machine.Pin(config.PIN_TURBIDEZ))
adc_turbidez.atten(machine.ADC.ATTN_11DB)
adc_turbidez.width(machine.ADC.WIDTH_12BIT)

adc_ph = machine.ADC(machine.Pin(config.PIN_PH))
adc_ph.atten(machine.ADC.ATTN_11DB)
adc_ph.width(machine.ADC.WIDTH_12BIT)

ow_pin = machine.Pin(config.PIN_TEMP)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ow_pin))
roms_temp = ds_sensor.scan()
print("Sensores DS18B20 detectados en pin", config.PIN_TEMP, ":", roms_temp)

cola_pendientes = []

# ==========================================
# 2. PERSISTENCIA DE SECUENCIA Y RELOJ (UTC)
# ==========================================
def obtener_siguiente_secuencia():
    seq = 1
    try:
        with open(config.ARCHIVO_SEQ, "r") as f:
            seq = int(f.read().strip()) + 1
    except:
        seq = 1
    try:
        with open(config.ARCHIVO_SEQ, "w") as f:
            f.write(str(seq))
    except:
        pass
    return seq

def obtener_timestamp_iso():
    t = time.gmtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(t[0], t[1], t[2], t[3], t[4], t[5])

def sincronizar_hora_ntp():
    try:
        ntptime.settime()
        print("Reloj sincronizado UTC:", obtener_timestamp_iso())
    except Exception as e:
        print("No se pudo sincronizar NTP (usando reloj interno):", e)

# ==========================================
# 3. ADQUISICIÓN Y FILTRADO ESTADÍSTICO
# ==========================================
def leer_adc_con_calidad(adc_obj, muestras=11):
    lecturas = []
    for _ in range(muestras):
        lecturas.append(adc_obj.read())
        time.sleep_ms(15)
    lecturas.sort()
    
    mediana_raw = lecturas[muestras // 2]
    dispersion_raw = lecturas[-1] - lecturas[0]
    
    voltaje_pin = (mediana_raw / 4095.0) * 3.3
    voltaje_sensor = voltaje_pin * config.FACTOR_DIVISOR
    
    return mediana_raw, round(voltaje_pin, 3), round(voltaje_sensor, 3), dispersion_raw

def leer_temperatura_ds18b20():
    global roms_temp
    if not roms_temp:
        roms_temp = ds_sensor.scan()
        if not roms_temp:
            return None, "TEMP_SENSOR_DISCONNECTED"
    try:
        ds_sensor.convert_temp()
        time.sleep_ms(750)
        temp = ds_sensor.read_temp(roms_temp[0])
        if temp == 85.0 or temp <= -127.0:
            return None, "TEMP_POWER_OR_BUS_ERROR"
        return round(temp, 2), None
    except Exception:
        return None, "TEMP_READ_EXCEPTION"

# ==========================================
# 4. CALIBRACIÓN Y CONVERSIÓN FÍSICA (AJUSTADA)
# ==========================================
def convertir_ph(voltaje_sensor):
    """
    Convierte el voltaje real del módulo PH-4502C a escala de pH (0-14)
    evitando valores negativos mediante límites estrictos.
    """
    ph = 7.0 + ((voltaje_sensor - config.VOLTAJE_BASE_PH) * config.PENDIENTE_PH)
    return round(max(0.0, min(14.0, ph)), 2)

def convertir_turbidez(voltaje_sensor):
    """
    Convierte el voltaje del sensor de turbidez a NTU aproximados
    usando como referencia inicial el voltaje base actual.
    """
    if voltaje_sensor >= config.VOLTAJE_BASE_AGUA:
        return 0.5  # Agua limpia
    else:
        diferencia = config.VOLTAJE_BASE_AGUA - voltaje_sensor
        ntu = diferencia * 100.0
        return round(max(0.0, min(3000.0, ntu)), 2)

# ==========================================
# 5. MOTOR DE VALIDACIÓN LOCAL (CALIDAD DE DATOS)
# ==========================================
def validar_calidad_medicion(ph, turb, temp, ph_raw, turb_raw, disp_ph, disp_turb, err_temp):
    flags = []
    status = "VALID"

    if err_temp:
        flags.append(err_temp)
        status = "SENSOR_ERROR"
    elif temp < 0.0 or temp > 50.0:
        flags.append("TEMP_OUTSIDE_PHYSICAL_RANGE")
        status = "INVALID"

    if ph_raw <= 5 or ph_raw >= 4090:
        flags.append("PH_ADC_SATURATED_OR_DISCONNECTED")
        status = "SENSOR_ERROR"
    if turb_raw <= 5:
        flags.append("TURBIDITY_SENSOR_DISCONNECTED")
        status = "SENSOR_ERROR"

    if status != "SENSOR_ERROR":
        if ph < 0.0 or ph > 14.0:
            flags.append("PH_OUTSIDE_PHYSICAL_RANGE")
            status = "INVALID"
        if turb < 0.0 or turb > 3000.0:
            flags.append("TURBIDITY_OUTSIDE_PHYSICAL_RANGE")
            status = "INVALID"

    if status == "VALID":
        if disp_ph > 400:
            flags.append("PH_SENSOR_UNSTABLE")
            status = "SUSPECT"
        if disp_turb > 400:
            flags.append("TURBIDITY_SPIKE_OR_UNSTABLE")
            status = "SUSPECT"

    return status, flags

# ==========================================
# 6. RED WI-FI, RETRIES Y ENVÍO SEGURO
# ==========================================
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return True
    print(f"Reconectando a Wi-Fi '{config.WIFI_SSID}'...")
    wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
    for _ in range(20):
        if wlan.isconnected():
            print("Wi-Fi Conectado! IP:", wlan.ifconfig()[0])
            sincronizar_hora_ntp()
            return True
        time.sleep(0.5)
    print("Sin conexión Wi-Fi.")
    return False

def enviar_con_reintentos(payload_dict):
    headers = {
        "Content-Type": "application/json",
        "X-Device-ID": config.DEVICE_ID,
        "X-Device-Secret": config.DEVICE_SECRET
    }
    json_data = ujson.dumps(payload_dict)
    
    for intento in range(1, 4):
        try:
            res = urequests.post(config.API_URL, data=json_data, headers=headers)
            codigo = res.status_code
            texto = res.text
            res.close()
            
            if codigo in (200, 201, 409):
                print(f"[Seq #{payload_dict['sequence_number']}] Entregado al Backend (HTTP {codigo})")
                return True
            else:
                print(f"Backend rechazó o falló (HTTP {codigo}): {texto}")
        except Exception as e:
            print(f"Fallo de red en intento {intento}/3:", e)
        
        time.sleep(intento * 2)
        
    return False

# ==========================================
# 7. BUCLE PRINCIPAL DE EJECUCIÓN
# ==========================================
print("\n=== NODO NARVAL EDGE INICIADO ===")

while True:
    try:
        gc.collect()
        seq_actual = obtener_siguiente_secuencia()
        timestamp_captura = obtener_timestamp_iso()

        # 1. Adquisición y Filtrado
        ph_raw, v_pin_ph, v_sens_ph, disp_ph = leer_adc_con_calidad(adc_ph)
        turb_raw, v_pin_turb, v_sens_turb, disp_turb = leer_adc_con_calidad(adc_turbidez)
        temp_c, err_temp = leer_temperatura_ds18b20()

        # 2. Calibración / Conversión (Con límites corregidos)
        ph_val = convertir_ph(v_sens_ph)
        turb_ntu = convertir_turbidez(v_sens_turb)

        # 3. Validación Local de Calidad del Dato
        q_status, q_flags = validar_calidad_medicion(
            ph_val, turb_ntu, temp_c, ph_raw, turb_raw, disp_ph, disp_turb, err_temp
        )

        # 4. Regla Atómica "Todo o Nada":
        # Si hay SENSOR_ERROR o INVALID en cualquiera, NO pasa ningún dato numérico al dashboard,
        # solo viajan los quality_flags con la alarma técnica y los valores raw para diagnóstico.
        pasan_datos = q_status in ("VALID", "SUSPECT")

        payload = {
            "schema_version": config.SCHEMA_VERSION,
            "device_id": config.DEVICE_ID,
            "sequence_number": seq_actual,
            "firmware_version": config.FIRMWARE_VERSION,
            "captured_at": timestamp_captura,
            "quality_status": q_status,
            "quality_flags": q_flags,
            "measurements": {
                "ph": ph_val if pasan_datos else None,
                "turbidity_ntu": turb_ntu if pasan_datos else None,
                "temperature_c": temp_c if pasan_datos else None,
                "ph_raw": ph_raw,
                "turbidity_raw": turb_raw
            }
        }

        # 5. Monitoreo en Consola Local
        wlan = network.WLAN(network.STA_IF)
        info_wifi = f"Wi-Fi OK ({wlan.ifconfig()[0]})" if wlan.isconnected() else "Sin Wi-Fi"

        print("\n--------------------------------------------------")
        print(f"Lectura #{seq_actual} | Hora: {timestamp_captura} | 📡 {info_wifi}")
        print(f"Calidad Dato: {q_status} | Flags: {q_flags}")
        print(f"Temp: {temp_c} °C")
        print(f"pH:   {ph_val} (Raw: {ph_raw} | V_Sensor: {v_sens_ph}V | Ruido: {disp_ph})")
        print(f"Turb: {turb_ntu} UNT (Raw: {turb_raw} | V_Sensor: {v_sens_turb}V | Ruido: {disp_turb})")
        print(f"JSON: {ujson.dumps(payload)}")

        # 6. Transmisión y Gestión de Cola Anti-Pérdida de Datos
        if config.ENVIAR_A_BACKEND:
            if conectar_wifi():
                exito = enviar_con_reintentos(payload)
                if not exito:
                    if len(cola_pendientes) < config.MAX_COLA:
                        cola_pendientes.append(payload)
                        print(f"Guardado en cola local. Pendientes: {len(cola_pendientes)}")
                else:
                    while len(cola_pendientes) > 0:
                        viejo = cola_pendientes[0]
                        if enviar_con_reintentos(viejo):
                            cola_pendientes.pop(0)
                            print(f"Recuperado de cola Seq #{viejo['sequence_number']}")
                        else:
                            break
            else:
                if len(cola_pendientes) < config.MAX_COLA:
                    cola_pendientes.append(payload)
                    print(f"Sin Wi-Fi. Guardado en cola local ({len(cola_pendientes)}/{config.MAX_COLA})")

        time.sleep(config.INTERVALO_SEGUNDOS)

    except Exception as e:
        print("Error crítico en bucle principal:", e)
        time.sleep(3)
