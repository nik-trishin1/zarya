#!/bin/sh
set -eu

PORT="${PORT:-8080}"
API_UPSTREAM="${API_UPSTREAM:-}"
API_UPSTREAM="${API_UPSTREAM%/}"
API_UPSTREAM="$(printf '%s' "${API_UPSTREAM}" | tr -d '[:space:]')"

if [ -z "${API_UPSTREAM}" ]; then
  echo "ERROR: API_UPSTREAM is not set on Railway (frontend service)."
  echo "Example: API_UPSTREAM=https://zarya-production-be.up.railway.app"
  exit 1
fi

case "${API_UPSTREAM}" in
  http://*|https://*) ;;
  *)
    API_UPSTREAM="https://${API_UPSTREAM}"
    echo "API_UPSTREAM missing scheme — using: ${API_UPSTREAM}"
    ;;
esac

# Railway may route public traffic to port 80 while setting PORT=8080 for healthchecks.
if [ "${PORT}" = "80" ]; then
  NGINX_EXTRA_LISTEN=""
else
  NGINX_EXTRA_LISTEN="listen 80;"
fi

export PORT API_UPSTREAM NGINX_EXTRA_LISTEN
envsubst '${PORT} ${API_UPSTREAM} ${NGINX_EXTRA_LISTEN}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "nginx listening on 0.0.0.0:${PORT}${NGINX_EXTRA_LISTEN:+, 0.0.0.0:80}, proxying API to: ${API_UPSTREAM}"
nginx -t
exec nginx -g 'daemon off;'
