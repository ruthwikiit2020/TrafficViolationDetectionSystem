from ultralytics import YOLO
import math
import cv2
import cvzone
import torch
from GroqOCR import predict_number_plate
from paddleocr import PaddleOCR
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
def connect_to_db():
    try:
        client = MongoClient("")  # MongoDB URI
        db = client["NumberPlates_Speed"]
        print("Connected to MongoDB.")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

db = connect_to_db()
collection = db["violations"]


def save_violation_to_db(date, time, class_name, numberplate=None, speed=None):
    try:
        # Define time buffer in seconds (e.g., 60 seconds)
        time_buffer = 300

        # Combine the current date and time into a datetime object
        violation_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")

        # Find the most recent record for this numberplate
        record = collection.find_one(
            {"numberplate": numberplate},
            sort=[("date", -1), ("time", -1)]
        )

        if record:
            # Combine the record's date and time to form a datetime object
            record_dt = datetime.strptime(f"{record['date']} {record['time']}", "%Y-%m-%d %H:%M:%S")
            time_diff = (violation_dt - record_dt).total_seconds()
            if time_diff < time_buffer:
                print(f"*****Violation for {numberplate} logged {time_diff:.2f} seconds ago. Skipping insertion.*****")
                return

        # Prepare the record for insertion
        new_record = {
            "date": date,
            "time": time,
            "class_name": class_name,
            "numberplate": numberplate
        }
        if speed is not None:
            new_record["speed"] = speed

        collection.insert_one(new_record)
        print(f"Violation saved to MongoDB: {new_record}")
    except Exception as e:
        print(f"Error saving violation to MongoDB: {e}")



cap = cv2.VideoCapture("videos/phone/ph3.mp4")  # For videos

model = YOLO("Hel_NP_best.pt")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
classNames = ["with helmet", "without helmet", "rider", "number plate"]
num = 0
old_npconf = 0

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output = cv2.VideoWriter('output.mp4', fourcc, fps, (frame_width, frame_height))

# ocr = PaddleOCR(use_angle_cls=True, lang='en')

while True:
    success, img = cap.read()
    if not success:
        print("No more frames to read. Exiting loop.")
        break

    new_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = model(new_img, stream=True, device=str(device))
    for r in results:
        boxes = r.boxes
        li = dict()
        rider_box = list()
        xy = boxes.xyxy
        confidences = boxes.conf
        classes = boxes.cls
        new_boxes = torch.cat((xy.to(device), confidences.unsqueeze(1).to(device), classes.unsqueeze(1).to(device)), 1)
        try:
            new_boxes = new_boxes[new_boxes[:, -1].sort()[1]]
            indices = torch.where(new_boxes[:, -1] == 2)
            rows = new_boxes[indices]
            for box in rows:
                x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                rider_box.append((x1, y1, x2, y2))
        except Exception as e:
            print(e)

        for i, box in enumerate(new_boxes):
            x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            conf = math.ceil((box[4] * 100)) / 100
            cls = int(box[5])
            if (classNames[cls] == "without helmet" and conf >= 0.5) or \
               (classNames[cls] == "rider" and conf >= 0.45) or \
               (classNames[cls] == "number plate" and conf >= 0.5):

                if classNames[cls] == "rider":
                    rider_box.append((x1, y1, x2, y2))
                if rider_box:
                    for j, rider in enumerate(rider_box):
                        if x1 + 10 >= rider_box[j][0] and y1 + 10 >= rider_box[j][1] and \
                           x2 <= rider_box[j][2] and y2 <= rider_box[j][3]:
                            if classNames[cls] == "without helmet":
                                box_color = (0, 0, 255)
                                text_color = (0, 0, 255)
                            else:
                                box_color = (255, 0, 0)
                                text_color = (248, 222, 34)

                            cvzone.cornerRect(img, (x1, y1, w, h), l=15, rt=5, colorR=box_color)
                            cvzone.putTextRect(img, f"{classNames[cls].upper()}", (x1 + 10, y1 - 10),
                                               scale=1.5, offset=10, thickness=2,
                                               colorT=(39, 40, 41), colorR=text_color)

                            li.setdefault(f"rider{j}", [])
                            li[f"rider{j}"].append(classNames[cls])

                            if classNames[cls] == "number plate":
                                npx, npy, npw, nph, npconf = x1, y1, w, h, conf
                                crop = img[npy:npy + h, npx:npx + w]

        if li:
            for key, value in li.items():
                if len(list(set(li[key]))) == 3:
                    try:
                        # Use the hybrid OCR function for the cropped number plate image.
                        vechicle_number, conf = predict_number_plate(crop)
                        if vechicle_number and conf:
                            cvzone.putTextRect(img, f"{vechicle_number} {round(conf * 100, 2)}%",
                                               (x1, y1 - 50), scale=1.5, offset=10,
                                               thickness=2, colorT=(39, 40, 41), colorR=(105, 255, 255))
                            current_time = datetime.now()
                            date = current_time.strftime("%Y-%m-%d")
                            time = current_time.strftime("%H:%M:%S")
                            class_name = "No-Helmet"
                            save_violation_to_db(date, time, class_name, vechicle_number)
                    except Exception as e:
                        print(e)

        output.write(img)
        cv2.imshow('Video', img)
        li = list()
        rider_box = list()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
output.release()
cv2.destroyAllWindows()
