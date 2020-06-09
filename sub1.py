import json
import paho.mqtt.subscribe as sub
import paho.mqtt.client as mqtt
import sqlite3
import time

broker_address = "13.76.87.87"
client = mqtt.Client("TurnOn1")
client.connect(broker_address)
client.subscribe("Control")
key1 = 5
key2 = 5

def check(a):
    global key1
    global key2
    if a == 1:
        key1 -= 1
        if key1 < 0:
            key1 = 5
            return True
    else:
        key2 -= 1
        if key2 < 0:
            key2 = 5
            return True
    return False

def print_msg(client, userdata, message):
    data = str(message.payload.decode("utf-8"))
    data = json.loads(data)
    if data["ID"] == 1:
        if int(data["value"][0]) > 95 or int(data["value"][1]) > 95:
            client.publish("Control", "ON")
        if check(1):
            print(f"""Temperature: {data["value"][0]} Humidity: {data["value"][1]}""")
    else:
        if int(data["value"]) > 95:
            client.publish("Control","ON")
        if check(2):
            print(f"""Intensity: {data["value"]}""")
    # print(data["ID"], data["value"])

sub.callback(print_msg, "Temp/Air/Light", hostname ="13.76.87.87")
