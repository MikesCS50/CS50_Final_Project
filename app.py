import os
import datetime
import subprocess
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from math import radians, sin, cos, sqrt, atan2

from helpers import login_required

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
    
    # if redirected or via link
    if request.method == "GET":
        # get saved data from the database for logged in user
        saved_data = db.execute("SELECT * FROM saved_data WHERE user_id = ?;", session["user_id"])
        # render homepage
        return render_template("index.html", saved_data=saved_data)

    # if delete buttons on homepage clicked
    if request.method == "POST":
        # gets the id corresponding to the button clicked
        id = request.form.get("row_id")
        # deletes data with that id
        if id is not None:
            db.execute("DELETE FROM saved_data WHERE user_id = ? AND id = ?;", session["user_id"], id)

            return redirect("/")
        # if the button clicked is "clear data" then all saved data for user is deleted
        else:
            db.execute("DELETE FROM saved_data WHERE user_id = ?;", session["user_id"])

            return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            message = 'No username submitted'
            return render_template("apology.html", message=message)

        # Ensure password was submitted
        elif not request.form.get("password"):
            message = 'No password submitted'
            return render_template("apology.html", message=message)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            message = 'Invalid username and/or password'
            return render_template("apology.html", message=message)

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
            message = 'Must enter username'
            return render_template("apology.html", message=message)
        # Ensure password was submitted
        elif not password:
            message = 'Must enter password'
            return render_template("apology.html", message=message)

        # checks password and confirmed password match
        if password != confirmation:
            message = 'Passwords do not match'
            return render_template("apology.html", message=message)

        # checks if the username in database and returns apology if sql query not empty
        username_check = db.execute("SELECT username FROM users WHERE username = ?;", username)
        if username_check:
            message = 'username already exists'
            return render_template("apology.html", message=message)

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

        # gets user input
        location = request.form.get('location')
        search_location = request.form.get('searchResult')
        search_location_number = request.form.get('searchResultNumber')
        area = float(request.form.get('area'))
        tariff = float(request.form.get('tariff'))
        annual_savings = 0
        station_number = ''

        if not location and not search_location:
            message = 'No location selected'
            return render_template("apology.html", message=message)

        if location:
            if location == 'Melbourne':
                station_number = '86232'
            elif location == 'Sydney':
                station_number ='066006'
            elif location == 'Perth':
                station_number ='063005'
            elif location == 'Brisbane':
                station_number ='040913'
            elif location == 'Adelaide':
                station_number ='023119'
            elif location == 'Hobart':
                station_number ='094193'
            elif location == 'Canberra':
                station_number ='070246'
        elif search_location:
            location = search_location
            station_number = search_location_number

        # runs scrapy to extract solar radiation data
        subprocess.run(['scrapy', 'crawl', 'sunspider', '-a', f'station_number={station_number}'], cwd='/home/micha/wslremote/Solagrid/sunscraper')

        file_path = '/home/micha/wslremote/Solagrid/sunscraper/sunscraper.json'

        # open json file where data has been saved and copy to variable
        with open(file_path, 'r') as file:
            mean_data = json.load(file)

        # convert mean to kWh, and calculate energy generation and savings based on user input. Estimate 15% efficiency
        for row in mean_data:
            row['mean'] = round(row['mean'] * 0.277778, 2)
            energy_gen = round(row['mean'] * 0.15 * area, 2)
            savings = round(energy_gen * tariff, 2)
            row['energy_gen'] = energy_gen
            row['savings'] = savings
            annual_savings = round(annual_savings + savings, 2)

        # render estimated page, passing in data
        return render_template("estimated.html", mean_data=mean_data, location=location, area=area, tariff=tariff, annual_savings=annual_savings)
    
@app.route("/save", methods=["POST"])
def save_data():
    """Saves calculated data which will be displayed in index.html"""

    # summary data passed via JS code in estimated.html
    data = request.get_json()

    # convert data back to float
    tariff = float(data[2].replace('$', ''))
    annual_savings = float(data[3].replace('$', ''))
    
    db.execute("INSERT INTO saved_data (user_id, location, area, tariff, savings) VALUES (?, ?, ?, ?, ?);", session["user_id"], data[0], data[1], tariff, annual_savings)

    return redirect("/")


@app.route("/search", methods=["POST"])
def search():
    """Searches for nearest weather stations, based on user input"""

    # get coordinates from html page via JS code
    coords = request.get_json()

    # extract latitude and longitude 
    try:
        user_latitude = float(coords['firstValue'])
        user_longitude = float(coords['secondValue'])
    except ValueError:
        message = 'No coordinates submitted'
        return render_template("apology.html", message=message)

    # initialise variables
    station_name = ''
    station_number = ''
    distance = 0

    # open station data list from database
    station_data = db.execute('SELECT * FROM station_data;')

    # iterate through each station, extract lat and long coordinates, calculate distance between station and user input
    for row in station_data:
        station_latitude = row['latitude']
        station_longitude = row['longitude']
        # calculate_distance calculates radial distance
        distance = calculate_distance(user_latitude, user_longitude, station_latitude, station_longitude)
        # if first row, sets it to closes station
        if row['id'] == 1:
            station_distance = distance
            station_name = row['station_name']
            station_number = row['station_number']
        # checks if each station is closer and changes variable accordingly
        elif distance < station_distance:
            station_distance = distance
            station_name = row['station_name']
            station_number = row['station_number']

    # returns closest station to html

    # print(station_distance, station_number, station_name)
    
    html_content = "<label for='searchResult'>Nearest station: </label>"
    html_content += f"<input type='text' id='searchResult' name='searchResult' value='{station_name}'>"
    html_content += f"<p>{station_distance} km from your coordinates</p>"
    html_content += f"<input type='hidden' id='searchResultNumber' name='searchResultNumber' value='{station_number}'>"

    return html_content

# calculate radial distance in km
def calculate_distance(user_latitude, user_longitude, station_latitude, station_longitude):
    radius = 6371.0

    # Convert latitude and longitude from degrees to radians
    user_latitude, user_longitude, station_latitude, station_longitude = map(radians, [
        user_latitude, user_longitude, station_latitude, station_longitude
        ])

    # Calculate the differences in coordinates
    dlat = station_latitude - user_latitude
    dlon = station_longitude - user_longitude

    # Haversine formula to calculate distance
    a = sin(dlat / 2)**2 + cos(user_latitude) * cos(station_latitude) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance = round(radius * c, 1)

    return distance