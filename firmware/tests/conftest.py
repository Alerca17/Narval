import importlib
import importlib.util
import json
import sys
import time
import types
from pathlib import Path
from unittest.mock import MagicMock
import pytest

FIRMWARE_DIR = Path(__file__).resolve().parent.parent
if str(FIRMWARE_DIR) not in sys.path:
    sys.path.insert(0, str(FIRMWARE_DIR))


def load_firmware_config():
    """Carga config.example.py como módulo config para pruebas unitarias sin secretos reales."""
    spec = importlib.util.spec_from_file_location("config", FIRMWARE_DIR / "config.example.py")
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    sys.modules["config"] = cfg
    return cfg


@pytest.fixture
def firmware_env(tmp_path, monkeypatch):
    """Provee los módulos main y boot del firmware con mocks deterministas de MicroPython y seq.txt aislado."""
    cfg = load_firmware_config()
    cfg.ARCHIVO_SEQ = str(tmp_path / "seq.txt")

    # time.sleep_ms es propio de MicroPython; se neutralizan esperas para ejecución rápida
    if not hasattr(time, "sleep_ms"):
        monkeypatch.setattr(time, "sleep_ms", lambda ms: None, raising=False)
    else:
        monkeypatch.setattr(time, "sleep_ms", lambda ms: None)
    monkeypatch.setattr(time, "sleep", lambda s: None)

    # Mock del módulo machine (Pin y ADC de 12 bits)
    machine_mod = types.ModuleType("machine")

    class DummyPin:
        def __init__(self, pin_num):
            self.pin_num = pin_num

    class DummyADC:
        ATTN_11DB = 3
        WIDTH_12BIT = 3

        def __init__(self, pin):
            self.pin = pin
            self.readings = [2048]
            self._idx = 0

        def atten(self, val):
            self._atten = val

        def width(self, val):
            self._width = val

        def read(self):
            val = self.readings[self._idx % len(self.readings)]
            self._idx += 1
            return val

    machine_mod.Pin = DummyPin
    machine_mod.ADC = DummyADC
    monkeypatch.setitem(sys.modules, "machine", machine_mod)

    # Mocks de bus OneWire y sonda DS18B20
    onewire_mod = types.ModuleType("onewire")
    onewire_mod.OneWire = MagicMock()
    monkeypatch.setitem(sys.modules, "onewire", onewire_mod)

    ds_mod = types.ModuleType("ds18x20")

    class DummyDS18X20:
        def __init__(self, ow):
            self.ow = ow
            self._roms = [b"\x28\x01\x02\x03"]
            self._temp = 21.5

        def scan(self):
            return list(self._roms)

        def convert_temp(self):
            return None

        def read_temp(self, rom):
            return self._temp

    ds_mod.DS18X20 = DummyDS18X20
    monkeypatch.setitem(sys.modules, "ds18x20", ds_mod)

    # Mock de red Wi-Fi (network.WLAN)
    network_mod = types.ModuleType("network")
    network_mod.STA_IF = 0
    wlan_instance = MagicMock()
    wlan_instance.isconnected.return_value = True
    wlan_instance.ifconfig.return_value = ("192.168.1.50", "255.255.255.0", "192.168.1.1", "8.8.8.8")
    network_mod.WLAN = MagicMock(return_value=wlan_instance)
    monkeypatch.setitem(sys.modules, "network", network_mod)

    # Mocks de serialización JSON, cliente HTTP y reloj NTP de MicroPython
    ujson_mod = types.ModuleType("ujson")
    ujson_mod.dumps = json.dumps
    ujson_mod.loads = json.loads
    monkeypatch.setitem(sys.modules, "ujson", ujson_mod)

    urequests_mod = types.ModuleType("urequests")
    urequests_mod.post = MagicMock()
    monkeypatch.setitem(sys.modules, "urequests", urequests_mod)

    ntptime_mod = types.ModuleType("ntptime")
    ntptime_mod.host = "pool.ntp.org"
    ntptime_mod.settime = MagicMock()
    monkeypatch.setitem(sys.modules, "ntptime", ntptime_mod)

    sys.modules.pop("main", None)
    sys.modules.pop("boot", None)

    fw_main = importlib.import_module("main")
    fw_boot = importlib.import_module("boot")

    return types.SimpleNamespace(
        main=fw_main,
        boot=fw_boot,
        config=cfg,
        wlan=wlan_instance,
        urequests=urequests_mod,
        ntptime=ntptime_mod,
    )
