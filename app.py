import datetime
import os
import functools
from flask import Flask, render_template, request, session, redirect, url_for, flash
from pymongo import MongoClient

app = Flask(__name__)

app.config['SECRET_KEY'] = "Hell5o@Wo4rld!4897It'sBu5r5ni75ngOutt3*"

client = MongoClient(os.getenv("MONGODB_URI"))
app.db = client.todo


def populateTasks():
    pass

def login_required(route):
    @functools.wraps(route)
    def raoute_wrapper(*args, **kwargs):
        email = session.get("email")
        if not email or not app.db.users.find_one({"email":email}):
            flash('you are not logged in. Please logIn')
            return redirect(url_for('login'))
        return route (*args,**kwargs)
    return raoute_wrapper
        


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        entry = dict(
            name = request.form.get('name'),
            email = request.form.get('email'),
            password = request.form.get('pass'),
            date = str(datetime.date.today()),
            tasks = {},
        )
        if app.db.users.find_one({"email":entry["email"]}):
            flash("You are already registerd. Please Login")
            return redirect(url_for('login'))
        # add session here
        session['email'] = entry["email"]
        app.db.users.insert_one(entry)
        return redirect(url_for('home'))
        
    return render_template('signup.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('pass')
        obj = app.db.users.find_one({"email": email})
        if obj and obj.get("password") == password:
            # add session here
            session['email'] = email
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

@app.route("/", methods = ["GET", "POST"])
@login_required
def home():
    email = session.get("email")
    tasks = app.db.users.find_one({"email":email}).get("tasks")
    print(tasks, "hi")
    if request.method == "POST":
        id = request.form.get("id")
        print(id, "hi")
        del tasks[id]
        print(tasks, "hi")
        app.db.users.update_one({"email":email}, {"$set":{"tasks":tasks}})
        return redirect(url_for('home'))
    return render_template('home.html',tasks=tasks)


@app.route("/edit", methods = ["GET", "POSt"])
@login_required
def edit():
    email = session["email"]
    id = request.args.get("id")
    tasks = app.db.users.find_one({"email":email}).get("tasks")
    task = tasks[id]
    if request.method == "POST":
        task["title"] = request.form.get("title")
        task["desc"] = request.form.get("desc")
        tasks[id] = task
        app.db.users.update_one({"email":email}, {"$set":{"tasks":tasks}})
        return redirect(url_for('home'))
    return render_template('edit.html', title = task["title"], desc=task["desc"], id=id)


@app.route("/add", methods= ["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        email = session["email"]
        tasks = app.db.users.find_one({"email":email}).get("tasks")
        i = 0
        newTask = dict(title=request.form.get("title"),desc=request.form.get("desc") )
        print(newTask)
        while True:
            if str(i) not in tasks:
                tasks[str(i)] = newTask
                app.db.users.update_one({"email":email}, {"$set":{"tasks":tasks}})
                break
            i+=1
        return redirect(url_for('home'))

    return render_template('add.html')




@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))
