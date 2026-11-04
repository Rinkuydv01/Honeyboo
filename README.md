# HoneyBoo: Honeybee Hive Activity and Health Monitoring System

[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-emerald.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-cyan.svg)](https://react.dev/)
[![YOLOv8 + ByteTrack](https://img.shields.io/badge/Vision-YOLO_%2B_ByteTrack-yellow.svg)](https://github.com/ultralytics/ultralytics)

> **HoneyBoo** is a non-invasive, computer vision-based system designed to monitor honeybee (*Apis mellifera*) colony activity at the hive entrance using optical video recordings. By detecting individual bees, maintaining persistent trajectories across video frames, and analyzing bidirectional crossings across a user-configured virtual entrance line, HoneyBoo quantifies incoming returning foragers, outgoing departures, net entrance drift, and statistical anomaly indicators.

---

> ### ⚠️ Scientific Limitation Notice
> HoneyBoo quantifies entrance activity observations based solely on video data. Fluctuations in entrance traffic and statistical anomaly alerts represent behavioral observations, **not medical diagnoses, colony disease determinations, or comprehensive colony health assessments**. Entrance traffic must be interpreted alongside physical internal hive inspections by qualified beekeepers.

---

## 1. Project Features

- **Object Detection:** Detects honeybees in entrance footage using a lightweight YOLO model.
- **Persistent Multi-Object Tracking:** Tracks bees frame-by-frame with ByteTrack data association.
- **Directional Entrance Line Counting:** Classifies crossings as **INCOMING** (returning foragers) or **OUTGOING** (departing bees) using vector cross-product orientation math.
- **Anti-Duplication & Noise Rejection:** Enforces trajectory cooldowns and minimum track history thresholds to reject hovering or grazing bees.
- **Statistical Anomaly Indicators:** Calculates moving averages, rolling Z-score variances, and sudden drop/spike indicators.
- **Full Annotated Video Output:** Generates downloadable MP4 videos with bounding boxes, tracking IDs, entrance lines, and real-time HUD overlays.
- **Interactive Web Dashboard:** Clean, honeybee-inspired responsive dashboard built with React, TypeScript, and Tailwind CSS.
- **Interactive Entrance Alignment Canvas:** Allows beekeepers to drag and drop virtual entrance line endpoints ($P_1$ and $P_2$) and orient the inside/outside vector to match any camera setup.
- **Low-Resource Optimized:** Runs locally on consumer laptops (Intel Core i5, 8GB RAM, 4GB VRAM GTX 1650 or CPU fallback) without requiring paid cloud APIs or expensive edge hardware (Raspberry Pi/Jetson).

---

## 2. Project Architecture

```
CSE471-honeyboo/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/         # REST API endpoints (videos, processing, dashboard, settings, health)
│   │   ├── core/                  # Configuration, low-resource profile, auto-device detection
│   │   ├── database/              # SQLite session and table initializers
│   │   ├── models/                # SQLAlchemy ORM models (Video, Session, Activity, Event, Alert)
│   │   ├── schemas/               # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── video_service.py     # Video validation, metadata extraction, frame previews
│   │   │   ├── detection_service.py # Hardware-aware YOLO inference & simulated fallback
│   │   │   ├── tracking_service.py  # ByteTrack multi-object tracker
│   │   │   ├── counting_service.py  # Vector line crossing counter & HUD annotator
│   │   │   ├── analytics_service.py # Temporal bucket aggregation & anomaly detection
│   │   │   └── job_manager.py       # Asynchronous background job manager with cancellation
│   │   ├── utils/                 # Synthetic hive video generator
│   │   └── main.py                # FastAPI initialization & static SPA mounts
│   ├── tests/                     # 14 automated pytest test suites
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/            # Navbar, StatCard, EntranceLineCanvas, ScientificDisclaimer
│   │   ├── pages/                 # Dashboard, Upload, Processing, Analytics, Alerts, History, Settings
│   │   ├── services/              # Axios API service client
│   │   └── types/                 # TypeScript interfaces
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── models/                        # Custom YOLO bee weights directory (README included)
├── sample_videos/                 # Sample test footage (entrance_sample.mp4 included)
├── storage/                       # Local uploaded videos, processed videos, and SQLite database
├── docs/
│   ├── academic_report.md         # Full college-level academic project report
│   ├── architecture.md            # Technical architecture and pipeline breakdown
│   ├── installation.md            # Step-by-step setup guide
│   ├── training_guide.md          # Guide to labeling and training custom YOLO bee weights
│   ├── user_manual.md             # Non-programmer user guide
│   └── testing.md                 # Automated test verification results
├── scripts/                       # Startup scripts for Linux/macOS (.sh) and Windows (.bat)
└── README.md
```

---

## 3. Quick Start Guide

### 3.1 Prerequisites
- Python 3.10+
- Node.js 18+ (with `npm`)

### 3.2 Installation (Linux / macOS)
```bash
# 1. Set up backend virtual environment
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# 2. Set up frontend dependencies
cd frontend
npm install
npm run build
cd ..

# 3. Verify tests
PYTHONPATH=. backend/venv/bin/python -m pytest -v backend/tests
```

### 3.3 Installation (Windows)
```cmd
REM 1. Set up backend virtual environment
python -m venv backend\venv
backend\venv\Scripts\activate
pip install -r backend\requirements.txt

REM 2. Set up frontend dependencies
cd frontend
npm install
npm run build
cd ..

REM 3. Verify tests
set PYTHONPATH=.
backend\venv\Scripts\python -m pytest -v backend\tests
```

---

## 4. Running the Application

### Option 1: Unified Script
- **Linux/macOS:**
  ```bash
  chmod +x scripts/*.sh
  ./scripts/run_all.sh
  ```
- **Windows:**
  ```cmd
  scripts\run_all.bat
  ```

### Option 2: Running Services Separately
- **Backend API Server:**
  ```bash
  source backend/venv/bin/activate
  uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
  ```
  API Docs (Swagger UI): **`http://127.0.0.1:8000/docs`**

- **Frontend Development Server:**
  ```bash
  cd frontend
  npm run dev
  ```
  Web Dashboard: **`http://127.0.0.1:5173`**

*(Note: When `npm run build` is executed, FastAPI also serves the full compiled dashboard directly at `http://127.0.0.1:8000`)*.

---

## 5. Using the Application

1. **Dashboard Home:** View cumulative incoming/outgoing bee counts, net traffic drift, latest session status, and active anomaly alerts.
2. **Upload & Setup:** Drag and drop an entrance video (`.mp4`, `.avi`, `.mov`).
3. **Align Entrance Line:** Use the interactive canvas to position the virtual entrance line over the hive landing board. Select the hive interior side (Bottom, Top, Left, Right).
4. **Start Processing:** Click "Start Entrance Counting Pipeline".
5. **Live Progress:** Monitor real-time frame progress and live incoming/outgoing counters with safe cancellation support.
6. **Analytics:** Inspect time-series graphs (1-min, 5-min, 15-min buckets), watch the annotated output video, and export crossing events.
7. **Anomaly Alerts:** Review automated traffic drop/surge alerts accompanied by the scientific limitation disclaimer.

---

## 6. Automated Testing Verification

The project includes 14 unit and integration tests across computer vision geometry, tracking association, interval aggregation, anomaly calculations, and REST APIs:

```bash
PYTHONPATH=. backend/venv/bin/python -m pytest -v backend/tests
```

Results:
```
backend/tests/test_analytics.py::test_interval_aggregation PASSED        [  7%]
backend/tests/test_analytics.py::test_anomaly_detection_and_disclaimer PASSED [ 14%]
backend/tests/test_api.py::test_health_endpoint PASSED                   [ 21%]
backend/tests/test_api.py::test_settings_endpoint PASSED                 [ 28%]
backend/tests/test_api.py::test_dashboard_summary_endpoint PASSED        [ 35%]
backend/tests/test_api.py::test_invalid_video_upload_rejection PASSED    [ 42%]
backend/tests/test_api.py::test_valid_video_upload PASSED                [ 50%]
backend/tests/test_counting.py::test_orientation_and_intersection_geometry PASSED [ 57%]
backend/tests/test_counting.py::test_incoming_crossing_classification PASSED [ 64%]
backend/tests/test_counting.py::test_outgoing_crossing_classification PASSED [ 71%]
backend/tests/test_counting.py::test_cooldown_duplicate_prevention PASSED [ 78%]
backend/tests/test_counting.py::test_parallel_grazing_rejection PASSED   [ 85%]
backend/tests/test_tracking.py::test_iou_calculation PASSED              [ 92%]
backend/tests/test_tracking.py::test_bytetracker_association_and_lifecycle PASSED [100%]

======================== 14 passed in 2.15s ========================
```

---

## 7. Custom Bee Model Training

To train a custom honeybee detector on your own entrance footage:
1. Label bee bounding boxes using CVAT or Roboflow in YOLO format (`images/` and `labels/`).
2. Train a lightweight YOLOv8n model using PyTorch:
   ```bash
   yolo detect train data=bee_dataset/data.yaml model=yolov8n.pt epochs=60 imgsz=640 batch=16
   ```
3. Copy the resulting `best.pt` file to `models/yolov8n_bee.pt`. HoneyBoo will automatically load the bee weights on the next session.
See `docs/training_guide.md` for complete details.

---

## 8. License & Academic Attribution
Developed for college-level computer vision and machine learning academic demonstration.
License: MIT.
