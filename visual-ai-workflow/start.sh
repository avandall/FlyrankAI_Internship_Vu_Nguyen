#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "=== Starting Visual AI Workflow System ==="

echo "1. Starting Backend on port 8000..."
cd "$DIR/backend"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "2. Starting Frontend on port 5173..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

echo "Systems running:"
echo " - Frontend: http://localhost:5173"
echo " - Backend API: http://localhost:8000"
echo " - Swagger Docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop."
wait
