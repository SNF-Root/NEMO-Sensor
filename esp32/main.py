import network
import time
import urequests
from machine import Pin, I2C
from sht31 import SHT31
from read_env import load_env
import ntptime

# Load .env variables
config = load_env()
SSID = config.get("SSID")
PASSWORD = config.get("PASSWORD")
API_URL = config.get("API_URL")
AUTH_TOKEN = config.get("AUTH_TOKEN")

# Initialize I2C and SHT31
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sht = SHT31(i2c)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    print("\nConnected:", wlan.ifconfig())

def get_iso_timestamp():
    t = time.localtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(*t[:6])

def post_sensor_data(sensor_id, value):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {AUTH_TOKEN}'
    }
    data = {
        'value': round(value, 2),
        'sensor': sensor_id,
        'created_date': get_iso_timestamp()
    }
    try:
        print("Posting:", data)
        response = urequests.post(API_URL, headers=headers, json=data)
        print("Response:", response.status_code)
        response.close()
    except Exception as e:
        print("Error posting data:", e)

def main():
    connect_wifi()

    try:
        ntptime.settime()
        print("Time synced via NTP")
    except Exception as e:
        print("NTP sync failed:", e)

    while True:
        try:
            temp, hum = sht.get_temp_humi()
            if temp is not None:
                post_sensor_data(5, temp)
            if hum is not None:
                post_sensor_data(7, hum)
        except Exception as e:
            print("Sensor error:", e)
        time.sleep(10)

main()
