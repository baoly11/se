import json
import paho.mqtt.subscribe as sub
import paho.mqtt.client as mqtt
import sqlite3
import time
import datetime
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# broker_address = "52.230.126.225"
# client = mqtt.Client("TurnOn1")
# client.connect(broker_address)
# client.subscribe("Control")

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
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
    t = datetime.datetime.now()
    if data[0]["device_id"] == 'Light':
        print("running...")
    #     if int(data["value"][0]) > 95 or int(data["value"][1]) > 95:
    #         client.publish("Control", "ON")
    #     if check(1):
    #         db.execute("INSERT INTO temp_air (device_id, temperature, humidity, time) VALUES (:device_id, :temperature, :humidity, :time)",
    #                    {"device_id": data["ID"], "temperature": data["value"][0], "humidity": data["value"][1], "time": t.strftime('%Y-%m-%d %H:%M:%S')})
    #         db.commit()
    #         print(f"""Temperature: {data["value"][0]} Humidity: {data["value"][1]}""")
    # else:
    #     if int(data["value"]) > 95:
    #         client.publish("Control","ON")
    #     if check(2):
    #         db.execute("INSERT INTO light (device_id, light_intensity, time) VALUES (:device_id, :light, :time)",
    #                    {"device_id": data["ID"], "light": data["value"],"time": t.strftime('%Y-%m-%d %H:%M:%S')})
    #         db.commit()
    #         print(f"""Intensity: {data["value"]}""")
        db.execute("INSERT INTO light (device_id, light_intensity, time) VALUES (:device_id, :light, :time)",
                   {"device_id": 2, "light": data[0]["values"][0],"time": t.strftime('%Y-%m-%d %H:%M:%S')})
        db.commit()
        print(f"""Intensity: {data[0]["values"][0]}""")

sub.callback(print_msg, "Topic/Light", hostname="13.76.250.158", auth={'username':"BKvm2", 'password':"Hcmut_CSE_2020"})
