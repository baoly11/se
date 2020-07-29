import os
from flask import Flask, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import json
import paho.mqtt.publish as publish


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
current_order_id = None

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
    begin_date = f"""{check_input(request.form.get("fyear"),"")}-{check_input(request.form.get("fmonth"),"month"):02d}-{check_input(request.form.get("fday"),"day"):02d} {check_input(request.form.get("fhour"),"hour"):02d}:{check_input(request.form.get("fminute"),"min"):02d}:00"""
    end_date = f"""{check_input(request.form.get("tyear"),"")}-{check_input(request.form.get("tmonth"),"month"):02d}-{check_input(request.form.get("tday"),"day"):02d} {check_input(request.form.get("thour"),"hour"):02d}:{check_input(request.form.get("tminute"),"min"):02d}:00"""
    result = []
    print(begin_date)
    print(end_date)
    try:
        data1 = db.execute(f"""SELECT * FROM temp_air WHERE time BETWEEN '{begin_date}'::timestamp AND '{end_date}'::timestamp""").fetchall()
        data2 = db.execute(f"""SELECT * FROM light WHERE time BETWEEN '{begin_date}'::timestamp AND '{end_date}'::timestamp""").fetchall()
    except:
        result = ["Invalid input"]
        return render_template("display-search.html", r=result)
    for x in data1:
        result.append(f"Time: {x[4]}    |    Device ID: {x[3]}    |    Temperature: {x[1]}    |    Humidity: {x[2]}")
    for x in data2:
        result.append(f"Time: {x[3]}    |    Device ID: {x[2]}    |    Light intensity: {x[1]}")
    return render_template("display-search.html", r = result)

def check_input(i,type):
    if i == '':
        return 0
    else:
        r = int(i)
        if type == "day":
            if r > 31 or r < 1:
                return 0
        if type == "month":
            if r > 12 or r < 1:
                return 0
        if type == "hour":
            if r > 24 or r < 1:
                return 0
        if type == "min":
            if r > 24 or r < 1:
                return 0
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

@app.route("/order")
def order():
    if check_user():
        return "Please login!"
    return render_template("order.html")


@app.route("/get-order", methods=["POST"])
def get_order():
    global current_order_id
    id = request.form.get("id")
    result = search_order(id)
    if not result[0]:
        current_order_id = None
        return jsonify({"success": True, "found": False, "msg": result[1]})
    current_order_id = id
    order = result[1]
    return jsonify({"success": True,
                    "id": order[0],
                    "name": order[1],
                    "date": order[2],
                    "status": order[3],
                    "item": order[4],
                    "quantity": order[5],
                    "found": True})

@app.route("/check-order", methods=["POST"])
def check_order():
    id = request.form.get("id")
    print(f"check order {id}")
    result = check_complete_order(id)
    return jsonify({"success": True,
                    "msg":result[1]})

@app.route("/confirm-order", methods=["POST"])
def confirm_order():
    id = request.form.get("id")
    print(f"check order {id}")
    result = check_complete_order(id, True)
    return jsonify({"success": True,
                    "done": result[0],
                    "msg": result[1]})

@app.route("/delete-order", methods=["POST"])
def delete_order():
    id = request.form.get("id")
    print(f"deleting order {id}")
    result = del_order(id)
    return jsonify({"success": True,
                    "done": result[0],
                    "msg": result[1]})

@app.route("/add-item-to-order")
def add_item_to_order():
    global current_order_id
    if current_order_id == None:
        return "Please select a order first!"
    return render_template("add-item-to-order.html", x = current_order_id )

@app.route("/adding-item", methods=["POST"])
def adding_item_to_order():
    global current_order_id
    item_id = request.form.get("itemId")
    if item_id == '':
        return jsonify({"success": True,
                        "msg": "Please enter item id"})
    quantity = request.form.get("quantity")
    if quantity == '':
        quantity = 0;
    print(item_id)
    print(quantity)
    result = add_item_to_order_do(current_order_id, item_id, quantity)
    return jsonify({"success": True,
                    "done": result[0],
                    "msg": result[1]})

@app.route("/remove-item-from-order")
def remove_item_from_order():
    global current_order_id
    if current_order_id == None:
        return "Please select a order first!"
    return render_template("remove-item-from-order.html", x = current_order_id )

@app.route("/removing-item", methods=["POST"])
def removing_item_from_order_do():
    global current_order_id
    item_id = request.form.get("itemId")
    if item_id == '':
        return jsonify({"success": True,
                        "msg": "Please enter item id"})
    result = remove_item_from_order_do(current_order_id, item_id)
    return jsonify({"success": True,
                    "done": result[0],
                    "msg": result[1]})

@app.route("/update-item-quantity-in-order")
def update_item_quantity_in_order():
    global current_order_id
    if current_order_id == None:
        return "Please select a order first!"
    return render_template("update-item-quantity-in-order.html", x = current_order_id )

@app.route("/updating-item", methods=["POST"])
def update_item_quantity_in_order_do():
    global current_order_id
    item_id = request.form.get("itemId")
    if item_id == '':
        return jsonify({"success": True,
                        "msg": "Please enter item id"})
    quantity = request.form.get("quantity")
    if quantity == '':
        quantity = 0;
    result = update_item_quantity_in_order_do(current_order_id, item_id, quantity)
    return jsonify({"success": True,
                    "done": result[0],
                    "msg": result[1]})

@app.route("/create-order")
def create_order():
    if check_user():
        return "Please login!"
    return render_template("create-order.html")

@app.route("/creating-order", methods=["POST"])
def creating_order():
    name = request.form.get("name")
    result = create_order_do(name, [])
    print(name)
    return jsonify({"success": True,
                    "done": result[0],
                    "msg": result[1]})

@app.route("/item")
def index1():
    if check_user():
        return "Please login!"
    return render_template("import_items.html")


@app.route("/manage")
def manage():
    if check_user():
        return "Please login!"
    try:
        items = db.execute("SELECT * FROM item ").fetchall()
    finally:
        db.close()
    return render_template("manage-item.html", items=items)


@app.route("/import", methods=["POST"])
def import_product():
    import_time = str(datetime.now().replace(microsecond=0))
    if len(str(request.form.get("item_id"))) != 6:
        return jsonify({"success": True, "response": "Wrong ID length"})
    try:
        item_id = str(request.form.get("item_id"))
        item_name = str(request.form.get("item_name"))
        item_quantity = int(request.form.get("item_quantity"))
        import_man = str(request.form.get("import_man"))
    except:
        return jsonify({"success": True, "response": "Wrong input type!"})

    db.execute(
        "INSERT INTO item_import (item_id, item_name, item_quantity, import_time, import_man) VALUES (:item_id, :item_name, :item_quantity, :import_time, :import_man)",
        {"item_id": item_id, "item_name": item_name, "item_quantity": item_quantity, "import_time": import_time,
         "import_man": import_man})
    db.commit()

    check_list = db.execute("SELECT item_id FROM item").fetchall()

    if item_id in check_list:
        db.execute("UPDATE item SET quantity = quantity + :item_quantity WHERE item_id = :item_id ",
                   {"item_quantity": item_quantity, "item_id": item_id})
        db.commit()
    else:
        db.execute(f"INSERT INTO item (item_id, name, quantity) VALUES (:item_id, :name, :quantity)", {"item_id": item_id, "name": item_name, "quantity": item_quantity})
        db.commit()
  
    return jsonify({"success": True, "response": "Done!"})


@app.route("/updateItems", methods=["POST"])
def updateItems():
    try:
        items = db.execute("SELECT * FROM item ").fetchall()
    finally:
        db.close()
    print(items)

    lst = []

    for item in items:
        lst.append(dict(item))
    print(lst)

    return jsonify({"success": True, "items": lst})


@app.route("/specific_item/<string:id>")
def specific_item(id):
    if check_user():
        return "Please login!"
    try:
        info = db.execute("SELECT * FROM item_import WHERE item_id = :item_id ", {"item_id": id}).fetchall()
    finally:
        db.close()
    return render_template('specific_item.html', info=info)


@app.route("/device-control")
def device_control():
    if check_user():
        return "Please login!"
    return render_template('device-control.html')

@app.route("/publish-to-device", methods=["POST"])
def publish_to_device():
    air = request.form.get("air")
    fan = request.form.get("fan")
    if air != '':
        try:
            air = int(air)
        except:
            return jsonify({"success": True,
                            "msg": "Invalid input."})
        if air > 100 or air < 1:
            return jsonify({"success": True,
                            "msg": "Invalid input."})
    if fan != '':
        try:
            fan = int(fan)
        except:
            return jsonify({"success": True,
                            "msg": "Invalid input."})
        if fan > 100 or fan < 1:
            return jsonify({"success": True,
                            "msg": "Invalid input."})
    p_data = {}
    p_data["device_id"] = "Air"
    p_data["value"] = f"{air}"
    data1 = json.dumps([p_data])
    publish.single("Control/AirCondition", data1, hostname="52.230.126.225")
    p_data["device_id"] = "Fan"
    p_data["value"] = f"{fan}"
    data2 = json.dumps([p_data])
    publish.single("Control/Fan", data2, hostname="52.230.126.225")
    return jsonify({"success": True,
                    "msg": "Done"})


@app.route("/report")
def report():
    return render_template('mail2.html')

@app.route("/get-info-for-report", methods=["POST"])
def info_report():
    return jsonify({"success": True})


####################################################################################################################################################################################






def search_order(id):
    # Join order_info and item_in_order to get all the information
    print(f"this is the id: {id}")
    try:
        int(id)
    except:
        return (False, "Wrong input type.")
    info = db.execute(
        f"SELECT * FROM (SELECT * FROM order_info WHERE id='{id}') AS O LEFT JOIN item_in_order ON O.id=item_in_order.order_id").fetchall()
    if not info:
        print("Cant find this order.")
        return (False, "Can't find this order.")
    # Get ID to Name list of item
    item_id_name = dict(db.execute("SELECT item_id,name FROM item ").fetchall())
    db.close()
    # Turn all the info in to a list [ID, name, date create, complete status, item_name_list, quantity_list, item_id_list]
    i_n = []
    q = []
    i_i = []
    for x in info:
        if x[5] is not None:
            i_n.append(item_id_name[x[5]])
            q.append(x[6])
            i_i.append(x[5])
    result = [info[0][0], info[0][1], info[0][2], info[0][3], i_n, q, i_i]
    print(result)
    return (True, result)


def check_complete_order(id, do = False):
    info = search_order(id)[1]
    if not info:
        print("Order does not exist")
        return (False, "Order does not exist")
    # Check if order is already completed or not
    if info[3]:
        print("Order is already completed")
        return (False, "Order is already completed")
    if len(info[4]) > 0:
        # Get id_to_name, id_to_quantity, item_order list
        item = db.execute("SELECT item_id,name,quantity FROM item ").fetchall()
        item_id_quantity = dict([(x[0],x[2]) for x in item])
        item_id_name = dict(zip(info[6], info[4]))
        check_list = dict(zip(info[6], info[5]))
        # Check the order
        for item_id in check_list:
            if item_id_quantity[item_id] < check_list[item_id]:
                print(f"We dont have enough {item_id_name[item_id]} for order with ID: {id}")
                return (False, f"We dont have enough {item_id_name[item_id]} for order with ID: {id}")
        if do:
            for item_id in check_list:
                new_quantity = item_id_quantity[item_id] - check_list[item_id]
                db.execute(f""" UPDATE item SET quantity={new_quantity} WHERE item_id='{item_id}' """)
                db.commit()
    msg = ''
    if do:
        db.execute(f"""UPDATE order_info SET status=true WHERE id='{id}'""")
        db.commit()
        print(f"Order with ID: {id} is completed")
        msg = f"Order with ID: {id} is completed"
    else:
        print(f"We have enough item for the order with ID: {id}")
        msg = f"We have enough item for the order with ID: {id}"
    db.close()
    return (True, msg)

def del_order(id):
    # Check if the order exist
    info = search_order(id)[1]
    if not info:
        print("order does not exist")
        return False
    if info[3]:
        print("Cannot delete order - order already complte")
        return (False, "Cannot delete order - order already complte")
    # Delete record from order_info
    db.execute(f"DELETE FROM order_info WHERE id={id}")
    db.commit()
    # Delete record from item_in_order
    db.execute(f"DELETE FROM item_in_order WHERE order_id={id}")
    db.commit()
    db.close()
    print(f"Deleted order with ID: {id}")
    return (True, f"Deleted order with ID: {id}")

def add_item_to_order_do(id, item, quantity):
    # Get the information of the order
    info = search_order(id)[1]
    print(info)
    if not info:
        print("Order does not exist")
        return (False, "Order does not exist")
    if info[3]:
        print("Cannot add - Order is already completed")
        return (False, "Cannot add - Order is already completed")
    # Check if item is in storage
    item_id_name = dict(db.execute("SELECT item_id,name FROM item ").fetchall())
    if item not in item_id_name:
        print(f"{item} is not in storage")
        return (False, f"{item} is not in storage")
    # Check if the order already has that item
    if len(info[6]) > 0:
        if item in info[6]:
            print(f"{item} is already in order")
            return (False, f"{item} is already in order")
    db.execute(f"INSERT INTO item_in_order (order_id, item_id, item_quantity) VALUES (:order_id, :item_id, :item_quantity)", {"order_id": id, "item_id": item, "item_quantity": quantity})
    db.commit()
    db.close
    print("done")
    return (True, "Done")

def remove_item_from_order_do(id, item):
    # Get the information of the order
    info = search_order(id)[1]
    if not info:
        print("Order does not exist")
        return (False, "Order does not exist")
    # Check if the order is completed
    if info[3]:
        print("Cannot update - Order is already completed")
        return (False, "Cannot update - Order is already completed")
    # Check if item is in order
    if len(info[6]) > 0:
        if item not in info [6]:
            print("Item is not in order")
            return (False, "Item is not in order")
    else:
        print("Item is not in order")
        return (False, "Item is not in order")
    # Get id of the item
    # item_id = info[6][info[4].index(item)]
    db.execute(f"DELETE FROM item_in_order WHERE order_id={id} AND item_id='{item}'")
    db.commit()
    db.close()
    print("done")
    return (True, "done")

def update_item_quantity_in_order_do(id, item, quantity):
    # Get the information of the order
    info = search_order(id)[1]
    if not info:
        print("Order does not exist")
        return False
    # Check if the order is completed
    if info[3]:
        print("Cannot update - Order is already completed")
        return False
    # Check if item is in order
    if len(info[6]) > 0:
        if item not in info [6]:
            print("Item is not in order")
            return (False, "Item is not in order")
    else:
        print("Item is not in order")
        return (False, "Item is not in order")
    # Get id of the item
    # item_id = info[6][info[4].index(item)]
    db.execute(f"UPDATE item_in_order SET item_quantity={quantity} WHERE order_id={id} AND item_id='{item}'")
    db.commit()
    db.close()
    print("done")
    return (True, "Done")

def create_order_do(name, item_list):
    # Check if all item in new order exist in storage
    if len(item_list) > 0:
        check_list = dict(db.execute("SELECT name,item_id FROM item ").fetchall())
        for item in item_list:
            if item not in check_list:
                print(f"Fail to add order {name} because storage don't have {item}")
                return (False, f"Fail to add order {name} because storage don't have {item}")
    # Create new record in order_info
    t = datetime.now()
    db.execute("INSERT INTO order_info (name, time, status) VALUES (:name, :time, :status)", {"name": name, "time": t.strftime('%Y-%m-%d %H:%M:%S'), "status": False})
    db.commit()
    # Get the new ID from order_info to add record of item to item_in_order
    new_id = db.execute("SELECT id FROM order_info WHERE id IN (SELECT MAX(id) FROM order_info)").fetchone()[0]
    if len(item_list) > 0:
        for item in item_list:
            db.execute("INSERT INTO item_in_order (order_id, item_id, item_quantity) VALUES (:order_id, :item_id, :item_quantity)",{"order_id": new_id, "item_id": check_list[f"{item}"], "item_quantity": item_list[f"{item}"]})
            db.commit()
    db.close()
    print(f"Finish adding order {name} with id: {new_id}")
    return (True, f"Finish adding order {name} with id: {new_id}")

def check_user():
    global current_user
    if current_user == "Guest":
        return True
    else:
        return False