import os
from flask import Flask, render_template, request, redirect, flash
from banking import Bank
from storage import SqliteStorage

app = Flask(__name__)
app.secret_key = "dev-only-change-this"
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
