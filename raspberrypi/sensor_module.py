# sensor_module.py
# Template for reading sensor data and formatting it for the Collector

# 👉 Import your sensor’s library here
# Example for SHT31 sensor:
import board
import busio
import adafruit_sht31d  # 🔁 Replace this with the library for your sensor

# 👉 Sensor setup (only runs once)
# For SHT31, uses I2C bus
i2c = busio.I2C(board.SCL, board.SDA)  # 🔁 If your sensor uses UART or GPIO, change this
sensor = adafruit_sht31d.SHT31D(i2c)   # 🔁 Replace with your sensor’s constructor

def get_sensor_data():
    """
    Reads from the sensor and returns a list of dicts like:
    [
        {"sensor_id": 1, "value": temperature},
        {"sensor_id": 2, "value": humidity}
    ]
    """
    try:
        # 👉 Read sensor values here
        # For SHT31: temperature and humidity
        temperature = round(sensor.temperature, 1)              # 🔁 Replace with your sensor’s method
        humidity = round(sensor.relative_humidity, 1)           # 🔁 Replace with your sensor’s method

        # 👉 Return the sensor values with correct sensor_id numbers
        return [
            {"sensor_id": 1, "value": temperature},  # Change sensor_id=1 to match your NEMO sensor
            {"sensor_id": 2, "value": humidity}      # Change sensor_id=2 to match your NEMO sensor
        ]

    except Exception as e:
        print(f"Sensor read error: {e}")
        return []  # Returning an empty list if reading fails

