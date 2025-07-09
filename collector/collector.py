from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests



app = Flask(__name__)

load_dotenv()

token = os.getenv('NEMO_TOKEN')
url = os.getenv('NEMO_URL')

headers = {
    "Authorization": f"Token {token}"
}

@app.route("/esp/receive_send", methods = ["POST"])
def receive_send():
    data = request.get_json()
    created_date = data.get("created_date")
    sensor_value = data.get("value")
    sensor_id = data.get("sensor")

    if not sensor_id or not sensor_value or not created_date:
        return jsonify({"error": "data packet missing data"}), 400
    
    nemo_payload = {
        "created_date": created_date,
        "value" : sensor_value,
        "sensor": sensor_id 
    }


    nemo_response = requests.post(url, json=nemo_payload, headers=headers)

    if nemo_response.status_code == 200:
        return jsonify({"message": "data packet successfully sent to NEMO"})
    else:
        return jsonify({"error": "the packet did not go through succesfully"}), nemo_response.status_code

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8000)
