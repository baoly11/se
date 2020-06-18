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

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


key1 = 1
key2 = 0
temp_threshold = 0
humi_threshold = 0

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
        if key2 < 0:
            key2 = 5
            return True
    return False


def print_msg(client, userdata, message):
    global temp_threshold
    global humi_threshold
    data = str(message.payload.decode("utf-8"))
    data = json.loads(data)
    t = datetime.now()

    # get new threshold
    if check(2):
        new_threshold = db.execute("SELECT * FROM device WHERE id IN (SELECT MAX(id) FROM device)").fetchone()
        temp_threshold = new_threshold[1]
        humi_threshold = new_threshold[2]

    # test
    if data["ID"] == 1:
        if int(data["value"][0]) > temp_threshold or int(data["value"][1]) > humi_threshold:
            device_control()
        print(f"""Temperature: {data["value"][0]} Humidity: {data["value"][1]}""")
        try:
            db.execute(
                "INSERT INTO temp_air (device_id, temperature, humidity, time) VALUES (:device_id, :temperature, :humidity, :time)",
                {"device_id": 1, "temperature": data["value"][0], "humidity": data["value"][1],
                 "time": t.strftime('%Y-%m-%d %H:%M:%S')})
            db.commit()
        finally:
            db.close()
        print("Done")

    # get real data
    # if data[0]["values"][0] > temp_threshold or data[0]["values"][1] > humi_threshold:
    #     device_control()
    # try:
    #     db.execute("INSERT INTO temp_air (device_id, temperature, humidity, time) VALUES (:device_id, :temperature, :humidity, :time)",
    #                {"device_id": 1, "temperature": data[0]["values"][0], "humidity": data[0]["values"][1], "time": t.strftime('%Y-%m-%d %H:%M:%S')})
    #     db.commit()
    # finally:
    #     db.close()
    # print(f"""Temperature: {data[0]["values"][0]} Humidity: {data[0]["values"][1]}""")


def device_control():
    p_data = {}
    p_data["device_id"] = "Light_D"
    p_data["value"] = ["1", "50"]
    data = json.dumps(p_data)
    publish.single("Topic/LightD", data, hostname="52.230.126.225")
    # publish.single("Topic/LightD", data, hostname="13.76.250.158", auth={'username': "BKvm2", 'password': "Hcmut_CSE_2020"})


sub.callback(print_msg, "Temp/Air/Light", hostname ="52.230.126.225")
# sub.callback(print_msg, "Topic/TempHumi", hostname="13.76.250.158", auth={'username':"BKvm2", 'password':"Hcmut_CSE_2020"})
