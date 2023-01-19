from flask import Flask ,request ,jsonify
from uuid import uuid1,uuid4
import os,json,pytz
from datetime import date,datetime
import pandas as pd
db={}
db_filename ="db.json"
#check whether db.json exists in the directory or not
if os.path.exists(db_filename):
    with open(db_filename, 'r') as f:
        db=json.load(f)
else:
    accesskey=str(uuid1())
    secretkey=str(uuid4())
    item_types=[
        "Food","Beverges","Clothing","Stationaries","Electronic Devics",
        "Wearables"
    ]
    db={
        "accesskey":accesskey,
        "secretkey":secretkey,
        "item_types":item_types,
        "users":[]
    }
    with open(db_filename, "w") as f:
        json.dump(db,f,indent=4)
app=Flask(__name__)
@app.route("/signup", methods=['POST'])
def signup():
    if request.method=="POST":
        print(request.form)
        name=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]
        usernames=request.form["username"]

        userDict={
            "name":name,
            "email":email,
            "password":password,
            "username":usernames,
            "purches":{}
        }
        email_list=[]
        for user in db["users"]:
            email_list.append(user["email"])

        if len(db["users"])==0 or userDict["email"] not in email_list:
            db["users"].append(userDict)
            with open(db_filename, "r+") as f:
                f.seek(0)
                json.dump(db,f,indent=4)
            return "User created successfully"
        else:
            return "User already exists"
    return "Methos not allowed"
@app.route("/login", methods=['POST'])
def login():
    email=request.form["email"]
    password=request.form["password"]
    user_idx=None
    # cheack for userswhich matches with email and password
    for user in db["users"]:
        if user["email"]==email and user["password"]==password:
            user_idx=db["users"].index(user)

            response={
                "message": "Login successful",
                "user_index": user_idx
            }
            return response
        else:
            continue
    return "Wrong user email or password please try again"
@app.route("/add_purchase",methods=['POST'])
def add_purchase():
    if request.method == "POST":
        user_idx=int(request.form["user_index"])
        item_name=request.form["item_name"]
        item_type=request.form["item_type"]
        item_price=request.form["item_price"]
    curr_date=str(date.today())
    curr_time=str(datetime.now(pytz.timezone("Asia/Kolkata")))
    itemDict={
        "item_name":item_name,
        "item_type":item_type,
        "item_price":item_price,
        "purchase_time":curr_time
    }
    exisisting_dates=list(db["users"][user_idx]["purches"].keys())
    # print(exisisting_dates)
    if len(db["users"][user_idx]["purches"])==0 or curr_date not in exisisting_dates:
        db["users"][user_idx]["purches"][curr_date]=[]
        db["users"][user_idx]["purches"][curr_date].append(itemDict)
        with open(db_filename, "r+") as f:
            f.seek(0)
            json.dump(db,f,indent=4)
        return "Item added successfully"
    else:
        db["users"][user_idx]["purches"][curr_date].append(itemDict)
        with open(db_filename, "r+") as f:
            f.seek(0)
            json.dump(db,f,indent=4)
        return "Item add sucessfully"
@app.route("/get_purchases_today", methods=["GET"])
def get_purchases_today():
    user_idx=request.args["user_index"]
    
    curr_date=str(date.today())
    purchases_today=db["users"][user_idx]["purchases"][curr_date]
    if len(purchases_today) == 0:
        return jsonify(msg="no items purchased today: ")
    return jsonify(purchases_for_today=purchases_today)
@app.route("/get_purchases",methods=["GET"])
def get_purchases():
    data=request.json
    # print(data)
    user_idx=data["user_index"]
    start_date=data["start_date"]
    end_date=data["end_date"]

    date_range=pd.date_range(start_date, end_date)
    #print(dates)
    
    db_dates=list(db["users"][user_idx]["purches"].keys())
    purchse_list={}
    for dt in db_dates:
        if dt in date_range:
            purchse_list[dt]=db["users"][user_idx]["purches"][dt]
        else:
            continue
    return purchse_list
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
  

  