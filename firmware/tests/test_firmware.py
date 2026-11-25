from unittest.mock import MagicMock
import pytest


def test_leer_adc_con_calidad_median_filtering_and_guard(firmware_env):
    """CP-M1-01 / CP-M1-02: El filtro de mediana descarta picos atípicos y muestras <= 0 lanza ValueError."""
    fw = firmware_env.main
    # 11 muestras con un pico alto (4095) y un pico bajo (10) -> mediana exacta = 2000
    fw.adc_ph.readings = [10, 1995, 1998, 2000, 2000, 2000, 2001, 2002, 2005, 2010, 4095]
    fw.adc_ph._idx = 0

    mediana, v_pin, v_sens, disp = fw.leer_adc_con_calidad(fw.adc_ph, muestras=11)
    assert mediana == 2000
    assert disp == 4095 - 10
    assert v_pin == round((2000 / 4095.0) * 3.3, 3)
    assert v_sens == round(v_pin * firmware_env.config.FACTOR_DIVISOR, 3)

    with pytest.raises(ValueError, match="muestras"):
        fw.leer_adc_con_calidad(fw.adc_ph, muestras=0)


def test_convertir_ph_and_turbidez_clamping(firmware_env):
    """CP-M1-02 / CP-M1-03: Las conversiones físicas acotan estrictamente pH [0, 14] y turbidez [0, 3000]."""
    fw = firmware_env.main
    cfg = firmware_env.config

    # pH en voltaje base -> 7.0
    assert fw.convertir_ph(cfg.VOLTAJE_BASE_PH) == 7.0
    # Voltaje extremo bajo -> acotado a 14.0
    assert fw.convertir_ph(0.0) == 14.0
    # Voltaje extremo alto -> acotado a 0.0
    assert fw.convertir_ph(12.0) == 0.0

    # Agua limpia (>= VOLTAJE_BASE_AGUA) -> 0.5 NTU
    assert fw.convertir_turbidez(cfg.VOLTAJE_BASE_AGUA) == 0.5
    assert fw.convertir_turbidez(cfg.VOLTAJE_BASE_AGUA + 0.5) == 0.5
    # Agua turbia bajo referencia -> NTU positivo acotado a 3000.0
    assert fw.convertir_turbidez(cfg.VOLTAJE_BASE_AGUA - 0.1) == 10.0
    assert fw.convertir_turbidez(-100.0) == 3000.0


def test_leer_temperatura_ds18b20_anomalies_and_valid(firmware_env):
    """CP-M1-04: Rechaza sonda desconectada, 85.0 °C, -127.0 °C y excepciones (nunca retorna 0.0 °C)."""
    fw = firmware_env.main

    # Lectura térmica válida
    fw.ds_sensor._temp = 21.456
    temp, err = fw.leer_temperatura_ds18b20()
    assert temp == 21.46
    assert err is None

    # Error de reinicio eléctrico (85.0 °C)
    fw.ds_sensor._temp = 85.0
    assert fw.leer_temperatura_ds18b20() == (None, "TEMP_POWER_OR_BUS_ERROR")

    # Sonda desconectada (-127.0 °C)
    fw.ds_sensor._temp = -127.0
    assert fw.leer_temperatura_ds18b20() == (None, "TEMP_POWER_OR_BUS_ERROR")

    # Sin dispositivos ROM en bus OneWire
    fw.roms_temp = []
    fw.ds_sensor._roms = []
    assert fw.leer_temperatura_ds18b20() == (None, "TEMP_SENSOR_DISCONNECTED")

    # Excepción eléctrica/CRC en lectura
    fw.roms_temp = [b"\x28\x01"]
    fw.ds_sensor.read_temp = MagicMock(side_effect=OSError("Error CRC OneWire"))
    assert fw.leer_temperatura_ds18b20() == (None, "TEMP_READ_EXCEPTION")


def test_validar_calidad_medicion_states(firmware_env):
    """Valida estados VALID, SENSOR_ERROR, INVALID y SUSPECT del motor de calidad local."""
    fw = firmware_env.main

    # Medición válida
    st, flags = fw.validar_calidad_medicion(7.1, 1.2, 22.0, 2100, 1900, 20, 30, None)
    assert st == "VALID"
    assert flags == []

    # Error físico de sensores (pH saturado, turbidez desconectada y fallo térmico)
    st, flags = fw.validar_calidad_medicion(7.0, 0.5, None, 4095, 2, 0, 0, "TEMP_SENSOR_DISCONNECTED")
    assert st == "SENSOR_ERROR"
    assert "TEMP_SENSOR_DISCONNECTED" in flags
    assert "PH_ADC_SATURATED_OR_DISCONNECTED" in flags
    assert "TURBIDITY_SENSOR_DISCONNECTED" in flags

    # Fuera de rango físico admisible
    st, flags = fw.validar_calidad_medicion(7.0, 1.0, 55.0, 2100, 1900, 10, 10, None)
    assert st == "INVALID"
    assert "TEMP_OUTSIDE_PHYSICAL_RANGE" in flags

    # Ruido o inestabilidad (dispersión > 400)
    st, flags = fw.validar_calidad_medicion(7.0, 1.0, 20.0, 2100, 1900, 450, 420, None)
    assert st == "SUSPECT"
    assert "PH_SENSOR_UNSTABLE" in flags
    assert "TURBIDITY_SPIKE_OR_UNSTABLE" in flags


def test_sequence_persistence_across_reboots(firmware_env):
    """Valida la persistencia incremental de secuencia en archivo local seq.txt."""
    fw = firmware_env.main
    assert fw.obtener_siguiente_secuencia() == 1
    assert fw.obtener_siguiente_secuencia() == 2
    assert fw.obtener_siguiente_secuencia() == 3


def test_enviar_con_reintentos_http_201_409_500_and_close(firmware_env):
    """CP-M1-05: Acepta 201 y 409, reintenta ante 500/red y siempre cierra el socket HTTP."""
    fw = firmware_env.main
    payload = {"sequence_number": 7, "device_id": "NARVAL-001"}

    # HTTP 201 Creado
    resp_201 = MagicMock(status_code=201, text='{"id":1}')
    firmware_env.urequests.post.return_value = resp_201
    assert fw.enviar_con_reintentos(payload) is True
    resp_201.close.assert_called_once()

    # HTTP 409 Conflicto (paquete duplicado idempotente)
    resp_409 = MagicMock(status_code=409, text='{"detail":"duplicado"}')
    firmware_env.urequests.post.return_value = resp_409
    assert fw.enviar_con_reintentos(payload) is True
    resp_409.close.assert_called_once()

    # HTTP 500 -> 3 reintentos -> False
    resp_500 = MagicMock(status_code=500, text="Error interno")
    firmware_env.urequests.post.return_value = resp_500
    assert fw.enviar_con_reintentos(payload) is False
    assert resp_500.close.call_count == 3

    # Excepción de red -> False
    firmware_env.urequests.post.side_effect = OSError("Tiempo de espera agotado")
    assert fw.enviar_con_reintentos(payload) is False
    firmware_env.urequests.post.side_effect = None


def test_ejecutar_ciclo_atomic_rule_and_fifo_queue(firmware_env):
    """Verifica la regla atómica 'Todo o Nada' ante fallo físico y recuperación de cola FIFO."""
    fw = firmware_env.main
    fw.cola_pendientes.clear()

    # 1. Fallo físico (pH saturado en 4095) y sin Wi-Fi -> oculta valores numéricos y encola localmente
    fw.adc_ph.readings = [4095]
    fw.adc_turbidez.readings = [2000]
    fw.ds_sensor._temp = 22.0
    firmware_env.wlan.isconnected.return_value = False

    bad_payload = fw.ejecutar_ciclo()
    assert bad_payload["quality_status"] == "SENSOR_ERROR"
    assert bad_payload["measurements"]["ph"] is None
    assert bad_payload["measurements"]["turbidity_ntu"] is None
    assert bad_payload["measurements"]["temperature_c"] is None
    assert bad_payload["measurements"]["ph_raw"] == 4095
    assert len(fw.cola_pendientes) == 1

    # 2. Sensores sanos y Wi-Fi restablecido -> envía lectura actual y vacía la cola FIFO
    fw.adc_ph.readings = [3500]
    fw.adc_turbidez.readings = [2000]
    fw.ds_sensor._temp = 21.0
    firmware_env.wlan.isconnected.return_value = True
    firmware_env.urequests.post.return_value = MagicMock(status_code=201, text="{}")

    ok_payload = fw.ejecutar_ciclo()
    assert ok_payload["quality_status"] == "VALID"
    assert ok_payload["measurements"]["ph"] is not None
    assert ok_payload["measurements"]["temperature_c"] == 21.0
    assert len(fw.cola_pendientes) == 0


def test_boot_wifi_offline_and_online(firmware_env):
    """Valida modo offline y conexión Wi-Fi inicial con sincronización NTP en boot.py."""
    boot = firmware_env.boot

    # Modo offline de pruebas
    firmware_env.config.CONECTAR_WIFI_PRUEBA = False
    assert boot.conectar_wifi_inicial() is False

    # Conexión Wi-Fi activa y formato de marca horaria UTC
    firmware_env.config.CONECTAR_WIFI_PRUEBA = True
    firmware_env.wlan.isconnected.return_value = True
    assert boot.conectar_wifi_inicial() is True
    assert boot.obtener_timestamp_iso().endswith("Z")
