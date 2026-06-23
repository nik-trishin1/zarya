#!/bin/sh
set -eu

PORT="${PORT:-80}"
API_UPSTREAM="${API_UPSTREAM:-}"

# Remove trailing slash so nginx proxy_pass keeps /api/... path
API_UPSTREAM="${API_UPSTREAM%/}"

if [ -z "${API_UPSTREAM}" ]; then
  echo "ERROR: API_UPSTREAM is not set. Example: https://your-backend.up.railway.app"
  exit 1
fi

export PORT API_UPSTREAM
envsubst '${PORT} ${API_UPSTREAM}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "nginx listening on port ${PORT}, proxying API to: ${API_UPSTREAM}"
exec nginx -g 'daemon off;'
