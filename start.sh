#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🏃 Marathon Time Predictor — Starting up..."
echo ""

# Backend
echo "📦 Installing Python dependencies..."
cd "$ROOT_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -q

echo "🤖 Training ML model..."
python model/train.py

echo "🚀 Starting FastAPI backend on http://localhost:8000 ..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
echo ""
echo "📦 Installing frontend dependencies..."
cd "$ROOT_DIR/frontend"
npm install --silent

echo "⚡ Starting React frontend on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are running!"
echo "   Frontend → http://localhost:3000"
echo "   Backend  → http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
