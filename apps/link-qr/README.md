# link-qr

Personal short-link + QR + UTM click analytics (v1). Sibling app to `zarya-tg` — no coupling into the Mini App.

## What it does

1. Create a short link (`/r/{slug}`) with optional default UTMs.
2. Download a PNG QR (`/qr/{slug}.png`).
3. Count clicks with breakdown by `utm_source` / `medium` / `campaign` / `content` / `term`.

Admin surfaces (`/`, `POST /links`, `/stats/{slug}`) require `ADMIN_TOKEN` (cookie after `/login`, form field, or `X-Admin-Token` header). Public: `/r/{slug}`, `/qr/{slug}.png`, `/health`.

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | yes (prod) | Postgres URL (`postgresql://…`) or local SQLite |
| `ADMIN_TOKEN` | yes | Shared secret for create + stats |
| `PUBLIC_BASE_URL` | yes (prod) | Canonical public origin used in short URLs and QR payloads |
| `PORT` | no | Default `8000` |

## Local run

```bash
cd apps/link-qr
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ADMIN_TOKEN=dev-token
export DATABASE_URL=sqlite+aiosqlite:///./link_qr.db
export PUBLIC_BASE_URL=http://localhost:8000
export PYTHONPATH=.

python run.py
```

Open `http://localhost:8000`, log in with `ADMIN_TOKEN`, create a link.

## Tests

```bash
cd apps/link-qr
pip install -r requirements.txt
ADMIN_TOKEN=test-token DATABASE_URL=sqlite+aiosqlite:///./test.db \
  PUBLIC_BASE_URL=http://test PYTHONPATH=. pytest -q
```

## Deploy (Railway)

- New service rooted at `apps/link-qr/` (uses `Dockerfile` + `railway.toml`).
- Attach its own Postgres; set `DATABASE_URL`, `ADMIN_TOKEN`, `PUBLIC_BASE_URL`.
- Healthcheck: `GET /health`.

## UTM merge on redirect

Request query wins. Missing `utm_*` keys are filled from the link’s `default_utm_json`. Non-UTM query params from the request are preserved on the destination. One `clicks` row is written per hit.

## Out of scope (v1)

Multi-user auth, public API, CSV export, geo, bots filtering, zarya-tg product integration. For Zarya campaigns, paste these short links manually.
