# This python file was used for loading the sations.txt file to a database, allowing access to the station data for the 
# flask application. It is not run as a subprocess in the flask app.

import json

from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///solagrid.db")

# opens .txt file
file = open("stations.txt", "r")

# List to save into
lines = []

# copies lines of text into variable
for row in file:
    lines.append(row.split('\n'))

# # option to save data to a list of dictionaries
# station_data = []

# iterates through list, ignoring header and footer
for i in range(19449):
    # finds the year station closed and checks if the station is still open
    if i >= 4 and i <= 19441:
        end_year = lines[i][0][66:70].strip()

        if end_year == '..':
            station_number = lines[i][0][1:7].strip()
            station_name = lines[i][0][14:57].strip()
            latitude = float(lines[i][0][71:79].strip())
            longitude = float(lines[i][0][81:89].strip())
            state = lines[i][0][105:109].strip()

            # saves data to sqlite3 database
            db.execute("INSERT INTO station_data (station_number, station_name, latitude, longitude, state) VALUES(?, ?, ?, ?, ?);", station_number, station_name, latitude, longitude, state)

            # # saves data to list instead of database
            # station_data.append({
            #     'station_number': station_number,
            #     'station_name': station_name,
            #     'latitude': latitude,
            #     'longitude': longitude,
            #     'state': state,
            # })