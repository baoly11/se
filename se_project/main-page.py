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
    return render_template("login-form.html", user = current_user)


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
        return "Wrong username or password"
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
        info1 = db.execute("SELECT * FROM temp_air").fetchall()
        info2 = db.execute("SELECT * FROM light").fetchall()
        print('get data successfully')
    finally:
        db.close()
    info1 = [dict(info1[len(info1) - 1])]
    info2 = [dict(info2[len(info2) - 1])]
    contents = info1 + info2
    return jsonify({"success": True, "info": contents})


# @app.route("/homepage", methods=["GET"])
# def homepage():
#     return render_template("homepage.html")

