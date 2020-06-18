import os
from flask import Flask, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_socketio import SocketIO, emit
# import sqlite3
from datetime import datetime


app = Flask(__name__)
socketio = SocketIO(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

current_user = 'Guest'
user_name = 'user1'
password = "12345"


@app.route("/")
def index():
    return render_template("login-form.html")


@app.route("/")
def logout():
    global current_user
    current_user = 'Guest'
    return render_template("login-form.html")
# @app.route("/login")
# def login():
#     return render_template("get-user-name.html")


@app.route("/home", methods=["POST"])
def authorize():
    global user_name
    global password
    global current_user
    name = request.form.get("name")
    pw = request.form.get("password")
    if password != pw or user_name != name:
        return render_template("login-form.html",r = True)
    else:
        current_user = name
        return render_template("homepage.html")


@app.route("/home", methods=["GET"])
def return_home():
    global current_user
    if current_user== 'Guest':
        return "Please login"
    return render_template("homepage.html")


@app.route("/search-page")
def search():
    global current_user
    if current_user == 'Guest':
        return "Please login"
    return render_template("search-page.html")


@app.route('/search-result', methods=["POST"])
def get():
    begin_date = f"""{check_input(request.form.get("fyear"))}-{check_input(request.form.get("fmonth")):02d}-{check_input(request.form.get("fday")):02d} {check_input(request.form.get("fhour")):02d}:{check_input(request.form.get("fminute")):02d}:00"""
    end_date = f"""{check_input(request.form.get("tyear"))}-{check_input(request.form.get("tmonth")):02d}-{check_input(request.form.get("tday")):02d} {check_input(request.form.get("thour")):02d}:{check_input(request.form.get("tminute")):02d}:00"""
    result = []
    print(begin_date)
    print(end_date)
    data1 = db.execute(f"""SELECT * FROM temp_air WHERE time BETWEEN '{begin_date}'::timestamp AND '{end_date}'::timestamp""").fetchall()
    data2 = db.execute(f"""SELECT * FROM light WHERE time BETWEEN '{begin_date}'::timestamp AND '{end_date}'::timestamp""").fetchall()
    for x in data1:
        result.append(f"Time: {x[4]}    |    Device ID: {x[3]}    |    Temperature: {x[1]}    |    Humidity: {x[2]}")
    for x in data2:
        result.append(f"Time: {x[3]}    |    Device ID: {x[2]}    |    Light intensity: {x[1]}")
    return render_template("display-search.html", r = result)


def check_input(i):
    if i == '':
        return 0
    else:
        return int(i)


@app.route("/updateHomepage", methods=["POST"])
def updateHomepage():
    try:
        info1 = db.execute("SELECT * FROM temp_air WHERE id IN (SELECT MAX(id) FROM temp_air)").fetchone()
        info2 = db.execute("SELECT * FROM light WHERE id IN (SELECT MAX(id) FROM light)").fetchone()
        device = db.execute("SELECT * FROM device WHERE id IN (SELECT MAX(id) FROM device)").fetchone()
        print('get data successfully')
    finally:
        db.close()
    info1 = dict(info1)
    info2 = dict(info2)
    device = dict(device)
    return jsonify({"success": True, "info1": info1, "info2": info2, "device": device})


# @app.route("/homepage", methods=["GET"])
# def homepage():
#     return render_template("homepage.html")


@app.route("/device-setting")
def device_setting():
    return render_template("device-setting.html")

@app.route("/update", methods=["POST"])
def update():
    time = str(datetime.now().replace(microsecond=0))
    try:
        temp = int(request.form.get("temp"))
        light = int(request.form.get("light"))
        humidity = int(request.form.get("humidity"))
    except:
        return jsonify({"success":True, "response":"Wrong input type!"})

    db.execute("INSERT INTO device (temperature, light, humidity, time) VALUES (:temp, :light, :humidity, :time)",
                {"temp": temp, "light": light, "humidity": humidity, "time":time})
    db.commit()
    return jsonify({"success":True, "response":"Device adjust successfully!"})



if __name__== "__main__":
    socketio.run(app)
