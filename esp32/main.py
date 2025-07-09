import network
import time
import urequests
import ntptime
from machine import Pin, I2C, deepsleep
from sht31 import SHT31
from read_env import load_env
from mq135 import MQ135
from w104 import W104

# Solid blue LED to indicate startup
LED = Pin(2, Pin.OUT)
LED.on()

version = "1.1.0" # Change version number upon appropriate updates
print(f"NEMO Sensor v{version}")

# Load .env variables
config = load_env()
SSID = config.get("SSID")
PASSWORD = config.get("PASSWORD")
API_URL = config.get("API_URL")
AUTH_TOKEN = config.get("AUTH_TOKEN")
GAS_PIN = int(config.get("MQ135_PIN"))
SOUND_PIN = int(config.get("W104_PIN"))
TEMP_ID = int(config.get("SHT31_TEMP_ID"))
HUMD_ID = int(config.get("SHT31_HUMD_ID"))
SOUND_ID = int(config.get("W104_ID"))
GAS_ID = int(config.get("MQ135_ID"))
SLEEP_TIME=int(config.get("SLEEP_TIME_IN_MS"))

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
mq135 = MQ135(GAS_PIN)

# Initialize W104 sound sensor
sound = W104(pin=SOUND_PIN)


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            LED.off()
            time.sleep(0.2)
            LED.on()
            time.sleep(0.3)
            timeout -= 1

    ip = wlan.ifconfig()[0]
    if ip == "0.0.0.0":
        print("\n❌ Wi-Fi failed — no IP address assigned.")
        for _ in range(3):  # Blink for failure
            LED.on(); time.sleep(0.3); LED.off(); time.sleep(0.3)
        return False

    print("\n✅ Connected with IP:", ip)
    LED.on()  # Solid ON again after connection
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
            # Pulse LED briefly to indicate success
            LED.off(); time.sleep(0.1); LED.on()
            return
        except Exception as e:
            print(f"Post failed on attempt {attempt + 1}: {e}")
            attempt += 1
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("❌ Failed to post after retries.")


def main():
    global sht

    connect_wifi()

    try:
        ntptime.settime()
        print("Time synced via NTP")
    except Exception as e:
        print("NTP sync failed:", e)

    if sht:
        try:
            temp, hum = sht.get_temp_humi()
            if temp is not None:
                post_sensor_data(TEMP_ID, temp)
                time.sleep(0.5)
            if hum is not None:
                post_sensor_data(HUMD_ID, hum)
        except Exception as e:
            print("SHT31 read error:", e)

    if mq135.r_zero is None:
        print("First run: calibrating...")
        mq135.calibrate()  
        # ^ This is assuming it is calibrated in FRESH OUTDOOR AIR for
        #   reasonable values. Otherwise, ppm is just relative (rise and fall trends)
    else:
        try:
            rs = mq135.get_resistance()
            if rs <= 0 or rs > 100000:  # Optional: reject nonsense readings
                raise ValueError("MQ135 not responding (invalid resistance)")
            
            ppm = mq135.get_ppm()
            print("CO₂ PPM:", ppm)
            post_sensor_data(GAS_ID, ppm)
        except Exception as e:
            print("⚠️ Skipping MQ135 —", e)

    try:
        db = sound.read_db()
        if db is not None:
            print("Sound level:", db, "dB")
            post_sensor_data(SOUND_ID, db)  # replace with your actual sensor ID
        else:
            print("🔇 Sound level too low — skipping")
    except Exception as e:
        print("⚠️ Sound read error:", e)

    print(f"Going to deep sleep for {SLEEP_TIME/60000} minutes...")
    LED.off()
    time.sleep(1)
    deepsleep(SLEEP_TIME)  # sleep time in ms (60,000 ms = 1 minute)
    # Using 60,000 for testing, but production will be closer to 15-20 minutes.

main()