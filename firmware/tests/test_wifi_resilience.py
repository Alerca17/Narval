"""Pruebas de resiliencia Wi-Fi y temporización del firmware Narval v1.1 (CP-M1-06 a CP-M1-09).

Verifican las correcciones aplicadas a las caídas de Wi-Fi observadas en banco:
- Ahorro de energía 802.11 desactivado (pm=0).
- Reconexión limpia: disconnect() antes de connect().
- Cierre del socket HTTP también cuando urequests lanza excepción (sin fuga de sockets lwIP).
- Intervalo de captura configurable (45 s) y espera interrumpible.
"""
from unittest.mock import MagicMock


def test_conectar_wifi_reconexion_limpia_y_pm_desactivado(firmware_env):
    """CP-M1-06: Si el enlace cayó, se desactiva PM, se hace disconnect() y luego connect()."""
    fw = firmware_env.main
    wlan = firmware_env.wlan
    wlan.reset_mock()
    # 1.ª consulta: desconectado; en el lazo de espera: desconectado y luego conectado
    wlan.isconnected.side_effect = [False, False, True]

    assert fw.conectar_wifi(reintentos=5) is True
    wlan.config.assert_any_call(pm=0)
    wlan.disconnect.assert_called_once()
    wlan.connect.assert_called_once_with(firmware_env.config.WIFI_SSID, firmware_env.config.WIFI_PASS)

    # El orden importa: disconnect() debe ocurrir antes de connect()
    nombres = [c[0] for c in wlan.method_calls]
    assert nombres.index("disconnect") < nombres.index("connect")
    wlan.isconnected.side_effect = None
    wlan.isconnected.return_value = True


def test_conectar_wifi_sin_red_retorna_false_sin_bloquear(firmware_env):
    """CP-M1-07: Sin punto de acceso, la función agota los reintentos y retorna False (el lazo sigue)."""
    fw = firmware_env.main
    wlan = firmware_env.wlan
    wlan.reset_mock()
    wlan.isconnected.side_effect = None
    wlan.isconnected.return_value = False

    assert fw.conectar_wifi(reintentos=3) is False
    assert wlan.connect.call_count == 1
    wlan.isconnected.return_value = True


def test_conectar_wifi_ya_conectado_no_reconecta(firmware_env):
    """CP-M1-07: Con enlace activo no se fuerza una reconexión innecesaria."""
    fw = firmware_env.main
    wlan = firmware_env.wlan
    wlan.reset_mock()
    wlan.isconnected.side_effect = None
    wlan.isconnected.return_value = True

    assert fw.conectar_wifi() is True
    wlan.connect.assert_not_called()
    wlan.disconnect.assert_not_called()


def test_enviar_cierra_socket_aun_con_respuesta_de_error(firmware_env):
    """CP-M1-08: La respuesta HTTP se cierra en cada intento (incluido HTTP 500) para no agotar sockets lwIP."""
    fw = firmware_env.main
    res_500 = MagicMock(status_code=500, text="error")
    res_201 = MagicMock(status_code=201, text="ok")
    firmware_env.urequests.post = MagicMock(side_effect=[res_500, res_201])
    fw.urequests = firmware_env.urequests

    assert fw.enviar_con_reintentos({"sequence_number": 1}) is True
    res_500.close.assert_called_once()
    res_201.close.assert_called_once()


def test_enviar_tolera_excepciones_de_red_y_falla_controladamente(firmware_env):
    """CP-M1-08: Un timeout/ECONNRESET en los 3 intentos devuelve False sin propagar la excepción."""
    fw = firmware_env.main
    firmware_env.urequests.post = MagicMock(side_effect=OSError(116, "ETIMEDOUT"))
    fw.urequests = firmware_env.urequests

    assert fw.enviar_con_reintentos({"sequence_number": 2}) is False
    assert firmware_env.urequests.post.call_count == 3


def test_intervalo_de_captura_configurado_en_45_segundos(firmware_env):
    """CP-M1-09: La plantilla de configuración define el intervalo de captura de 45 s."""
    assert firmware_env.config.INTERVALO_SEGUNDOS == 45
