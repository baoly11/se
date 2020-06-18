import os
import json
import paho.mqtt.subscribe as sub
import paho.mqtt.publish as publish
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime


# Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))


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
    t = datetime.now()
    if data["ID"] == 1:
    # if data[0]["device_id"] == 'TempHumi ':
        print("running...")
        if int(data["value"][0]) > 80 or int(data["value"][1]) > 80:
            device_control(0)
        print(f"""Temperature: {data["value"][0]} Humidity: {data["value"][1]}""")
        # try:
        #     db.execute("INSERT INTO temp_air (device_id, temperature, humidity, time) VALUES (:device_id, :temperature, :humidity, :time)",
        #                {"device_id": 1, "temperature": data[0]["values"][0], "humidity": data[0]["values"][1], "time": t.strftime('%Y-%m-%d %H:%M:%S')})
        #     db.commit()
        # finally:
        #     db.close()
        # print(f"""Temperature: {data[0]["values"][0]} Humidity: {data[0]["values"][1]}""")
        # emit('update realtime', {'temp':  data[0]["values"][0], 'humi': data[0]["values"][1]}, broadcast = True)


def device_control(x):
    p_data = {}
    p_data["device_id"] = "Light_D"
    p_data["value"] = ["1", "50"]
    data = json.dumps(p_data)
    if x == 0:
        publish.single("Topic/LightD", data, hostname="52.230.126.225")
    else:
        publish.single("Topic/LightD", data, hostname="13.76.250.158", auth={'username': "BKvm2", 'password': "Hcmut_CSE_2020"})


sub.callback(print_msg, "Temp/Air/Light", hostname ="52.230.126.225")
# sub.callback(print_msg, "Topic/TempHumi", hostname="13.76.250.158", auth={'username':"BKvm2", 'password':"Hcmut_CSE_2020"})
