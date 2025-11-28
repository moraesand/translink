import requests
import time
from google.transit import gtfs_realtime_pb2
import csv
from config import API_KEY, ROUTE_MAP_FILE, STOP_MAP_FILE

# --- Load route map ---
ROUTE_MAP = {}
with open(ROUTE_MAP_FILE, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        route_id = row["route_id"]
        short_name = row["route_short_name"]
        if short_name:
            ROUTE_MAP[route_id] = short_name

# --- Load stops map: public stop_code → internal stop_id ---
STOP_MAP = {}
with open(STOP_MAP_FILE, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        stop_id = row["stop_id"]
        stop_code = row["stop_code"]
        if stop_code:
            STOP_MAP[stop_code] = stop_id