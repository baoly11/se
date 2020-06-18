import os
import json
import paho.mqtt.subscribe as sub
import paho.mqtt.publish as publish
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime


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


key1 = 1
key2 = 0
light_threshold = 0

def check(a):
    global key1
    global key2
    if a == 1:
        key1 -= 1
        if key1 <= 0:
            key1 = 9
            return True
    else:
        key2 -= 1
        if key2 <= 0:
            key2 = 11
            return True
    return False


def print_msg(client, userdata, message):
    global light_threshold
    data = str(message.payload.decode("utf-8"))
    data = json.loads(data)
    t = datetime.now()

    # get new threshold
    if check(2):
        new_threshold = db.execute("SELECT * FROM device WHERE id IN (SELECT MAX(id) FROM device)").fetchone()
        light_threshold = new_threshold[3]

    # test
    if data["ID"] == 2:
        if int(data["value"]) > light_threshold:
            device_control()
        print(f"""Light: {data["value"]}""")
        try:
            db.execute("INSERT INTO light (device_id, light_intensity, time) VALUES (:device_id, :light, :time)",
                       {"device_id": 2, "light": data["value"], "time": t.strftime('%Y-%m-%d %H:%M:%S')})
            db.commit()
        finally:
            db.close()
        print("Done")

    # get real data
    # if data[0]["values"][0] > light_threshold:
    #     device_control()
    # if check(1):
    #     try:
    #         db.execute("INSERT INTO light (device_id, light_intensity, time) VALUES (:device_id, :light, :time)",{"device_id": 2, "light": data[0]["values"][0],"time": t.strftime('%Y-%m-%d %H:%M:%S')})
    #         db.commit()
    #     finally:
    #         db.close()
    # print(f"""Intensity: {data[0]["values"][0]}""")


def device_control():
    p_data = {}
    p_data["device_id"] = "Light_D"
    p_data["value"] = ["1", "50"]
    data = json.dumps(p_data)
    publish.single("Topic/LightD", data, hostname="52.230.126.225")
    # publish.single("Topic/LightD", data, hostname="13.76.250.158", auth={'username': "BKvm2", 'password': "Hcmut_CSE_2020"})


sub.callback(print_msg, "Temp/Air/Light", hostname ="52.230.126.225")
# sub.callback(print_msg, "Topic/Light", hostname="13.76.250.158", auth={'username':"BKvm2", 'password':"Hcmut_CSE_2020"})
