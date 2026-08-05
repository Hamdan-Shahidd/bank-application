import os
from flask import Flask, render_template, request, redirect, flash, session
from banking import Bank
from storage import SqliteStorage
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from agent import interpret

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
csrf = CSRFProtect(app)

def current_user():
    uid = session.get("user_id")
    return bank.storage.find_by_id(uid) if uid else None

@app.route("/")
def home():
    return render_template("home.html")


bank = Bank(SqliteStorage())
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            user = bank.sign_up(request.form["username"],
                                request.form["gmail"],
                                request.form["password"])
        except (ValueError, RuntimeError) as e:
            flash(str(e))
            return redirect("/signup")
        flash(f"Account created. Your account number is {user.account_number}")
        return redirect("/login")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            user = bank.log_in(request.form["gmail"], request.form["password"])
        except ValueError as e:
            flash(str(e))
            return redirect("/login")
        session["user_id"] = user.user_id
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    user = current_user()
    if user is None:
        return redirect("/login")
    return render_template("dashboard.html", user=user)

@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    user = current_user()
    if user is None:
        return redirect("/login")

    if request.method == "POST":
        raw = request.form["amount"]
        if not raw.isdecimal() or int(raw) == 0:
            flash("Enter a whole number greater than 0")
            return redirect("/deposit")
        try:
            bank.deposit(user, int(raw))
        except ValueError as e:
            flash(str(e))
            return redirect("/deposit")
        flash(f"{raw} deposited")
        return redirect("/dashboard")

    return render_template("deposit.html")

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    user = current_user()
    if user is None:
        return redirect("/login")

    if request.method == "POST":
        raw = request.form["amount"]
        if not raw.isdecimal() or int(raw) == 0:
            flash("Enter a whole number greater than 0")
            return redirect("/transfer")
        try:
            bank.transfer(user, request.form["account_number"], int(raw))
        except ValueError as e:
            flash(str(e))
            return redirect("/transfer")
        flash("Transfer complete")
        return redirect("/dashboard")
    return render_template("transfer.html")




# For Agents: 
@app.route("/assistant" , methods = ["GET" , "POST"])
def assistant():
    user = current_user()
    if user is None:
        return redirect("/login")
    if request.method == "POST":
        kind, payload = interpret(request.form["message"])
        if kind == "proposal":
            session["pending"] = payload
            return render_template("assistant.html" , proposal = payload)
        return render_template("assistant.html" , reply = payload)
    return render_template("assistant.html")
    
