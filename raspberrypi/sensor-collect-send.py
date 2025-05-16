import time
import json
import requests
from abc import ABC, abstractmethod
import board
import busio
import adafruit_sht31d
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from dotenv import load_dotenv
import os

load_dotenv()
collector_url = os.getenv("COLLECTOR_URL")
if not collector_url:
	raise ValueError("COLLECTOR_URL not defined in .env file")

# ---------------- Base Sensor Class ----------------
class Sensor(ABC):
	@abstractmethod
	def read(self):
		pass

# ---------------- SHT31 I2C Sensor ----------------
class SHT31Sensor(Sensor):
	def __init__(self, sensor_id_temp, sensor_id_humid):
		i2c = busio.I2C(board.SCL, board.SDA)
		self.sensor = adafruit_sht31d.SHT31D(i2c)
		self.sensor_id_temp = sensor_id_temp
		self.sensor_id_humid = sensor_id_humid

	def read(self):
		return [
        	{"sensor_id": self.sensor_id_temp, "value": round(self.sensor.temperature, 2)},
        	{"sensor_id": self.sensor_id_humid, "value": round(self.sensor.relative_humidity, 2)}
    	]

# ---------------- Mock UART Sensor ----------------
class MockUARTSensor(Sensor):
	def __init__(self, sensor_id_pm25):
		self.sensor_id_pm25 = sensor_id_pm25

	def read(self):
		import random
		pm25 = round(10 + random.uniform(-1, 1), 2)
		return [{"sensor_id": self.sensor_id_pm25, "value": pm25}]

# ------------- W104 w/ ADS1015 I2C Sensor -------------
class W104SoundSensor:
	def __init__(self, sensor_id, channel=0):
		i2c = busio.I2C(board.SCL, board.SDA)
		self.ads = ADS.ADS1015(i2c)
		self.chan = AnalogIn(self.ads, getattr(ADS, f'P{channel}'))  # e.g. channel=0 → ADS.P0
		self.sensor_id = sensor_id

	def read(self):
		voltage = round(self.chan.voltage, 3)  # raw voltage reading
    	# Optional: convert to dB using a custom calibration if you have one
		return [{"sensor_id": self.sensor_id, "value": voltage}]

# ---------------- Main Loop ----------------
def run_sensors(sensors, interval=60, collector_url=collector_url):
	while True:
		payload = []
		for sensor in sensors:
			try:
				readings = sensor.read()
				payload.extend(readings)
			except Exception as e:
				print(f"Error reading sensor: {e}")

		print("Sending:", json.dumps(payload))

		try:
			response = requests.post(collector_url, json=payload)
			print(f"Collector response: {response.status_code} - {response.text}")
		except Exception as e:
			print(f"Error sending data to collector: {e}")

		time.sleep(interval)

# ---------------- Start ----------------
if __name__ == "__main__":
	sensors = [
    	SHT31Sensor(sensor_id_temp=5, sensor_id_humid=7),
    	# MockUARTSensor(sensor_id_pm25=3)
	]
	run_sensors(sensors)
