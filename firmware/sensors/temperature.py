# firmware/sensors/temperature.py
from machine import Pin
import onewire
import ds18x20
import time

class TemperatureSensor:
    def __init__(self, pin_num: int):
        self.ow = onewire.OneWire(Pin(pin_num))
        self.ds = ds18x20.DS18X20(self.ow)
        self.roms = self.ds.scan()

    def read(self) -> dict:
        """Lee la sonda DS18B20 descartando lecturas anómalas (-127°C o 85°C)."""
        if not self.roms:
            # Reintentar escaneo si no había sonda conectada
            self.roms = self.ds.scan()
            if not self.roms:
                return {"celsius": None, "is_valid": False}

        try:
            self.ds.convert_temp()
            time.sleep_ms(750)  # Tiempo de conversión requerido a 12 bits
            rom = self.roms[0]
            temp = self.ds.read_temp(rom)

            # 85.0 °C indica lectura prematura de memoria; -127.0 °C indica desconexión
            if temp == 85.0 or temp <= -127.0 or temp > 125.0:
                return {"celsius": None, "is_valid": False}

            return {
                "celsius": round(temp, 2),
                "is_valid": True
            }
        except Exception:
            return {"celsius": None, "is_valid": False}
