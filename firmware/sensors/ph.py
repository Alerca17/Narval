# firmware/sensors/ph.py
from machine import Pin, ADC
import time

class PHSensor:
    def __init__(self, pin_num: int, is_calibrated: bool = False, slope: float = -5.70, intercept: float = 21.34):
        self.adc = ADC(Pin(pin_num))
        # Configurar atenuación completa (0 - 3.3V)
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        self.is_calibrated = is_calibrated
        self.slope = slope
        self.intercept = intercept

    def read(self, samples: int = 10) -> dict:
        """Lee múltiples muestras del ADC y calcula el promedio para reducir ruido."""
        raw_sum = 0
        for _ in range(samples):
            raw_sum += self.adc.read()
            time.sleep_ms(10)
        
        raw_avg = raw_sum / samples
        voltage = (raw_avg / 4095.0) * 3.3

        if self.is_calibrated:
            ph_value = round((self.slope * voltage) + self.intercept, 2)
            ph_value = max(0.0, min(14.0, ph_value))
        else:
            ph_value = None

        return {
            "raw": int(raw_avg),
            "voltage": round(voltage, 3),
            "value": ph_value,
            "is_calibrated": self.is_calibrated
        }
