@echo off
REM Start HoneyBoo Backend API on Windows
cd /d "%~dp0\.."
echo ==========================================================
echo 🐝 Starting HoneyBoo Backend API Server...
echo ==========================================================

if exist backend\venv\Scripts\activate.bat (
    call backend\venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please create it first.
    pause
    exit /b 1
)

set PYTHONPATH=.
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
