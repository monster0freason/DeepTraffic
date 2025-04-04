# from flask import Flask, jsonify, request
# import time
# import requests
# from flask_cors import CORS  # Import CORS
# import threading

# app = Flask(__name__)

# # Allow requests from any origin
# CORS(app)  # Allow all origins by default

# # Define the API for getting GST from the existing lane API
# LANE_API_URL = "http://127.0.0.1:5000/traffic"  # Your API endpoint

# # Define the lanes and their corresponding video paths
# LANES = {
#     "lane1": "vid1.mp4",  # Replace with actual video paths
#     "lane2": "vid2.mp4",
#     "lane3": "vid3.mp4",
#     "lane4": "vid4.mp4"
# }

# # Define the order of lanes to cycle through
# LANES_CYCLE = ["lane1", "lane2", "lane3", "lane4"]

# # Track the current state of traffic signals
# lane_states = {
#     "lane1": {"color": "red", "densities": {}, "gst": 0},
#     "lane2": {"color": "red", "densities": {}, "gst": 0},
#     "lane3": {"color": "red", "densities": {}, "gst": 0},
#     "lane4": {"color": "red", "densities": {}, "gst": 0}
# }

# current_lane = 0  # Index to track the current lane
# cycling = False  # Flag to control the cycling of lanes

# def get_gst_for_lane(video_path):
#     """Make a GET request to get the GST for a specific lane based on video path."""
#     try:
#         response = requests.get(LANE_API_URL, params={"video_path": video_path})
#         if response.status_code == 200:
#             response_data = response.json()
#             gst = response_data.get("GST")  # Extract the green signal time
#             densities = response_data.get("densities")  # Get vehicle density data
#             return gst, densities  # Return GST and density data
#         else:
#             print(f"Error fetching GST for {video_path}: {response.status_code} - {response.text}")
#             return None, {}
#     except Exception as e:
#         print(f"Error fetching GST for video {video_path}: {e}")
#         return None, {}

# def manage_traffic_cycle():
#     """Cycle through the traffic signals for all lanes."""
#     global current_lane, cycling
#     while cycling:
#         lane = LANES_CYCLE[current_lane]
#         video_path = LANES[lane]

#         # Get GST and density data for the current lane
#         gst, densities = get_gst_for_lane(video_path)

#         if gst is not None:
#             total_vehicles = sum(densities.values())
#             lane_states[lane] = {"color": "green", "densities": densities, "gst": gst}
            
#             # Set other lanes to red
#             for other_lane in LANES_CYCLE:
#                 if other_lane != lane:
#                     lane_states[other_lane] = {"color": "red",  "densities": lane_states[other_lane]["densities"], "gst": 0}
            
#             print(f"Setting {lane} to green for {gst} seconds.")
#             time.sleep(gst)  # Keep the lane green for the GST duration
            
#             # Move to the next lane in the cycle
#             current_lane = (current_lane + 1) % len(LANES_CYCLE)
#         else:
#             print(f"Error: Could not retrieve data for {lane}. Moving to the next lane.")
#             current_lane = (current_lane + 1) % len(LANES_CYCLE)

# @app.route("/start_cycle", methods=["POST"])
# def start_traffic_cycle():
#     """Start the traffic signal cycle management."""
#     global cycling
#     if not cycling:  # Start only if not already cycling
#         cycling = True
#         threading.Thread(target=manage_traffic_cycle, daemon=True).start()
#         return {"status": "Traffic cycle started"}, 200
#     else:
#         return {"status": "Traffic cycle already running"}, 400

# @app.route("/stop_cycle", methods=["POST"])
# def stop_traffic_cycle():
#     """Stop the traffic signal cycle management."""
#     global cycling
#     cycling = False
#     return {"status": "Traffic cycle stopped"}, 200

# @app.route("/get_lane_status", methods=["GET"])
# def get_lane_status():
#     """Endpoint to get the current status of all lanes."""
#     return jsonify(lane_states)

# if __name__ == "__main__":
#     app.run(port=5006, debug=True)


from flask import Flask, jsonify, request
import time
import requests
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)  # Allow all origins by default

# Define the API for getting GST from the existing lane API
LANE_API_URL = "http://127.0.0.1:5000/traffic"

# Define lanes and their video paths
LANES = {
    "lane1": "vid5.mp4",
    "lane2": "vid3.mp4",
    "lane3": "vid4.mp4",
    "lane4": "vid1.mp4"
}
LANES_CYCLE = ["lane1", "lane2", "lane3", "lane4"]

# Track the current state of traffic signals
lane_states = {lane: {"color": "red", "densities": {}, "gst": 0} for lane in LANES_CYCLE}


current_lane = 0  # Index to track the current lane
cycling = False  # Flag to control the cycling of lanes
next_gst_data = {}  # Store pre-fetched GST and densities

def get_gst_for_lane(video_path):
    """Fetch GST and densities from the API."""
    try:
        response = requests.get(LANE_API_URL, params={"video_path": video_path})
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("GST"), response_data.get("densities", {})
        else:
            print(f"Error fetching GST for {video_path}: {response.status_code} - {response.text}")
            return None, {}
    except Exception as e:
        print(f"Error fetching GST for video {video_path}: {e}")
        return None, {}

def fetch_next_lane_data():
    """Fetch GST & density data for the next lane while the current lane is running."""
    global next_gst_data
    next_lane = LANES_CYCLE[(current_lane + 1) % len(LANES_CYCLE)]
    video_path = LANES[next_lane]
    gst, densities = get_gst_for_lane(video_path)
    if gst is not None:
        next_gst_data = {"lane": next_lane, "gst": gst, "densities": densities}

def manage_traffic_cycle():
    """Manage the cycling of traffic signals while pre-fetching next lane's data."""
    global current_lane, cycling, next_gst_data
    while cycling:
        lane = LANES_CYCLE[current_lane]
        
        # If pre-fetched data exists, use it, otherwise fetch it
        if next_gst_data and next_gst_data["lane"] == lane:
            gst, densities = next_gst_data["gst"], next_gst_data["densities"]
            next_gst_data = {}  # Reset cached data
        else:
            gst, densities = get_gst_for_lane(LANES[lane])

        if gst is not None:
            lane_states[lane] = {"color": "green", "densities": densities, "gst": gst}
            for other_lane in LANES_CYCLE:
                if other_lane != lane:
                    lane_states[other_lane] = {"color": "red", "densities": lane_states[other_lane]["densities"], "gst": 0}

            print(f"Setting {lane} to green for {gst} seconds.")
            
            # Start fetching next lane data in a separate thread
            threading.Thread(target=fetch_next_lane_data, daemon=True).start()
            
            time.sleep(gst)  # Wait for the green signal duration
            current_lane = (current_lane + 1) % len(LANES_CYCLE)
        else:
            print(f"Error: Could not retrieve data for {lane}. Moving to next lane.")
            current_lane = (current_lane + 1) % len(LANES_CYCLE)

@app.route("/start_cycle", methods=["POST"])
def start_traffic_cycle():
    """Start the traffic signal cycle management."""
    global cycling
    if not cycling:
        cycling = True
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

if __name__ == "__main__":
    app.run(port=5006, debug=True)