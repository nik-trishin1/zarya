# zarya-tg — Launch / ops checklist

Process only: verify and document. No feature work from this list. Status as of 2026-11-26 (items 1, 3, 5 rechecked); update the **Status** and **Evidence** columns when an item is checked.

**Status:** `known` = evidence in repo/CI/ticket history · `unknown` = needs a human or dashboard check · `gap` = known not done.

**Do not change without the owner (Nikita):** Railway secrets and variables, bot token, production DB schema.

| # | Item | Status | Evidence / next check |
|---|------|--------|-----------------------|
| 1 | CI Railway log scan has `RAILWAY_TOKEN` (secret) + `RAILWAY_SERVICE_NAMES` (variable) | **gap** | Re-verified 2026-11-26. Workflow wiring is correct: job `railway-logs` in [`ci.yml`](../../../.github/workflows/ci.yml) passes `secrets.RAILWAY_TOKEN` and `vars.RAILWAY_SERVICE_NAMES` / `RAILWAY_ENVIRONMENT` / `RAILWAY_PROJECT_ID` / `RAILWAY_LOG_LINES` to `process/ai-factory/scripts/check-railway-logs.sh`. Latest `main` CI run (2026-11-18, run 44251904427) still prints `Railway log scan skipped: RAILWAY_TOKEN secret not configured.` (`RAILWAY_SERVICE_NAMES` was empty too). Secret/variable values and existence are not readable by agents (GitHub API 403) — **owner must set by hand**: Settings → Secrets and variables → Actions → secret `RAILWAY_TOKEN` (Railway project token, `zarya-friends` / production) and variable `RAILWAY_SERVICE_NAMES` = `be,fe` (real Railway service names; the `zarya-backend,zarya-frontend` example in `CI.md` does not match prod). Optional: `RAILWAY_ENVIRONMENT=production`. After setting, re-run CI on `main` and expect `Deploy logs: service=be …` instead of `skipped`. Once the token is set the job fails on `Traceback`, `CRITICAL`, `Unhandled`, ` ERROR `, `Exception:`, `FATAL`; prod logs currently contain transient aiogram polling retries (Telegram `Bad Gateway` / timeouts) that look like `ERROR:aiogram.dispatcher:…` — watch the first runs for false positives and tune `RAILWAY_ERROR_GREP` only with the owner. |
| 2 | Telegram bot webhook configured | **n/a (polling)** | The bot uses long polling (`dp.start_polling` in `backend/app/bot/handlers.py`; guide checks the `Telegram bot polling started` log line in [`deploy-railway.md`](deploy-railway.md)). No webhook is configured by design. Check instead: exactly one backend process per `BOT_TOKEN` (no local `dev-local.sh` with the prod token). Switching to webhook needs an ADR. |
| 3 | Backend deployed and healthy on Railway | **known (prod running; rechecked 2026-11-26)** | T-213/214/215 confirmed on prod by the owner (see [`tasks-archive.md`](tasks-archive.md)). Recheck: backend logs show `Telegram bot polling started`; `GET <frontend>/api/events` returns `{"detail":"Missing Telegram init data"}`. | Rechecked 2026-11-26: `be` and `fe` deployments `SUCCESS` (last deploy 2026-11-18), `Postgres` `SUCCESS`; `GET /api/events` → `401 Missing Telegram init data`; 7-day 5xx rate 0% on both (only ~5 requests — no real traffic yet); latest `be` runtime logs (101 lines) contain only transient aiogram `Bad Gateway` / timeout retries followed by `Connection established`, no tracebacks. The `Telegram bot polling started` line is outside the log window — it appears only at process start.
| 4 | Frontend deployed and healthy (static + nginx proxy) | **known (prod running)** | Same evidence. Recheck `API_UPSTREAM` points at backend; `VITE_API_URL` unset ([`deploy-railway.md`](deploy-railway.md) troubleshooting). |
| 5 | Production env sane (`DEV_MODE=false`, `WEBAPP_URL` public HTTPS, `CORS_ORIGINS`) | **known (mostly) — owner confirms values** | Read-only check 2026-11-26 (Railway project `zarya-friends`, env `production`, service `be`; no variables changed, no values printed). **DEV_MODE:** variable is set on `be`, but Railway MCP returns names only, so its literal value was not read. Behavioural proof it is effectively off: `GET https://zarya-production-fe.up.railway.app/api/events` without Telegram init data → `401 {"detail":"Missing Telegram init data"}` (with `DEV_MODE=true` the backend skips auth and returns 200 — `Settings.allow_browser_dev`). **CORS:** request with `Origin: https://evil.example` gets no `access-control-allow-origin` header and preflight returns 400, so `CORS_ORIGINS` is not `*`. **WEBAPP_URL / ADMIN_TELEGRAM_IDS / BOT_TOKEN / SECRET_KEY:** names present on `be`; values unverified. Frontend is served over HTTPS (`200`). Owner by hand: Railway → `zarya-friends` → `be` → Variables: `DEV_MODE` is `false` or empty, `WEBAPP_URL` = `https://zarya-production-fe.up.railway.app`, `CORS_ORIGINS` lists the frontend URL + `https://web.telegram.org`, `SECRET_KEY` is not `change-me-in-production`, `ADMIN_TELEGRAM_IDS` contains your id. |
| 6 | End-to-end run with real Telegram accounts (list → register → cancel → `.ics` → admin `/admin` create/edit) | **unknown** | No recorded e2e run in docs. One non-admin and one admin account; note result under Evidence. |
| 7 | Pilot: invite ~20 users, validate flows | **unknown** | No pilot record found. Define success before inviting: registration completes, reminders arrive, no 5xx in logs. |
| 8 | Triage bugs from the pilot | **unknown** (blocked by 7) | One backlog line per bug in [`tasks.md`](tasks.md); bugfixes skip NMT/DoR. |
| 9 | Optional: Cursor Automation `factory-implement` | **gap (optional)** | Not created. Prompt and operator checklist: [`process/ai-factory/ORCHESTRATOR.md`](../../../process/ai-factory/ORCHESTRATOR.md). Dry-run on one DoR ticket first; no ticket is DoR-ready today (`tasks.md`). |

## After ship (each product change with a user-visible claim)

- [ ] Open a followthrough row in Project store `docs/followthrough/<change-id>.md` (template: [`process/ai-factory/FOLLOWTHROUGH.md`](../../../process/ai-factory/FOLLOWTHROUGH.md)): baseline, expected effect, check-by date, owner. Link that path from the PR and ticket; record the verdict `keep` / `tweak` / `rollback` in the same store file after the check (do not leave the only copy in a closed PR body).

## Order

1 → 5 (owner, short) → 6 → 7 → 8. Item 9 waits until a DoR-ready ticket exists.

## Open questions for the owner

- Is the pilot already informally running (items 6–7 may be done but unrecorded)?
- Should the Railway scan stay a skip-on-missing-token no-op, or become a required gate once the token is set?
