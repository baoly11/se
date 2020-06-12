from flask import Flask, render_template, request, jsonify
import sqlite3


app = Flask(__name__)
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
    if request.method == "GET":
        return "Please enter your name!"
    name = request.form.get("name")
    pw = request.form.get("password")
    if password != pw or user_name != name:
        return "Wrong username or password"
    else:
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
    conn = sqlite3.connect('warehouse.db')
    cursor = conn.cursor()
    data1 = cursor.execute(f"""SELECT * FROM test1 WHERE time < '{end_date}' AND time > '{begin_date}'""").fetchall()
    data2 = cursor.execute(f"""SELECT * FROM test2 WHERE time < '{end_date}' AND time > '{begin_date}'""").fetchall()
    cursor.close()
    conn.close()
    result = []
    for x in data1:
        result.append(f"Time: {x[0]}    |    Device ID: {x[1]}    |    Temperature: {x[2]}    |    Humidity: {x[3]}")
    for x in data2:
        result.append(f"Time: {x[0]}    |    Device ID: {x[1]}    |    Light intensity: {x[2]}")
    return render_template("display_search.html", r = result)

def check_input(i):
    if i == '':
        return 0
    else:
        return int(i)