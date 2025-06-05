import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import time
import random

load_dotenv()
token = os.getenv('NEMO_TOKEN')
headers = {

    "Authorization": f"Token {token}"

}
def furnacePush():


   

    data = {

        "created_date": datetime.now(timezone(timedelta(hours=-7))).isoformat(),

        "value": 0, 

        "sensor": 1

    }

 

    # API endpoint

    url = "https://nemo-dev.stanford.edu/api/sensors/sensor_data/"

 

    # Send the data as JSON

    response = requests.post(url, json=data, headers=headers)

 

    print(response.status_code)

    print(response.json())

   

while True:

    furnacePush()
    time.sleep(5)