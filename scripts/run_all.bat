@echo off
REM Start HoneyBoo Backend and Frontend together on Windows
cd /d "%~dp0\.."
echo ==========================================================
echo 🐝 Launching HoneyBoo System (Windows)...
echo ==========================================================

start "HoneyBoo Backend Server" cmd /k "scripts\start_backend.bat"
start "HoneyBoo Frontend Server" cmd /k "scripts\start_frontend.bat"

echo.
echo Both servers have been launched in separate windows!
echo Backend & Swagger Docs: http://127.0.0.1:8000/docs
echo Frontend Dashboard UI:  http://127.0.0.1:5173
echo.
pause
