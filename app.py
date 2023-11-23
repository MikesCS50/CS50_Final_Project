import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///solagrid.db")

# global variable for today's date
today = datetime.date.today()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    
    if request.method == "GET":
        return render_template("index.html")

    else:
        return apology("page under construction")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":

        return render_template("register.html")

    # if form submitted (post)
    if request.method == "POST":

        first_name = request.form.get("first_name")
        second_name = request.form.get("second_name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # checks password and confirmed password match
        if password != confirmation:
            return apology("passwords do no match", 400)

        # checks if the username in database and returns apology if sql query not empty
        username_check = db.execute("SELECT username FROM users WHERE username = ?;", username)
        if username_check:
            return apology("username already exists", 400)

        # hash password
        hashed_password = generate_password_hash(password)

        # insert username and hash into finance.db
        db.execute("INSERT INTO users (username, first_name, second_name, hash) VALUES (?, ?, ?, ?);", username, first_name, second_name, hashed_password)

        # return to login page
        return render_template("login.html")
    

@app.route("/estimate", methods=["GET", "POST"])
def estimate():
    """Estimate solar power generation"""

    if request.method == "GET":
        return render_template("estimate.html")

    # if form submitted (post)
    if request.method == "POST":
        return render_template("estimated.html")