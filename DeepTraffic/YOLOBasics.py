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
vehicle_classes = {"car", "truck", "motorcycle", "ambulance", "bus"}

# Store processed videos with timestamps to prevent redundant processing
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

# def process_entire_video(video_path, force_refresh=False):
#     """
#     Process video frames to count unique vehicles.
    
#     Args:
#         video_path: Path to the video file
#         force_refresh: If True, reprocess the video even if cached results exist
        
#     Returns:
#         Tuple of (densities dictionary, error message)
#     """
#     if not force_refresh and video_path in processed_videos:
#         print(f"Using cached results for {video_path}")
#         return processed_videos[video_path]
    
#     print(f"Processing video (force_refresh={force_refresh}): {video_path}")
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         return None, "Failed to open video."
    
#     unique_counts = {cls: 0 for cls in vehicle_classes}
#     track_ids = {cls: set() for cls in vehicle_classes}
#     frame_count = 0
#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
#     print(f"Processing {video_path} ({total_frames} frames)")
#     start_time = time.time()
    
#     while True:
#         success, frame = cap.read()
#         if not success:
#             break
        
#         frame_count += 1
#         if frame_count % 29 != 0:
#             continue  # Process every 29th frame
        
#         results = model(frame, stream=True)
#         detections = []
#         class_ids = []
        
#         for r in results:
#             for box in r.boxes:
#                 try:
#                     x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
#                     conf = float(box.conf[0])
#                     cls_id = int(box.cls[0])
#                     detected_class = r.names.get(cls_id, "unknown")
                    
#                     if detected_class in vehicle_classes:
#                         detections.append([[x1, y1, x2, y2], conf, detected_class])
#                         class_ids.append(detected_class)
#                 except Exception as e:
#                     print(f"Error processing detection: {e}")
        
#         if "ambulance" in class_ids:
#             cap.release()
#             processed_videos[video_path] = {"ambulance": 1}, None
#             return {"ambulance": 1}, None
        
#         if detections:
#             try:
#                 tracks = tracker.update_tracks(detections, frame=frame)
#                 for track in tracks:
#                     if not track.is_confirmed():
#                         continue
                    
#                     track_id = track.track_id
#                     detected_class = track.det_class
                    
#                     if detected_class in vehicle_classes and track_id not in track_ids[detected_class]:
#                         track_ids[detected_class].add(track_id)
#                         unique_counts[detected_class] += 1
#             except Exception as e:
#                 print(f"Error in tracking: {e}")
#                 continue
    
#     cap.release()
#     processing_time = time.time() - start_time
#     print(f"Video processing completed in {processing_time:.2f} seconds")
    
#     processed_results = {f"{cls}_density": unique_counts[cls] for cls in vehicle_classes if cls != "ambulance"}
#     processed_videos[video_path] = processed_results, None
#     print(f"Processing complete. {processed_results}")
#     return processed_results, None

def process_entire_video(video_path, force_refresh=False):
    """
    Process video frames to count unique vehicles.
    """
    if not force_refresh and video_path in processed_videos:
        print(f"Using cached results for {video_path}")
        return processed_videos[video_path]
    
    print(f"Processing video (force_refresh={force_refresh}): {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, "Failed to open video."
    
    # # Create a new tracker instance for each video
    # video_tracker = DeepSort(
    #     max_age=30,
    #     n_init=3,
    #     max_iou_distance=0.7,
    #     max_cosine_distance=0.2,
    #     nn_budget=100
    # )
    video_tracker = DeepSort(
    max_age=45,               # Keep track alive for ~1.5s
    n_init=3,                 # Trust object quickly due to sparse frames
    max_iou_distance=0.95,    # Allow more movement across skipped frames
    max_cosine_distance=0.7,  # Let similar vehicles be matched
    nn_budget=120             # Memory budget for appearance features
)
    
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
        if frame_count % 29 != 0:
            continue  # Process every 29th frame
        
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
                        detections.append([x1, y1, x2, y2, conf, cls_id, detected_class])
                        class_ids.append(detected_class)
                        
                        # Debug print
                        print(f"Detected {detected_class} with confidence {conf:.2f}")
                except Exception as e:
                    print(f"Error processing detection: {e}")
        
        if "ambulance" in class_ids:
            cap.release()
            processed_videos[video_path] = {"ambulance": 1}, None
            return {"ambulance": 1}, None
        
        if detections:
            try:
                # Format detections for DeepSort - This might be where the issue is
                detections_for_tracker = []
                for det in detections:
                    x1, y1, x2, y2, conf, cls_id, cls_name = det
                    detections_for_tracker.append(
                        [[x1, y1, x2, y2], conf, cls_name]
                    )
                
                tracks = video_tracker.update_tracks(detections_for_tracker, frame=frame)
                print(f"Number of tracks: {len(tracks)}")
                
                for track in tracks:
                    if not track.is_confirmed():
                        continue
                    
                    track_id = track.track_id
                    detected_class = track.det_class
                    
                    print(f"Confirmed track {track_id}, class {detected_class}")
                    
                    if detected_class in vehicle_classes and track_id not in track_ids[detected_class]:
                        track_ids[detected_class].add(track_id)
                        unique_counts[detected_class] += 1
                        print(f"Added new {detected_class} with track_id {track_id}")
                        print(f"Current counts: {unique_counts}")
                
            except Exception as e:
                print(f"Error in tracking: {e}")
                continue
    
    cap.release()
    processing_time = time.time() - start_time
    print(f"Video processing completed in {processing_time:.2f} seconds")
    
    # Debug print current counts before returning
    print(f"Final counts: {unique_counts}")
    print(f"Track IDs: {track_ids}")
    
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
    max_gst = 60
    min_gst = 10
    weights = {"car_density": 10, "bikes_density": 7, "truck_density": 20, "bus_density": 15}
    GST = sum(densities.get(k, 0) * v for k, v in weights.items()) / 4
    GST = adjust_gst_with_prediction(GST, densities)
    return max(min(math.ceil(GST), max_gst), min_gst)

@app.route('/traffic', methods=['GET'])
def traffic_density():
    """Endpoint to get traffic density and GST based on video analysis."""
    video_path = request.args.get('video_path')
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    if not video_path:
        return jsonify({"error": "No video path provided"}), 400
    
    try:
        densities, error = process_entire_video(video_path, force_refresh=force_refresh)
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

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    """Clear the video processing cache."""
    global processed_videos
    processed_videos.clear()
    print("Cache cleared successfully")
    return jsonify({"status": "Cache cleared successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)

    # process_entire_video("vid1.mp4")
