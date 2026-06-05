#!/usr/bin/env python3
import requests
import os
import sys
import random
from datetime import datetime, timedelta
import pytz
import time  # Import time for sleep function

TEAM_ID = "darkonbullt"

# Token aus ENV
API_TOKEN = os.getenv("KEY")
if not API_TOKEN:
    sys.exit("Error: API token not found. Please set KEY environment variable.")

# Turnieroptionen mit klaren Namen
OPTIONS = [
     {"name": "Hourly Bullet 30s+0",   "clock": {"limit": 30,  "increment": 0},  "nbRounds": 20},                                                
     {"name": "Hourly Bullet 1+0",   "clock": {"limit": 60,  "increment": 0},  "nbRounds": 15}, 
     {"name": "Hourly Bullet 1+1",   "clock": {"limit": 60,  "increment": 1},  "nbRounds": 11},
     {"name": "Hourly Bullet 2+1",   "clock": {"limit": 120,  "increment": 1},  "nbRounds": 9},
]


def utc_millis_for_hour(hour):
    utc = pytz.utc
    now = datetime.now(utc)
    tomorrow = now + timedelta(days=1)
    start = datetime(tomorrow.year, tomorrow.month, tomorrow.day, hour, 25, tzinfo=utc)
    return int(start.timestamp() * 1000), start

def read_description():
    path = os.path.join(os.path.dirname(__file__), "description.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "Welcome to our Swiss tournament!"

def create_swiss():
    for hour in range(24):
        option = random.choice(OPTIONS)
        startDate, start_dt = utc_millis_for_hour(hour)
        payload = {
            "name": f"{option['name']} ",
            "clock.limit": option["clock"]["limit"],
            "clock.increment": option["clock"]["increment"],
            "nbRounds": option["nbRounds"],
            "rated": "true",
            "description": read_description(),
            "startsAt": startDate,
            "conditions.playYourGames": "true"
        }
        url = f"https://lichess.org/api/swiss/new/{TEAM_ID}"
        headers = {"Authorization": f"Bearer {API_TOKEN}"}

        print(f"➡ Creating: {payload['name']} "
              f"({payload['clock.limit']//60}+{payload['clock.increment']}, "
              f"{payload['nbRounds']}R, Start {start_dt} UTC)")

        r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 200:
            data = r.json()
            print("✅ Tournament created!")
            print("URL:", f"https://lichess.org/swiss/{data.get('id')}")
        else:
            print("❌ Error:", r.status_code, r.text)

        time.sleep(2)  # Wait 2 seconds between requests to avoid simultaneous creation

if __name__ == "__main__":
    create_swiss()
