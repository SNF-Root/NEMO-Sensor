import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import time
import json

# Load .env token, NEMO API endpoint, JSON file path
load_dotenv()
token = os.getenv('NEMO_TOKEN')
url = os.getenv('API_URL')
master_list = os.getenv('JSON_FILE_PATH')

headers = {
	"Authorization": f"Token {token}"
}

def push_from_json():
	try:
		with open(master_list, 'r') as f:
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
 
