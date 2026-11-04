#!/usr/bin/env bash
# Start HoneyBoo FastAPI Backend
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🐝 Starting HoneyBoo Backend API Server..."
echo "=========================================================="

if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found! Please run 'python3 -m venv backend/venv && pip install -r backend/requirements.txt' first."
    exit 1
fi

export PYTHONPATH=.
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
