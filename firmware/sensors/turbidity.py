# firmware/sensors/turbidity.py
from machine import Pin, ADC
import time

class TurbiditySensor:
    def __init__(self, pin_num: int, is_calibrated: bool = False, slope: float = -1120.4, intercept: float = 5742.3):
        self.adc = ADC(Pin(pin_num))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        self.is_calibrated = is_calibrated
        self.slope = slope
        self.intercept = intercept

    def read(self, samples: int = 10) -> dict:
        """Lee múltiples muestras del ADC y calcula voltaje y NTU si está calibrado."""
        raw_sum = 0
        for _ in range(samples):
            raw_sum += self.adc.read()
            time.sleep_ms(10)
        
        raw_avg = raw_sum / samples
        voltage = (raw_avg / 4095.0) * 3.3

        if self.is_calibrated:
            # Modelo de transferencia típico o polinomio calibrado
            ntu_val = (self.slope * voltage) + self.intercept
            ntu_val = round(max(0.0, ntu_val), 2)
        else:
            ntu_val = None

        return {
            "raw": int(raw_avg),
            "voltage": round(voltage, 3),
            "value": ntu_val,
            "is_calibrated": self.is_calibrated
        }
