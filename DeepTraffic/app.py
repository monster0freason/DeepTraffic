from flask import Flask, jsonify, request
import time
import requests
from flask_cors import CORS
import threading
from threading import Lock

app = Flask(__name__)
CORS(app)  # Allow all origins by default

# Define the API for getting GST from the existing lane API
LANE_API_URL = "http://127.0.0.1:5000/traffic"

# Define lanes and their video paths
LANES = {
    "lane1": "vid2.mp4",
    "lane2": "vid6.mp4",
    "lane3": "vid5.mp4",
    "lane4": "vid4.mp4"
}
LANES_CYCLE = ["lane1", "lane2", "lane3", "lane4"]

# Track the current state of traffic signals
lane_states = {lane: {"color": "red", "densities": {}, "gst": 0} for lane in LANES_CYCLE}

# Add a lock for thread safety
data_lock = Lock()

current_lane = 0  # Index to track the current lane
cycling = False  # Flag to control the cycling of lanes
next_gst_data = {}  # Store pre-fetched GST and densities

# Configuration for refresh frequency
REFRESH_EVERY_N_CYCLES = 3  # Refresh cache every 3 full cycles
cycle_count = 0

def get_gst_for_lane(video_path, force_refresh=False):
    """
    Fetch GST and densities from the API.
    
    Args:
        video_path: Path to the video file
        force_refresh: If True, force the API to reprocess the video
    """
    try:
        response = requests.get(
            LANE_API_URL, 
            params={
                "video_path": video_path,
                "force_refresh": str(force_refresh).lower()
            }
        )
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("GST"), response_data.get("densities", {})
        else:
            print(f"Error fetching GST for {video_path}: {response.status_code} - {response.text}")
            return None, {}
    except Exception as e:
        print(f"Error fetching GST for video {video_path}: {e}")
        return None, {}

def fetch_next_lane_data(force_refresh=False):
    """
    Fetch GST & density data for the next lane while the current lane is running.
    
    Args:
        force_refresh: If True, force a refresh of the video data
    """
    global next_gst_data
    next_lane = LANES_CYCLE[(current_lane + 1) % len(LANES_CYCLE)]
    video_path = LANES[next_lane]
    
    print(f"Pre-fetching data for {next_lane} (force_refresh={force_refresh})")
    gst, densities = get_gst_for_lane(video_path, force_refresh=force_refresh)
    
    if gst is not None:
        with data_lock:
            next_gst_data = {"lane": next_lane, "gst": gst, "densities": densities}

def clear_traffic_api_cache():
    """Clear the cache in the traffic API service."""
    try:
        response = requests.post("http://127.0.0.1:5000/clear_cache")
        if response.status_code == 200:
            print("Traffic API cache cleared successfully")
            return True
        else:
            print(f"Failed to clear traffic API cache: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error clearing traffic API cache: {e}")
        return False

def manage_traffic_cycle():
    """Manage the cycling of traffic signals while pre-fetching next lane's data."""
    global current_lane, cycling, next_gst_data, cycle_count
    
    while cycling:
        lane = LANES_CYCLE[current_lane]
        
        # Determine if we should force refresh the data
        # Force refresh at the start of every Nth cycle
        should_refresh = (current_lane == 0 and cycle_count % REFRESH_EVERY_N_CYCLES == 0)
        
        if should_refresh:
            print(f"Starting cycle {cycle_count+1}: Forcing refresh of all lanes")
            clear_traffic_api_cache()
        
        with data_lock:
            # If pre-fetched data exists and matches current lane, use it
            if next_gst_data and next_gst_data["lane"] == lane:
                print(f"Using pre-fetched data for {lane}")
                gst, densities = next_gst_data["gst"], next_gst_data["densities"]
                next_gst_data = {}  # Reset cached data
            else:
                # Otherwise fetch it now
                print(f"Fetching data for {lane} (force_refresh={should_refresh})")
                gst, densities = get_gst_for_lane(LANES[lane], force_refresh=should_refresh)
        
        if gst is not None:
            with data_lock:
                lane_states[lane] = {"color": "green", "densities": densities, "gst": gst}
                for other_lane in LANES_CYCLE:
                    if other_lane != lane:
                        # Only update color, preserve densities
                        lane_states[other_lane]["color"] = "red"
                        lane_states[other_lane]["gst"] = 0
            
            print(f"Setting {lane} to green for {gst} seconds with densities: {densities}")
            
            # Start fetching next lane data in a separate thread
            threading.Thread(
                target=fetch_next_lane_data, 
                args=(should_refresh,),
                daemon=True
            ).start()
            
            time.sleep(gst)  # Wait for the green signal duration
            current_lane = (current_lane + 1) % len(LANES_CYCLE)
            
            # If we've completed a full cycle, increment the cycle counter
            if current_lane == 0:
                cycle_count += 1
                print(f"Completed cycle {cycle_count}")
        else:
            print(f"Error: Could not retrieve data for {lane}. Moving to next lane.")
            current_lane = (current_lane + 1) % len(LANES_CYCLE)

@app.route("/start_cycle", methods=["POST"])
def start_traffic_cycle():
    """Start the traffic signal cycle management."""
    global cycling, cycle_count
    if not cycling:
        cycling = True
        cycle_count = 0
        threading.Thread(target=manage_traffic_cycle, daemon=True).start()
        return {"status": "Traffic cycle started"}, 200
    else:
        return {"status": "Traffic cycle already running"}, 400

@app.route("/stop_cycle", methods=["POST"])
def stop_traffic_cycle():
    """Stop the traffic signal cycle management."""
    global cycling
    cycling = False
    return {"status": "Traffic cycle stopped"}, 200

@app.route("/get_lane_status", methods=["GET"])
def get_lane_status():
    """Endpoint to get the current status of all lanes."""
    return jsonify(lane_states)

@app.route("/force_refresh", methods=["POST"])
def force_refresh():
    """Force a refresh of the data for all lanes."""
    if clear_traffic_api_cache():
        return {"status": "Cache cleared successfully"}, 200
    else:
        return {"status": "Failed to clear cache"}, 500

if __name__ == "__main__":
    app.run(port=5006, debug=True)