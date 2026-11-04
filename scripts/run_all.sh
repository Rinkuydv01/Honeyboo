#!/usr/bin/env bash
# HoneyBoo All-in-One Runner (Backend + Frontend)
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🐝 Launching HoneyBoo System..."
echo "=========================================================="

# Trap SIGINT to kill background children on exit
trap 'kill $(jobs -p) 2>/dev/null || true' EXIT

# 1. Start Backend in background
echo "-> Starting Backend API on http://127.0.0.1:8000..."
source backend/venv/bin/activate
export PYTHONPATH=.
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# 2. Start Frontend Dev Server
echo "-> Starting Frontend UI on http://127.0.0.1:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "=========================================================="
echo "HoneyBoo is running!"
echo "Backend & Swagger API Docs: http://127.0.0.1:8000/docs"
echo "Frontend Dashboard UI:      http://127.0.0.1:5173"
echo "Press Ctrl+C to terminate both servers."
echo "=========================================================="

wait
