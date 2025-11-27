import requests
import time
from google.transit import gtfs_realtime_pb2
import csv
from config import API_KEY, ROUTE_MAP_FILE, STOP_MAP_FILE

# --- Load route map ---
route_map = {}
with open(ROUTE_MAP_FILE, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        route_id = row["route_id"]
        short_name = row["route_short_name"]
        if short_name:
            route_map[route_id] = short_name

# --- Load stops map: public stop_code → internal stop_id ---
stop_map = {}
with open(STOP_MAP_FILE, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        stop_id = row["stop_id"]
        stop_code = row["stop_code"]
        if stop_code:
            stop_map[stop_code] = stop_id

# --- GTFS-Realtime feed URL ---
url = f"https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey={API_KEY}"

# --- User input ---
bus_stop = input("Enter public bus stop number (leave blank to see all): ").strip()
bus_route = input("Enter bus route (leave blank to see all): ").strip()

# Map public stop number to internal stop_id
bus_stop_id = stop_map.get(bus_stop) if bus_stop else None

def bus_updates():
    """Fetch GTFS-Realtime feed and parse entities."""
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print("Error:", r.status_code, r.text)
            return []
        feed.ParseFromString(r.content)
        return feed.entity
    except Exception as e:
        print("Error fetching data:", e)
        return []

while True:
    print("\n--- Live Bus Arrivals ---")
    entities = bus_updates()

    if not entities:
        print("No data available.")
    else:
        for entity in entities:
            if entity.HasField("trip_update"):
                update = entity.trip_update
                internal_route = update.trip.route_id if update.trip.route_id else "Unknown"
                public_route = route_map.get(internal_route, internal_route)

                # Filter by route if user entered one
                if bus_route and public_route != bus_route:
                    continue

                for stop_time in update.stop_time_update:
                    stop_id = stop_time.stop_id

                    # Filter by stop if user entered one
                    if bus_stop_id and stop_id != bus_stop_id:
                        continue

                    # Pick arrival or departure
                    if stop_time.HasField("arrival"):
                        timestamp = stop_time.arrival.time
                    elif stop_time.HasField("departure"):
                        timestamp = stop_time.departure.time
                    else:
                        continue

                    readable = time.strftime("%H:%M:%S", time.localtime(timestamp))
                    print(f"Route {public_route} → Stop {bus_stop or stop_id} | ETA: {readable}")

    time.sleep(5)

