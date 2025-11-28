import requests
import time
from google.transit import gtfs_realtime_pb2
from config import API_KEY
from read_csv import ROUTE_MAP, STOP_MAP  # your preloaded maps

# --- GTFS-Realtime feed URL ---
url = f"https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey={API_KEY}"

# --- User input ---
bus_stop_public = input("Enter public bus stop number (leave blank to see all): ").strip()
bus_route = input("Enter bus route (leave blank to see all): ").strip()

# Convert user stop_code → internal stop_id
bus_stop_internal = STOP_MAP.get(bus_stop_public) if bus_stop_public else None

print("Mapped public stop", bus_stop_public, "→ internal", bus_stop_internal)

def bus_updates():
    """Fetch GTFS-Realtime feed and parse entities."""
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        req = requests.get(url)
        req.raise_for_status()
        feed.ParseFromString(req.content)
        return feed.entity
    except Exception as e:
        print("Error fetching data:", e)
        return []

while True:
    print("\n--- Live Bus Arrivals ---")
    entities = bus_updates()

    found_any = False

    for entity in entities:
        if not entity.HasField("trip_update"):
            continue

        update = entity.trip_update

        # Actual internal route ID from GTFS-RT
        internal_route = update.trip.route_id
        if not internal_route:
            continue

        # Convert internal route → public route_short_name
        public_route = ROUTE_MAP.get(internal_route, None)

        # No mapping? skip  
        if public_route is None:
            continue

        # Route filter  
        if bus_route and public_route != bus_route:
            continue

        # # Debug: print stops available  
        # print(f"[DEBUG] Route {public_route} contains stops:",
        #       [st.stop_id for st in update.stop_time_update])

        for st in update.stop_time_update:
            stop_id = st.stop_id

            # Stop filter
            if bus_stop_internal and stop_id != bus_stop_internal:
                continue

            # Get arrival/departure  
            if st.HasField("arrival"):
                timestamp = st.arrival.time
            elif st.HasField("departure"):
                timestamp = st.departure.time
            else:
                continue

            readable = time.strftime("%H:%M:%S", time.localtime(timestamp))

            print(f"Route {public_route} → Stop {bus_stop_public or stop_id} | ETA: {readable}")
            found_any = True

    if not found_any:
        print("No matching realtime buses (bus may not have started yet).")

    time.sleep(5)
