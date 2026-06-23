#!/usr/bin/env bash
# Local development without Docker (macOS / Linux)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> zarya local dev (no Docker)"
echo "    API:      http://localhost:8000"
echo "    Mini App: http://localhost:5173"
echo ""

# --- Prerequisites ---

find_python() {
  for candidate in python3.12 python3.11 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      version=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
      major=${version%%.*}
      minor=${version#*.}
      if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
        echo "$candidate"
        return 0
      fi
    fi
  done
  return 1
}

ensure_node() {
  if command -v npm >/dev/null 2>&1; then
    return 0
  fi
  # nvm is common on macOS but not loaded in non-interactive shells
  if [ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
  fi
  if command -v npm >/dev/null 2>&1; then
    return 0
  fi
  echo "ERROR: npm not found."
  echo "Install Node.js 20+ from https://nodejs.org"
  echo "Or on macOS: brew install node"
  exit 1
}

PYTHON_BIN=$(find_python) || {
  echo "ERROR: Python 3.10+ required (3.11+ recommended)."
  echo "On macOS: brew install python@3.11"
  exit 1
}

ensure_node

PY_VERSION=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
NODE_VERSION=$(node -v)
echo "==> Using Python $PY_VERSION ($PYTHON_BIN), Node $NODE_VERSION"
echo ""

# --- Backend ---
echo "==> Setting up backend..."
cd "$ROOT/backend"

if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
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
