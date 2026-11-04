# HoneyBoo Installation and Setup Guide

HoneyBoo is designed to run locally on resource-constrained consumer hardware (e.g., Intel Core i5, 8GB RAM, NVIDIA GTX 1650 4GB or standard CPU). No cloud subscriptions, specialized edge boards (Raspberry Pi/Jetson), or paid APIs are required.

---

## 1. Prerequisites

Before installing, ensure the following are installed on your machine:
- **Python:** Version 3.10, 3.11, 3.12, or 3.14.
- **Node.js:** Version 18.x, 20.x, or higher (with `npm`).
- **Git:** Standard git client.

---

## 2. Linux and macOS Installation

### Step 2.1: Clone or Open the Repository
```bash
cd /path/to/CSE471-honeyboo
```

### Step 2.2: Set Up Backend Virtual Environment
```bash
# Create python virtual environment
python3 -m venv backend/venv

# Activate virtual environment
source backend/venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 2.3: Set Up Frontend Dependencies
```bash
cd frontend
npm install
npm run build
cd ..
```

### Step 2.4: Run Automated Tests to Verify Setup
```bash
PYTHONPATH=. backend/venv/bin/python -m pytest -v backend/tests
```
All 14 tests should report **PASSED**.

---

## 3. Windows Installation

### Step 3.1: Open Command Prompt or PowerShell
Navigate to the HoneyBoo directory:
```cmd
cd C:\path\to\CSE471-honeyboo
```

### Step 3.2: Set Up Backend Virtual Environment
```cmd
python -m venv backend\venv
backend\venv\Scripts\activate
pip install --upgrade pip
pip install -r backend\requirements.txt
```

### Step 3.3: Set Up Frontend Dependencies
```cmd
cd frontend
npm install
npm run build
cd ..
```

### Step 3.4: Verify Tests on Windows
```cmd
set PYTHONPATH=.
backend\venv\Scripts\python -m pytest -v backend\tests
```

---

## 4. Running the Application

### Option A: Unified Startup (Single Command)
Run the all-in-one startup script:
- **Linux/macOS:**
  ```bash
  chmod +x scripts/*.sh
  ./scripts/run_all.sh
  ```
- **Windows:**
  ```cmd
  scripts\run_all.bat
  ```

### Option B: Separate Terminal Windows

#### Terminal 1 (Backend API & Local File Server):
```bash
# On Linux/macOS
source backend/venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# On Windows
backend\venv\Scripts\activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be accessible at: `http://127.0.0.1:8000/docs`

#### Terminal 2 (Frontend React Development Server):
```bash
cd frontend
npm run dev
```
Dashboard will be accessible at: `http://127.0.0.1:5173`

*(Note: If you have run `npm run build`, FastAPI also serves the frontend directly at `http://127.0.0.1:8000`!)*

---

## 5. Troubleshooting Common Issues

### Issue 1: `SSL: CERTIFICATE_VERIFY_FAILED` when downloading weights
- **Cause:** Restrictive corporate proxy or firewall intercepting HTTPS requests.
- **Solution:** HoneyBoo includes an automatic fallback that switches to local test simulation mode without crashing. To use real weights offline, place `yolov8n_bee.pt` directly into `models/`.

### Issue 2: CUDA Out of Memory (OOM) on 4GB GPU
- **Cause:** Extremely high video resolution (e.g., 4K).
- **Solution:** HoneyBoo automatically resizes video frames to max width 960px and supports frame skipping ($2\times$ or $3\times$) to keep VRAM usage below 2 GB. In `Settings`, you can also select CPU execution.
