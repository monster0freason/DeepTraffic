# from flask import Flask, request, jsonify
# import cv2
# from ultralytics import YOLO
# import random
# import math
# import requests
# import numpy as np
# import os
# import sys
# import time

# # Add DeepSORT imports
# from deep_sort_realtime.deepsort_tracker import DeepSort

# app = Flask(__name__)

# # YOLO Model initialization
# model = YOLO('yolov8n.pt')

# # Initialize DeepSORT tracker
# tracker = DeepSort(
#     max_age=30,               # Maximum frames to keep lost tracks
#     n_init=3,                 # Frames required for track confirmation
#     max_iou_distance=0.7,     # Maximum IOU distance for association
#     max_cosine_distance=0.2,  # Maximum cosine distance for appearance features
#     nn_budget=100             # Maximum size of appearance descriptors gallery
# )

# # Class names
# classNames = ["person", "bicycle", "car", "motorbike", "ambulance", "bus", "train", "truck",
#               "traffic light", "fire hydrant", "stop sign", "bird", "cat",
#               "dog", "horse", "sheep", "cow"]

# PREDICTION_API_URL = "http://localhost:5001/predict"

# # Dictionary to track processed videos
# processed_videos = {}

# def get_random_values():
#     """Generate random values for the prediction API."""
#     return {
#         "Time_of_Day": random.randint(0, 23),
#         "Day_of_Week": random.randint(1, 7),
#         "Month": random.randint(1, 12),
#         "Weather_Condition": random.randint(0, 1),
#         "Temperature": random.uniform(15, 35),
#         "Humidity": random.uniform(20, 80),
#         "Traffic_Volume": random.randint(50, 500),
#         "Event_Indicator": random.randint(0, 1)
#     }

# def process_entire_video(video_path):
#     """Process all frames of a video and count unique vehicles using DeepSORT."""
#     # Check if video has already been processed
#     if video_path in processed_videos:
#         return processed_videos[video_path]
    
#     # Initialize the video capture
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         return None, "Failed to open video."
    
#     # Initialize counters for unique vehicles
#     unique_vehicle_counts = {
#         "car": 0,
#         "truck": 0,
#         "motorbike": 0,
#         "ambulance": 0,
#         "bus": 0
#     }
    
#     # Initialize sets to track unique track IDs by class
#     track_ids = {
#         "car": set(),
#         "truck": set(),
#         "motorbike": set(),
#         "ambulance": set(),
#         "bus": set()
#     }
    
#     frame_count = 0
#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
#     print(f"Processing video {video_path} with {total_frames} frames")
#     start_time = time.time()
    
#     # Process each frame in the video
#     while True:
#         success, frame = cap.read()
#         if not success:
#             break
        
#         frame_count += 1
#         if frame_count % 10 != 0:  # Process every 10th frame to improve speed
#             continue
            
#         # Run YOLO detection
#         results = model(frame, stream=True)
        
#         # Extract detections for DeepSORT format
#         # Each detection should be: [x1, y1, x2, y2, confidence, class_id]
#         detections = []
#         class_ids = []
        
#         for r in results:
#             boxes = r.boxes
#             for box in boxes:
#                 # Convert tensor to numpy and handle potential float64 issues
#                 try:
#                     # Extract coordinates as float values instead of numpy arrays
#                     xyxy = box.xyxy[0].cpu().numpy()
#                     x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])
#                     conf = float(box.conf[0])
#                     cls_id = int(box.cls[0])
#                     detected_class = r.names.get(cls_id, "unknown")
                    
#                     # Filter for vehicle classes we're interested in
#                     if detected_class in ["car", "truck", "motorbike", "ambulance", "bus"]:
#                         detections.append([x1, y1, x2, y2, conf])
#                         class_ids.append(detected_class)
#                 except Exception as e:
#                     print(f"Error processing detection: {e}")
#                     continue
        
#         # Special case for ambulance - immediate priority
#         if "ambulance" in class_ids:
#             cap.release()
#             processed_videos[video_path] = {"ambulance": 1}, None
#             return {"ambulance": 1}, None
        
#         # Run tracker if we have detections
#         if len(detections) > 0:
#             try:
#                 # Convert to numpy array for DeepSORT
#                 detections_np = np.array(detections)
                
#                 # Update the tracker with new detections
#                 tracks = tracker.update_tracks(detections_np, frame=frame)
                
#                 # Process tracks to count unique vehicles
#                 for track in tracks:
#                     if not track.is_confirmed():
#                         continue
                    
#                     track_id = track.track_id
                    
#                     # Get detection class - handle potential index issues
#                     detection_idx = track.detection_index
                    
#                     # Make sure detection_idx is an integer and within bounds
#                     if detection_idx is not None:
#                         # Convert to int if it's a numpy number type
#                         if isinstance(detection_idx, (np.int64, np.int32, np.float64, np.float32)):
#                             detection_idx = int(detection_idx)
                        
#                         if isinstance(detection_idx, int) and detection_idx < len(class_ids):
#                             detected_class = class_ids[detection_idx]
#                             if track_id not in track_ids[detected_class]:
#                                 track_ids[detected_class].add(track_id)
#                                 unique_vehicle_counts[detected_class] += 1
#             except Exception as e:
#                 print(f"Error in tracking: {e}")
#                 continue
        
#         # Print progress periodically
#         if frame_count % 50 == 0:
#             elapsed = time.time() - start_time
#             progress = frame_count / total_frames * 100
#             print(f"Processing: {progress:.1f}% complete. Elapsed time: {elapsed:.1f}s")
#             print(f"Current counts: {unique_vehicle_counts}")
    
#     # Release video resources
#     cap.release()
    
#     # Store results for future requests
#     processed_results = {
#         "car_density": unique_vehicle_counts["car"],
#         "truck_density": unique_vehicle_counts["truck"],
#         "bikes_density": unique_vehicle_counts["motorbike"],
#         "bus_density": unique_vehicle_counts["bus"]
#     }
    
#     # Cache the results
#     processed_videos[video_path] = processed_results, None
    
#     print(f"Video processing complete. Found {sum(unique_vehicle_counts.values())} unique vehicles")
#     print(f"Counts by type: {unique_vehicle_counts}")
    
#     return processed_results, None

# def adjust_gst_with_prediction(gst, densities):
#     """Adjust GST based on prediction API."""
#     data = get_random_values()
#     try:
#         response = requests.post(PREDICTION_API_URL, json=data)
#         if response.status_code == 200:
#             try:
#                 prediction_data = response.json()
#             except ValueError:
#                 print("Invalid JSON response from API")
#                 return gst
#             prediction_percentage = prediction_data.get("Predicted Adjustment Factor", 0)
#             adjusted_gst = gst * (1 + prediction_percentage / 100)
#             adjusted_gst = math.ceil(adjusted_gst)
#             print(f"Original GST: {gst}, Adjusted GST: {adjusted_gst} (Percentage: {prediction_percentage}%)")
#             return adjusted_gst
#         else:
#             print(f"Error from prediction API: {response.status_code} - {response.text}")
#             return gst
#     except Exception as e:
#         print(f"Error calling prediction API: {e}")
#         return gst

# def get_GST(densities):
#     """Calculate GST based on densities."""
#     max_allocation_possible = 100
#     min_allocation_possible = 10
    
#     # Weights for different vehicle types
#     av_times = {
#         "car_density": 10,
#         "bikes_density": 7,
#         "truck_density": 20,
#         "bus_density": 15
#     }
    
#     # Calculate weighted sum
#     GST = sum(densities.get(k, 0) * v for k, v in av_times.items() if k in densities)
    
#     # Apply divisor to get reasonable time
#     GST /= 4
    
#     # Adjust based on prediction API
#     GST = adjust_gst_with_prediction(GST, densities)
    
#     # Ensure GST is within bounds
#     GST = max(min(GST, max_allocation_possible), min_allocation_possible)
    
#     return math.ceil(GST)

# @app.route('/traffic', methods=['GET'])
# def traffic_density():
#     video_path = request.args.get('video_path')
#     if not video_path:
#         return jsonify({"error": "No video path provided"}), 400
    
#     try:
#         densities, error = process_entire_video(video_path)
        
#         if densities is None:
#             return jsonify({"error": error}), 500
        
#         # Special case for ambulance
#         if "ambulance" in densities and densities["ambulance"] > 0:
#             return jsonify({"densities": {"ambulance": 1}, "GST": 120})
        
#         # Calculate total vehicle count
#         total_density = sum(densities.values())
#         densities["total_density"] = total_density
        
#         # Calculate GST based on the densities
#         GST = get_GST(densities)
        
#         return jsonify({
#             "densities": densities,
#             "GST": GST
#         })
#     except Exception as e:
#         print(f"Error in traffic_density endpoint: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     # Test if DeepSORT is installed, if not print installation instructions
#     try:
#         from deep_sort_realtime.deepsort_tracker import DeepSort
#         print("DeepSORT library found, starting server...")
#     except ImportError:
#         print("ERROR: DeepSORT library not found. Please install it using:")
#         print("pip install deep-sort-realtime")
#         sys.exit(1)
        
#     app.run(debug=True)



from flask import Flask, request, jsonify
import cv2
from ultralytics import YOLO
import random
import math
import requests
import numpy as np
import os
import time
from deep_sort_realtime.deepsort_tracker import DeepSort

app = Flask(__name__)

# Initialize YOLO Model
model = YOLO('yolov8n.pt')

# Initialize DeepSORT tracker
tracker = DeepSort(
    max_age=30,
    n_init=3,
    max_iou_distance=0.7,
    max_cosine_distance=0.2,
    nn_budget=100
)

# Vehicle classes of interest
vehicle_classes = {"car", "truck", "motorcycle​", "ambulance", "bus"}

# Store processed videos to prevent redundant processing
processed_videos = {}

PREDICTION_API_URL = "http://localhost:5001/predict"

def get_random_values():
    """Generate random values for the prediction API."""
    return {
        "Time_of_Day": random.randint(0, 23),
        "Day_of_Week": random.randint(1, 7),
        "Month": random.randint(1, 12),
        "Weather_Condition": random.randint(0, 1),
        "Temperature": random.uniform(15, 35),
        "Humidity": random.uniform(20, 80),
        "Traffic_Volume": random.randint(50, 500),
        "Event_Indicator": random.randint(0, 1)
    }

def process_entire_video(video_path):
    """Process video frames to count unique vehicles."""
    if video_path in processed_videos:
        return processed_videos[video_path]
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, "Failed to open video."
    
    unique_counts = {cls: 0 for cls in vehicle_classes}
    track_ids = {cls: set() for cls in vehicle_classes}
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Processing {video_path} ({total_frames} frames)")
    start_time = time.time()
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame_count += 1
        if frame_count % 30 != 0:
            continue  # Process every 10th frame
        
        results = model(frame, stream=True)
        detections = []
        class_ids = []
        
        for r in results:
            for box in r.boxes:
                try:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    detected_class = r.names.get(cls_id, "unknown")
                    
                    if detected_class in vehicle_classes:
                        detections.append([[x1, y1, x2, y2], conf, detected_class])
                        class_ids.append(detected_class)
                except Exception as e:
                    print(f"Error processing detection: {e}")
        
        if "ambulance" in class_ids:
            cap.release()
            processed_videos[video_path] = {"ambulance": 1}, None
            return {"ambulance": 1}, None
        
        if detections:
            try:
                tracks = tracker.update_tracks(detections, frame=frame)
                for track in tracks:
                    if not track.is_confirmed():
                        continue
                    
                    track_id = track.track_id
                    detected_class = track.det_class
                    
                    if detected_class in vehicle_classes and track_id not in track_ids[detected_class]:
                        track_ids[detected_class].add(track_id)
                        unique_counts[detected_class] += 1
            except Exception as e:
                print(f"Error in tracking: {e}")
                continue
        
    cap.release()
    processed_results = {f"{cls}_density": unique_counts[cls] for cls in vehicle_classes if cls != "ambulance"}
    processed_videos[video_path] = processed_results, None
    print(f"Processing complete. {processed_results}")
    return processed_results, None

def adjust_gst_with_prediction(gst, densities):
    """Adjust GST based on prediction API."""
    data = get_random_values()
    try:
        response = requests.post(PREDICTION_API_URL, json=data)
        if response.status_code == 200:
            prediction_data = response.json()
            adjustment_factor = prediction_data.get("Predicted Adjustment Factor", 0)
            adjusted_gst = math.ceil(gst * (1 + adjustment_factor / 100))
            return adjusted_gst
    except Exception as e:
        print(f"Error calling prediction API: {e}")
    return gst

def get_GST(densities):
    """Calculate GST based on densities."""
    max_gst = 100
    min_gst = 10
    weights = {"car_density": 10, "bikes_density": 7, "truck_density": 20, "bus_density": 15}
    GST = sum(densities.get(k, 0) * v for k, v in weights.items()) / 4
    GST = adjust_gst_with_prediction(GST, densities)
    return max(min(math.ceil(GST), max_gst), min_gst)

@app.route('/traffic', methods=['GET'])
def traffic_density():
    video_path = request.args.get('video_path')
    if not video_path:
        return jsonify({"error": "No video path provided"}), 400
    
    try:
        densities, error = process_entire_video(video_path)
        if densities is None:
            return jsonify({"error": error}), 500
        
        if "ambulance" in densities:
            return jsonify({"densities": {"ambulance": 1}, "GST": 120})
        
        densities["total_density"] = sum(densities.values())
        GST = get_GST(densities)
        return jsonify({"densities": densities, "GST": GST})
    except Exception as e:
        print(f"Error in traffic_density endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
