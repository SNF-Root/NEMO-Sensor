from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

JSON_FILE_PATH = "sensor_data.json"

# Load existing data or return empty list
def load_sensor_data():
	if os.path.exists(JSON_FILE_PATH):
		with open(JSON_FILE_PATH, 'r') as f:
			return json.load(f)
	return []

# Save updated sensor data
def save_sensor_data(data_list):
	with open(JSON_FILE_PATH, 'w') as f:
		json.dump(data_list, f, indent=2)

@app.route('/submit', methods=['POST'])
def receive_sensor_data():
	try:
		sensor_entries = request.json

		if not isinstance(sensor_entries, list):
			return jsonify({"error": "Expected a list of sensor entries"}), 400

		data_list = load_sensor_data()

		for entry in sensor_entries:
			sensor_id = entry.get("sensor_id")
			value = entry.get("value")

		if sensor_id is None or value is None:
			print(f"Skipping invalid entry: {entry}")
			continue

        	# Overwrite or append the sensor entry
			updated = False
			for d in data_list:
				if d["sensor_id"] == sensor_id:
					d["value"] = round(float(value), 1)
					updated = True
					break
				if not updated:
					data_list.append({"sensor_id": sensor_id, "value": round(float(value), 1)})

		save_sensor_data(data_list)

		return jsonify({"status": "success", "updated_sensors": len(sensor_entries)}), 200

	except Exception as e:
		return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)


 
