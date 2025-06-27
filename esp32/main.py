import network
import time
import urequests
import ntptime
from machine import Pin, I2C, deepsleep
from sht31 import SHT31
from read_env import load_env
from mq135 import MQ135

# Load .env variables
config = load_env()
SSID = config.get("SSID")
PASSWORD = config.get("PASSWORD")
API_URL = config.get("API_URL")
AUTH_TOKEN = config.get("AUTH_TOKEN")

# Initialize I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Detect and initialize SHT31 if present
sht = None
try:
    devices = i2c.scan()
    if 0x44 in devices:  # default I2C address of SHT31
        sht = SHT31(i2c)
        print("✅ SHT31 detected and initialized.")
    else:
        print("⚠️ SHT31 not detected — skipping temperature/humidity reading.")
except Exception as e:
    print("I2C error during SHT31 detection:", e)
    sht = None


# Initialize MQ135
mq135 = MQ135(34)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(0.5)
            print(".", end="")
            timeout -= 1

    ip = wlan.ifconfig()[0]
    if ip == "0.0.0.0":
        print("\n❌ Wi-Fi failed — no IP address assigned.")
        return False

    print("\n✅ Connected with IP:", ip)
    return True

def get_iso_timestamp():
    t = time.localtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(*t[:6])

def post_sensor_data(sensor_id, value, max_retries=3, delay=2):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {AUTH_TOKEN}'
    }
    data = {
        'value': round(value, 1),
        'sensor': sensor_id,
        'created_date': get_iso_timestamp()
    }

    attempt = 0
    while attempt < max_retries:
        try:
            print(f"Posting attempt {attempt + 1}:", data)
            response = urequests.post(API_URL, headers=headers, json=data)
            print("Response:", response.status_code)
            response.close()
            return  # Exit on success
        except Exception as e:
            print(f"Post failed on attempt {attempt + 1}: {e}")
            attempt += 1
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("❌ Failed to post after retries.")


def main():
    connect_wifi()

    try:
        ntptime.settime()
        print("Time synced via NTP")
    except Exception as e:
        print("NTP sync failed:", e)

    # try:
    #     temp, hum = sht.get_temp_humi()
    #     if temp is not None:
    #         post_sensor_data(5, temp)
    #         time.sleep(0.5)  # short delay to stabilize socket
    #     if hum is not None:
    #         post_sensor_data(7, hum)
    # except Exception as e:
    #     print("SHT31 error:", e)

    if mq135.r_zero is None:
        print("First run: calibrating...")
        mq135.calibrate() 
        
        # ^ This is assuming it is calibrated in FRESH OUTDOOR AIR for
        #   reasonable values. Otherwise, ppm is just relative (rise and fall trends)

        try:
            ppm = mq135.get_ppm()
            print("CO₂ PPM:", ppm)
            post_sensor_data(8, ppm)
        except Exception as e:
            print("MQ135 read error:", e)
    else:
        try:
            ppm = mq135.get_ppm()
            print("CO₂ PPM:", ppm)
            post_sensor_data(8, ppm)
        except Exception as e:
            print("MQ135 read error:", e)



    print("Going to deep sleep for 5 minutes...")
    time.sleep(1)
    deepsleep(300000)  # sleep time in ms (60,000 ms = 1 minute)

main()
