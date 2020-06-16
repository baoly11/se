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

# To control device
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
    # if data["ID"] == 1:
    if data[0]["device_id"] == 'TempHumi ':
        print("running...")
        # if int(data["value"][0]) > 95 or int(data["value"][1]) > 95:
        #     client.publish("Control", "ON")
        # if check(1):
        #     db.execute("INSERT INTO temp_air (device_id, temperature, humidity, time) VALUES (:device_id, :temperature, :humidity, :time)",
        #                {"device_id": data["ID"], "temperature": data["value"][0], "humidity": data["value"][1], "time": t.strftime('%Y-%m-%d %H:%M:%S')})
        #     db.commit()
        #     print(f"""Temperature: {data["value"][0]} Humidity: {data["value"][1]}""")
        db.execute("INSERT INTO temp_air (device_id, temperature, humidity, time) VALUES (:device_id, :temperature, :humidity, :time)",
                   {"device_id": 1, "temperature": data[0]["values"][0], "humidity": data[0]["values"][1], "time": t.strftime('%Y-%m-%d %H:%M:%S')})
        db.commit()
        print(f"""Temperature: {data["values"][0]} Humidity: {data["values"][1]}""")
    # else:
    #     print("hi2")
    #     if int(data["value"]) > 95:
    #         client.publish("Control","ON")
    #     if check(2):
    #         # conn = sqlite3.connect('warehouse.db')
    #         # cursor = conn.cursor()
    #         # cursor.execute(f"""INSERT INTO test2 VALUES(datetime('now', 'localtime'),{data["ID"]} , {data["value"]})""")
    #         # conn.commit()
    #         # cursor.close()
    #         # conn.close()
    #         db.execute("INSERT INTO light (device_id, light, time) VALUES (:device_id, :light, :time)",
    #                    {"device_id": data["ID"], "light": data["value"],"time": t.strftime('%Y-%m-%d %H:%M:%S')})
    #         db.commit()
    #         print(f"""Intensity: {data["value"]}""")
    # print(data["ID"], data["value"])

# sub.callback(print_msg, "Temp/Air/Light", hostname ="52.230.126.225")
sub.callback(print_msg, "Topic/TempHumi", hostname="13.76.250.158", auth={'username':"BKvm2", 'password':"Hcmut_CSE_2020"})