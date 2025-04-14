import cv2
import numpy as np
import threading
import torch
import time
from datetime import datetime
from pymongo import MongoClient
from collections import deque
import math
from GroqOCR import predict_number_plate
from ultralytics import YOLO
from sort import Sort

# Define the classes corresponding to vehicles (e.g., car, truck, etc.)
VEHICLE_CLASSES = [2, 3, 5, 7]


def estimatespeed(Location1, Location2):
    # Calculate the Euclidean distance between two locations (in pixels)
    d_pixel = math.sqrt((Location2[0] - Location1[0]) ** 2 + (Location2[1] - Location1[1]) ** 2)
    ppm = 8  # pixels per meter conversion factor (example value)
    time_constant = 15 * 3.6  # Conversion constant to get km/h (15 is an arbitrary time factor, multiplied by 3.6 to convert m/s to km/h)
    speed = (d_pixel / ppm) * time_constant
    return int(speed)


def get_car(license_plate, tracked_vehicles):
    # Unpack the license plate detection details
    lx1, ly1, lx2, ly2, score, cls = license_plate
    # Check each tracked vehicle to see if the license plate box falls within the vehicle box
    for veh in tracked_vehicles:
        vx1, vy1, vx2, vy2, track_id = veh
        if lx1 >= vx1 and ly1 >= vy1 and lx2 <= vx2 and ly2 <= vy2:
            return veh
    return None


class SpeedEstimator:
    def __init__(self, vehicle_model_path="Vehi_best_yolov8m.pt", plate_model_path="OverSpeed_best.pt", speed_limit=80):
        # Load YOLO models for vehicle and number plate detection
        self.vehicle_detector = YOLO(vehicle_model_path)
        self.plate_detector = YOLO(plate_model_path)
        # Initialize a SORT tracker to track vehicles across frames
        self.tracker = Sort()
        # Data structure to store historical center positions for speed estimation
        self.data_deque = {}
        # Data structure to store estimated speeds over time for each tracked vehicle
        self.speed_line_queue = {}
        # Keep track of which vehicle IDs have already been logged as violations
        self.logged_ids = set()
        self.speed_limit = speed_limit
        self.db_connection = self.connect_to_db()

    def connect_to_db(self):
        try:
            client = MongoClient("") #MONGODB URI
            db = client["NumberPlates_Speed"]
            print("Connected to MongoDB.")
            return db
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise

    def save_violation_to_db(self, date, time_str, class_name, numberplate=None, speed=None):
        """
        Save a violation record to the database, using a time buffer to avoid duplicate logging.

        Parameters:
          date (str): Date in "YYYY-MM-DD" format.
          time_str (str): Time in "HH:MM:SS" format.
          class_name (str): Violation type (e.g., "OverSpeeding").
          numberplate (str, optional): Recognized license plate text.
          speed (int, optional): Estimated vehicle speed.
        """
        try:
            # Define a time buffer (in seconds)
            time_buffer = 300

            # Combine the provided date and time into a datetime object
            violation_dt = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M:%S")

            # Get the violations collection from the connected database
            collection = self.db_connection["violations"]
            # Find the most recent record for this numberplate
            record = collection.find_one(
                {"numberplate": numberplate},
                sort=[("date", -1), ("time", -1)]
            )

            if record:
                # Combine the record's date and time into a datetime object
                record_dt = datetime.strptime(f"{record['date']} {record['time']}", "%Y-%m-%d %H:%M:%S")
                # Calculate the time difference in seconds
                time_diff = (violation_dt - record_dt).total_seconds()
                if time_diff < time_buffer:
                    print(f"Violation for {numberplate} logged {time_diff:.2f} seconds ago. Skipping insertion.")
                    return

            # Prepare the new violation record for insertion
            new_record = {
                "date": date,
                "time": time_str,
                "class_name": class_name,
                "numberplate": numberplate
            }
            if speed is not None:
                new_record["speed"] = speed

            collection.insert_one(new_record)
            print(f"Violation saved to MongoDB: {new_record}")
        except Exception as e:
            print(f"Error saving violation to MongoDB: {e}")

    def process_frame(self, frame):
        # Get the current timestamp for logging purposes
        current_time = datetime.now()
        # Run the vehicle detector on the frame
        vehicle_results = self.vehicle_detector(frame)[0]
        detections = []
        # Iterate through each detection from the vehicle model
        for detection in vehicle_results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            # Check if the detected object belongs to one of the specified vehicle classes
            if int(class_id) in VEHICLE_CLASSES:
                detections.append([x1, y1, x2, y2, score])
        # Convert the list of detections to a NumPy array (or an empty array if none)
        dets = np.array(detections) if len(detections) > 0 else np.empty((0, 5))
        # Update the tracker with the current detections; each tracked vehicle gets a unique ID
        tracked_vehicles = self.tracker.update(dets)

        # Run the plate detector on the same frame
        plate_results = self.plate_detector(frame)[0]
        plate_detections = plate_results.boxes.data.tolist()

        # Process each tracked vehicle for speed estimation and potential violations
        for veh in tracked_vehicles:
            x1, y1, x2, y2, track_id = veh
            track_id = int(track_id)
            # Calculate the center point of the vehicle's bounding box
            center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            # Initialize a deque (with a maximum length) for this vehicle if not already present
            if track_id not in self.data_deque:
                self.data_deque[track_id] = deque(maxlen=64)
                self.speed_line_queue[track_id] = []
            # Append the latest center position to the left of the deque (for a history of positions)
            self.data_deque[track_id].appendleft(center)
            # If there are at least two recorded positions, estimate the speed
            if len(self.data_deque[track_id]) >= 2:
                spd = estimatespeed(self.data_deque[track_id][1], self.data_deque[track_id][0])
                self.speed_line_queue[track_id].append(spd)
                # Calculate the average speed over the stored speed measurements
                avg_speed = round(sum(self.speed_line_queue[track_id]) / len(self.speed_line_queue[track_id]))
            else:
                avg_speed = 0

            # Draw the bounding box for the vehicle
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            # Label the vehicle with its track ID and estimated speed
            label = f"ID {track_id}: {avg_speed} km/h"
            cv2.putText(frame, label, (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Process the number plate detections and try to associate a plate with the current vehicle
            for plate in plate_detections:
                associated_vehicle = get_car(plate, tracked_vehicles)
                if associated_vehicle is not None and int(associated_vehicle[4]) == track_id:
                    lx1, ly1, lx2, ly2, plate_score, _ = plate
                    # Crop the region of interest containing the number plate
                    plate_crop = frame[int(ly1):int(ly2), int(lx1):int(lx2)]
                    # Run OCR on the cropped plate image to recognize text
                    ocr_text, ocr_conf = predict_number_plate(plate_crop)
                    # Draw a rectangle around the number plate and overlay the recognized text
                    cv2.rectangle(frame, (int(lx1), int(ly1)), (int(lx2), int(ly2)), (0, 0, 255), 2)
                    cv2.putText(frame, ocr_text, (int(lx1), int(ly1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    # If the vehicle is speeding, the plate was detected, and this violation hasn't been logged recently...
                    if avg_speed > self.speed_limit and track_id not in self.logged_ids and ocr_text and ocr_text.strip():
                        # Format the current date and time
                        date_str = current_time.strftime("%Y-%m-%d")
                        time_str = current_time.strftime("%H:%M:%S")
                        class_name = "OverSpeeding"
                        # Spawn a separate thread to save the violation to the database using our new function
                        threading.Thread(
                            target=self.save_violation_to_db,
                            args=(date_str, time_str, class_name, ocr_text.strip(), avg_speed)
                        ).start()
                        self.logged_ids.add(track_id)
                    break  # Break out after processing the associated plate for this vehicle
        return frame


if __name__ == "__main__":
    cap = cv2.VideoCapture("videos/tj.mp4")
    if not cap.isOpened():
        print("Error opening video file")
        exit()
    speed_estimator = SpeedEstimator()

    # Setup video writer for output
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("OSoutput.mp4", fourcc, 20.0, (1020, 500))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Resize the frame for processing
        frame = cv2.resize(frame, (1020, 500))
        # Process the frame to detect vehicles, estimate speed, perform OCR, and log violations if necessary
        result_frame = speed_estimator.process_frame(frame)
        out.write(result_frame)
        cv2.imshow("Overspeed Detection", result_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
