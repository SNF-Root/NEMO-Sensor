# w104.py
from machine import ADC, Pin
import utime
import math

class W104:
    def __init__(self, pin=35, ref_voltage=0.775):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)  # 0–3.6V range
        self.adc.width(ADC.WIDTH_12BIT)  # 12-bit (0–4095)
        self.ref_voltage = ref_voltage

    def read_db(self, samples=100, delay_us=100):
        values = []
        for _ in range(samples):
            val = self.adc.read()
            values.append(val)
            utime.sleep_us(delay_us)

        mean = sum(values) / len(values)
        squares = [(v - mean) ** 2 for v in values]
        rms = math.sqrt(sum(squares) / len(squares))

        voltage = rms * (3.3 / 4095)  # Convert ADC to voltage
        if voltage <= 0:
            return 0

        db = 20 * math.log10(voltage / self.ref_voltage)
        return round(db, 1)
