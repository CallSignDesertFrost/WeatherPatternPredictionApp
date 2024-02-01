import requests
import json

api_key = "your_api_key"
base_url = "https://api.weather.gov/stations/"
station_id = "KBOX"  # example station ID for Boston, MA
start_date = "2022-01-01"
end_date = "2022-01-31"

url = f"{base_url}{station_id}/observations?start={start_date}T00:00:00&end={end_date}T23:59:59"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)
data = json.loads(response.text)

import psycopg2

# Connect to the database
conn = psycopg2.connect(database="weather_db", user="postgres", password="your_password", host="localhost", port="5432")
cur = conn.cursor()

# Loop through the data and insert it into the database
for observation in data["features"]:
    properties = observation["properties"]
    timestamp = properties["timestamp"]
    temperature = properties["temperature"]
    humidity = properties["humidity"]
    pressure = properties["pressure"]
    wind_speed = properties["windSpeed"]
    wind_direction = properties["windDirection"]

    # Get the location and condition IDs
    cur.execute("SELECT id FROM locations WHERE name = %s", (properties["station"],))
    location_id = cur.fetchone()[0]

    cur.execute("SELECT id FROM weather_conditions WHERE name = %s", (properties["skyCondition"],))
    condition_id = cur.fetchone()[0]

    # Insert the data into the historical_data table
    cur.execute("""
        INSERT INTO historical_data (location_id, condition_id, temperature, humidity, pressure, wind_speed, wind_direction, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (location_id, condition_id, temperature, humidity, pressure, wind_speed, wind_direction, timestamp))

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()

import pandas as pd

# Connect to the database
conn = psycopg2.connect(database="weather_db", user="postgres", password="your_password", host="localhost", port="5432")
cur = conn.cursor()

# Query the data from the database
cur.execute("SELECT location_id, temperature FROM historical_data")
data = cur.fetchall()

# Load the data into a pandas DataFrame
df = pd.DataFrame(data, columns=["location_id", "temperature"])

# Group the data by location and calculate the mean temperature
grouped = df.groupby("location_id")["temperature"].mean()

# Print the mean temperature for each location
print(grouped)

cur.close()
conn.close()

import numpy as np
from sklearn.linear_model import LinearRegression

# Connect to the database
conn = psycopg2.connect(database="weather_db", user="postgres", password="your_password", host="localhost", port="5432")
cur = conn.cursor()

# Query the data from the database
cur.execute("SELECT location_id, temperature FROM historical_data")
data = cur.fetchall()

# Load the data into a NumPy array
X = np.array(data)[:, 0].reshape(-1, 1)
y = np.array(data)[:, 1].reshape(-1, 1)

# Create a linear regression model
model = LinearRegression()

# Fit the model to the data
model.fit(X, y)

cur