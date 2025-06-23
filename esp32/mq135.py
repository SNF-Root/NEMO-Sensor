from machine import ADC, Pin

class MQ135:
    def __init__(self, pin_num, r_load=10.0):
        self.adc = ADC(Pin(pin_num))
        self.adc.atten(ADC.ATTN_11DB)  # Range: 0–3.3V
        self.r_load = r_load           # Load resistor in kilo-ohms
        self.r_zero = None             # To be calibrated

    def get_raw(self):
        return self.adc.read()

    def get_voltage(self):
        return self.adc.read() / 4095.0 * 3.3

    def get_resistance(self):
        v_out = self.get_voltage()
        if v_out == 0:
            return -1  # avoid div by zero
        return self.r_load * (3.3 - v_out) / v_out

    def calibrate(self):
        # Call this in clean air
        self.r_zero = self.get_resistance()
        print("Calibrated R0:", self.r_zero)
        return self.r_zero

    def get_ppm(self):
        if self.r_zero is None:
            raise ValueError("Sensor not calibrated. Run .calibrate() first.")
        rs = self.get_resistance()
        ratio = rs / self.r_zero
        ppm = 116.6020682 * (ratio ** -2.769034857)
        return ppm
