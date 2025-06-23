from machine import ADC, Pin
import ujson

class MQ135:
    def __init__(self, pin_num, r_load=10.0, r0_file="mq135_r0.json"):
        self.adc = ADC(Pin(pin_num))
        self.adc.atten(ADC.ATTN_11DB)
        self.r_load = r_load
        self.r0_file = r0_file
        self.r_zero = self.load_r0()

    def get_voltage(self):
        return self.adc.read() / 4095.0 * 3.3

    def get_resistance(self):
        v_out = self.get_voltage()
        if v_out == 0:
            return -1
        return self.r_load * (3.3 - v_out) / v_out

    def calibrate(self):
        rs = self.get_resistance()
        self.r_zero = rs
        self.save_r0(rs)
        print("Calibrated R0:", rs)
        return rs

    def get_ppm(self):
        if self.r_zero is None:
            raise ValueError("R0 not set. Calibrate first.")
        rs = self.get_resistance()
        ratio = rs / self.r_zero
        return 116.6020682 * (ratio ** -2.769034857)

    def save_r0(self, r0):
        with open(self.r0_file, "w") as f:
            ujson.dump({"r0": r0}, f)

    def load_r0(self):
        try:
            with open(self.r0_file, "r") as f:
                return ujson.load(f)["r0"]
        except:
            return None
