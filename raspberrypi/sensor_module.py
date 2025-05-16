# sensor_module.py
import random
import time

def get_sensor_data():
    return [
        {"sensor_id": 1, "value": round(random.uniform(20, 25), 1)},
        {"sensor_id": 2, "value": round(random.uniform(40, 60), 1)}
    ]
