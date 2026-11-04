#!/usr/bin/env bash
# Start HoneyBoo Frontend Dev Server
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR/frontend"

echo "=========================================================="
echo "🐝 Starting HoneyBoo Frontend React Dev Server..."
echo "=========================================================="

if [ ! -d "node_modules" ]; then
    echo "node_modules not found. Running npm install..."
    npm install
fi

npm run dev
