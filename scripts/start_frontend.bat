@echo off
REM Start HoneyBoo Frontend Dev Server on Windows
cd /d "%~dp0\..\frontend"
echo ==========================================================
echo 🐝 Starting HoneyBoo Frontend Dev Server...
echo ==========================================================

if not exist node_modules (
    echo node_modules not found. Running npm install...
    call npm install
)

call npm run dev
