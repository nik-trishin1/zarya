#!/usr/bin/env bash
# Local development without Docker (macOS / Linux)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> zarya local dev (no Docker)"
echo "    API:      http://localhost:8000"
echo "    Mini App: http://localhost:5173"
echo ""

# --- Backend ---
echo "==> Setting up backend..."
cd "$ROOT/backend"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "    Created backend/.env (SQLite + DEV_MODE enabled)"
fi

mkdir -p uploads

echo "==> Starting backend on :8000..."
python run.py &
BACKEND_PID=$!

# --- Frontend ---
echo "==> Setting up frontend..."
cd "$ROOT/frontend"
npm install --silent

if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "==> Starting frontend on :5173..."
npm run dev &
FRONTEND_PID=$!

cleanup() {
  echo ""
  echo "==> Stopping..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo ""
echo "==> Ready. Press Ctrl+C to stop."
wait
