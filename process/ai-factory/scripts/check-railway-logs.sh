#!/usr/bin/env bash
# Portable Railway log scanner for CI.
# Skips (exit 0) when RAILWAY_TOKEN is unset — forks stay green.
# Fails (exit 1) when token is set and error signatures appear in recent logs.
set -euo pipefail

if [[ -z "${RAILWAY_TOKEN:-}" ]]; then
  echo "Railway log scan skipped: RAILWAY_TOKEN secret not configured."
  exit 0
fi

SERVICE_NAMES="${RAILWAY_SERVICE_NAMES:-}"
if [[ -z "$SERVICE_NAMES" ]]; then
  echo "Railway log scan skipped: RAILWAY_SERVICE_NAMES is empty."
  echo "Set a repo variable like: zarya-backend,zarya-frontend"
  exit 0
fi

ENVIRONMENT="${RAILWAY_ENVIRONMENT:-production}"
LINES="${RAILWAY_LOG_LINES:-200}"
# Extended regex; override with RAILWAY_ERROR_GREP if needed.
ERROR_GREP="${RAILWAY_ERROR_GREP:-Traceback|CRITICAL|Unhandled|[[:space:]]ERROR[[:space:]]|Exception:|FATAL|panic:}"
CHECK_HTTP="${RAILWAY_CHECK_HTTP:-1}"

echo "Installing Railway CLI…"
curl -fsSL https://railway.com/install.sh | sh
export PATH="${HOME}/.railway/bin:${PATH}"
command -v railway >/dev/null

extra_args=()
if [[ -n "${RAILWAY_PROJECT_ID:-}" ]]; then
  extra_args+=(--project "$RAILWAY_PROJECT_ID")
fi
extra_args+=(--environment "$ENVIRONMENT")

failed=0
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

IFS=',' read -r -a services <<< "$SERVICE_NAMES"
for raw in "${services[@]}"; do
  service="$(echo "$raw" | xargs)"
  [[ -z "$service" ]] && continue

  echo "────────────────────────────────────────"
  echo "Deploy logs: service=$service env=$ENVIRONMENT lines=$LINES"
  deploy_file="$tmpdir/${service}.deploy.log"
  if ! railway logs --service "$service" --lines "$LINES" "${extra_args[@]}" >"$deploy_file" 2>"$tmpdir/${service}.deploy.err"; then
    echo "WARN: failed to fetch deploy logs for $service:"
    cat "$tmpdir/${service}.deploy.err" || true
    failed=1
    continue
  fi

  if grep -E "$ERROR_GREP" "$deploy_file" >/dev/null; then
    echo "FAIL: error signatures in deploy logs for $service:"
    grep -E "$ERROR_GREP" "$deploy_file" | tail -n 50 || true
    failed=1
  else
    echo "OK: no error signatures in deploy logs for $service"
  fi

  if [[ "$CHECK_HTTP" == "1" ]]; then
    echo "HTTP 5xx (last ${LINES} matching): service=$service"
    http_file="$tmpdir/${service}.http.log"
    if railway logs --http --service "$service" --status ">=500" --lines "$LINES" "${extra_args[@]}" >"$http_file" 2>"$tmpdir/${service}.http.err"; then
      if [[ -s "$http_file" ]] && grep -q '[^[:space:]]' "$http_file"; then
        echo "FAIL: recent HTTP 5xx for $service:"
        tail -n 50 "$http_file" || true
        failed=1
      else
        echo "OK: no recent HTTP 5xx for $service"
      fi
    else
      echo "WARN: HTTP log fetch failed for $service (service may lack HTTP logs):"
      cat "$tmpdir/${service}.http.err" || true
    fi
  fi
done

if [[ "$failed" -ne 0 ]]; then
  echo "Railway log scan failed. Inspect deploy/HTTP errors above before merging."
  exit 1
fi

echo "Railway log scan passed."
