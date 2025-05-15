import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import time
import json

# Load .env token
load_dotenv()
token = os.getenv('NEMO_TOKEN')

headers = {
	"Authorization": f"Token {token}"
}

# Path to your JSON file
JSON_FILE_PATH = "sensor_data.json"

# NEMO API endpoint
url = "https://nemo-dev.stanford.edu/api/sensors/sensor_data/"

def push_from_json():
	try:
    	with open(JSON_FILE_PATH, 'r') as f:
        	sensor_list = json.load(f)

    	for entry in sensor_list:
        	sensor_id = entry.get("sensor_id")
        	value = entry.get("value")

        	if sensor_id is None or value is None:
            	print(f"Skipping incomplete entry: {entry}")
            	continue

        	data = {
            	"created_date": datetime.now(timezone(timedelta(hours=-7))).isoformat(),
            	"value": round(float(value), 1),
            	"sensor": int(sensor_id)
        	}

        	response = requests.post(url, json=data, headers=headers)

        	print(f"Sensor {sensor_id}: {response.status_code} - {response.json()}")

	except Exception as e:
    	print(f"Error loading or posting sensor data: {e}")

# Main loop: push every 60 seconds
while True:
	push_from_json()
	time.sleep(60)
 
