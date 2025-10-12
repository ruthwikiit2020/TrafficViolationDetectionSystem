🚦 Traffic Violation Detection System

### 👥 Team Members

* **Ruthwik Siddhartha**
* **Ananth**
* **Siddhanth**
* **Aryan**

---

## 📘 Overview

The **Traffic Violation Detection System** is an AI-powered application designed to automate the detection of traffic rule violations such as **helmet absence** and **overspeeding**.
By leveraging **computer vision** and **OCR**, the system identifies offenders from live or recorded traffic video streams and automatically generates **e-challan reports**, which are displayed on an interactive **web dashboard**.

---

## 🧠 Tech Stack

### ⚙️ Backend & AI

* **YOLOv8** – Object detection for identifying vehicles and helmet usage.
* **OpenCV** – Video stream processing and frame extraction.
* **PaddleOCR** – Optical Character Recognition for license plate text extraction.
* **Python** – For AI model integration and video analysis pipeline.

### 💻 Frontend & Database

* **React.js** – Interactive dashboard for monitoring violations.
* **Node.js & Express.js** – Backend server for handling API requests and communication.
* **MongoDB** – Database for storing violation records and e-challan reports.

---

## 🔍 Features

✅ **Helmet Detection** – Detects riders not wearing helmets in traffic videos.
✅ **Overspeed Detection** – Calculates vehicle speed and identifies overspeeding instances.
✅ **License Plate Recognition** – Extracts license numbers using OCR.
✅ **Real-time Logging** – Stores detected violations instantly in MongoDB.
✅ **E-Challan Generation** – Automatically creates and displays reports for each violation.
✅ **Dashboard Visualization** – Provides daily, weekly, and monthly violation statistics.

---

## 🧩 System Architecture

1. **Video Input** (live CCTV or pre-recorded footage)
2. **YOLOv8 Detection** (helmet and vehicle identification)
3. **Speed Estimation Module** (using frame timestamps and vehicle displacement)
4. **PaddleOCR Recognition** (license plate extraction)
5. **Database Logging** (violation details stored in MongoDB)
6. **Dashboard Display** (React frontend visualizing reports and analytics)

---

## 📊 Dashboard Preview (Key Sections)

* **Violation Summary** – Total helmet and speed violations detected.
* **E-Challan Reports** – Detailed offender information.
* **Statistics & Charts** – Visual representation of daily and monthly trends.

---

## 🧱 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/TrafficViolationDetectionSystem.git
cd TrafficViolationDetectionSystem
```

### 2️⃣ Backend Setup

```bash
cd backend
npm install
node server.js
```

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm start
```

### 4️⃣ AI Module Setup

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### 5️⃣ Run the Detection Script

```bash
python detect_violations.py
```

---

## 📦 Output

* Detected violations displayed in the dashboard.
* OCR-extracted license plates stored in MongoDB.
* Auto-generated e-challan records.
* Analytical charts for daily reports.

---

## 🧾 Future Enhancements

* Integration with **ANPR (Automatic Number Plate Recognition)** databases.
* **GPS and IoT integration** for live traffic monitoring.
* Improved **multi-camera tracking** and cloud-based storage.
* **Automated SMS/email notifications** to violators.
