# Solagrid
#### Video Demo: https://youtu.be/7zTd6fTWEMo
#### Description: A flask web application that will calculate the potential electricity generated from solar panels

## Introduction
This is Solagrid. A flask web application that will calculate the potential electricity generated from solar panels based on the users location input in Australia. The project contains an app.py file that runs the flask app, a web scraper, sunscraper, that extracts solar radiation data for a users location

### /templates
This folder contains all of the html files needed for the application. layout.html is used as a template for all of the html files.

### /static/styles.css
This file contains css styles used in the html files

### stations.py and stations.txt
stations.txt contains a list of all the weather stations in Australia that measure solar radiation data. stations.py extracts the weather station details, cleans the data as required and stores them in a table in an SQL solagrid database

### solagrid.db
This is an SQL database that stores the data for the web application. There are three tables in the database: users; this contains users login information, saved_data; this contains any calculated solar energy data the user has decided to save, and station_data; this contains details about weather stations in Australia including coordinates, station number and station name.

### app.py
#### Register
The flask app requires a user to register and login in register.html. Through `@app.route("/register", methods=["GET", "POST"])` the user is required to enter a name, username, password and confirm the password. The username is checked against a list of usernames stored in an SQL database. If the username does not exist and the password/confirm password match, the password is hashed and stored in the database along with the users details. The user is then redirected to index.html. The user remains logged in using Session function until user logs out.

#### Login
User inputs their username and password in login.html. Through `@app.route("/login", methods=["GET", "POST"])` These details are checked against details stored in an SQL database. If they match a user, that user is
logged in. 

#### Logout
User logs out and through `@app.route("/logout")` session data is cleared. User is redirected to login.html and login is required to re-enter web app

#### Estimate
Is can navigate to estimate.html via 'GET' method where the user can select their location by either selecting one of the major population centres in Australia or by searching for their nearest weather station by inputting their latitude and longitude coordinates. When the search button is clicked, JavaScript will send the coordinates to `@app.route("/search", methods=["POST"])` where the closest weather station is found by iterating through a list of weather stations from the station_data table in solagrid.db. The station is found by calculating the radial distance to the users coordinates using the `def calculate_distance()` function. The closest weather station is returned to estimate.html. The user then must enter solar panel area and electricity tariff and submit the form by clicking the button. The 'POST' method through `@app.route("/estimate", methods=["GET", "POST"])`, will extract users input and then run a scrapy spider subprocess to scrape solar radiation data from the internet for the users location. The returned solar radiation data is used to calculate the energy generation and electricity savings based on the users input solar panel area and electricity tariff. The estimated.html page is rendered, displaying this data.

#### Save
The user can decide if they want to save the data displayed in estimated.html by clicking save. When clicked JavaScript is used to extract the data displayed in the table in estimated.html and send the data to `@app.route("/save", methods=["POST"])` via 'POST' method, using an AJAX request. The data is stored in the saved_data table in the solagrid.db SQL database.

#### Index
The homepage (index.html) shows a table listing any estimated solar energy generation data the user has saved, showing location, solar panel area, electricity tariff and annual savings from using solar panels. If the user has not got any data saved, the table is hidden and a message is displayed instead. Each row in the table has a delete button so that the user can delete the saved_data individually or they can delete all their data using the 'clear data' button.

### /sunscraper
This is a scrapy project containing the spider, sunspider. This spider is launched via a subprocess from `@app.route("/estimate", methods=["GET", "POST"])`. It takes the weather station number retrieved from the station_data table in solagrid.db SQL database and uses it to retrieve a url containing solar radiation data gathered at that weather station. The solar radiation data is then scraped and stored in sunscraper.json. The scrapy project also contains other .py files that are essential for scraping the website including middlewares.py and settings.py.
