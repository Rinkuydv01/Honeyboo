# HoneyBoo Testing & Verification Report

This document records the automated testing strategy, synthetic validation datasets, and test execution results for HoneyBoo.

---

## 1. Automated Test Suite Structure

The test suite is located in `backend/tests/` and executed using `pytest`:

```
backend/tests/
├── test_counting.py    # Directional crossing geometry, duplicate suppression, grazing rejection
├── test_tracking.py    # ByteTrack association, IoU calculations, track confirmation
├── test_analytics.py   # Interval aggregation, statistical Z-score anomalies, disclaimers
└── test_api.py         # REST API endpoints, file uploads, invalid file rejection, previews
```

---

## 2. Test Execution Commands

### On Linux / macOS:
```bash
PYTHONPATH=. backend/venv/bin/python -m pytest -v backend/tests
```

### On Windows:
```cmd
set PYTHONPATH=.
backend\venv\Scripts\python -m pytest -v backend\tests
```

---

## 3. Test Cases & Verification Results

### Suite 1: Entrance Counting Geometry & Logic (`test_counting.py`)
- `test_orientation_and_intersection_geometry`: Validates 2D cross-product line orientation and parametric segment intersection calculations (**PASSED**).
- `test_incoming_crossing_classification`: Simulates a bee trajectory moving from outside ($y=410$) across line ($y=500$) to inside ($y=530$). Confirms `INCOMING` classification (**PASSED**).
- `test_outgoing_crossing_classification`: Simulates a bee trajectory moving from inside ($y=590$) to outside ($y=450$). Confirms `OUTGOING` classification (**PASSED**).
- `test_cooldown_duplicate_prevention`: Simulates a bee lingering and oscillating across the line 3 frames later; confirms secondary crossing is suppressed by the cooldown window (**PASSED**).
- `test_parallel_grazing_rejection`: Simulates a bee flying parallel to the line without crossing; confirms zero count recorded (**PASSED**).

### Suite 2: Multi-Object Tracking (`test_tracking.py`)
- `test_iou_calculation`: Verifies Intersection over Union for identical, overlapping, and disjoint bounding boxes (**PASSED**).
- `test_bytetracker_association_and_lifecycle`: Verifies two-stage data association, tentative-to-confirmed state promotion, velocity estimation, and temporary detection loss recovery (**PASSED**).

### Suite 3: Activity Analytics & Anomaly Detection (`test_analytics.py`)
- `test_interval_aggregation`: Confirms that timestamped crossing events are correctly bucketed into discrete 60s windows with net movement calculation (**PASSED**).
- `test_anomaly_detection_and_disclaimer`: Simulates a baseline activity series followed by a traffic surge ($Z > 2.0$) and a subsequent 90% sudden drop. Confirms `HIGH_ACTIVITY` and `SUDDEN_DROP` alerts and verifies that the scientific limitation disclaimer is present on all alerts (**PASSED**).

### Suite 4: REST API & Integration (`test_api.py`)
- `test_health_endpoint`: Verifies `/api/health` returns healthy status and reports hardware device information (**PASSED**).
- `test_settings_endpoint`: Verifies `/api/settings` returns configurable hyperparameters (**PASSED**).
- `test_dashboard_summary_endpoint`: Verifies `/api/dashboard/summary` returns system totals and device info (**PASSED**).
- `test_invalid_video_upload_rejection`: Uploads a mock `.exe` file; verifies rejection with HTTP 400 Bad Request (**PASSED**).
- `test_valid_video_upload`: Uploads a synthetic video, checks metadata extraction, verifies preview frame capture, and cleans up (**PASSED**).

---

## 4. Test Execution Summary

```
============================= test session starts ==============================
platform darwin -- Python 3.14.4, pytest-9.2.0, pluggy-1.7.0
rootdir: /Users/rinkuyadav/Documents/CSE471-honeyboo
collected 14 items

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

======================== 14 passed, 2 warnings in 2.15s ========================
```

---

## 5. End-to-End Pipeline Verification with Synthetic Video

The project includes an offline synthetic hive video generator in `backend/app/utils/synthetic_generator.py` generating `sample_videos/entrance_sample.mp4`:
- Resolution: 640x360
- Frame rate: 25 FPS
- Realistic simulated honeybee bodies, wing oscillations, and bidirectional crossings.
- Running the full pipeline on this video verified:
  - 3 Incoming crossings detected.
  - 3 Outgoing crossings detected.
  - 6 Total activity count recorded.
  - Net movement: 0.
  - Annotated output video generated at `/storage/processed/annotated_test_synthetic_session.mp4` (1.1 MB).
