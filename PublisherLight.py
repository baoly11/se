import json
import paho.mqtt.client as mqtt
import time
from random import seed, randint, random
import datetime

broker_address = "13.76.87.87"
client = mqtt.Client("GenerateFakeLight")
client.connect(broker_address)
client.subscribe("Temp/Air")

while(True):
    seed(int(time.time()))
    public_data = {}
    public_data["ID"] = 2
    public_data["value"] = str(randint(0,100))
    public_data_json_packet = json.dumps(public_data)
    client.publish("Temp/Air/Light",public_data_json_packet)
    time.sleep(3)