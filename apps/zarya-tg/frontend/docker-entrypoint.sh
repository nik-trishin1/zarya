#!/bin/sh
set -eu

API_UPSTREAM="${API_UPSTREAM:-http://localhost:8000}"
# Remove trailing slash so nginx proxy_pass keeps /api/... path
API_UPSTREAM="${API_UPSTREAM%/}"

if [ -z "${API_UPSTREAM}" ]; then
  echo "ERROR: API_UPSTREAM is not set. Example: https://your-backend.up.railway.app"
  exit 1
fi

export API_UPSTREAM
envsubst '${API_UPSTREAM}' < /etc/nginx/templates/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "nginx proxying API to: ${API_UPSTREAM}"
exec nginx -g 'daemon off;'
