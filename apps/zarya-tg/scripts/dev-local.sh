#!/usr/bin/env bash
# Local development without Docker (macOS / Linux)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> zarya local dev (no Docker)"
echo "    API:      http://localhost:8000"
echo "    Mini App: http://localhost:5173"
echo ""

MIN_PYTHON_MINOR=9

python_version_ok() {
  local version="$1"
  local major=${version%%.*}
  local minor=${version#*.}
  [ "$major" -eq 3 ] && [ "$minor" -ge "$MIN_PYTHON_MINOR" ]
}

find_python() {
  local candidates=(
    python3.12 python3.11 python3.10 python3
    /opt/homebrew/bin/python3.12
    /opt/homebrew/bin/python3.11
    /opt/homebrew/bin/python3.10
    /opt/homebrew/opt/python@3.12/bin/python3.12
    /opt/homebrew/opt/python@3.11/bin/python3.11
    /opt/homebrew/opt/python@3.10/bin/python3.10
    /usr/local/bin/python3.12
    /usr/local/bin/python3.11
    /usr/local/bin/python3.10
  )

  local candidate version
  for candidate in "${candidates[@]}"; do
    if command -v "$candidate" >/dev/null 2>&1; then
      version=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null) || continue
      if python_version_ok "$version"; then
        echo "$candidate"
        return 0
      fi
    fi
  done
  return 1
}

print_python_diagnostics() {
  echo "Python interpreters found on this machine:"
  local found=0
  local candidates=(python3.12 python3.11 python3.10 python3 python)
  local candidate version
  for candidate in "${candidates[@]}"; do
    if command -v "$candidate" >/dev/null 2>&1; then
      version=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null) || version="?"
      echo "  $candidate -> $version"
      found=1
    fi
  done
  if [ "$found" -eq 0 ]; then
    echo "  (none)"
  fi
  echo ""
  echo "Install Python 3.11 on macOS:"
  echo "  brew install python@3.11"
  echo "  echo 'export PATH=\"/opt/homebrew/opt/python@3.11/bin:\$PATH\"' >> ~/.zshrc"
  echo "  source ~/.zshrc"
  echo ""
  echo "Then recreate the virtualenv:"
  echo "  cd apps/zarya-tg/backend && rm -rf .venv"
  echo "  ./scripts/dev-local.sh"
}

ensure_node() {
  if command -v npm >/dev/null 2>&1; then
    return 0
  fi
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
  echo "ERROR: Python 3.${MIN_PYTHON_MINOR}+ required."
  echo ""
  print_python_diagnostics
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

# Recreate venv if it was built with an older Python
if [ -d .venv ]; then
  VENV_PY=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "")
  if [ -f .venv/pyvenv.cfg ]; then
    OLD_PY=$(grep '^version' .venv/pyvenv.cfg | cut -d= -f2 | tr -d ' ')
    OLD_MINOR=${OLD_PY#*.}
    OLD_MINOR=${OLD_MINOR%%.*}
    if [ -n "$OLD_MINOR" ] && [ "$OLD_MINOR" -lt "$MIN_PYTHON_MINOR" ]; then
      echo "    Removing old .venv (Python $OLD_PY)..."
      rm -rf .venv
    fi
  fi
fi

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
