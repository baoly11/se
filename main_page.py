import os
from flask import Flask, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# import sqlite3


app = Flask(__name__)


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
    return render_template("intro.html", user = current_user)


@app.route("/login")
def login():
    return render_template("get_user_name.html")


@app.route("/", methods=["POST","GET"])
def authorize():
    global user_name
    global password
    global current_user
    if request.method == "GET":
        return "Please enter your name!"
    name = request.form.get("name")
    pw = request.form.get("password")
    if password != pw or user_name != name:
        return "Wrong username or password"
    else:
        current_user = name
        return render_template("intro.html", user = user_name)


@app.route("/search")
def search():
    if user_name == 'Guest':
        return "Please enter your name!"
    return render_template("search.html")


@app.route('/search-result', methods=["POST"])
def get():
    begin_date = f"""{check_input(request.form.get("fyear"))}-{check_input(request.form.get("fmonth")):02d}-{check_input(request.form.get("fday")):02d} {check_input(request.form.get("fhour")):02d}:{check_input(request.form.get("fminute")):02d}:00"""
    end_date = f"""{check_input(request.form.get("tyear"))}-{check_input(request.form.get("tmonth")):02d}-{check_input(request.form.get("tday")):02d} {check_input(request.form.get("thour")):02d}:{check_input(request.form.get("tminute")):02d}:00"""
    # conn = sqlite3.connect('warehouse.db')
    # cursor = conn.cursor()
    # data1 = cursor.execute(f"""SELECT * FROM temp_air WHERE time < '{end_date}' AND time > '{begin_date}'""").fetchall()
    # data2 = cursor.execute(f"""SELECT * FROM light WHERE time < '{end_date}' AND time > '{begin_date}'""").fetchall()
    # cursor.close()
    # conn.close()
    result = []
    print(begin_date)
    print(end_date)
    data1 = db.execute(f"""SELECT * FROM temp_air WHERE time BETWEEN '{begin_date}'::timestamp AND '{end_date}'::timestamp""").fetchall()
    data2 = db.execute(f"""SELECT * FROM light WHERE time BETWEEN '{begin_date}'::timestamp AND '{end_date}'::timestamp""").fetchall()
    for x in data1:
        result.append(f"Time: {x[4]}    |    Device ID: {x[3]}    |    Temperature: {x[1]}    |    Humidity: {x[2]}")
    for x in data2:
        result.append(f"Time: {x[3]}    |    Device ID: {x[2]}    |    Light intensity: {x[1]}")

    return render_template("display_search.html", r = result)


def check_input(i):
    if i == '':
        return 0
    else:
        return int(i)