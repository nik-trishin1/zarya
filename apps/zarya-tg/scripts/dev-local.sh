#!/usr/bin/env bash
# Local development without Docker (macOS / Linux)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BACKEND_ONLY=false
if [ "${1:-}" = "--backend-only" ]; then
  BACKEND_ONLY=true
fi

echo "==> zarya local dev (no Docker)"
echo "    API:      http://localhost:8000"
if [ "$BACKEND_ONLY" = false ]; then
  echo "    Mini App: http://localhost:5173"
fi
echo ""

MIN_PYTHON_MINOR=10
MAX_PYTHON_MINOR=13  # pydantic-core / PyO3 do not support 3.14 yet

python_version_ok() {
  local version="$1"
  local major=${version%%.*}
  local minor=${version#*.}
  [ "$major" -eq 3 ] && [ "$minor" -ge "$MIN_PYTHON_MINOR" ] && [ "$minor" -le "$MAX_PYTHON_MINOR" ]
}

find_python() {
  # Prefer 3.12 — best compatibility with project dependencies
  local candidates=(
    python3.12 python3.13 python3.11 python3.10
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12
    /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11
    /Library/Frameworks/Python.framework/Versions/3.10/bin/python3.10
    /opt/homebrew/bin/python3.12
    /opt/homebrew/bin/python3.13
    /opt/homebrew/bin/python3.11
    /opt/homebrew/bin/python3.10
    /opt/homebrew/opt/python@3.12/bin/python3.12
    /opt/homebrew/opt/python@3.13/bin/python3.13
    /opt/homebrew/opt/python@3.11/bin/python3.11
    /opt/homebrew/opt/python@3.10/bin/python3.10
    /usr/local/bin/python3.12
    /usr/local/bin/python3.13
    /usr/local/bin/python3.11
    /usr/local/bin/python3.10
    python3
    /usr/local/bin/python3
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
  local candidates=(python3.14 python3.13 python3.12 python3.11 python3.10 python3 python)
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
  if command -v python3.14 >/dev/null 2>&1; then
    echo "NOTE: Python 3.14 is installed but NOT supported (pydantic fails to build)."
    echo "      Install Python 3.12 from https://www.python.org/downloads/"
    echo ""
  fi
  echo "Install Python 3.12 on macOS (recommended, no Homebrew required):"
  echo "  1. Open https://www.python.org/downloads/release/python-3120/"
  echo "  2. Download macOS installer (.pkg) at the bottom of the page"
  echo "  3. Run installer, restart Terminal"
  echo "  4. Verify: python3.12 --version"
  echo ""
  echo "Supported range: Python 3.${MIN_PYTHON_MINOR} – 3.${MAX_PYTHON_MINOR}"
  echo ""
  echo "Remove incompatible venv and retry:"
  echo "  cd apps/zarya-tg/backend && rm -rf .venv"
  echo "  cd .. && ./scripts/dev-local.sh"
}

add_dir_to_path_if_npm() {
  local dir="$1"
  if [ -x "$dir/npm" ]; then
    export PATH="$dir:$PATH"
    return 0
  fi
  return 1
}

load_node_env() {
  if command -v npm >/dev/null 2>&1; then
    return 0
  fi

  # Homebrew (Apple Silicon + Intel)
  add_dir_to_path_if_npm /opt/homebrew/bin || true
  add_dir_to_path_if_npm /usr/local/bin || true
  command -v npm >/dev/null 2>&1 && return 0

  # Volta
  add_dir_to_path_if_npm "$HOME/.volta/bin" || true
  command -v npm >/dev/null 2>&1 && return 0

  # nvm
  if [ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
    nvm use default >/dev/null 2>&1 || nvm use node >/dev/null 2>&1 || nvm use --lts >/dev/null 2>&1 || true
  fi
  command -v npm >/dev/null 2>&1 && return 0

  # fnm
  if command -v fnm >/dev/null 2>&1; then
    # shellcheck disable=SC2046
    eval $(fnm env)
  elif [ -x "$HOME/.local/share/fnm/fnm" ]; then
    # shellcheck disable=SC2046
    eval $($HOME/.local/share/fnm/fnm env)
  fi
  command -v npm >/dev/null 2>&1 && return 0

  # asdf
  if [ -s "$HOME/.asdf/asdf.sh" ]; then
    # shellcheck disable=SC1091
    source "$HOME/.asdf/asdf.sh"
  fi
  command -v npm >/dev/null 2>&1 && return 0

  # Login shell profile (last resort — macOS often sets PATH only in .zprofile)
  for profile in "$HOME/.zprofile" "$HOME/.zshrc" "$HOME/.bash_profile"; do
    if [ -f "$profile" ]; then
      # shellcheck disable=SC1090
      source "$profile" 2>/dev/null || true
      command -v npm >/dev/null 2>&1 && return 0
    fi
  done

  return 1
}

print_node_diagnostics() {
  echo "Node/npm not found in PATH."
  echo ""
  echo "Install Node.js 20+ on macOS (no Homebrew required):"
  echo ""
  echo "  Option A — official installer (easiest):"
  echo "    1. Open https://nodejs.org/en/download"
  echo "    2. Download macOS Installer (.pkg) for LTS"
  echo "    3. Run the installer, then restart Terminal"
  echo "    4. Verify: node -v && npm -v"
  echo ""
  echo "  Option B — nvm (no admin install):"
  echo "    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
  echo "    source ~/.zshrc"
  echo "    nvm install 20"
  echo "    nvm use 20"
  echo ""
  echo "  Option C — install Homebrew first, then node:"
  echo "    /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
  echo "    brew install node"
  echo ""
  echo "  Option D — run backend only (no Mini App UI):"
  echo "    ./scripts/dev-local.sh --backend-only"
  echo ""
  echo "Verify after install:"
  echo "    node -v"
  echo "    npm -v"
}

ensure_node() {
  if load_node_env; then
    return 0
  fi
  echo "ERROR: npm not found."
  echo ""
  print_node_diagnostics
  exit 1
}

PYTHON_BIN=$(find_python) || {
  echo "ERROR: Python 3.${MIN_PYTHON_MINOR}–3.${MAX_PYTHON_MINOR} required."
  echo ""
  print_python_diagnostics
  exit 1
}

if [ "$BACKEND_ONLY" = false ]; then
  ensure_node
fi

PY_VERSION=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "==> Using Python $PY_VERSION ($PYTHON_BIN)"
if [ "$BACKEND_ONLY" = false ]; then
  NODE_VERSION=$(node -v)
  NPM_VERSION=$(npm -v)
  echo "==> Using Node $NODE_VERSION, npm $NPM_VERSION"
fi
echo ""

# --- Backend ---
echo "==> Setting up backend..."
cd "$ROOT/backend"

if [ -d .venv ]; then
  if [ -f .venv/pyvenv.cfg ]; then
    OLD_PY=$(grep '^version' .venv/pyvenv.cfg | cut -d= -f2 | tr -d ' ')
    OLD_MINOR=${OLD_PY#*.}
    OLD_MINOR=${OLD_MINOR%%.*}
    if [ -n "$OLD_MINOR" ] && { [ "$OLD_MINOR" -lt "$MIN_PYTHON_MINOR" ] || [ "$OLD_MINOR" -gt "$MAX_PYTHON_MINOR" ]; }; then
      echo "    Removing old .venv (Python $OLD_PY — need 3.${MIN_PYTHON_MINOR}–3.${MAX_PYTHON_MINOR})..."
      rm -rf .venv
    fi
  elif [ -x .venv/bin/python ]; then
    VENV_MINOR=$(.venv/bin/python -c 'import sys; print(sys.version_info.minor)')
    if [ "$VENV_MINOR" -lt "$MIN_PYTHON_MINOR" ] || [ "$VENV_MINOR" -gt "$MAX_PYTHON_MINOR" ]; then
      echo "    Removing old .venv (Python 3.$VENV_MINOR — need 3.${MIN_PYTHON_MINOR}–3.${MAX_PYTHON_MINOR})..."
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

echo "==> Waiting for backend..."
BACKEND_READY=false
for _ in $(seq 1 30); do
  if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    BACKEND_READY=true
    echo "    Backend ready at http://localhost:8000/health"
    break
  fi
  sleep 1
done
if [ "$BACKEND_READY" = false ]; then
  echo "    WARNING: Backend did not respond on :8000 — check errors above"
fi

if [ "$BACKEND_ONLY" = true ]; then
  echo ""
  echo "==> Backend only. API: http://localhost:8000/health"
  echo "==> Press Ctrl+C to stop."
  wait "$BACKEND_PID"
  exit 0
fi

# --- Frontend ---
echo "==> Setting up frontend..."
cd "$ROOT/frontend"
npm install --silent

if [ ! -f .env ]; then
  cp .env.example .env
fi
# Route API through Vite proxy in local dev (avoids CORS and connection issues)
if grep -q '^VITE_API_URL=' .env; then
  sed -i.bak 's|^VITE_API_URL=.*|VITE_API_URL=|' .env && rm -f .env.bak
else
  echo 'VITE_API_URL=' >> .env
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
