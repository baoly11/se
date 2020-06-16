import os

from flask import Flask, render_template, url_for, jsonify,request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import json
import paho.mqtt.subscribe as sub
import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime

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

@app.route("/")
def index():
    return render_template("index.html")

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

@app.route("/updateHomepage", methods=["POST"])
def updateHomepage():    
    try:
        info1 = db.execute("SELECT * FROM temp_air").fetchall()
        info2 = db.execute("SELECT * FROM light").fetchall()
        device = db.execute("SELECT * FROM device").fetchall()
        print('get dat successfully')    
    finally:
        db.close()     
    
    info1 = dict(info1[len(info1)-1])
    info2 = dict(info2[len(info2)-1])
    device = dict(device[len(device)-1])
    return jsonify({"success":True,"info1": info1, "info2": info2, "device": device})

    
@app.route("/homepage", methods=["GET"])
def homepage():
    return render_template("homepage.html")


    