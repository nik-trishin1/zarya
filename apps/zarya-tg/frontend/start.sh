#!/bin/sh
set -eu

PORT="${PORT:-8080}"
API_UPSTREAM="${API_UPSTREAM:-}"
API_UPSTREAM="${API_UPSTREAM%/}"

if [ -z "${API_UPSTREAM}" ]; then
  echo "ERROR: API_UPSTREAM is not set on Railway (frontend service)."
  echo "Example: API_UPSTREAM=https://zarya-production-be.up.railway.app"
  exit 1
fi

export PORT API_UPSTREAM
envsubst '${PORT} ${API_UPSTREAM}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "nginx listening on 0.0.0.0:${PORT}, proxying API to: ${API_UPSTREAM}"
nginx -t
exec nginx -g 'daemon off;'
